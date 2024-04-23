from robocorp import browser
from robocorp.tasks import task
from RPA.Excel.Files import Files as Excel
from RPA.Browser.Selenium import Selenium
from RPA.Browser.Selenium import By
from RPA.Browser.Selenium import WebDriverWait
from RPA.Browser.Selenium import expected_conditions as EC
from RPA.Browser.Selenium import FirefoxOptions
from RPA.Browser.Selenium import selenium_webdriver as wd
from pathlib import Path
import os
import requests
import io
from PIL import Image

FILE_NAME = "challenge.xlsx"
OUTPUT_DIR = Path(os.environ.get('ROBOT_ARTIFACTS'))
EXCEL_URL = f"https://rpachallenge.com/assets/downloadFiles/{FILE_NAME}"


from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import time

search_phrase = "War"
# options = webdriver.FirefoxOptions()

# Function to scroll to position of 'Show More' Button.
# Total result set after clicking 'Show More' = 20
def scroll_shim(passed_in_driver, object):
    x = object.location['x']
    y = object.location['y']
    scroll_by_coord = 'window.scrollTo(%s,%s);' % (
        x,
        y
    )
    scroll_nav_out_of_way = 'window.scrollBy(0, -120);'
    passed_in_driver.execute_script(scroll_by_coord)
    passed_in_driver.execute_script(scroll_nav_out_of_way)

# Function to download article image
def download_image(download_path, url, file_name):
	try:
		image_content = requests.get(url).content
		image_file = io.BytesIO(image_content)
		image = Image.open(image_file)
		file_path = download_path + file_name

		with open(file_path, "wb") as f:
			image.save(f, "JPEG")

		print("Success")
	except Exception as e:
		print('FAILED -', e)

# options.add_argument('--ignore-certificate-errors-spki-list')
# options.add_argument('--ignore-ssl-errors')

# service = Service(executable_path="geckodriver.exe")


@task
def runwebsite():
    
    driver = Selenium(auto_close=False)
    # webdriver.Firefox(service=service, options=options)
    # driver.open_chrome_browser("https://www.aljazeera.com/")
    driver.set_selenium_page_load_timeout(10)
    driver.open_available_browser("https://www.aljazeera.com/")
    # driver.open_available_browser4

    # driver.maximize_browser_window()
    # Find and click search button
    # buttons = driver.find_element('//button[.//span[text()[contains(., "Click here to search")]]]')
    driver.click_element('class:site-header__search-trigger')

    # buttons.click()
    driver.input_text_when_element_is_visible('class:search-bar__input', search_phrase + Keys.ENTER)
    #Enter search term into input field
    # inputBar = driver.find_element("//input[@class='search-bar__input']")
    # inputBar.send_keys(search_phrase + Keys.ENTER)
    # Select Date category

    driver.click_element_when_visible("class:search-summary__select")
    # dropdown.click()

    dropdown_options = driver.find_elements("tag:option")

    print(dropdown_options)

    i = 0
    while i < len(dropdown_options):
        if(dropdown_options[i].text == "Date"):
            dropdown_options[i].click()
            break
        i = i + 1

    
    # Scroll down and Press show more button
    EC.visibility_of_element_located
    show_more_btn = driver.wait_until_page_contains_element("class:show-more-button grid-full-width", 60)
    # WebDriverWait(driver, 60).until(
    #     EC.presence_of_element_located("class:show-more-button grid-full-width")
    # )
    

    # if 'firefox' in driver.capabilities['browserName']:
    #     scroll_shim(driver, show_more_btn)

    ActionChains(driver).move_to_element(show_more_btn).click().perform()

    time.sleep(10)
    articles = driver.find_elements('tag:article')

    # WebDriverWait(driver, 360).until(
    #     EC.presence_of_all_elements_located((By.TAG_NAME, 'article'))
    # )

    print(articles)
    # //article[@class="gc u-clickable-card gc--type-customsearch#result gc--list gc--with-image"]
    # driver.find_elements('xpath', '//article[@class="gc u-clickable-card gc--type-customsearch#result gc--list gc--with-image"]')

    title = []
    desc = []
    date = []
    count = []
    money = []
    image_urls = []
    image_file_names = []

    j = 0
    while j < len(articles):
        ttl = articles[j].find_element('.//h3[@class="gc__title"]//span').get_attribute('innerHTML').replace('\n', '').replace('<br>', '').replace('&nbsp;', '')
        title.append(ttl)
        string_list = articles[j].find_element('.//div[@class="gc__excerpt"]//p').text.split('...')
        desc.append(string_list[1].replace('\n', '').replace('<br>', '').replace('&nbsp;', ''))
        date.append(string_list[0])
        count.append(ttl.count(search_phrase) + string_list[1].count(search_phrase))
        money.append(True if(ttl.find('$' or 'dollars' or 'USD') != -1 or string_list[1].find('$' or 'dollars' or 'USD') != -1)
                    else False)
        image_urls.append(articles[j].find_element('.//img[@class="article-card__image gc__image"]').get_attribute('src'))
        image_file_names.append(search_phrase + "_img" + str(j))
        j = j + 1

    dframe = pd.DataFrame({'title':title, 'description': desc, 'date': date, 'search_phrase count': count, 'currency': money, 'iamge_name': image_file_names})

    print(dframe)
    dframe.to_csv("files\\" + search_phrase + ".csv")

    for i, url in enumerate(image_urls):
        download_image("img\\", url, search_phrase + "_img" + str(i) + ".jpg")
    # urls = get_image_urls(driver=driver)

    # for i, url in enumerate(urls):
    #     print(i, ' : ', url)

    # time.sleep(50)

    # driver.quit()