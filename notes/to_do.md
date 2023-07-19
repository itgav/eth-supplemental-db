# GOAL

# TO DO

- scrape price data
- create a file that creates outline DB creation, and then table creation
  - I manually created the DB in PGAdmin but the table was created w/ code
- ERC20, 721, etc contract ABIs in a folder to reference when to circumvent proxy contracts
- consolidate scraping functions
- add ENV that maps url_head to source
  - don't have this within function but this way can use as input for the functions
  - don't want to have built into function due to the one offs/ad hoc DB additions
- add optional record input for Missing ID scrape, that way don't have to start at 1st ID in DB if you've already done part of it
  - this is the slower scrape and there will always be some records missing, so if you know 0-100k is fine then should be able to say start at 100k
- add function where to help with determing what blockchain RPC method to use:
  - you can input list of outputs you want and then get list of RPC methods that are possible
  - also be able to input list of inputs and then refine list
- combine 'write_csv' and 'append_csv' function in the 'scrape_data_helper' --> make sure to update in the scraping scripts as well
- refactor scrapers, especially the etherscan scrape
- analyze etherscan token scrape data to figure out best way to parse/refactor and then insert into DB
- etherscan scape --> need to excel filter file
- uniform naming for csv file folders and scraping files
- add DB upload as part of etherscan and 4 bytes if not already
- remove unused imports
- remove duplicate or unused functions
- go through all files
- finalize SQL for remove duplicate key
- add file to create 'blockchain' database
- can you partition a table after the fact? what happens if outside of defined partitions?
- 'latest' block not working, try syncing node and then re-try
- terminal, goals, summaries for all code
- annotate all code
- to TO_DO add next steps in supplement_db and where the data sources are:
  - CEX APIs or Kaggle files
  - de-anonymized data
  - etc
- change all file paths in files to be dynamic or parameterize
- parameterize functions --> args, kwargs, etc
- make a single file to do both of these files' jobs: 'missing log data' 'logs data'
  - same with the 'tx_data' scrapes
- use multiprocessing/multithreading for all 'scrape_blockchain' files. Right now only used for 'state_and_slots'
- need to look into how to have a private .env file or need to remove some variables from there.
  - could just make a variables file
- the 'db_missing_ids' function in 'utility_scrape' could probably be made more efficient by making the DB results a set and then subtracting from itertools.chain --> similar to 'db_missing_blocks' in 'scraping_missing_logs'

## Database

- eventually add a 'currency' table with columns:
  - UID
  - token abbreviation
  - token name
  - token address
- see if there are any duplicates or changes in storage slots
  - same slot/contract for multiple wallet's
  - same contract/wallet but multiple slots

## 'tx_state_diff' and 'contract_storage' scrape

- add scrape for missing blocks

## TESTS

- count and matching tx_hash of a wallet address
- block by time returns correct block

## Organization

- create a venv and requirements.txt
  - <https://www.youtube.com/watch?v=6nwwq2Knb4A&ab_channel=KahanDataSolutions>
