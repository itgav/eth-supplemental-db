# TERMINAL: python -m

# GOAL:
################################################################################################

# Used to go to a website, manually log-in, and then save the cookies for the log-in credentials
# ^^^ then can load cookies in a scraping script so that you don't have to re-login with the selenium browser

from selenium import webdriver
from site_cookies.cookie_functions import save_cookie


url = "https://etherscan.io/"
cookie_file_name = "etherscan_cookie"

driver = webdriver.Chrome()
driver.get(url)

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! --> make sure to do below when running
# type anything into the terminal and then hit 'enter'
foo = input()

cookie_file_path = f"./cookie_files/{cookie_file_name}"
save_cookie(driver, cookie_file_path)
