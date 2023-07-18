# Use these for scraping websites to first get cookie info for log-in so that you're automatically logged into the website

### STEPS TO SAVE COOKIES AND THEN IMPLEMENT IN SCRAPING SCRIPT
###########################################################################################
# 1) Prerequisites: 'site_cookies' folder, 'cookie_functions.py' file, 'get_cookies.py' file
# 2) run 'get_cookies.py' for the website you want cookies for when you are scraping (so the website you'll be scraping)
# 3) in your scraping file, import 'load_cookie' --> have webdriver get(url) --> load_cookie(for that url) --> webdriver.refresh()
# ... so go to page, load cookie file for that page, refresh page and then you should be auto-logged in

import json


def save_cookie(driver, path):
    with open(path, "w") as filehandler:
        json.dump(driver.get_cookies(), filehandler)


def load_cookie(driver, path):
    with open(path, "r") as cookiesfile:
        cookies = json.load(cookiesfile)
    for cookie in cookies:
        driver.add_cookie(cookie)
