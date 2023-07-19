# TERMINAL: python -m scrape_blockchain.add_missing_log_data

# GOAL:
################################################################################################

import time
import csv
import psycopg2
import itertools

from scripts.utility_misc import env_var, node_rpc_command
from scripts.utility_db import db_fetch_data

# will use to specify how you want to scrape
# definitions:
#   - 'newest' blocks: blocks from highest block in local DB to highest block from local node data
#   - 'oldest' blocks: blocks from lowest block in local DB to lowest block from local node data
#   - 'missing' blocks: counting the blocks in the local DB from lowest to highest, any block not present in DB that stops the contiguous n+1 counting
# 'how' potential values:
#   - 'full': scrape all blocks--starting with newest, then missing, then oldest
#   - 'newest': scrape newest blocks from highest in DB to highest in node data
#   - 'oldest': scrape newest blocks from lowest in DB to lowest in node data
#   - 'missing': scrape missing blocks from DB from lowest to highest
#   - 'exact': the user specifies the range of blocks to scrape, blocks within range are scraped in same sequence as 'full'
#   - 'start': the user specifies the lowest block to scrape, blocks >= are scraped in same sequence as 'full'
VALID_HOW_VALUES = {"full", "newest", "missing", "oldest", "exact", "start"}


db_name = env_var("DB_NAME")
db_user = env_var("DB_USER")
db_password = env_var("DB_PASSWORD")

schema_table = "public.tx_logs"

# completed:


def main():
    # highest_block = int(node_rpc_command("eth_getBlockByNumber", "latest", False)["result"]["number"], 16)
    master_add_tx_to_db(14000000, 16252285, 200000, 200)


def master_add_logs_to_db(how="full", start_block=None, end_block=None, blocks_per_upload=200, rows_per_db_query=20000):
    # checks if kwargs have compliant values
    if type(how) is not str:
        raise TypeError(f"'how' value must be a string and one of {VALID_HOW_VALUES}")
    if how == "exact" and not (isinstance(start_block, int) or isinstance(end_block, int)):
        raise TypeError(
            f"When how='exact', a 'start_block' and 'end_block' must be provided and > 0. {start_block = }, {end_block = }")
    if how == "start" and not isinstance(start_block, int):
        raise TypeError(f"When how='start', a 'start_block' must be provided and > 0. {start_block = }")
    if type(blocks_per_upload) is not str:
        raise TypeError(f"'blocks_per_upload' value must be an integer > 0")
    if type(rows_per_db_query) is not str:
        raise TypeError(f"'rows_per_db_query' value must be an integer > 0")

    if how not in VALID_HOW_VALUES:
        raise ValueError(f"'how' value must be one of {VALID_HOW_VALUES}")
    if how == "exact" and (start_block is None or end_block is None):
        raise ValueError(
            f"When how='exact', a 'start_block' and 'end_block' must be provided. {start_block = }, {end_block = }")
    if how == "start" and start_block is None:
        raise ValueError(f"When how='start', a 'start_block' must be provided. {start_block = }")

    min_block = 1
    max_block = 1
    node_max_block = int(node_rpc_command("eth_getBlockByNumber", "latest", False)["result"]["number"], 16)
    sql_script = f"SELECT DISTINCT(block_number) FROM {schema_table} ORDER BY block_number ASC LIMIT 1"
    db_min_block = db_fetch_data(sql_script)
    sql_script = f"SELECT DISTINCT(block_number) FROM {schema_table} ORDER BY block_number DESC LIMIT 1"
    db_max_block = db_fetch_data(sql_script)


# logic that corresponds with kwargs.....


def master_add_tx_to_db(start_block, end_block, db_query_threshold, upload_threshold):
    blocks_in_csv = 0
    # holds the missing DB blocks -> 'blocks_to_get' are the 'upload_threshold' blocks subset of 'blocks_to_add'
    blocks_to_add = []
    blocks_to_get = []  # holds the blocks that we are querying to then upload to DB
    while start_block <= end_block:
        upload_threshold = min(upload_threshold, (end_block - start_block) + 1)
        print(f"start block: {start_block}, end block: {end_block}, upload threshold: {upload_threshold}")
        print("Get missing blocks")
        if blocks_to_add == []:
            blocks_to_add = db_missing_blocks(start_block, min(db_query_threshold, end_block - start_block))
            block_end_range = start_block + db_query_threshold
        if blocks_to_add != []:
            x_threshold = min(upload_threshold, len(blocks_to_add))
            blocks_to_get = blocks_to_add[:x_threshold]
            blocks_to_add = list(set(blocks_to_add) - set(blocks_to_get))
            print("Get tx data into dictionary")
            try:
                log_dict = get_log_data(blocks_to_get)
            except Exception as x_exception:
                print(f"ERROR in 'get_tx_data' {x_exception}")
                time.sleep(10)
                try:
                    log_dict = get_log_data(blocks_to_get)
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
            print("Add log dict to CSV")
            path_to_csv = add_log_to_csv(
                "./eth_trader_profit/tx_database/csv_files_blockchain/", "log_data_grab", log_dict, op_symbol
            )
            blocks_in_csv += upload_threshold
            time.sleep(0.1)

            # # once reach upload threshold or at the final block, then upload CSV file to the db
            # if blocks_in_csv >= block_threshold or start_block + block_threshold >= end_block:
            print("Upload CSV")
            try:
                con = psycopg2.connect(database=db_name, user=db_user, password=db_password)
                cur = con.cursor()
                # add_tx_to_db(connection, cursor, csv_path, db_schema_table)
                add_log_to_db(con, cur, path_to_csv, schema_table)
                blocks_in_csv = 0
            except Exception as x_exception:
                print(f"ERROR adding CSV to DB: {x_exception}")
                cur.close()
                con.close()
                time.sleep(0.3)
            else:
                pass

        if blocks_to_add == []:
            start_block = block_end_range
        else:
            pass


def db_missing_blocks(start_block, block_increment):
    end_block = start_block + block_increment
    sql_script = f"SELECT DISTINCT(block_number) FROM {schema_table} WHERE block_number >= {start_block} AND block_number < {end_block}"
    db_blocks = db_fetch_data(sql_script)
    db_blocks = set(itertools.chain(*db_blocks))
    missing_blocks = list(set(x for x in range(start_block, end_block)) - db_blocks)
    return missing_blocks


def get_log_data(missing_blocks):
    tx_log_data = {}
    # for every block, for each tx in the block add the relevant data to the 'tx_log_data' dictionary.
    # ... this dict will later be added to a CSV which is then uploaded to the DB
    for block_no in missing_blocks:
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
