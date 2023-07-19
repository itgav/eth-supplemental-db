# TERMINAL: python -m scrape_blockchain.add_state_and_slots

# GOAL:
################################################################################################

# SUMMARY
#############################################################################################
# Get the wallet/token/value data that shows how a wallet's ETH or token balance was altered from a tx
# Get each token contract's storage slot that represents the balance of each specific wallet
# Add the balance change and storage slot data to the database tables
#############################################################################################

# CAVEATS
#############################################################################################
# The method to link wallet addresses to contract storage slot is probably 95%+ correct, but is not fool proof
#   Additionally, it can create many-to-1 links between records/wallets and storage slots in the 'contract_storage' table
#   ... will address the dupes in a later script/methodology. I do not in this script for simplicity and speed.
#############################################################################################

import os
import sys
import concurrent.futures
import time
import requests
import psycopg2
import math
import tracemalloc
import psutil
import itertools

# my files
from scripts.utility_misc import env_var, node_rpc_command
from scripts.utility_scrape import add_to_csv
from scripts.utility_db import db_fetch_data
from scripts.utility_db_admin import import_csv_to_db, remove_dup_key


DB_NAME = env_var("DB_NAME")
DB_USER = env_var("DB_USER")
DB_PASSWORD = env_var("DB_PASSWORD")

STATEDIFF_TABLE = "public.tx_state_diff"
CONTRACT_STORAGE_TABLE = "public.contract_storage"

MY_URL = env_var("MY_URL")
NORMAL_BAL_SIGNATURE = env_var("NORMAL_BAL_SIGNATURE")
ERC1155_BAL_SIGNATURE = env_var("ERC1155_BAL_SIGNATURE")
# Web3.keccak(text=transfer_function_code).hex()
# Transfer(address _from, address _to, uint256 _value)
# TransferSingle(address _operator, address _from, address _to, uint256 _id, uint256 _value)
# TransferBatch(address _operator, address _from, address _to, uint256[] _ids, uint256[] _values)
#   - equivalent to multiple {TransferSingle} events, where `operator`, `from` and `to` are the same for all transfers.
# Sent(address _operator, address _from, address _to, uint256 _amount, bytes _data, bytes _operatorData)
TRANSFER_HEX = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
TRANSFER_SINGLE_HEX = "0xc3d58168c5ae7397731d063d5bbf3d657854427343f4c083240f7aacaa2d0f62"
TRANSFER_BATCH_HEX = "0x4a39dc06d4c0dbc64b70af90fd698a233a518aa5d07e595d983b8c0526c8f7fb"
SENT_ERC77_HEX = "0x06b541ddaa720db2b10a4d0cdac39b8d360425fc073085fac19bc82614677987"


##################################################################################################################################
# functions 'parse_op', 'parse_trace', and 'dump_stack' are taken from the GitHub repository 'erc20-scanner' by 'meronym'
#   - link: https://github.com/meronym/erc20-scanner
def parse_op(op, values):
    # op = { 'cost': int, 'ex': {}, 'pc': int, 'sub': <trace or null> }
    for val in op["ex"]["push"]:
        assert val.startswith("0x") and len(val) <= 2 + 64
        values.add("0x" + val[2:].zfill(64))
    if op["sub"] is not None:
        parse_trace(op["sub"], values)


def parse_trace(trace, values):
    # trace = { 'code': '', 'ops': [op1, op2, ...] }
    for op in trace["ops"]:
        parse_op(op, values)


def dump_stack(trace):
    values = set()
    # double recursivity ftw
    parse_trace(trace, values)
    return values


##################################################################################################################################

# will try to send post request until reach 'attempt_threshold'
# I've only seen this come into play when sockets get filled and need a cool down.
# If get an error because sockets fill up, can reduce their 'TIME_WAIT' in the registry
def try_x_times(session, request_args, attempt_threshold, wait_time):
    for i in range(attempt_threshold):
        try:
            x_result = session.post(MY_URL, json=request_args).json()
            break
        except Exception as x_exception:
            print(f"ERROR: {x_exception}")
            if i != attempt_threshold - 1:
                time.sleep(wait_time)
    else:
        print("ERROR: unable to execute without error")
        # print(f"Args to the ERROR: {request_args}")
        x_result = None

    return x_result


