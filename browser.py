from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time

# export PATH=$PATH:/home/develop/Документы/python/sber-our-house-task1/

# url = 'https://xn--80az8a.xn--d1aqf.xn--p1ai/%D1%81%D0%B5%D1%80%D0%B2%D0%B8%D1%81%D1%8B/%D0%BA%D0%B0%D1%82%D0%B0%D0%BB%D0%BE%D0%B3-%D0%BD%D0%BE%D0%B2%D0%BE%D1%81%D1%82%D1%80%D0%BE%D0%B5%D0%BA/%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA-%D0%BE%D0%B1%D1%8A%D0%B5%D0%BA%D1%82%D0%BE%D0%B2/%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA?page=2&limit=1000'


class Browser:

    def __init__(self, headless=True):
        self.browser = None
        self.headless = headless

    def create_browser(self):
        options = webdriver.FirefoxOptions()
        options.headless = self.headless
        options.set_preference("dom.push.enabled", False)
        options.set_preference("geo.enabled", False)
        self.browser = webdriver.Firefox(options=options)
        return self.browser

    def close_browser(self):
        self.browser.quit()

    def get_page(self, url, delay=None, wait_class_name=None):
        try:
            self.browser.get(url)
            if not wait_class_name:
                return self.browser.page_source

            if wait_class_name:
                if delay:
                    # self.browser.implicitly_wait(10)
                    WebDriverWait(self.browser, delay)\
                        .until(EC.presence_of_element_located((By.CLASS_NAME, wait_class_name)))
                return self.browser.page_source

        except Exception as e:
            return e

    def fetch_hrefs_from_page_by_css_selector(self, css_selector):
        urls = set()
        elements = self.browser.find_elements_by_css_selector(css_selector)
        print('Элементов: ', len(elements))
        for e in elements:
            urls.add(e.get_attribute("href"))
        return urls


def create_browser():

    options = webdriver.FirefoxOptions()
    options.headless = False
    options.set_preference("dom.push.enabled", False)
    browser = webdriver.Firefox(options=options)

    return browser


def get_page_with_js(browser, url):
    browser.get(url)
    delay = 5
    try:
        WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'Newbuindings')))
        print("Page is ready!")
    except TimeoutException:
        print("Loading took too much time!")

    return browser.page_source


def close_browser(browser):
    browser.quit()
