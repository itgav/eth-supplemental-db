import time
import emoji  # need to remove emojis from text to add to CSV (ex: Alchemy token)
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager  # handles driver download and auto-reference
from site_cookies.cookie_functions import load_cookie  # used to auto-login
from scripts.utility_scrape import write_csv, append_csv
# from scrape_web.etherscan_scape import


# to do:
# error handling
# smoother way to handle "no subcategories"
# integrate "token" pages --> is there a way to integrate or will it have to be separate?
# change write_csv function and then update in scaping functions

# For each protocol/category go to their 'token' page, scrape data from each page of 'token' data, then add data to CSV file
# **kwargs: 'starting_point': name of the protocol/category to start scraping at
def scrape_escan_tokens(**kwargs):
    # Setup webdriver
    ##################################################################################################
    options = Options()
    options.add_experimental_option("detach", True)  # won't close browser automatically
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Load url and refresh so that cookies are saved it auto-logins your user
    ##################################################################################################
    url = "https://etherscan.io/labelcloud"
    driver.get(url)
    driver.maximize_window()
    time.sleep(5)

    # get cookies for auto-login then refresh (will be auto-logged in after refresh)
    cookie_file_name = "etherscan_cookie"
    cookie_file_path = f"./eth_trader_profit/site_cookies/cookie_files/{cookie_file_name}"
    load_cookie(driver, cookie_file_path)
    driver.refresh()
    time.sleep(5)

    # Get list of URLs to visit --> want the "token" URLs
    ##################################################################################################
    print("Make url lists for 'tokens'")
    base_url_list = []  # syntax: [{"name": name, "base_url": link}, {}, ...]
    try:
        kwargs["starting_point"]
        after_start = False
    except:
        after_start = True
    # get "token" href for each protocol/category
    # syntax for href: "/tokens/label/name-of-protocol"
    dropdowns = driver.find_elements("xpath", "//div[div/a[contains(@href, '/tokens/label/')]][@class='dropdown']")
    for x in dropdowns:
        link = x.find_element("xpath", ".//a[contains(@href, '/tokens/label')]")
        link = link.get_attribute("href")
        name = x.find_element("xpath", "./button/span")
        name = name.get_attribute("innerHTML").split("<span")[0].strip()
        # if 'starting_point' or after then append to 'base_url_list'
        if after_start is True or name == kwargs["starting_point"]:
            after_start = True
            base_url_list.append({"name": name, "base_url": link})
        else:
            continue

    print(f"# Base URLs = {len(base_url_list)}")

    # syntax: [[{}], [{}], ...]
    # ... 'keys': wallet_address, name_tag, token_name, source, protocol_or_category, status, token_website
    data_scraped = []
    # Go to each URL and scrape the data
    ##################################################################################################
    # base_url_list syntax: [[{"name": name, "base_url": link}], [{}], ...]
    first_loop = True
    for protocol in base_url_list:
        print(protocol)
        page_size = 100
        start_pg_index = 0
        base_url = protocol["base_url"]

        # Go to protocol URL and get list of subcategories
        ##############################################################################################
        url = f"{base_url}?size={page_size}&start={start_pg_index}&col=3&order=desc"
        print(f"Go to url: {url}")
        driver.get(url)
        time.sleep(5)

        subcat_list = []
        # get subcategories on protocol's page will need to loop through all of the subcategories and all of the pages for each subcategory
        try:
            subcats = driver.find_elements("xpath", "//li[@class='nav-item']/a")
            for x_sub in subcats:
                subcat_name = x_sub.get_attribute("name")
                subcat_val = x_sub.get_attribute("val")
                subcat_list.append({"subcat_name": subcat_name, "subcat_val": subcat_val})
            if len(subcat_list) == 0:  # no subcategories --> still need ID for urls and such
                subcat_val = driver.find_element("xpath", "//div[@id[contains(., 'subcattab-')]]")
                subcat_val = subcat_val.get_attribute("id")
                # parse result (ex: initally returns "subcattab-2", will parse that to only be "2")
                subcat_val = subcat_val.split("subcattab-")[1]
                subcat_list.append({"subcat_name": "N/A", "subcat_val": subcat_val})
                one_subcategory = True
            else:
                one_subcategory = False
                pass
            print(f"Subcategories before ordering: {subcat_list}")
        except Exception as x_exception:
            print("ERROR: get and make subcategory list")
            print(f"ERROR: {x_exception}")
            continue  # will move onto next loop

        if one_subcategory is True:
            pass
        else:
            # mark which subcategory the protocol link opened up to
            try:
                first_subcat = driver.find_element("xpath", "//li[@class='nav-item']/a[@class[contains(., 'active')]]")
                first_subcat_name = first_subcat.get_attribute("name")
                first_subcat_val = first_subcat.get_attribute("val")
                # remove 'first_subcat' then add to front of list, want to make sure it matches up with 1st loop of the 'for' loop for below logic
                subcat_list = [x for x in subcat_list if x["subcat_val"] != first_subcat_val]
                subcat_list = [{"subcat_name": first_subcat_name, "subcat_val": first_subcat_val}] + subcat_list
                print(f"Subcategories after ordering: {subcat_list}")
            except Exception as x_exception:
                print("ERROR: get current subcategory and add to front of list")
                print(f"ERROR: {x_exception}")
                continue  # will move onto next loop

        # For each protocol subcategory, scape all pages
        ##############################################################################################
        for x_sub in subcat_list:
            start_pg_index = 0  # 0 indexed
            end_of_pages = False
            while end_of_pages is False:
                if x_sub == subcat_list[0] and start_pg_index == 0:
                    pass  # already on page from code above
                else:  # get page to scrape
                    url = f"{base_url}?subcatid={x_sub['subcat_val']}&size={page_size}&start={start_pg_index}&col=3&order=desc"
                    driver.get(url)
                    print(f"Go to url: {url}")
                    time.sleep(5)

                # if on the error page URL then end loop
                current_url = driver.current_url
                print(f"current_url: {current_url}")
                if current_url == "https://etherscan.io/error":
                    end_of_pages = True
                    print(f"ERROR url, end while loop")
                    break
                else:
                    pass

                # figure out what page we're on --> will use to decide whether or not to go to next page
                page_of = driver.find_element(
                    "xpath", f"//div[@id='table-subcatid-{x_sub['subcat_val']}_paginate']//span[@class='page-link']"
                )
                page_of = page_of.text
                print(f"page_of: {page_of}")
                current_page = int(page_of.split("Page ")[1].split(" of")[0])
                last_page = int(page_of.split("of ")[1])
                print(f"current page: {current_page}, last_page: {last_page}")
                print(f"on lage page: {current_page == last_page}")
                if current_page == last_page:
                    end_of_pages = True  # will be last loop
                    print(f"End of pages, this is last while loop")
                else:
                    pass

                table_rows = len(
                    driver.find_elements("xpath", f"//*[@id='table-subcatid-{x_sub['subcat_val']}']/tbody/tr")
                )
                print(f"Rows on page: {table_rows}")

                # see if on page after all of table records
                try:
                    driver.find_element(
                        "xpath",
                        f"//*[@id='table-subcatid-{x_sub['subcat_val']}']/tbody/tr/td/div[contains(text(), 'no matching entries')]",
                    )
                    end_of_pages = True
                    print(f"End of pages, end while loop")
                    continue
                except NoSuchElementException:  # still on page
                    pass

                # for every row in the table of data, grab the 'address' and 'name_tag'
                for i in range(1, table_rows + 1):
                    try:
                        address = driver.find_element(
                            "xpath", f"//*[@id='table-subcatid-{x_sub['subcat_val']}']/tbody/tr[{i}]/td[2]//a"
                        ).text
                    except NoSuchElementException:
                        print("ERROR: no address")
                        continue  # exit loop --> don't want to append if don't have address

                    try:
                        token_name = driver.find_element(
                            "xpath", f"//*[@id='table-subcatid-{x_sub['subcat_val']}']/tbody/tr[{i}]/td[3]/div/div/a"
                        ).text
                        token_name = emoji.replace_emoji(
                            token_name, ""
                        )  # if there's an emoji in the name then replace it
                    except NoSuchElementException:
                        print("ERROR: no token name")
                        token_name = "N/A"

                    try:
                        website = driver.find_element(
                            "xpath", f"//*[@id='table-subcatid-{x_sub['subcat_val']}']/tbody/tr[{i}]/td[6]/a"
                        )
                        website = website.get_attribute("href")
                    except NoSuchElementException:
                        print("ERROR: no website")
                        website = "N/A"

                    # data_scraped 'keys': wallet_address, name_tag, token_name, source, protocol_or_category, status, token_website
                    data_scraped.append(
                        [
                            address,
                            "N/A",
                            token_name,
                            "Etherscan Label Cloud",
                            protocol["name"],
                            x_sub["subcat_name"],
                            website,
                        ]
                    )

                print(f"data_scraped: {len(data_scraped)}, data_scraped[-1]: {data_scraped[-1]}")
                # add data to CSV
                print("add to CSV")
                if first_loop is True:
                    write_csv("eth_trader_profit/scrapers/csv_files_web", "etherscan_token_scrape", data_scraped)
                    first_loop = False
                else:
                    append_csv("eth_trader_profit/scrapers/csv_files_web", "etherscan_token_scrape", data_scraped)
                time.sleep(5)
                data_scraped = []
                # reset variables for next loop
                start_pg_index += table_rows  # used to tell URL what slice of data we want

    driver.quit()


def main():
    # scrape_escan_tokens(starting_point="Art")
    scrape_escan_tokens()


if __name__ == "__main__":
    main()
