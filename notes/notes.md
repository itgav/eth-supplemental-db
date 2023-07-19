# GOAL

- added "source" column to DB after the fact
- for the second scrape of 4bytes (to fill in DB data) to get the "old ungotten records", am going to start from end of DB and then scrape until end of website.
  - am doing this instead of, end of website to end of DB because if our scrape for some reason is unsuccessful, there will still be a contiguous piece from end of DB to end of website.
- scrape_etherscan.py:
  - would get the following error: "[4496:9784:0114/182620.398:ERROR:util.cc(134)] Can't create base directory: C:\Program Files\Google\GoogleUpdater"
  - this would occur when i was scraping 1 protocol, on the last subcategory which is weird that it didn't occur on the first or 2nd subcategories
  - FIX: manually create the folder "GoogleUpdater" at path C:\Program Files\Google\GoogleUpdater
    - Not sure what webdriver-manager uses it for, but seems like was gettign error because need admin privilege to create the folder

- tx data:
  - 'to: None' in the data means a contract was created, on Etherscan the 'to' field has the contract address
    - ex: 0xb51ca5fbc701005275b9d0b89f169bf0956bcb9460d9f705092609e1301f9e78
  - no trace_call revert when attempting an 'invalid' balanceOf call
    - ex: 0x78ec6a60c93694ac9dc5598890ae7d472d3d91ba0292c84daae2751fc70c3adb
- tx net balance:
  - can't figure out why balance from stateDiff doesn't match, it seems to be due to the fee the miner received I think it is from the tip
    - ex: 0x1b5aea06ffc08d841829b355b439a0398e1430316d1a151ff943f656e4587ca3 to 0xf4099d45e37814256e9a59a8af22201f0270b5ee0ed67c25bbb41d2c5c753bfd
    - the tx is a type 0, so I think all the excess goes to the miner automatically. However, I'm not sure how to see the amount that goes to the miner.
  - wallet 0xfc66531369f28578c3dc560d7f6c94ed887e91dc has a balance change from tx 0xe92bb53f84cf391f952341f4c2899eff138629ab2e4fae63b5de0d49548e06ec, where they are not the 'from' or 'to. It will be difficult to accurately determine net balance change until we can query for stateDiffs involving an address.
  - only have transactions in a block, which excludes any failed transactions a person made, this would balance could decrease from gas used for failed transactions
  - when determine what contracts represent tokens, and therefore, which ones to add data to the DB for:
    - don't anticipate the checks in the "net balance" scrape being exhaustive --> will need to develop an actual separate test to determine if it meets standards
      - however, the checks should do a decent enough job to capture most instances

- contract storage slot:
  - storage slot from stateDiff is 66 length and actual is 65 length: -> stateDiff is zero padded
    - actual storage slot: "0x409631f0d946f511693071a0a22ff236939d83b8b43943d96b619b96814fee3"
    - slot from stateDiff: "0x0409631f0d946f511693071a0a22ff236939d83b8b43943d96b619b96814fee3"
    - tx hash = "0x9a9f77c15467a14e2d45ced30e79a7bf3428a527ef2809e266334630515ff53e"
    - x_contract = "0x9e46a38f5daabe8683e10793b06749eef7d733d1" --> erc-20
    - x_address = "0xd3c2139385052890f33a2b990b6913e7a88a0dcd"
    - block = 14000799

- gas:
  - gas fee can't be calculated from 'eth_getTransactionByHash', you need the transaction RECEIPT data
  - when the block is mined, the base_fee is burned

- gas fee calculation:
  - prior to London upgrade (August 2021): gas_used * gas_price = gas_fee
    - remember 'gas_used' is capped by 'gas_limit'
    - miners received the total gas fee from any transaction included in a block
  - after London upgrade: gas_used * (base_fee + priority_fee)
  - maxFeePerGas: will be refunded any amount less but ultimately places a ceiling on willingness to spend
  - the tx_sender sets the 'maxPriorityFee' you can calculate the 'priorityFeePerGas' based on what the miner actually receives.
    - miner is only paid from tips, the rest is burnt
    - (priorityFeePerGas = minerEthIncrease / gasUsed)
