import requests
import json
from datetime import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from collections import Counter
from web3 import Web3
from web3.contract import Contract
from web3.logs import STRICT, IGNORE, DISCARD, WARN


def main():
    x = env_var("MY_URL")
    print(x)
    # y = get_address_type("0xa8eb9cbde6d804684e1d80b529a6212f4b0b08be", "latest")
    # print(y)
    # z = get_block_info("latest")
    # print(z)


# Load environment variable by name -> not sure if this is the best way to do this
def env_var(variable):
    from dotenv import load_dotenv
    import os

    load_dotenv()
    return os.getenv(variable)


# can input a viable RPC command it's paramaters
def node_rpc_command(method, *args):
    my_url = env_var("MY_URL")
    block_values = {"id": 1, "jsonrpc": "2.0", "method": method, "params": list(args)}
    response = requests.post(my_url, json=block_values).json()
    return response


# get data tx for a range of blocks -> excludes value data (except for gasUsed)
def get_tx_data(start_block, end_block):
    tx_data_list = []
    logs_data_list = []
    for block in range(start_block, end_block + 1):
        block_receipts = node_rpc_command("eth_getBlockReceipts", block)["result"]
        for i in range(len(block_receipts)):
            tx_hash = block_receipts[i]["transactionHash"]
            tx_from = block_receipts[i]["from"]
            tx_to = block_receipts[i]["to"]
            tx_gas_used = int(block_receipts[i]["gasUsed"], 16)
            tx_logs = block_receipts[i]["logs"]
            tx_data_list.append([tx_hash, tx_from, tx_to, tx_gas_used])
            if len(tx_logs) == 0:
                pass
            else:
                for i in range(len(tx_logs)):
                    logs_address = tx_logs[i]["address"]
                    logs_topics = tx_logs[i]["topics"]
                    logs_data = tx_logs[i]["data"]
                    logs_data_list.append([tx_hash, logs_address, logs_topics, logs_data])

    return tx_data_list, logs_data_list


# return block info
def get_block_info(block_number, detail=False):
    my_url = env_var("MY_URL")

    # get timestamp of most recent block
    rpc_values = {"id": 1, "jsonrpc": "2.0", "method": "eth_getBlockByNumber", "params": [block_number, detail]}
    response = requests.post(my_url, json=rpc_values)

    block_result = response.json()["result"]
    block_result["number"] = int(block_result["number"], 16)  # change hexadecimal to decimal
    block_result["timestamp"] = int(block_result["timestamp"], 16)  # change hexadecimal to decimal

    return block_result


# Get a list of the 'from' and 'to' wallets within a block
def block_wallets(block_number):
    block_tx = get_block_info(block_number, True)["transactions"]
    tx_in_block = len(block_tx)

    wallets_in_block = []
    for i in range(
        tx_in_block
    ):  # loop through transactions in block and create list of wallets from the 'from' and 'to' fields
        from_wallet = block_tx[i]["from"]
        wallets_in_block.append(from_wallet)
        to_wallet = block_tx[i]["to"]
        wallets_in_block.append(to_wallet)

    return wallets_in_block


# create function to get address result from eth_getCode function --> determine if EOA or contract address
def get_address_type(wallet_address, block_number):
    block_values = {"id": 1, "jsonrpc": "2.0", "method": "eth_getCode", "params": [wallet_address, block_number]}
    response = requests.post(env_var("MY_URL"), json=block_values)
    result = response.json()["result"]

    # Determine if address is an EOA, contract, or and edge case to look into
    if result == "0x":
        result = "EOA"
    elif result == "0x0":
        result
    elif len(result) <= 20:
        result = "Short Length"
    else:
        result = "Contract"

    return result


if __name__ == "__main__":
    main()