# returns two lists: 'trace_state_data' and 'contract_storage'
#   'trace_state_data': has a tuple for each address and token that had a balance change and the resulting change
#   'contract_storage': has a tuple for each address and the token/storage_slot combo that corresponds to the storage_slot for their token balance
# scrape_state_and_storage(int, int)
def scrape_state_and_storage(start_block, total_blocks):
    attempt_threshold = 1
    wait_time = 15
    # trace_state_data = [(tx_hash, block_no, wallet_address, token_address, token_id, start_value, end_value), ]
    trace_state_data = []
    # storage_data = [(token_address, token_id, wallet_address, storage_slot), ]
    storage_data = []

    # using a session so that sockets can be re-used and therefore, don't need a "TIME_WAIT" after each request
    with requests.Session() as s:
        for block_no in range(start_block, start_block + total_blocks):
            # print(f"{block_no = }, {os.getpid() = }")

            #############################################################################################
            # BLOCK TRACES & ETH VALUE CHANGES
            #############################################################################################
            rpc_values = {"id": 1, "jsonrpc": "2.0",
                          "method": "trace_replayBlockTransactions", "params": [block_no, ["stateDiff"]]}
            block_traces = try_x_times(s, rpc_values, attempt_threshold, wait_time)
            # have seen an inaccurate trace issue due to the tx sender supposedly not having enough for gas+fees... See: https://github.com/ledgerwatch/erigon/issues/7747
            if 'error' in block_traces:
                print(
                    f"ERROR: couldn't 'trace_replayBlockTransactions' for {block_no = }. {block_traces['error']['message']}")
                # !!! will skip for now. Need to figure out if this is the correct behavior for the RPC. I don't think it is. Waiting to hear back from Erigon.
                continue
            else:
                block_traces = block_traces['result']
            block_traces = {tx_trace["transactionHash"]: tx_trace["stateDiff"] for tx_trace in block_traces}

            # receipt data is limited based on state data but state data such as 'contract_slot_tx' is not limited based on receipt data.
            #   reason being, boils down to state data being the truth and receipt data is just the events that the contract devs choose to emit
            #   if we find a combo from 'call_combos' that matches a slot to the wallet address, then we want the state data where the slot changes regardless of
            #   ... whether or not the 'tx' produces appropriate logs to lead to a 'call_combo'
            # {contract_1: {slot_1: {tx_hash_1, tx_hash_n}, }, contract_2: {{}}, }
            contract_slot_tx = {}
            # tx_altered_contracts = # {tx_hash_1: {contract_1, contract_2}, tx_hash_2: {}, }
            tx_altered_contracts = {tx_hash: {
                x_contract for x_contract in block_traces[tx_hash] if block_traces[tx_hash][x_contract]["storage"] != {}} for tx_hash in block_traces}
            for tx_hash in block_traces:
                state = block_traces[tx_hash]
                # tx_altered_contracts = {tx_hash: {x_contract for x_contract in block_traces[tx_hash] if state[x_contract]["storage"] != {}}}
                if tx_altered_contracts[tx_hash] != set():  # altered contracts
                    # add data to 'contract_slot_tx'
                    # contract_slot_tx = {} # {contract_1: {slot_1: {tx_hash_1, tx_hash_n}, }, contract_2: {{}}, }
                    for x_contract in tx_altered_contracts[tx_hash]:
                        if x_contract not in contract_slot_tx:  # add nested dictionary and key
                            contract_slot_tx[x_contract] = {}
                        for x_slot in state[x_contract]["storage"]:
                            # update set of tx_hashes
                            if x_slot in contract_slot_tx[x_contract]:
                                contract_slot_tx[x_contract][x_slot].add(
                                    tx_hash)
                            else:  # add a set w/ tx_hash
                                contract_slot_tx[x_contract][x_slot] = {tx_hash}
                else:  # no altered contracts -> delete empty key w/ empty value of set()
                    del tx_altered_contracts[tx_hash]

                #############################################################################################
                # GET ETH VALUE CHANGES
                #############################################################################################
                # balance characters: "*", "+", "="
                #   seem to mean: "*" -> altered an existing ETH balance; "+" -> 1st ETH balance; "=" -> no change
                for x_address in state:
                    # if ETH balance changed, data stucture will be like:
                    #   'balance': {'*': {'from': '0x19444fd2e4fef4ab16', 'to': '0x19468b18eb86f6b3ea'}}
                    # if no ETH change then:
                    #   'balance': '='
                    balance_key = list(state[x_address]["balance"])[0]

                    # get ETH values for the addresses
                    if "*" == balance_key:  # convert change in ETH balance
                        start_value = int(
                            state[x_address]["balance"]["*"]["from"], 16)
                        end_value = int(
                            state[x_address]["balance"]["*"]["to"], 16)
                    elif "+" == balance_key:  # convert initial ETH balance
                        start_value = 0
                        end_value = int(state[x_address]["balance"]["+"], 16)
                    else:  # no alteration of ETH balance for the address
                        pass

                    # !!!!!!!! not sure if start_value should ever equal end_value, but I've seen it --> find examples
                    # if ETH value changed then append data
                    if balance_key in {"*", "+"} and start_value != end_value:
                        # trace_state_data = [(tx_hash, block_no, wallet_address, token_address, token_id, start_value, end_value), ]
                        trace_state_data.append(
                            (tx_hash, block_no, x_address, "ETH", "N/A", start_value, end_value))

            #############################################################################################
            # GET AND FILTER BLOCK RECEIPTS
            #############################################################################################
            # from 'transfer' events, get 'address that emitted', 'from'/'to' addresses and 'token_id' if the token has one
            rpc_values = {"id": 1, "jsonrpc": "2.0",
                          "method": "eth_getBlockReceipts", "params": [block_no]}
            block_receipts = try_x_times(
                s, rpc_values, attempt_threshold, wait_time)
            # haven't noticed any issues yet but implementing as a countermeasure so the scrape continues
            if 'error' in block_receipts:
                print(
                    f"ERROR: couldn't 'eth_getBlockReceipts' for {block_no = }. {block_receipts['error']['message']}")
                continue
            else:
                block_receipts = block_receipts['result']

            # block_receipts = {tx_hash_1 : [{address: x, topics: [x,x,x], data: x}, {log_2}], tx_hash_2: [{}, {}]}
            # doing quite a bit of filtering in the dict comprehensions:
            #   - only logs that are transfer events
            #   - where actual logs/topics aren't blank -> tx_log["topics"] == [] # ex: tx_hash = '0x43b196f07af5b601312282cf606ab79256f9fe9a8829f30bec9e54bf3a6168fb'
            #   - that have a tx_hash in 'tx_altered_contracts'
            #   - ... in following logic will limit so that log emitting address is in 'tx_altered_contracts'
            block_receipts = {tx_receipt["transactionHash"]: [{"address": tx_log["address"], "topics": tx_log["topics"], "data": tx_log["data"]} for tx_log in tx_receipt["logs"] if tx_log["topics"] != [] and tx_log["topics"][0] in {
                TRANSFER_HEX, TRANSFER_SINGLE_HEX, TRANSFER_BATCH_HEX, SENT_ERC77_HEX}] for tx_receipt in block_receipts if tx_receipt["logs"] != [] and tx_receipt["transactionHash"] in tx_altered_contracts}

            #############################################################################################
            # GET 'call_combos' TO THEN LOOP OVER AND TRY TO FIND STORAGE SLOT MATCH W/ STATEDIFF
            #############################################################################################
            call_combos = set()  # will hold the unique (contract, wallet, token_id) combinations to then use 'trace_call' 'balanceOf()'
            # ... for block 14,001,200 -> using 'call_combos' to limit to only the unique combos cuts down the 'trace_call' from 317 to 242
            for tx_hash in block_receipts:
                for log in block_receipts[tx_hash]:
                    # the log emitting address has altered storage slots
                    if log["address"] in tx_altered_contracts[tx_hash]:
                        topic_list = [x for x in log["topics"]]
                        # if less than normal topics and event info is in the 'data' field --> aggregate relevant data in 'topics_list'
                        #   ex: tx_hash = '0x6c84d8aabdd43d99277bc1485cdf87363fa122a88766ab4d38e640c49c492641'
                        # 322 = 2 + 64*5 --> 5 is the most we would ever need for the data we want from the transfer events (based on transfer event ABI)
                        log_data = log["data"][2:322]
                        for i in range(int(len(log_data) / 64)):
                            topic_list.append("0x" + log_data[:64])
                            log_data = log_data[64:]

                        if log["topics"][0] == TRANSFER_HEX:
                            from_addr = "0x" + topic_list[1][26:]  # from address
                            to_addr = "0x" + topic_list[2][26:]  # to address
                            token_id = "N/A"  # only have ID for ERC-1155 transfers
                        elif log["topics"][0] in {TRANSFER_SINGLE_HEX, TRANSFER_BATCH_HEX}:
                            from_addr = "0x" + topic_list[2][26:]
                            to_addr = "0x" + topic_list[3][26:]
                            token_id = topic_list[4]
                        else:  # ERC-777 "sent"
                            from_addr = "0x" + topic_list[2][26:]
                            to_addr = "0x" + topic_list[3][26:]
                            token_id = "N/A"

                        call_combos.add((log["address"], from_addr, token_id))
                        call_combos.add((log["address"], to_addr, token_id))
            # del block_traces # --> if do this then get an 'UnboundLocalError'

            #############################################################################################
            # TRY TO MATCH STORAGE SLOTS/TOKEN BALANCES TO WALLET ADDRESSES
            #############################################################################################
            # assumptions to constitute match between address and contract storage slot:
            #   - address is the from/to address in the transfer/sent event log
            #   - contract is the 'address' that emitted the transfer/sent event log
            #   - storage slot from the 'stateDiff' is the only storage slot match when calling 'balanceOf()' for the address
            #   - the 'balanceOf()' call doesn't REVERT and doesn't produce the output '0x'

            rpc_list = []
            rpc_id = 0
            # try calling the 'balanceOf()' function for the token_contract, w/ the x_address
            #   will use the results to see if there's an intersection between the token_contract's storage slots and the trace results
            #   will use batch RPC calls to speed up the process
            # 'call_combos' = {(emit_address, wallet_address, token_id), }
            for x_combo in call_combos:
                rpc_id += 1
                x_contract = x_combo[0]
                x_address = x_combo[1]
                x_id = x_combo[2]
                sender_address = x_address[2:]
                sender_address = (64 - len(sender_address)) * "0" + sender_address

                if x_id == "N/A":
                    data = NORMAL_BAL_SIGNATURE + sender_address
                else:  # ERC-1155 which requires a token ID
                    data = ERC1155_BAL_SIGNATURE + sender_address + x_id[2:]
                    # converting now to avoid logic when appending to 'trace_state_data'
                    x_id = str(int(x_id, 16))

                rpc_values = {"id": rpc_id, "jsonrpc": "2.0", "method": "trace_call", "params": [
                    {"data": data, "to": x_contract}, ["trace", "vmTrace"], block_no]}
                rpc_list.append(rpc_values)
            # print(rpc_list)

            # if there are log_transfer events
            if rpc_id > 0:
                # erigon default is 100. I didn't notice much performance improvement in changing batch size
                batch_limit = 100
                total_batches = math.ceil(rpc_id / batch_limit)
                batch_len = math.ceil(rpc_id / total_batches)
                starting_index = 0
                for i in range(total_batches):
                    # print(f"{batch_limit = }, {total_batches = }, {batch_len = }, {starting_index = }")
                    batch_rpc_list = rpc_list[starting_index: starting_index + batch_len]
                    starting_index += len(batch_rpc_list)

                    # for some will get the error: "maximum recursion depth exceeded while decoding a JSON array from a unicode string"
                    #   ex: rpc_values = {'id': 1, 'jsonrpc': '2.0', 'method': 'trace_call', 'params': [{'data': '0x70a082310000000000000000000000004fbc9b2eb49dbb61d760cda57561b24048a2b25b', 'to': '0x0144b7e66993c6bfab85581e8601f96bfe50c9df'}, ['trace', 'vmTrace'], 14496182]}
                    #   you can bypass this by increasing Python's limit -> just Google and you'll see
                    #   the couple tx I looked into where it occurred, they seemed like garbage token contracts that are incorrectly relating 'balanceOf' and the balance mapping to each other
                    total_bal_trace = try_x_times(s, batch_rpc_list, attempt_threshold, wait_time)
                    if total_bal_trace is None:  # there was an error, will do individual RPC calls -> likely due to recusion limit
                        total_bal_trace = []
                        for x_rpc in batch_rpc_list:
                            x_trace = try_x_times(s, x_rpc, attempt_threshold, wait_time)
                            if x_trace is not None:
                                total_bal_trace.append(x_trace)

                    # if total_bal_trace is not None:
                    # derive info from the trace results to then append to the data lists
                    for bal_trace in total_bal_trace:
                        x_contract = bal_trace["result"]["trace"][0]["action"]["to"]
                        bal_trace_input = bal_trace["result"]["trace"][0]["action"]["input"]
                        if len(bal_trace_input) == 74:
                            x_address = "0x" + bal_trace_input[34:]
                            x_id = "N/A"
                        elif len(bal_trace_input) == 138:
                            x_address = "0x" + bal_trace_input[34:74]
                            x_id = str(int("0x" + bal_trace_input[74:], 16))
                        else:
                            # haven't ever seen this happen
                            print(bal_trace_input)
                            print(len(bal_trace_input))
                            print("ERROR: len(bal_trace) != 74 or 138")
                            break

                        # should only get error if the call is reverted, which means the contract doesn't have a function ABI that matches our sent data
                        # ... or, the output is '0x' which, from what I've seen, occurs when the balanceOf() function doesn't match the ABI but its call doesn't REVERT
                        if "error" not in bal_trace["result"]["trace"][0] and bal_trace["result"]["output"] != "0x":
                            # intersection of 'trace_call' slots and stateDiff slots -> if there's a matching slot then assume it's the balance slot for the wallet address
                            slot_match = list(dump_stack(bal_trace["result"]["vmTrace"]) & set(
                                contract_slot_tx[x_contract]))

                            #############################################################################################
                            # APPEND DATA FOR TOKEN BALANCES AND STORAGE SLOT MATCHES
                            #############################################################################################
                            if len(slot_match) == 1:  # if only 1 matching slot, assume it's correct
                                slot_match = slot_match[0]
                                # storage_data = [(token_address, token_id, wallet_address, storage_slot), ]
                                storage_data.append((x_contract, x_id, x_address, slot_match))

                                # get the token value changes from the 'state'
                                for tx_hash in contract_slot_tx[x_contract][slot_match]:
                                    state = block_traces[tx_hash]
                                    # balance characters: "*", "+", "="
                                    #   seem to mean: "*" -> altered and existing slot; "+" -> slots 1st alteration; "=" -> no change

                                    # if storage changed, data stucture will be like:
                                    #   'storage': {'x_slot': {'*': {'from': '0x19444fd2e4fef4ab16', 'to': '0x19468b18eb86f6b3ea'}}}
                                    # if storage new, data stucture will be like:
                                    #   'storage': {'x_slot': {'+': '0x19444fd2e4fef4ab16'}}
                                    # if no storage change then:
                                    #   'storage': {}
                                    balance_key = list(state[x_contract]["storage"][slot_match])[0]

                                    # get storage values (i.e. balances) for the addresses
                                    if "*" == balance_key:  # convert change in token balance
                                        start_value = int(state[x_contract]["storage"][slot_match]["*"]["from"], 16)
                                        end_value = int(state[x_contract]["storage"][slot_match]["*"]["to"], 16)
                                    elif "+" == balance_key:  # convert initial token balance
                                        start_value = 0
                                        end_value = int(state[x_contract]["storage"][slot_match]["+"], 16)
                                    else:  # no alteration of token balance for the address
                                        pass
                                    # trace_state_data = [(tx_hash, block_no, wallet_address, token_address, token_id, start_value, end_value), ]
                                    trace_state_data.append((tx_hash, block_no, x_address,
                                                            x_contract, x_id, start_value, end_value))

    return [trace_state_data, storage_data]


