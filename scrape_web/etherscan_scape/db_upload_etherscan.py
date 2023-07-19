# TERMINAL: python -m scripts.db_upload_etherscan

# GOAL:
################################################################################################

import os
import psycopg2
from scripts.utility_misc import env_var
from scripts.utility_db import import_csv_to_db

DB_NAME = env_var("DB_NAME")
DB_USER = env_var("DB_USER")
DB_PASSWORD = env_var("DB_PASSWORD")

DB_TABLE = "wallet_info"
FILE_NAME = "clean_etherscan_scrape"

csv_path = os.path.abspath(os.path.join('.')).replace('\\', '/')  # using double '\\' to escape the first '\'
csv_path = f"{csv_path}/scrapers/csv_files_web/{FILE_NAME}.csv"
# wasn't working with the above, it seems to be due to the double backslash path vs the single forward slash below
# csv_path = "C:/Users/Gavin/projects_python/eth_retail_trading_strat/eth_trader_profit/scrapers/csv_files_web/clean_etherscan_scrape.csv"


def main():
    print("Insert from csv to database")
    try:
        # connect to database
        con = psycopg2.connect(database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
        cur = con.cursor()
        import_csv_to_db(con, cur, csv_path, DB_TABLE)
        upload_success = True
        print(f"Upload success: {upload_success}")
        # close db connection
        cur.close()
        con.close()
    # if exception and is due to duplicate primary key, then remove that row of data and try again
    # ... else stop and don't upload
    except Exception as x_exception:
        # close lingering db connection
        cur.close()
        con.close()
        print(f"exception on upload {x_exception}")


if __name__ == "__main__":
    main()
