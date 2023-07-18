### scraping data from 4bytes and adding to DB
- could definitely make the scraping functions more combined and cleaner, rather than three 
- need to change wait time to not be based off of page # but "n_loops" --> if start on page 20 n_loop would be 0.
- for the scrape new data function, need to add threshold for upload into the function. Right now there's no threshold so could scrape 1B records before uploading.
- make one of the scrape function input be "event or input" then if either the URL, signature_length, db_table, etc will be matched accordingly

# scraping data from etherscan cloudlabel
### tokens
- {'name': 'Remittance', 'base_url': 'https://etherscan.io/tokens/label/remittance+'}
    Go to url: https://etherscan.io/tokens/label/remittance+?size=100&start=0&col=3&order=desc
    ERROR: get and make subcategory list
    ERROR: Message: no such element: Unable to locate element: {"method":"xpath","selector":"//div[@id[contains(., 'subcattab-')]]"}
    (Session info: chrome=109.0.5414.75)
    Stacktrace:
- scraped blank wallet addresses: only a few and in "Compound" and "idle.finance"

# net balance
- could have a contract that maps balances to addresses within its constructor -> the balance/mapping wouldn't be known through tracing until the address transacts
- for some 'trace_call' 'balanceOf()' you'll get the error: "maximum recursion depth exceeded while decoding a JSON array from a unicode string"
    - ex: rpc_values = {'id': 1, 'jsonrpc': '2.0', 'method': 'trace_call', 'params': [{'data': '0x70a082310000000000000000000000004fbc9b2eb49dbb61d760cda57561b24048a2b25b', 'to': '0x0144b7e66993c6bfab85581e8601f96bfe50c9df'}, ['trace', 'vmTrace'], 14496182]}
    - will need to loop through after initial scrape and fill any block holes in DB
    - you can bypass this error by increasing Python's limit -> just Google and you'll see
    - the couple tx I looked into where it occurred, they seemed like garbage token contracts that are incorrectly relating 'balanceOf' and the balance mapping to each other