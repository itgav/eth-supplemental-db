# GOAL

- url: <https://etherscan.io/labelcloud>
- inspiration: <https://github.com/brianleect/etherscan-labels>

### impute randomness

- wait time
- index to choose token/protocol link

### notes while making code

- how to identify protocol created vs other user created (ex: uniswap, maybe sushiswap)
- which ones to exclude if no nametag?:
  - ideas: uniswap, website down
- ones to exclude:
- have error checks so we know where to fix logic and or re-scrape
  - exception when don't find missing entry
  - exception when go to far past pg index
  - how to blank nametags show up?
- don't forget to add source to data_scraped prior to upload
- afterwards:
  - cross-check tokens vs accounts results
  - any duplicate names or wallet addresses?
- get subcategory name to include in data
- not going to make manual list of subcategories because unsure the total that exists
  - example: "abracadabra.money", their 2nd category is '0' where as others is '3-0'
- Am using 'time.sleep()' to wait. Don't see a real need to use explicit or implicit waits since everything loads fine and I want to give the site some wait time.

### issues

- how to handle "real estate" accounts --> there's a link but no account info