# Execute 'scrape_state_and_storage' with multiple threads
def thread_scrape(start_block_list, block_range_list, max_threads_list):
    # results = []
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    # OLD WAY --> supposedly keeps the 'futures' in memory until all are done
    # results = list(executor.map(scrape_state_and_storage, start_block_list, block_range_list))
    # executor.shutdown(wait=True, cancel_futures=False)

    # NEW WAY --> supposedly releases future from memory when it's done by adding the to the 'results'
    # future_results = {
    #     executor.submit(scrape_state_and_storage, start_block_list[i], block_range_list[i]): i for i in range(len(start_block_list))
    # }

    # for future in concurrent.futures.as_completed(future_results):
    #     results.append(future.result())
    #     future_results.pop(future)
    # executor.shutdown(wait=True, cancel_futures=False)

    ################################################################################
    # Source of some of the inspiration: https://alexwlchan.net/2019/adventures-with-concurrent-futures/
    # all of the memory throttling aspects were my contribution

    n_futures = max_threads_list[0]
    memory_ceil = 90
    memory_floor = 75
    remaining_tasks = len(start_block_list) - n_futures
    remaining_results = len(start_block_list)
    # needs to be an iterable
    tasks_to_do = zip(start_block_list, block_range_list)
    results = []

    with concurrent.futures.ThreadPoolExecutor() as executor:

        # Schedule the first N futures.  We don't want to schedule them all
        # at once, to avoid consuming excessive amounts of memory.
        futures = {executor.submit(scrape_state_and_storage, *task)
                   for task in itertools.islice(tasks_to_do, n_futures)}
        # print(f"outer futures: {futures = }")

        while remaining_results > 0:
            # print("outer while")
            # print(f"{os.getpid() = }, {remaining_results = }, {remaining_tasks = }")
            # print(tasks_to_do)

            # Wait for the next future to complete.
            # the returned values function like an iterator, they pop off once returned
            # returns a tuple of the current set of futures -> (completed, incomplete)
            # Will return as soon as 1 is completed, if multiple are completed then it will return multiple values
            done, futures = concurrent.futures.wait(futures, return_when=concurrent.futures.FIRST_COMPLETED)
            # print(f"{os.getpid() = }, {futures = }, {done = }")

            for fut in done:
                results.append(fut.result())
                remaining_results -= 1

            # time.sleep(3)

            while remaining_tasks > 0 and remaining_results > 0:
                # print("inner while")
                # print(f"{os.getpid() = }, {remaining_tasks = }")

                # returns RAM utilization (90.0% = 90.0)
                current_memory = psutil.virtual_memory()[2]
                if current_memory < memory_ceil:
                    # print(f"{os.getpid() = }, memory < ceil")
                    for task in itertools.islice(tasks_to_do, len(done)):
                        # executor.submit(scrape_state_and_storage, *task)
                        futures.add(executor.submit(scrape_state_and_storage, *task))
                        remaining_tasks -= len(done)

                    # print(f"inner futures: {futures = }")

                    if current_memory < memory_floor:
                        # print(f"{os.getpid() = }, memory < floor")
                        n_plus_futures = 1
                        for task in itertools.islice(tasks_to_do, n_plus_futures):
                            # executor.submit(scrape_state_and_storage, *task)
                            futures.add(executor.submit(scrape_state_and_storage, *task))
                            remaining_tasks -= 1

                        # print(f"inner futures: {futures = }")

    ##############################################################################################

    return results


