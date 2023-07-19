# TERMINAL: python -m scrape_web.fourbytes_scrape.scrape_4bytes

# GOAL:
################################################################################################

import time
import psycopg2
from scripts.utility_misc import env_var
from scripts.utility_scrape import scrape_json, write_csv, page_estimator
from scripts.utility_db import db_fetch_data
from scripts.utility_db_admin import import_csv_to_db, remove_duplicate_key


def main():
    # url_head = env_var("URL_EVENT_4BYTES")
    # scrape_data(url_head, "event_signature", "event_signature_1", "4Bytes")
    url_head = env_var("URL_INPUT_4BYTES")
    scrape_data(url_head, "input_signature", "input_signature_1", "4Bytes")


def scrape_data(url_head, db_table, csv_name, source):
    db_name = env_var("DB_NAME")
    db_user = env_var("DB_USER")
    db_password = env_var("DB_PASSWORD")
    relative_path = "csv_files_web"
    upload_threshold = 1000  # rows of data in 'data_scraped' before uploading to database
    # "new" "records_uploaded" could be overstated if in first upload for "old" but were removed due to duplicates
    summary_stats = [
        {"stage": "new", "pages_scraped": 0, "records_scraped": 0, "records_uploaded": 0},
        {"stage": "old", "pages_scraped": 0, "records_scraped": 0, "records_uploaded": 0},
    ]

    page_number = 1
    results_per_page = 100
    url = f"{url_head}?page={page_number}"
    r_json = scrape_json(url=url, api_attempt_threshold=5)
    # ['count'] has total records on 4bytes website, each full page has 100 records. roundup(total records/ records on page)
    site_highest_page = -int(-r_json["count"] // results_per_page)
    # grab most recent "id" from site ("id" is really just an ascending count by record)
    site_highest_id = r_json["results"][0]["id"]
    # hardcoded since I've verified, could make dynamic if needed
    site_lowest_id = 1
    try:
        db_highest_id = db_fetch_data(
            f"SELECT id_from_source FROM {db_table} WHERE source = '{source}' ORDER BY id_from_source DESC LIMIT 1"
        )[0][0]

        db_lowest_id = db_fetch_data(
            f"SELECT id_from_source FROM {db_table} WHERE source = '{source}' ORDER BY id_from_source ASC LIMIT 1"
        )[0][0]
    # if no results (likely because list index out of range... original return is [])
    except Exception as x_exception:
        db_highest_id = 0
        db_lowest_id = 0
        print("ERROR: couldn't query DB for 'db_highest_id' and 'db_lowest_id'. Setting values to zero.")
        print(f"...exception was {x_exception}")

    # if full page then scrape full page, else scrape only ones not on DB
    # once initial round then do end of DB; once end of DB then do missing
    # SCRAPE DATA ############################################################
    stage_loops = 0
    scrape_state = 1  # will use to scrape new and then old records, this way can reuse logic (1 = "new", -1 = "old")
    data_scraped = []
    end_scrape = False
    # scrape records not in database in following order: 1) high ID records (aka new), 2) low id records (aka old/ungotten), 3) missing records
    # high id scrape: start from highest ID on website then work down until reach highest DB ID
    # low id scrape: start from lowest ID on website then work up until reach lowest DB ID
    if (db_highest_id < site_highest_id and scrape_state == 1) or (
        db_lowest_id > site_lowest_id and scrape_state == -1
    ):
        print("Scraping new records")
        while end_scrape == False:
            # if first loop of "low ID" scrape then rest page # to the last one on the website
            if stage_loops == 0 and scrape_state == -1:
                page_number = site_highest_page
                print("Scraping old records")

            url = f"{url_head}?page={page_number}"
            try:
                r_results = scrape_json(url=url, api_attempt_threshold=5)["results"]

                # scrape full page
                if (scrape_state == 1 and db_highest_id < r_results[-1]["id"]) or (
                    scrape_state == -1 and db_lowest_id > r_results[0]["id"]
                ):
                    print(f"scrape: full page, page# {page_number}")
                    for x_result in r_results:
                        hex_signature = x_result["hex_signature"]
                        text_signature = x_result["text_signature"]
                        id_from_source = x_result["id"]
                        data_scraped.append([hex_signature, text_signature, id_from_source, source])

                    stage_loops += 1  # keeping track of loops per scraping stage
                # else scrape only records on the page that aren't in database --> which means last loop of the stage
                else:
                    print(f"scrape: partial page, page# {page_number}")
                    # wanted to experimented with generator expressions
                    for x_result in (
                        x
                        for x in r_results
                        if (scrape_state == 1 and db_highest_id < x["id"])
                        or (scrape_state == -1 and db_lowest_id > x["id"])
                    ):
                        hex_signature = x_result["hex_signature"]
                        text_signature = x_result["text_signature"]
                        id_from_source = x_result["id"]
                        data_scraped.append([hex_signature, text_signature, id_from_source, source])

                    stage_loops += 1  # keeping track of loops per scraping stage

                    # if finishing the initial scrape for "new" records
                    if scrape_state == 1:
                        summary_stats[0]["pages_scraped"] = stage_loops
                        summary_stats[0]["pages_scraped"] = stage_loops
                        # will subtract from first upload of "old" to keep stats more accurate
                        new_in_first_old_upload = len(data_scraped)
                        stage_loops = 0  # reset variable for next stage
                        scrape_state = -1  # used to indicate that the initial scrape for "new" records is finished
                        print(f"change to scrape state {scrape_state}")
                    else:
                        summary_stats[1]["pages_scraped"] = stage_loops
                        end_scrape = True
                        print(f"end scrape of 'old' records")

            except:  # likely due to reaching the end of the websites total pages or reaching the "api_attempt_threshold"
                print(
                    f"Unable to return 'r_results for next page. request status: {scrape_json(url=url, api_attempt_threshold=5)}"
                )
                if scrape_state == 1:  # if finishing the initial scrape for "new" records
                    summary_stats[0]["pages_scraped"] = stage_loops
                    summary_stats[0]["records_scraped"] += len(data_scraped)
                    # will subtract from first upload of "old" to keep stats more accurate
                    new_in_first_old_upload = len(data_scraped)
                    stage_loops = 0  # reset variable for next stage
                    scrape_state = -1  # used to indicate that the initial scrape for "new" records is finished
                else:
                    summary_stats[1]["pages_scraped"] = stage_loops
                    end_scrape = True  # if errored on "low ID" scrape then end while loop

            # WRITE DATA TO CSV AND UPLOAD TO DATABASE ############################
            # once reach upload threshold, write contents of 'data_scraped' to the csv file then upload to the database
            # ...OR if we've scraped some data but errored out on requests, then upload the remaining 'data_scraped'
            if (len(data_scraped) >= upload_threshold or end_scrape == True) and data_scraped != []:
                print("write data to csv")
                # syntax: write_csv(relative_path, file_name, data)
                csv_path = write_csv(relative_path, csv_name, data_scraped)
                # update summary stats
                if scrape_state == 1:
                    summary_stats[0]["records_scraped"] += len(data_scraped)
                else:
                    summary_stats[1]["records_scraped"] += len(data_scraped) - new_in_first_old_upload
                # add all rows of csv file to database table
                print("Insert from csv to database")
                upload_success = False
                attempts = 0
                while upload_success == False and attempts < len(data_scraped) - 1:
                    try:
                        # connect to database
                        con = psycopg2.connect(database=db_name, user=db_user, password=db_password)
                        cur = con.cursor()
                        import_csv_to_db(con, cur, csv_path, db_table)
                        upload_success = True  # if success then stop loop
                        print(f"Upload success: {upload_success}")
                        # update summary stats
                        if scrape_state == 1:
                            summary_stats[0]["records_uploaded"] += len(data_scraped)
                        else:
                            summary_stats[1]["records_uploaded"] += max(0, len(data_scraped) - new_in_first_old_upload)
                            summary_stats[0]["records_uploaded"] += new_in_first_old_upload
                            new_in_first_old_upload = 0
                        # close db connection
                        cur.close()
                        con.close()
                    # if exception and is due to duplicate primary key, then remove that row of data and try again
                    # ... else stop and don't upload
                    except Exception as x_exception:
                        # close lingering db connection
                        cur.close()
                        con.close()
                        print(f"exception on upload, upload attempts: {attempts}")
                        attempts += 1
                        # if exception is primary key then try to delete issue from csv and continue trying until no remaining data or exception is fixed
                        if x_exception.pgcode == "23505":  # code for 'UniqueViolation'
                            data_scraped = remove_duplicate_key(x_exception, relative_path, csv_name, db_table)
                            csv_path = write_csv(relative_path, csv_name, data_scraped)
                        else:
                            print(x_exception)
                            break  # if a different excpetion then exit while loop
                        time.sleep(0.5)

                data_scraped = []  # reset after upload
            else:  # either no data in 'data_scraped' or haven't reached upload threshold
                pass

            page_number += scrape_state

    else:  # if no new/old records to add
        print("No new or old records to scrape, contine to missing records")
        pass

    # check for non-contiguous IDs in database for given source. If results then try to scrape 'missing_ids' from source then upload to DB
    missing_data_stats = scrape_missing_data(url_head, db_table, csv_name, source, upload_threshold)

    # print out summary stats
    summary_stats = summary_stats + missing_data_stats
    print(summary_stats)


# check for non-contiguous IDs in database for given source. If results then try to scrape 'missing_ids' from source then upload to DB
# meant to fill in any missing gaps left by initial scrape... hopefully, there aren't any but just in case.
def scrape_missing_data(url_head, db_table, csv_name, source, upload_threshold):
    print("Scrape missing data")
    db_name = env_var("DB_NAME")
    db_user = env_var("DB_USER")
    db_password = env_var("DB_PASSWORD")
    relative_path = "csv_files_web"
    summary_stats = [
        {"stage": "missing", "pages_scraped": 0, "records_scraped": 0, "records_uploaded": 0, "missing_ids": 0}
    ]

    # GET BOUNDS TO HELP WITH PAGE ESTIMATION #########################################################
    page_number = 1
    results_per_page = 100
    url = f"{url_head}?page={page_number}"
    r_json = scrape_json(url=url, api_attempt_threshold=5)
    # ['count'] has total records on 4bytes website, each full page has 100 records. roundup(total records/ records on page)
    site_highest_page = -int(-r_json["count"] // results_per_page)  # get a page ceiling
    site_highest_id = r_json["results"][0]["id"]
    site_lowest_page = 1

    # GET MISSING DB IDs, SCRAPE FROM SOURCE, THEN UPLOAD TO DB #######################################
    try:
        db_highest_id = db_fetch_data(
            f"SELECT id_from_source FROM {db_table} WHERE source = '{source}' ORDER BY id_from_source DESC LIMIT 1"
        )[0][0]

        db_lowest_id = db_fetch_data(
            f"SELECT id_from_source FROM {db_table} WHERE source = '{source}' ORDER BY id_from_source ASC LIMIT 1"
        )[0][0]
        # db_lowest_id = 495000
    # if no results (likely because list index out of range... original return is [])
    except Exception as x_exception:
        db_highest_id = 0
        db_lowest_id = 0
        print("ERROR: couldn't query DB for 'db_highest_id' and 'db_lowest_id'. Setting values to zero.")
        print(f"...exception was {x_exception}")

    # might want to to dynamically relate data_increment to upload_threshold
    data_increment = 5000
    low_end = db_lowest_id
    top_end = min(low_end + data_increment - 1, db_highest_id)
    data_scraped = []
    end_scrape = False
    while end_scrape == False:
        # GET MISSING DB IDs UP UNTIL THRESHOLD #######################################################
        # query our DB from lowest ID to highest in increments of 'data_increment'
        # look for any non-contiguous ID #'s append them to 'ids_to_grab' list (ex: DB ID data = [1, 2, 3, 5] --> missing ID would be '4')
        ids_to_grab = []
        # exit loop if reached the end of our DB or we already have reached our 'upload_threshold'
        while low_end < db_highest_id and (len(ids_to_grab) + len(data_scraped)) < upload_threshold:
            # originally returned as tuples with syntax: (id,)
            db_ids = db_fetch_data(
                f"SELECT id_from_source FROM {db_table} WHERE source = '{source}' AND id_from_source >= {low_end} AND id_from_source <= {top_end} ORDER BY id_from_source ASC"
            )
            db_ids = [id[0] for id in db_ids]
            print(f"Query DB from {low_end} through {top_end}")
            # create list of all IDs in range that are not in results from DB query, then join to 'ids_to_grab' list
            ids_to_grab = ids_to_grab + list(x_id for x_id in range(low_end, top_end + 1) if x_id not in db_ids)
            summary_stats[0]["missing_ids"] += len(ids_to_grab)
            # update values for next DB loop
            low_end = min(top_end + 1, db_highest_id)
            top_end = min(top_end + data_increment, db_highest_id)

            # if looped through end of db data or have reached quantity threshold, then don't loop again
            if low_end >= db_highest_id:
                end_scrape = True
                print("Queried last of data from DB will end scrape after cycle through 'ids_to_grab'")
            else:
                pass

        print(f"ids to grab[0]: {ids_to_grab[0]}, ids_to_grab[-1]: {ids_to_grab[-1]}")
        # SCRAPE DATA FOR EACH MISSING ID #############################################################
        # ... keep in mind that the source may not have contiguous ID #'s so may not be able to scrape "missing" ID
        page_number = 0
        for missing_id in ids_to_grab:
            # if ID was removed because its page was checked, then don't need to loop through again
            if missing_id not in ids_to_grab:
                # print(f"missing id {missing_id} is NOT in ids_to_grab")
                pass
            else:
                # print(f"missing id {missing_id} is in ids_to_grab")
                # FIND PAGE WHERE MISSING ID IS #######################################################
                on_page = False
                try:  # try to get last 30 results of prior 'missing_id'
                    bounds_on_page = bounds_on_page[-30:]
                except:
                    bounds_on_page = []

                try:  # if ID should be on a previously visited page then no need for estimation/multiple attempts
                    # ... also I think this could only return results if the 'missing_id' is the first of the 'ids_to_grab'
                    # ... because we look for all 'ids_on_page' then remove them
                    page_number = [x["page"] for x in bounds_on_page if (x["max_id"] >= missing_id >= x["min_id"])][0]
                    on_page = True
                    print(f"Exact page {page_number}. Missing ID: {missing_id}")
                    url = f"{url_head}?page={page_number}"
                    r_results = scrape_json(url, api_attempt_threshold=5)["results"]
                    page_first_id = r_results[0]["id"]
                    page_last_id = r_results[-1]["id"]
                except:
                    page_number = min(
                        max(1, page_estimator(site_highest_id, 0, 1, missing_id, results_per_page)), site_highest_page
                    )
                    # print(f"Estimated page {page_number}. Missing ID: {missing_id}")
                # find exact page where 'missing_id' should be, if didn't already in above logic
                # it should take < 5 'missing_page_attempts', the threshold is mainly in-place to stop an edge case where the logic
                # ... can't find the page, and otherwise, would cycle through all the pages
                missing_page_threshold = 10
                missing_page_attempts = 0
                active_scrape = False
                pages_visited = []
                while on_page == False and missing_page_attempts < missing_page_threshold:
                    print(
                        f"Look for exact page. Attempts: {missing_page_attempts}, Starting page: {page_number}. Missing ID: {missing_id}"
                    )
                    # if have relevant page data in memory then use it
                    if page_number in [x["page"] for x in bounds_on_page]:
                        url = f"{url_head}?page={page_number}"
                        page_first_id = [x["max_id"] for x in bounds_on_page if x["page"] == page_number][0]
                        page_last_id = [x["min_id"] for x in bounds_on_page if x["page"] == page_number][0]
                        active_scrape = False
                    else:  # actually scrape
                        url = f"{url_head}?page={page_number}"
                        r_results = scrape_json(url, api_attempt_threshold=5)["results"]
                        page_first_id = r_results[0]["id"]
                        page_last_id = r_results[-1]["id"]
                        bounds_on_page.append({"page": page_number, "max_id": page_first_id, "min_id": page_last_id})
                        active_scrape = True
                    pages_visited.append(page_number)
                    # print(f"page: {page_number}, max_id: {page_first_id}, min_id: {page_last_id}")
                    # find direction to traverse
                    # not correct page
                    if missing_id > page_first_id or missing_id < page_last_id:
                        estimated_id_var = abs(missing_id - page_first_id)
                        #### GET ACCURACY OF UPPER AND LOWER PAGE BOUNDS BASED ON PAST REQUEST DATA ##########################
                        try:
                            # not correct page, try lower page --> lowest unvisited page that makes sense
                            if missing_id > page_first_id:
                                # print("try missing > page 1st: lower bound")
                                # over estimated pg #: so want the highest page that's less than our 'missing_id' and is smaller pg# than our over estimation
                                pg_lower_bound = max(
                                    [
                                        x["page"]
                                        for x in bounds_on_page
                                        if missing_id < x["min_id"] and page_number > x["page"]
                                    ]
                                )
                                # print(f"pg lower bound: {pg_lower_bound}")
                            # {missing_id < page_last_id} try higher page --> first unvisited page that makes sense
                            else:
                                # print("try missing < page last: lower bound")
                                # under estimated pg #: so want the highest page that's less than our 'missing_id' and is higher pg# than our under estimation
                                pg_lower_bound = max(
                                    [
                                        x["page"]
                                        for x in bounds_on_page
                                        if missing_id < x["min_id"] and page_number < x["page"]
                                    ]
                                )
                                # print(f"pg lower bound: {pg_lower_bound}")
                            lower_bound_last_id = [x["min_id"] for x in bounds_on_page if x["page"] == pg_lower_bound][
                                0
                            ]
                            lower_bound_id_var = lower_bound_last_id - missing_id
                        except:
                            pg_lower_bound = site_lowest_page - 1
                            lower_bound_id_var = estimated_id_var
                        try:
                            if missing_id > page_first_id:
                                # print("try missing > page 1st: upper bound")
                                pg_upper_bound = min(
                                    [
                                        x["page"]
                                        for x in bounds_on_page
                                        if missing_id > x["max_id"] and page_number > x["page"]
                                    ]
                                )
                                # print(f"pg upper bound: {pg_upper_bound}")
                            else:  # {missing_id < page_last_id} try higher page --> first unvisited page that makes sense
                                # print("try missing < page last: upper bound")
                                pg_upper_bound = min(
                                    [
                                        x["page"]
                                        for x in bounds_on_page
                                        if missing_id > x["max_id"] and page_number < x["page"]
                                    ]
                                )
                                # print(f"pg upper bound: {pg_upper_bound}")
                            upper_bound_first_id = [
                                x["max_id"] for x in bounds_on_page if x["page"] == pg_upper_bound
                            ][0]
                            upper_bound_id_var = missing_id - upper_bound_first_id
                        except:
                            pg_upper_bound = site_highest_page + 1
                            upper_bound_id_var = estimated_id_var

                        # print(
                        #     f"id vars...estimated: {estimated_id_var}, lower bound: {lower_bound_id_var}, upper bound: {upper_bound_id_var}"
                        # )
                        min_id_var = min(estimated_id_var, lower_bound_id_var, upper_bound_id_var)
                        # estimate page # based on our closest data point
                        if estimated_id_var == min_id_var:
                            # page_estimator(start_value, start_index, start_page, find_value, page_size):
                            page_number = page_estimator(page_first_id, 0, page_number, missing_id, results_per_page)
                        elif lower_bound_id_var == min_id_var:
                            page_number = page_estimator(
                                lower_bound_last_id, results_per_page - 1, pg_lower_bound, missing_id, results_per_page
                            )
                        else:  # upper_bound_id_var === min_id_var
                            page_number = page_estimator(
                                upper_bound_first_id, 0, pg_upper_bound, missing_id, results_per_page
                            )
                        # print(f"page est before bounds: {page_number}")
                        # keep page_number within known bounds
                        page_number = min(max(pg_lower_bound + 1, page_number), pg_upper_bound - 1)
                        # print(f"page est after bounds: {page_number}")

                        # should only happen if ID exists in-between adjacent pages
                        if page_number in pages_visited:
                            print(f"have already visited pg# {page_number}, removing ID")
                            ids_to_grab = [x_id for x_id in ids_to_grab if x_id != missing_id]
                            on_page = True
                        else:
                            pass
                        missing_page_attempts += 1
                    else:  # there are results on this page to scrape so scrape the ones that make sense
                        on_page = True

                # GO TO PAGE AND SCRAPE DATA FOR ALL MISSING IDs ON THAT PAGE ##############################
                if (
                    active_scrape == False
                ):  # if pulled page info from memory then actually scrape to get all the records
                    r_results = scrape_json(url, api_attempt_threshold=5)["results"]
                else:
                    pass
                # page_first_id = r_results[0]["id"]
                # page_last_id = r_results[-1]["id"]
                print(f"Scraping page...page_first_id: {page_first_id}, page_last_id: {page_last_id}")
                # make list of potential missing ids on page to limit data to sift through
                ids_on_page = [x_id for x_id in ids_to_grab if x_id <= page_first_id and x_id >= page_last_id]
                print(f"starting records in ids_to_grab: {len(ids_to_grab)}")
                # print(f"total ids_on_page: {len(ids_on_page)}")
                # for all 'ids_on_page' add their desired data to a list that will then be appended to 'data_scraped'
                # a 'for' loop would be more readable but I wanted to play around with generators
                # ... actually just learned that this is an iterable and is therefore store in memory. Generators have "()" around them instead of "[]" and are not stored in memory
                found_id_data = [
                    [x_result["hex_signature"], x_result["text_signature"], x_result["id"], source]
                    for x_result in r_results
                    if x_result["id"] in ids_on_page
                ]
                data_scraped = data_scraped + found_id_data
                # remove 'ids_on_page' from 'ids_to_grab'
                ids_to_grab = [x_id for x_id in ids_to_grab if x_id not in ids_on_page]
                print(f"ending records in ids_to_grab: {len(ids_to_grab)}")
                summary_stats[0]["pages_scraped"] += 1

        # WRITE DATA TO CSV AND UPLOAD TO DATABASE ########################################################
        # once reach upload threshold, write contents of 'data_scraped' to the csv file then upload to the database
        # ...OR if we've scraped some data but errored out on requests, then upload the remaining 'data_scraped'
        if (len(data_scraped) >= upload_threshold or end_scrape == True) and data_scraped != []:
            print("write data to csv")
            # syntax: write_csv(relative_path, file_name, data)
            csv_path = write_csv(relative_path, csv_name, data_scraped)
            # update summary stats
            summary_stats[0]["records_scraped"] += len(data_scraped)
            # add all rows of csv file to database table
            print("Insert from csv to database")
            upload_success = False
            attempts = 0
            while upload_success == False and attempts < len(data_scraped) - 1:
                try:
                    # connect to database
                    con = psycopg2.connect(database=db_name, user=db_user, password=db_password)
                    cur = con.cursor()
                    import_csv_to_db(con, cur, csv_path, db_table)
                    upload_success = True  # if success then stop loop
                    print(f"Upload success: {upload_success}")
                    # update summary stats
                    summary_stats[0]["records_uploaded"] += len(data_scraped)
                    # close db connection
                    cur.close()
                    con.close()
                # if exception and is due to duplicate primary key, then remove that row of data and try again
                # ... else stop and don't upload
                except Exception as x_exception:
                    # close lingering db connection
                    cur.close()
                    con.close()
                    print(f"exception on upload, upload attempts: {attempts}")
                    attempts += 1
                    # if exception is primary key then try to delete issue from csv and continue trying until no remaining data or exception is fixed
                    if x_exception.pgcode == "23505":  # code for 'UniqueViolation'
                        data_scraped = remove_duplicate_key(x_exception, relative_path, csv_name, db_table)
                        csv_path = write_csv(relative_path, csv_name, data_scraped)
                    else:
                        print(x_exception)
                        break  # if a different excpetion then exit while loop
                    time.sleep(0.5)

            data_scraped = []  # reset after upload
        else:  # either no data in 'data_scraped' or haven't reached upload threshold
            pass

    return summary_stats


if __name__ == "__main__":
    main()
