# TERMINAL: python -m

# GOAL:
################################################################################################

import psycopg2
import json
import csv
import os
from scripts.utility_misc import env_var


db_name = env_var("DB_NAME")
db_user = env_var("DB_USER")
db_password = env_var("DB_PASSWORD")


def main():
    # create_db_table(
    #     "input_signature",
    #     "hex_signature VARCHAR(10) PRIMARY KEY, text_signature VARCHAR NOT NULL, id_from_source INTEGER",
    # )
    # delete_db_table_data("input_signature")
    pass


# create new table in DB -> opens a file with the SQL code and executes the code in the DB
# assumes the file is located in the same folder as the file that is executing the 'create_db_table' function
def create_db_table(file_path):
    # Open SQL file
    with open(file_path, "r") as f:
        sql_script = f.read()
    # Connect to DB
    con = psycopg2.connect(database=db_name, user=db_user, password=db_password)
    cur = con.cursor()
    # Create table by executing code in SQL file
    try:
        cur.execute(sql_script)
        print(f"The sql script was executed successfully")
    except Exception as x_except:  # Fine if you have already created the table w/ the correct parameters
        assert x_except.__class__.__name__ == 'DuplicateTable'
        print("ERROR: can't execute, duplicate table.")
    finally:
        con.commit()
        cur.close()
        con.close()


def delete_db_table_data(table_name):
    # delete all rows in table "event_signature"
    # ... 'TRUNCATE' is faster than 'DELETE' -> delete allows use of 'WHERE' but truncate does not
    con = psycopg2.connect(database=db_name, user=db_user, password=db_password)
    cur = con.cursor()
    try:
        cur.execute(f"TRUNCATE {table_name}")
    finally:
        con.commit()
        cur.close()
        con.close()


# if column name is text, need to encase in quotes and encase with apostrophes (ex: "'text_name'")
def db_add_column(table_name, column_name, column_dtype):
    con = psycopg2.connect(database=db_name, user=db_user, password=db_password)
    cur = con.cursor()
    try:
        cur.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_dtype}")
    finally:
        con.commit()
        cur.close()
        con.close()


def db_update_column_value(table_name, column_name, extra_code):
    con = psycopg2.connect(database=db_name, user=db_user, password=db_password)
    cur = con.cursor()
    try:
        cur.execute(f"UPDATE {table_name} SET {column_name} = {extra_code}")
    finally:
        con.commit()
        cur.close()
        con.close()

# def import_csv_to_db(connection, cursor, csv_path, db_table):
#     # import csv data to database
#     with open(csv_path, "r") as csvfile:
#         # 'COPY' is more efficient than 'INSERT'
#         # need to use 'copy_expert' instead of 'copy_from' to specify 'CSV'
#         # ... otherwise, just specifying delimiter in 'copy_from' causes errors when encountering values that have commas within then (ex: transferERC(uint256, uint256))
#         sql_statement = f"COPY {db_table} FROM STDIN WITH DELIMITER ',' CSV"
#         cursor.copy_expert(sql_statement, csvfile)
#         connection.commit()
#         cursor.close()
#         connection.close()
#     return


def import_csv_to_db(connection, cursor, csv_path, db_schema_table):
    import_success = False
    try:
        # import csv data to database
        with open(csv_path, "r") as csvfile:
            # 'COPY' is more efficient than 'INSERT'
            # need to use 'copy_expert' instead of 'copy_from' to specify 'CSV'
            # ... otherwise, just specifying delimiter in 'copy_from' causes errors when encountering values that have commas within them
            sql_statement = f"COPY {db_schema_table} FROM STDIN WITH DELIMITER ',' CSV"
            cursor.copy_expert(sql_statement, csvfile)
            connection.commit()
            cursor.close()
            connection.close()
        import_success = True
        return [import_success, ""]
    except Exception as x_exception:
        cursor.close()
        connection.close()
        print(x_exception)
        return [import_success, x_exception]


if __name__ == "__main__":
    main()