# execute 'scrape_state_and_storage' with multiple processes and threads
# 'start_block': inclusive
# 'end_block': inclusive
# 'blocks_per_process': max == 'total_blocks', min == 1
# 'blocks_per_scrape': max == 'blocks_per_process', min == 1
def process_scrape(start_block, end_block, blocks_per_process, blocks_per_scrape, max_processes, max_threads):
    #############################################################################################
    # DIVVY UP BLOCK RANGES TO SCRAPE
    #############################################################################################
    # if 'blocks_per_process' isn't a multiple of 'total_blocks' then will have +1 process with the remaining blocks
    # if 'blocks_per_scrape' isn't a multiple of the blocks for that process, then will have +1 scrape with the remaining blocks
    x_start = start_block
    start_block_list = []
    block_range_list = []
    max_threads_list = []
    remaining_blocks = (end_block - start_block) + 1
    blocks_per_process = min(blocks_per_process, remaining_blocks)
    n_processes = math.ceil(remaining_blocks / blocks_per_process)

    for i in range(n_processes):
        n_start_list = []
        n_range_list = []
        n_max_thread_list = []
        n_blocks_per_scrape = min(blocks_per_scrape, blocks_per_process)
        n_scrapes = math.ceil(blocks_per_process / blocks_per_scrape)
        n_remaining_blocks = blocks_per_process
        # print(f"outer |||| {blocks_per_process = }, {n_blocks_per_scrape = }, {start_block = }, {remaining_blocks = }")
        for i in range(n_scrapes):
            # print(f"{blocks_per_process = }, {blocks_per_scrape = }, {start_block = }, {remaining_blocks = }")
            n_start_list.append(start_block)
            n_range_list.append(n_blocks_per_scrape)
            n_max_thread_list.append(max_threads)
            start_block += n_blocks_per_scrape
            remaining_blocks -= n_blocks_per_scrape
            n_remaining_blocks -= n_blocks_per_scrape
            n_blocks_per_scrape = min(n_blocks_per_scrape, n_remaining_blocks)

        blocks_per_process = min(blocks_per_process, remaining_blocks)
        start_block_list.append(n_start_list)
        block_range_list.append(n_range_list)
        max_threads_list.append(n_max_thread_list)

    # print(f"{start_block_list = }")
    # print(f"{block_range_list = }")
    # print(f"{sum([sum(x) for x in block_range_list]) == end_block - x_start + 1}")

    #############################################################################################
    # EXECUTE PROCESSES
    #############################################################################################
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_processes) as executor:
        process_results = executor.map(thread_scrape, start_block_list, block_range_list, max_threads_list)
        executor.shutdown(wait=True, cancel_futures=False)

    # process_results = [thread_results_1,..., thread_results_n]
    # thread_results = [x_block_1,..., x_block_n]
    # x_block = [trace_state_data, storage_data]
    # trace_state_data = [[tx_hash, block_no, wallet_address, token_address, token_id, start_value, end_value], ]
    # storage_data = [[token_address, token_id, wallet_address, storage_slot], ]

    # can't use list comprehension on a generator more than once, so aggregate 'x_block' results here then will parse out
    x_block_results = [x_block for thread_results in process_results for x_block in thread_results]
    trace_state_results = {x for x_block in x_block_results for x in x_block[0]}
    storage_results = {x for x_block in x_block_results for x in x_block[1]}

    return [trace_state_results, storage_results]


