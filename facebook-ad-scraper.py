from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd
import time
from datetime import datetime
from bs4 import BeautifulSoup
import os

#   for lines that are pretty self-explanatory, comments are unnecessary,
#   especially when variable names can do the work for you; for example,
#
#       last_height = driver.execute_script("return document.body.scrollHeight")
#
#   as pointed out below can become
#
#       last_height = driver.execute_script(GET_SCROLL_HEIGHT)
#
#   which says in the variable name what it does - the driver executes a script
#   that gets the scroll height and stores it in the last_height variable.
#
#   generally, other programmers will prefer code that uses clear variable and function
#   names to communicate over code that has a comment above each line explaining what it does,
#   and save comments for complicated or unintuitive code.

# see comment on line 51 about file paths
driver_path = '/Users/Admin/Desktop/chromedriver/chromedriver.exe'
driver = webdriver.Chrome(executable_path=driver_path)

# infinite scroll function from https://dev.to/hellomrspaceman/python-selenium-infinite-scrolling-3o12
# including the link where you got the code is extremely good and I wish my coworkers did it more
# to rename an argument to a function, just change the name of the argument
def scroll(driver, scroll_pause_time):

    # it's a best practice to extract repeated constants into variables, so changing the value here
    # automatically propagates to everywhere in the program
    GET_SCROLL_HEIGHT = "return document.body.scrollHeight;"
    SCROLL_TO_BOTTOM = "window.scrollTo(0, document.body.scrollHeight);"

    new_height = 0
    last_height = driver.execute_script(GET_SCROLL_HEIGHT)

    # it's more idiomatic to check the condition at the top of the loop, instead of using `while True` and `break`
    while new_height != last_height:
        last_height = new_height
        driver.execute_script(SCROLL_TO_BOTTOM)
        time.sleep(scroll_pause_time)
        new_height = driver.execute_script(GET_SCROLL_HEIGHT)

# if this script needed to be executed by others, it would be best to
# 1. commit the CSV file, or an example of a valid file, into the repo, and
# 2. use a relative path, like "./facebook_pages_to_watch.csv", to get it from the same folder where the script is running
# if the script needed to be used with other CSVs, you could use argparse to take in the filepath as an argument to the script
urls = pd.read_csv("/Users/Admin/Documents/adscraper/facebook_pages_to_watch.csv")

run_time = datetime.now().strftime("%m-%d-%Y %H.%M.%S")

for ind in urls.index:

    site_name = urls['Name'][ind]
    site_url = urls['fbURL'][ind]

    # load url and scroll to bottom of page

    driver.get(site_url)

    scroll(driver, 4)

    # open html in beautiful soup
    soup = BeautifulSoup(driver.page_source, 'lxml')
    scraped_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    adlist = soup.find_all(class_='_7owt')

    # create table to store ad data
    adtable = pd.DataFrame(columns=['ad_date','ad_id','ad_status','ad_text',
                                    'debug_duplicate','debug_missing'])

    # loop through each ad
    for i in range(len(adlist)):
        ad = adlist[i]
        ad_date = ad.select('._7jwu')
        ad_id = ad.select('._8jox')
        ad_status = ad.select('._7jw1')

        duplicate_debug = max(len(ad_date),len(ad_id), len(ad_status))
        missing_debug = min(len(ad_date),len(ad_id), len(ad_status))

        # get all the text, including text in the links, etc.
        ad_text = " ".join([x.get_text() for x in ad.select('._7jyr, ._231w, ._4yee')]) 

        # add data to adtable
        adtable.loc[i] = [ad_date[0].get_text(),
                          ad_id[0].get_text(),
                          ad_status[0].get_text(),
                          ad_text,
                          duplicate_debug,
                          missing_debug]

    # add data to table

    adtable['site_name'] = site_name
    adtable['scraped_time'] = scraped_time

    # write table
    os.makedirs("".join(["/Users/Admin/Documents/adscraper/data/",
                            run_time,"/",site_name]))
    adtable.to_csv("".join(["/Users/Admin/Documents/adscraper/data/",
                            run_time,"/",site_name,"/data.csv"]))
    
