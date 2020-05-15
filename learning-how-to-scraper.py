from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd
import time
from datetime import datetime
from bs4 import BeautifulSoup
import os

driver_path = '/Users/Admin/Desktop/chromedriver/chromedriver.exe'
driver = webdriver.Chrome(executable_path=driver_path)

# infinite scroll function from https://dev.to/hellomrspaceman/python-selenium-infinite-scrolling-3o12
def scroll(driver, timeout):
    scroll_pause_time = timeout

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(scroll_pause_time)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            # If heights are the same it will exit the function
            break
        last_height = new_height


# load csv w/ urls
urls = pd.read_csv("/Users/Admin/Documents/adscraper/facebook_pages_to_watch.csv")
#urls = pd.read_csv("/Users/Admin/Documents/adscraper/testing_lol.csv")



# loop through URLs

run_time = datetime.now().strftime("%m-%d-%Y %H.%M.%S")

for ind in urls.index:

    site_name = urls['Name'][ind]
    site_url = urls['fbURL'][ind]

    # load url and scroll to bottom of page

    driver.get(site_url)

    scroll(driver, 4)

    # open html in beautiful soup
    soup=BeautifulSoup(driver.page_source, 'lxml')
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