# Executing scraping script, add data to CSV, import data to DB
def master_add_state_and_slots(start_block, total_blocks, blocks_per_process, blocks_per_scrape, max_processes, max_threads):
    metrics = {}
    #############################################################################################
    # EXECUTE SCRAPING SCRIPT: 'process_scrape'
    #############################################################################################
    end_block = start_block + total_blocks - 1
    # Found optimal to be 1 for 'blocks_per_process' and 'blocks_per_scrape'
    # blocks_per_process = 1
    # blocks_per_scrape = 1
    start_time = time.perf_counter()
    print(f"Scrape blocks: {start_block = }, {end_block = }")
    # process_scrape(start_block, end_block, blocks_per_process, blocks_per_scrape, max_processes, max_threads)
    results = process_scrape(start_block, end_block, blocks_per_process, blocks_per_scrape, max_processes, max_threads)
    trace_state_results = results[0]
    storage_results = results[1]
    finish_time = time.perf_counter()
    print(f"Scrape finished in {(finish_time - start_time):.3f} seconds")

    #############################################################################################
    # ADD TO DB TABLE: 'tx_state_diff'
    #############################################################################################
    ########################!!!!!!!!!!!!! parameterize so can use a function for both tables
    start_time = time.perf_counter()
    try:
        print("Add trace_state_results to CSV")
        # add_to_csv(relative_path, file_name, data, op_symbol): -> return full_path
        path_to_csv = add_to_csv("./eth_trader_profit/tx_database/csv_files_blockchain/",
                                 "state_diff_data", trace_state_results, "w")
        time.sleep(0.1)

        con = psycopg2.connect(database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
        cur = con.cursor()
        # ???????????? edit return data????
        # import_csv_to_db(connection, cursor, csv_path, db_schema_table): -> return [import_success, x_exception]
        x_import = import_csv_to_db(con, cur, path_to_csv, STATEDIFF_TABLE)
    except Exception as x_exception:
        print(f"ERROR adding CSV to DB: {x_exception}")
        cur.close()
        con.close()
        time.sleep(0.2)
    metrics["trace_state_diff"] = len(trace_state_results)
    del trace_state_results
    finish_time = time.perf_counter()
    print(f"Adding 'tx_state_diff' to DB finished in {(finish_time - start_time):.3f} seconds")

    #############################################################################################
    # ADD TO DB TABLE: 'contract_storage'
    #############################################################################################
    start_time = time.perf_counter()
    try:
        print("Add storage_results to CSV")
        # add_to_csv(relative_path, file_name, data, op_symbol): -> return full_path
        path_to_csv = add_to_csv("./eth_trader_profit/tx_database/csv_files_blockchain/",
                                 "contract_storage_data", storage_results, "w")
        time.sleep(0.1)

        con = psycopg2.connect(database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
        cur = con.cursor()
        # import_csv_to_db(connection, cursor, csv_path, db_schema_table): -> return [import_success, x_exception]
        x_import = import_csv_to_db(con, cur, path_to_csv, CONTRACT_STORAGE_TABLE)
        # ???????????? edit return data????
        # if x_import[1] != "":  # an exception was raised from 'import_csv_to_db'
    except Exception as x_exception:
        print(f"ERROR adding CSV to DB: {x_exception}")
        cur.close()
        con.close()
        time.sleep(0.2)
    metrics["contract_storage"] = len(storage_results)
    del storage_results
    finish_time = time.perf_counter()
    print(f"Adding 'contract_storage' to DB finished in {(finish_time - start_time):.3f} seconds")

    print(metrics)


# Will scrape from 'db_highest_block' until 'latest_block', then from 1 until 'db_lowest_block'
# 'master_add_state_and_slots' scrapes lowest to highest for the amount of blocks inputted
if __name__ == "__main__":
    # PRODUCTION ###########################################################################################
    blockchain_lowest_block = 1
    blockchain_highest_block = int(node_rpc_command("eth_getBlockByNumber", "latest", False)["result"]["number"], 16)

    # CONCURRENCY PARAMETERS -> can alter speed/memory consumption
    # ##### High consumption when not using computer
    # blocks_per_scrape_cycle = 100
    # blocks_per_process = 5
    # blocks_per_scrape = 5
    # max_processes = 5  # 5 seems to work best for me, 6 starts to really push memory at higher total_blocks
    # max_threads = 15  # will only have an impact if 'blocks_per_process' > 'max_threads'
    # ##### Lower consumption so I can work on computer while running
    blocks_per_scrape_cycle = 15
    blocks_per_process = 5
    blocks_per_scrape = 5
    max_processes = 3  # 5 seems to work best for me, 6 starts to really push memory at higher total_blocks
    max_threads = 15  # will only have an impact if 'blocks_per_process' > 'max_threads'
    # ##### debugging
    # blocks_per_scrape_cycle = 1
    # blocks_per_process = 1
    # blocks_per_scrape = 1
    # max_processes = 1  # 5 seems to work best for me, 6 starts to really push memory at higher total_blocks
    # max_threads = 1  # will only have an impact if 'blocks_per_process' > 'max_threads'

    try:
        db_highest_block = db_fetch_data(
            f"SELECT block_number FROM {STATEDIFF_TABLE} ORDER BY block_number DESC LIMIT 1")[0][0]

        db_lowest_block = db_fetch_data(
            f"SELECT block_number FROM {STATEDIFF_TABLE} ORDER BY block_number ASC LIMIT 1")[0][0]
    # if no results (likely because list index out of range... original return is [])
    except Exception as x_exception:
        db_highest_block = 0
        db_lowest_block = 0
        print("ERROR: couldn't query DB for 'db_highest_block' and 'db_lowest_block'. Setting values to zero.")
        print(f"...exception was {x_exception}")

    #!!!!!!!!!!!!!!!!!! adding to skip block# 15,003,063 due to inaccurate trace issue see: https://github.com/ledgerwatch/erigon/issues/7747
    # if db_highest_block == 15003062:
    #     db_highest_block = 15003063

    # print(f"{db_highest_block = }")
    # print(f"{blockchain_highest_block = }")

    # scrape the high blocks
    if db_highest_block < blockchain_highest_block:
        remaining_blocks = blockchain_highest_block - db_highest_block
        while remaining_blocks >= blocks_per_scrape_cycle:
            master_add_state_and_slots(db_highest_block + 1, blocks_per_scrape_cycle, blocks_per_process,
                                       blocks_per_scrape, max_processes, max_threads)
            db_highest_block += blocks_per_scrape_cycle
            remaining_blocks = blockchain_highest_block - db_highest_block
        else:
            master_add_state_and_slots(db_highest_block + 1, remaining_blocks, blocks_per_process,
                                       blocks_per_scrape, max_processes, max_threads)

    # scrape the low blocks
    if db_lowest_block > blockchain_lowest_block:
        remaining_blocks = db_lowest_block - blockchain_lowest_block
        while remaining_blocks >= blocks_per_scrape_cycle:
            master_add_state_and_slots(db_lowest_block - blocks_per_scrape_cycle - 1, blocks_per_scrape_cycle, blocks_per_process,
                                       blocks_per_scrape, max_processes, max_threads)
            db_lowest_block -= blocks_per_scrape_cycle
            remaining_blocks = db_lowest_block - blockchain_lowest_block
        else:
            master_add_state_and_slots(db_lowest_block - remaining_blocks - 1, remaining_blocks, blocks_per_process,
                                       blocks_per_scrape, max_processes, max_threads)
    # PRODUCTION ^^^ ###########################################################################################

    # DEBUG 'scrape_state_and_storage'
    ######################################################
    # start_block = 15003063
    # # scrape_state_and_storage(start_block, total_blocks) -> return [trace_state_data, storage_data]
    # results = scrape_state_and_storage(start_block, 1)
    # print(f"{len(results) = }")
    ######################################################

    # for i in range(3):
    #     start_block = start_block + (i * blocks_per_script)
    #     start_time = time.perf_counter()
    #     # master_add_state_and_slots(start_block, total_blocks)
    #     master_add_state_and_slots(start_block, blocks_per_script)
    #     finish_time = time.perf_counter()
    #     print(f"Main finished in {(finish_time - start_time):.3f} seconds")

    # start_block = 15000000
    # start_time = time.perf_counter()
    # end_block = start_block - 1 + blocks_per_scrape_cycle

    # print(f"{start_block = }, {end_block = }, {end_block - start_block = }")
    # results[0] = 54485, results[1] = 9375
    # results = process_scrape(start_block, end_block, blocks_per_process, blocks_per_scrape, max_processes, max_threads)

    # master_add_state_and_slots(start_block, total_blocks, blocks_per_process, blocks_per_scrape, max_processes, max_threads)
    # results = master_add_state_and_slots(start_block, blocks_per_scrape_cycle, blocks_per_process,
    #                                      blocks_per_scrape, max_processes, max_threads)
    # # print(results[0])
    # # print(results[1])
    # print(f"{len(results) = }, {len(results[0]) = }, {len(results[1]) = }")
    # results = scrape_state_and_storage(start_block, blocks_per_script)
    # block_range_list = []
    # start_block_list = []
    # for i in range(blocks_per_script):
    #     block_range_list.append(1)
    #     start_block_list.append(start_block + (1 * i))

    # results = thread_scrape(start_block_list, block_range_list)
    # x_block_results = [x_block for x_block in results]
    # trace_state_results = [x for x_block in x_block_results for x in x_block[0]]
    # snapshot = tracemalloc.take_snapshot()
    # print(len(trace_state_results))
    # finish_time = time.perf_counter()
    # print(f"Scrape finished in {(finish_time - start_time):.3f} seconds")
    # top_stats = snapshot.statistics('lineno')

    # # Print top 10 files allocating the most memory
    # print("[ Top 10 ]")
    # for stat in top_stats[:10]:
    #     print(stat)

    # peak_bytes = psutil.Process().memory_info().peak_wset
    # print(f"{peak_bytes} peak bytes, {peak_bytes / 1000000000} peak gb")

    # end_block = start_block + total_blocks - 1
    # # Found optimal to be 1 for 'blocks_per_process' and 'blocks_per_scrape'
    # blocks_per_process = 1
    # blocks_per_scrape = 1

    # start_time = time.perf_counter()
    # results = process_scrape(start_block, end_block, blocks_per_process, blocks_per_scrape)

    # print(f"{len(results[0]) = }")  # 'trace_state_results'
    # print(f"{len(results[1]) = }")  # 'storage_results'
    # print(results[0][0])
    # print(results[1][0])

    # finish_time = time.perf_counter()
    # print(f"Main finished in {(finish_time - start_time):.3f} seconds")

    #############################################################################################
    # CAN CHECK FOR OPTIMAL 'blocks_per_process' AND 'blocks_per_scrape'
    #############################################################################################
    # optimal turned out to be 1 for 'blocks_per_process' and 'blocks_per_scrape'
    #   this resulted in 500 blocks completed in 73.7 seconds
    #   interestingly, just using 'ThreadPoolExecutor' with 1 'blocks_per_scrape', takes 287 seconds

    # start_block = 14486122
    # total_blocks = 300
    # end_block = start_block + total_blocks - 1
    # # Found optimal to be 1 for 'blocks_per_process' and 'blocks_per_scrape'
    # blocks_per_process = 1
    # blocks_per_scrape = 1

    # metrics = {}
    # param_list = {"25": [1, 5], "10": [1, 5, 10], "5": [1, 5], "3": [1, 2, 3], "2": [1, 2], "1": [1]}
    # results_len = []
    # # for x in per_process_list:
    # for x in param_list:
    #     blocks_per_process = int(x)
    #     for y in param_list[x]:
    #         blocks_per_scrape = y
    #         start_time = time.perf_counter()
    #         results = process_scrape(start_block, end_block, blocks_per_process, blocks_per_scrape)
    #         results_len.append(len(results))
    #         print(f"{len(results) = }")
    #         finish_time = time.perf_counter()
    #         print(f"{x} per process, {y} per scrape finished in {(finish_time - start_time):.3f} seconds")
    #         metrics[str(x) + "_" + str(y)] = finish_time - start_time
    # print(metrics)
    # print(results_len)
