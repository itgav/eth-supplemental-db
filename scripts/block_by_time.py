# terminal: python -m scripts.block_by_time

from datetime import datetime as dt
from scripts.utility_misc import get_block_info


def main():
    x = block_by_time(2021, 12, 23, 23, 44, 0)
    print(x)


# Returns the approximate blocks from start date to end date based by taking -> (total time / avg block time)
# inputs 'start_date' and 'end_date' should be datetime objects --> datetime(year, month, day, hour, minute, second)
def approx_block_per_time(start_date, end_date):
    start_date = dt.timestamp(start_date)
    end_date = dt.timestamp(end_date)
    lesser_date = min(start_date, end_date)

    # source: https://ycharts.com/indicators/ethereum_average_block_time#:~:text=Ethereum%20Average%20Block%20Time%20is,9.34%25%20from%20one%20year%20ago.
    block_time_dates = [dt(2022, 9, 15, 0, 0, 0).timestamp(), dt(2019, 3, 3, 0, 0, 0).timestamp()]
    avg_block_time = [12, 13, 14]

    # get estimated blocks in time period based on what the avg seconds per block was during the time period
    if lesser_date >= block_time_dates[0]:
        approx_blocks = int((end_date - start_date) / avg_block_time[0])
    elif lesser_date >= block_time_dates[1]:
        approx_blocks = int(
            (max(end_date, block_time_dates[0]) - block_time_dates[0]) / avg_block_time[0]
            + (min(end_date, block_time_dates[0]) - start_date) / avg_block_time[1]
        )
    else:
        approx_blocks = int(
            (max(end_date, block_time_dates[0]) - block_time_dates[0]) / avg_block_time[0]
            + (min(max(end_date, block_time_dates[1]), block_time_dates[0]) - block_time_dates[1]) / avg_block_time[1]
            + (min(end_date, block_time_dates[1]) - start_date) / avg_block_time[2]
        )

    return approx_blocks


# Get the block # just before inputted time -> can be made more efficient, currently takes ~3-5 loops to get approx block and ~3-5 loops to get final block.
# First, gets close to block # by extrapolating block # based on time between inputted time and most recent block time stamp
# Finally, uses the approximated block # to then go block by block until it finds the one just before the inputted time
def block_by_time(year, month, day, hour, minute, second):
    input_time = dt(year, month, day, hour, minute, second)

    time_threshold = 13 * 10  # (avg_block_time * # of blocks)
    loop_threshold = 10  # max loops to try and find block within 'time_threshold'
    pred_block_current = 0
    pred_block_next = "latest"
    time_var = time_threshold + 1
    n_loops = 0
    # 1) looks at most recent block time and the time you input, extrapolates what block would be at input time based on avg block time to get a predicted block
    # 2) compares predicted block to input time, extrapolates what block would be at input time based on avg block time; repeat
    # ... 1&2 are pretty much the same, except for 1) you start at the "latest" block, while 2) you start at the block predicted from prior loop
    while time_var > time_threshold and n_loops < loop_threshold:
        if n_loops == 0:
            pred_block_current = get_block_info(pred_block_next)[
                "number"
            ]  # this step is only needed on first loop when it's "latest"
        else:
            pred_block_current = pred_block_next
        pred_timestamp_current = get_block_info(pred_block_next)["timestamp"]
        time_var = abs(input_time.timestamp() - pred_timestamp_current)
        approx_block_var = approx_block_per_time(input_time, dt.fromtimestamp(pred_timestamp_current))
        pred_block_next = pred_block_current - approx_block_var
        n_loops += 1
        # print(f"block: {pred_block_current}, date: {dt.fromtimestamp(pred_timestamp_current)}, timestamp: {pred_timestamp_current}, time var: {time_var}, next block pred: {pred_block_next}")

    if n_loops == loop_threshold and time_var > time_threshold:
        print("ERROR: couldn't find a close enough block within the loop threshold.")
    else:  # find block just before inputted time
        manual_threshold = 20  # manual tries to find block just before inputted time
        manual_attempts = 0
        # the smallest block found that's greater than the inputted time
        min_greater_input = get_block_info("latest")["number"]  # start as largest block #
        block_to_return = 0
        block_to_return_time = 0
        while manual_attempts < manual_threshold and block_to_return + 1 != min_greater_input:
            # if 1st attempt: use 'pred_block_next' if makes sense; otherwise, +/- 'pred_block_current'
            if manual_attempts == 0:
                # if predicted block makes sense use it to start
                if (input_time.timestamp() > pred_timestamp_current and pred_block_next > pred_block_current) or (
                    input_time.timestamp() <= pred_timestamp_current and pred_block_next <= pred_block_current
                ):
                    block_to_return_time = get_block_info(pred_block_next)["timestamp"]
                    block_to_return = pred_block_next
                elif input_time.timestamp() > pred_timestamp_current:
                    block_to_return_time = get_block_info(pred_block_current + 1)["timestamp"]
                    block_to_return = pred_block_current + 1
                else:
                    block_to_return_time = get_block_info(pred_block_current - 1)["timestamp"]
                    block_to_return = pred_block_current - 1
            else:
                if input_time.timestamp() > block_to_return_time:
                    block_to_return_time = get_block_info(block_to_return + 1)["timestamp"]
                    block_to_return = block_to_return + 1
                else:
                    block_to_return_time = get_block_info(block_to_return - 1)["timestamp"]
                    block_to_return = block_to_return - 1

            # adjust 'min_greater_input' -> the block just after our time period
            if block_to_return < min_greater_input and block_to_return_time > input_time.timestamp():
                min_greater_input = block_to_return
            else:
                pass

            manual_attempts += 1
            # print(f"input time: {input_time.timestamp()}, potential return block time: {block_to_return_time}, potential return block: {block_to_return}, min greater input: {min_greater_input}")

        if manual_attempts == manual_threshold and block_to_return + 1 != min_greater_input:
            print(f"ERROR: Unable to find block for inputted time within the 'manual threshold' for the while loop.")

    return block_to_return


if __name__ == "__main__":
    main()
