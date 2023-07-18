import requests
import json
import csv
import time
import psycopg2

from scripts.utility_misc import env_var
from scripts.utility_db import db_fetch_data


def main():
    print("hi")


def scrape_json(url, api_attempt_threshold):
    # get datafrom page
    api_attempts = 1
    request_status = 0
    while api_attempts <= api_attempt_threshold and request_status != 200:
        try:
            r = requests.get(url)
            request_status = r.status_code
            print(f"Request status: {r.status_code}")
            r_json = r.json()
            r_json["request_status"] = request_status
            return r_json
        except:
            print(f"ERROR: Bad request. Status code: {r.status_code}. Attempt #: {api_attempts}")
            api_attempts += 1
            time.sleep(3)


# create and write a list of data to a csv file
def write_csv(relative_path, file_name, data):
    full_path = f"{relative_path}/{file_name}.csv"
    with open(full_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        for i in range(len(data)):
            try:
                writer.writerow(data[i])
            except UnicodeEncodeError:
                # try to remove the text that had the error and re-try to write to CSV
                try:
                    for x_i in range(len(data[i])):
                        data[i][x_i] = data[i][x_i].encode("utf-8").decode("ascii", "ignore")
                    writer.writerow(data[i])
                except Exception as x_exception:
                    print(f"ERROR adding row to CSV: {x_exception}")
                    pass
    return full_path


# create and write a list of data to a csv file
def append_csv(relative_path, file_name, data):
    full_path = f"{relative_path}/{file_name}.csv"
    with open(full_path, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        for i in range(len(data)):
            try:
                writer.writerow(data[i])
            except UnicodeEncodeError:
                # try to remove the text that had the error and re-try to write to CSV
                try:
                    for x_i in range(len(data[i])):
                        data[i][x_i] = data[i][x_i].encode("utf-8").decode("ascii", "ignore")
                    writer.writerow(data[i])
                except Exception as x_exception:
                    print(f"ERROR adding row to CSV: {x_exception}")
                    pass
    return full_path


def add_to_csv(relative_path, file_name, data, op_symbol):
    full_path = f"{relative_path}/{file_name}.csv"
    with open(full_path, op_symbol, newline="") as csvfile:
        writer = csv.writer(csvfile)
        for i in data:
            try:
                if type(data) == dict:
                    writer.writerow(list(data[i].values()))
                else:  # assume 'data' is a list
                    writer.writerow(i)
            except Exception as x_exception:
                print(f"ERROR adding row to CSV: {x_exception}")
                pass
    return full_path


# determine what page of results a value is on based on a starting value, its page, the value we are trying to located, and how many results are on each page.
def page_estimator(start_value, start_index, start_page, find_value, page_size):
    # for 4 bytes: large values on low page. If below positive then find_page will be larger
    value_var = abs(start_value - find_value)
    if start_value > find_value:  # start page will be < find page
        on_start_page = page_size - start_index  # how many latter entries on page
        # "//" operator rounds down -> end result is rounding up
        page_var = -int(-(value_var - on_start_page) // page_size)
        find_page = start_page + page_var
    elif start_value < find_value:  # start page will be > find page
        on_start_page = start_index  # how many prior entries on page
        page_var = -int(-(value_var - on_start_page) // page_size)
        find_page = start_page - page_var
    else:
        on_start_page = 0  # if find_value is start_value then no need for a difference
        find_page = start_page

    return find_page


if __name__ == "__main__":
    main()
