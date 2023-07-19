# TERMINAL: python -m

# GOAL:
################################################################################################

import psycopg2
from scripts.utility_misc import env_var


db_name = env_var("DB_NAME")
db_user = env_var("DB_USER")
db_password = env_var("DB_PASSWORD")


def main():
    print("hi")


# query data from DB --> doesn't work if you need to loop
def db_fetch_data(sql_script):
    queried_data = None
    # Connect to DB
    con = psycopg2.connect(database=db_name, user=db_user, password=db_password)
    cur = con.cursor()
    # Execute query
    try:
        cur.execute(sql_script)
        queried_data = cur.fetchall()
    # close DB connection
    finally:
        cur.close()
        con.close()

    return queried_data


# Get list of missing IDs from our database, they may or may not be on the website (ID > ID count on website) --> meant to fill in holes after initial scrape
# ex: db id data = [1, 2, 3, 5] --> missing id would be '4'
def db_missing_ids(table_name, source, quantity_threshold):
    db_highest_id = db_fetch_data(
        f"SELECT id_from_source FROM {table_name} WHERE source = '{source}' ORDER BY id_from_source DESC LIMIT 1"
    )[0][0]
    db_lowest_id = db_fetch_data(
        f"SELECT id_from_source FROM {table_name} WHERE source = '{source}' ORDER BY id_from_source ASC LIMIT 1"
    )[0][0]

    # query our DB from lowest ID to highest in increments of 'data_increment'
    # look for any non-contiguous ID #'s append them to 'ids_to_grab' list
    keep_looping = True
    data_increment = 5000
    low_end = db_lowest_id
    top_end = min(low_end + data_increment, db_highest_id + 1)
    current_id = low_end
    ids_to_grab = []
    while keep_looping == True:
        db_ids = db_fetch_data(
            f"SELECT id_from_source FROM {table_name}  WHERE source = '{source}' AND id_from_source >= {low_end} AND id_from_source < {top_end} ORDER BY id_from_source ASC"
        )

        if db_ids == []:  # if no data for range in db
            ids_to_grab = ids_to_grab + list(range(low_end, top_end))  # append full range to 'ids_to_grab'
            current_id = top_end - 1
        elif len(db_ids) != data_increment:  # some 'ids' are missing
            # print(f"low end: {low_end}, top end: {top_end}, missing: {top_end - low_end - len(db_ids)}")
            for i in range(len(db_ids)):
                # determine prior_id
                if i == 0:
                    prior_id = min(low_end, current_id)
                else:
                    prior_id = db_ids[i - 1][0]

                current_id = db_ids[i][0]
                step = current_id - prior_id

                if step == 1:  # number increase from prior id to current id is 1, aka no missing number in between
                    pass
                else:
                    for i in range(1, step):
                        ids_to_grab.append(prior_id + i)
        else:  # no missing ids in DB for the range
            current_id = top_end - 1
            pass

        # if looped through end of db data or have reached quantity threshold, then don't loop again
        if top_end == db_highest_id + 1 or len(ids_to_grab) >= quantity_threshold:
            keep_looping = False
        else:
            pass

        # update values for next DB loop
        low_end = min(top_end, db_highest_id + 1)
        top_end = min(top_end + data_increment, db_highest_id + 1)
        data_increment = top_end - low_end

    return ids_to_grab


if __name__ == "__main__":
    main()
