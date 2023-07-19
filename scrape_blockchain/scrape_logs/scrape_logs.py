# TERMINAL: python -m scrape_blockchain.add_to_logs_data

# GOAL:
################################################################################################

import time
import csv
import psycopg2

from scripts.utility_misc import env_var, node_rpc_command


db_name = env_var("DB_NAME")
db_user = env_var("DB_USER")
db_password = env_var("DB_PASSWORD")

schema_table = "public.tx_logs"

# completed blocks:


def main():
    # highest_block = int(node_rpc_command("eth_getBlockByNumber", "latest", False)["result"]["number"], 16)
    master_add_tx_to_db(14000000, 16252285, 50, 200)


def master_add_tx_to_db(start_block, end_block, block_dict_treshold, block_upload_threshold):
    blocks_in_csv = 0
    while start_block <= end_block:
        block_dict_treshold = min(block_dict_treshold, (end_block - start_block) + 1)
        print(f"start block: {start_block}, end block: {end_block}, block dict threshold: {block_dict_treshold}")
        print("Get log data into dictionary")
        try:
            log_dict = get_log_data(start_block, block_dict_treshold)
        except Exception as x_exception:
            # typically due to RPC connection so will wait and then try again
            print(f"ERROR in 'get_log_data' {x_exception}")
            time.sleep(10)
            try:
                log_dict = get_log_data(start_block, block_dict_treshold)
            except Exception as x_exception:
                print(f"ERROR in 2nd attempt 'get_log_data' at start block: {start_block}")
                print(f"ERROR in 2nd attempt 'get_log_data' {x_exception}")
        time.sleep(0.1)

        # if csv is empty or fully uploaded then write to a new csv
        if blocks_in_csv == 0:
            op_symbol = "w"
        else:  # append data to current working csv
            op_symbol = "a"
        print(f"op symbol: {op_symbol}")
        # add data in dictionary to CSV file that will later be uploaded
        # add_log_to_csv(relative_path, file_name, data, op_symbol)
        print("Add log dict to CSV")
        path_to_csv = add_log_to_csv(
            "./eth_trader_profit/tx_database/csv_files_blockchain/", "log_data_grab", log_dict, op_symbol
        )
        blocks_in_csv += block_dict_treshold
        time.sleep(0.1)

        # once reach upload threshold or at the final block, then upload CSV file to the db
        if blocks_in_csv >= block_upload_threshold or start_block + block_dict_treshold >= end_block:
            print("Upload CSV")
            try:
                con = psycopg2.connect(database=db_name, user=db_user, password=db_password)
                cur = con.cursor()
                # add_log_to_db(connection, cursor, csv_path, db_schema_table)
                add_log_to_db(con, cur, path_to_csv, schema_table)
                blocks_in_csv = 0
            except Exception as x_exception:
                print(f"ERROR adding CSV to DB: {x_exception}")
                cur.close()
                con.close()
            time.sleep(0.3)
        else:
            pass

        start_block += block_dict_treshold


def get_log_data(start_block, block_increment):
    tx_log_data = {}
    # for every block, for each tx in the block add the relevant data to the 'tx_log_data' dictionary.
    # ... this dict will later be added to a CSV which is then uploaded to the DB
    for block_no in range(start_block, start_block + block_increment):
        # get log data and add to dictionary
        block_receipts = node_rpc_command("eth_getBlockReceipts", block_no)["result"]
        for receipt in block_receipts:
            tx_hash = receipt["transactionHash"]
            block_number = int(receipt["blockNumber"], 16)
            for log in receipt["logs"]:
                emit_address = log["address"]
                log_data = log["data"]
                topic_len = len(log["topics"])
                # There can be variable # of topics 0 to 4
                # I could do try/except, but I think this will be faster
                if topic_len == 4:
                    log_topic_1 = log["topics"][0]
                    log_topic_2 = log["topics"][1]
                    log_topic_3 = log["topics"][2]
                    log_topic_4 = log["topics"][3]
                elif topic_len == 3:
                    log_topic_1 = log["topics"][0]
                    log_topic_2 = log["topics"][1]
                    log_topic_3 = log["topics"][2]
                    log_topic_4 = "0x"
                elif topic_len == 2:
                    log_topic_1 = log["topics"][0]
                    log_topic_2 = log["topics"][1]
                    log_topic_3 = "0x"
                    log_topic_4 = "0x"
                elif topic_len == 1:
                    log_topic_1 = log["topics"][0]
                    log_topic_2 = "0x"
                    log_topic_3 = "0x"
                    log_topic_4 = "0x"
                else:
                    log_topic_1 = "0x"
                    log_topic_2 = "0x"
                    log_topic_3 = "0x"
                    log_topic_4 = "0x"

                tx_log_data[tx_hash] = {
                    "tx_hash": tx_hash,
                    "block_number": block_number,
                    "emit_address": emit_address,
                    "log_topic_1": log_topic_1,
                    "log_topic_2": log_topic_2,
                    "log_topic_3": log_topic_3,
                    "log_topic_4": log_topic_4,
                    "log_data": log_data,
                }

    return tx_log_data


def add_log_to_csv(relative_path, file_name, data, op_symbol):
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


def add_log_to_db(connection, cursor, csv_path, db_schema_table):
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