- determining if the contract is an ERC standard token
  - have been using 2 strategies:
        1. use the 'balanceOf' function for the ERC-normal and ERC-1155 to see if the calls revert
            - if both revert or neither revert then it's not a token --> issue is WETH (contract: 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2) which doesn't revert
        2. looking to see if the 'RETURN' occurs in the 'vmTrace' for the 2 'balanceOf' calls, specifically is the last opcode. If 'RETURN' then valid
            - issue is when both of the 'balanceOf' calls have the 'RETURN' opcode (ex contract: 0xe85be3a69c2cd473b80a7c32f0e286f2afcba82b)
                - seems to be flawless if you logic is: only 1 of the 'balanceOf' calls has the 'RETURN' opcode
  - Issues:
    - contract 0x3496b523e5c00a4b4150d6721320cddb234c3079: doesn't revert and returns for both --> only returns balance for ERC-20
      - same issue but may be erc-1155 or erc-normal
      - contract 0xa342f5D851E866E18ff98F351f2c6637f4478dB5
    - contract 0x1a2a1c938ce3ec39b6d47113c7955baa9dd454f2: for both balanceOf(): 'RETURN', no revert, but has output of '0x'
      - is NOT a contract. The output may be a better indicator than  the 'RETURN'
      - I think the output will also cover those that 'REVERT'
    - contract reverts one block but then doesn't and returns the next:
      - x_contract in storage_map: 0x38ec27c6f05a169e7ed03132bca7d0cfee93c2c5
        - x_address in log_addresses: 0x3caeac7ff83b19f4d14c02cda879c4740b4f0378
        - criteria_string: NNV-ZNV
        - block: 13738484
- no data for block_traces = node_rpc_command["trace_replayBlockTransactions", 13738482, ["stateDiff"]]("result")
  - but there's data for the blocks around that. Not sure if data should be returned for that block or not

### SQL

- table sizes:
    select
    table_name,
    pg_size_pretty(pg_relation_size(quote_ident(table_name))),
    pg_relation_size(quote_ident(table_name))
    from information_schema.tables
    where table_schema = 'public'

### MULTIPROCESSING

- for 'multiprocessing' library, 'Process(target=x_func)' if you instead put 'Process(target=x_func())':
  - side effects I've observed:
    - if 'x_func' needs the memory of the main process then it will error w/o '()' but won't with '()'
    - if '()' are included then a new process is created but the whole script still runs in order
    - if you try to define multiple processes:
      - if both use '()' then they will each have the same process ID and will run in order
      - if only 1 uses '()' then they will have different process IDs but will still run in order
  - TAKEAWAY: to run parallel processes the syntax is 'Process(target=x_func)'

### PYTHON SPEED

- comparing speed of "if 'x' and 'y':" vs "if 'x': if 'y':":
  - the speed difference is fairly negligible but...
  - the speed seems correlated to how many booleans the need to be check before it can evaluate. ex:
    - if 'x' and 'y' -> are TRUE. Then the above example will be pretty much the same speed because for both, the code only has to check 'x' and 'y' once.
    - however, if the above example had an additional check prior to the 'x' and 'y'. ex --> "if 'x' and not 'y':" vs "if 'x': if 'y':"
      - in the new example, the nested 'if' would be faster because it only requires to checks. Whereas the 'if and' would require some third or more checks before it gets to the portion where it can evaluate as TRUE.

### ERIGON RPC FLAGS

- improving speed:
  - rpc.batch.concurrency --> slight improvement
  - db.read.concurrency --> haven't seen much change with this
    - It should already be at max, see: <https://stackoverflow.com/questions/17853831/what-is-the-gomaxprocs-default-value>
