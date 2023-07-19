# TERMINAL: python -m db_tables.create_db_tables

# GOAL:
################################################################################################
# Create the tables for your local PostgreSQL database
# These tables will later be populated from data scraped from the web and from your node

import os
from scripts.utility_db_admin import create_db_table


def main():
    # file path to this file
    file_path = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")

    # get list of our '.sql' files that CREATE TABLE's
    file_list = os.listdir(os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"))
    file_list = [file for file in file_list if file[:9] == 'db_create' and file[-4:] == ".sql"]
    print(f"{file_list = }")

    # create tables by executing the code in the SQL files
    for sql_file in file_list:
        sql_file_path = f"{file_path}/{sql_file}"
        create_db_table(sql_file_path)


if __name__ == "__main__":
    main()
