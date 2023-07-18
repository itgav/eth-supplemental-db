import os
from scripts.utility_misc import env_var
from scripts.utility_db_admin import create_db_table


db_name = env_var("DB_NAME")
db_user = env_var("DB_USER")
db_password = env_var("DB_PASSWORD")


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
