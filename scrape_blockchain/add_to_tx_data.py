# terminal: python -m scrape_blockchain.add_to_tx_data

import time
import csv
import psycopg2

from scripts.utility_misc import env_var, node_rpc_command


db_name = env_var("DB_NAME")
db_user = env_var("DB_USER")
db_password = env_var("DB_PASSWORD")

# schema_table = "public.tx_data"
schema_table = "public.tx_data_part"

# completed:
# 0-1000000
# 14000000-16000000


def main():
    # highest_block = int(node_rpc_command("eth_getBlockByNumber", "latest", False)["result"]["number"], 16)
    master_add_tx_to_db(16000001, 16252285, 50, 150)


def master_add_tx_to_db(start_block, end_block, block_dict_treshold, block_upload_threshold):
    blocks_in_csv = 0
    while start_block <= end_block:
        block_dict_treshold = min(block_dict_treshold, (end_block - start_block) + 1)
        print(f"start block: {start_block}, end block: {end_block}, block dict threshold: {block_dict_treshold}")
        print("Get tx data into dictionary")
        try:
            tx_dict = get_tx_data(start_block, block_dict_treshold)
        except Exception as x_exception:
            print(f"ERROR in 'get_tx_data' {x_exception}")
            time.sleep(10)
            try:
                tx_dict = get_tx_data(start_block, block_dict_treshold)
            except Exception as x_exception:
                print(f"ERROR in 2nd attempt 'get_tx_data' at start block: {start_block}")
                print(f"ERROR in 2nd attempt 'get_tx_data' {x_exception}")
        time.sleep(0.1)

        # if csv is empty or fully uploaded then write to a new csv
        if blocks_in_csv == 0:
            op_symbol = "w"
        else:  # append data to current working csv
            op_symbol = "a"
        print(f"op symbol: {op_symbol}")
        # add data in dictionary to CSV file that will later be uploaded
        # add_tx_to_csv(relative_path, file_name, data, op_symbol)
        print("Add tx dict to CSV")
        path_to_csv = add_tx_to_csv(
            "./eth_trader_profit/tx_database/csv_files_blockchain/", "tx_data_grab", tx_dict, op_symbol
        )
        blocks_in_csv += block_dict_treshold
        time.sleep(0.1)

        # once reach upload threshold or at the final block, then upload CSV file to the db
        if blocks_in_csv >= block_upload_threshold or start_block + block_dict_treshold >= end_block:
            print("Upload CSV")
            try:
                con = psycopg2.connect(database=db_name, user=db_user, password=db_password)
                cur = con.cursor()
                # add_tx_to_db(connection, cursor, csv_path, db_schema_table)
                add_tx_to_db(con, cur, path_to_csv, schema_table)
                blocks_in_csv = 0
            except Exception as x_exception:
                print(f"ERROR adding CSV to DB: {x_exception}")
                cur.close()
                con.close()
            time.sleep(0.3)
        else:
            pass

        start_block += block_dict_treshold


def get_tx_data(start_block, block_increment):
    tx_data = {}
    # for every block, for each tx in the block add the relevant data to the 'tx_data' dictionary.
    # ... this dict will later be added to a CSV which is then uploaded to the DB
    for block_no in range(start_block, start_block + block_increment):
        # get tx data and add to dictionary
        block_tx = node_rpc_command("eth_getBlockByNumber", block_no, True)["result"]["transactions"]
        for tx in block_tx:
            tx_hash = tx["hash"]
            block_number = int(tx["blockNumber"], 16)
            tx_from = tx["from"]
            if tx["to"] is None:
                tx_to = "0x" + "0" * 40
            else:
                tx_to = tx["to"]
            eth_value = int(tx["value"], 16)
            gas_limit = int(tx["gas"], 16)
            gas_price = int(tx["gasPrice"], 16)
            # tx_input_signature = tx["input"]
            from_nonce = int(tx["nonce"], 16)
            tx_type = int(tx["type"], 16)
            if "maxFeePerGas" in tx.keys():
                max_fee_per_gas = int(tx["maxFeePerGas"], 16)
            else:
                max_fee_per_gas = "0"
            if "maxFeePerGas" in tx.keys():
                max_priority_fee_per_gas = int(tx["maxPriorityFeePerGas"], 16)
            else:
                max_priority_fee_per_gas = "0"

            tx_data[tx_hash] = {
                "tx_hash": tx_hash,
                "block_number": block_number,
                "tx_from": tx_from,
                "tx_to": tx_to,
                # "contract_created": "",
                "eth_value": eth_value,
                "gas_limit": gas_limit,
                "gas_price": gas_price,
                "effective_gas_price": "",
                "gas_used": "",
                "max_fee_per_gas": max_fee_per_gas,
                "max_priority_fee_per_gas": max_priority_fee_per_gas,
                "from_nonce": from_nonce,
                "tx_type": tx_type,
                "tx_success": "",
                "contract_created": ""
                # "tx_input_signature": tx_input_signature
            }

        # get/add remaining data to the dictionary
        block_receipts = node_rpc_command("eth_getBlockReceipts", block_no)["result"]
        for receipt in block_receipts:
            tx_hash = receipt["transactionHash"]
            # effective_gas_price = int(receipt["effectiveGasPrice"], 16)
            # gas_used = int(receipt["gasUsed"], 16)
            # tx_success = int(receipt["status"], 16)
            if receipt["contractAddress"] is None:
                tx_data[tx_hash]["contract_created"] = False
            else:
                tx_data[tx_hash]["contract_created"] = True
                tx_data[tx_hash]["tx_to"] = receipt["contractAddress"]

            tx_data[tx_hash]["effective_gas_price"] = int(receipt["effectiveGasPrice"], 16)
            tx_data[tx_hash]["gas_used"] = int(receipt["gasUsed"], 16)
            tx_data[tx_hash]["tx_success"] = int(receipt["status"], 16)

    return tx_data


def add_tx_to_csv(relative_path, file_name, data, op_symbol):
    full_path = f"{relative_path}/{file_name}.csv"
    with open(full_path, op_symbol, newline="") as csvfile:
        writer = csv.writer(csvfile)
        for i in data:
            try:
                writer.writerow(list(data[i].values()))
            except Exception as x_exception:
                print(f"ERROR adding row to CSV: {x_exception}")
                pass
    return full_path


def add_tx_to_db(connection, cursor, csv_path, db_schema_table):
    try:
        with open(csv_path, "r") as csvfile:
            # 'COPY' is more efficient than 'INSERT'
            # need to use 'copy_expert' instead of 'copy_from' to specify 'CSV'
            # ... otherwise, just specifying delimiter in 'copy_from' causes errors when encountering values that have commas within them
            sql_statement = f"COPY {db_schema_table} FROM STDIN WITH DELIMITER ',' CSV"
            cursor.copy_expert(sql_statement, csvfile)
            connection.commit()
            cursor.close()
            connection.close()
    except Exception as x_exception:
        cursor.close()
        connection.close()
        print(x_exception)


if __name__ == "__main__":
    main()
