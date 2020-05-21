import requests
import json
import logging
import Colorer
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import socket
import time
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from pyvirtualdisplay import Display


class zoomeye():

    predefined_syntax_basic_url      = "https://www.zoomeye.org/searchResult?q="
    use_rest_api                     = False;
    visibility                       = False;
    fineTune                         = 15;


    def __init__( self, __api_key__, __models__):
        __api_key = str(__api_key__).split(",")[2]
        logging.info(" api key : %s ", __api_key.split("@")[1])
        self.api_key = __api_key.split("@")[1]
        logging.debug(" API KEY : %s ", self.api_key)
        if (None == self.api_key):
            self.use_rest_api = False;

        logging.info(" censys api init")
        self.api_keywords = __models__
        logging.info(" >> decrypted models key :: %s ", __models__)

    def _build_urls(self):
        url_built = []
        for __keyword__ in self.api_keywords.split(','):
            logging.info(" models search = %s", __keyword__)
            url = self.predefined_syntax_basic_url  + __keyword__.replace(" ","%20")
            logging.debug(" url :: %s ", url);
            url_built.append(url)

        logging.debug(" url :: %s ", url_built);
        return url_built

    def _getPotentialStreamers(self):
        line  = []
        logging.info("Check Potential Streamers :")
        next_page = self.driver.find_elements_by_css_selector(".ant-pagination-next")
        try :
            while None != next_page:
                results = self.driver.find_elements_by_css_selector("div.search-result-item");
                for line in results[0].text.split('\n'):
                    #stripped_line = line.strip()
                    logging.debug("Search info : %s ", line)

                next_page = self.driver.find_elements_by_css_selector(".ant-pagination-next")
                if None == next_page:
                    self.driver.close()
                    return line
                self.driver.find_element_by_css_selector('.ant-pagination-next').click()
        except :
            logging.error("error page ")
        return line

    def search(self):
        __urls__ = self._build_urls()
        logging.info(" urls : %s ", __urls__)
        page_results = []
        self.profile = webdriver.ChromeOptions()
        self.profile.add_argument('--ignore-certificate-errors')
        self.profile.add_argument('--headless')
        self.driver = webdriver.Chrome(chrome_options=self.profile)
        if (self.visibility):
           self.display = Display(visible=self.visibility, size=(800, 600))
           self.display.start()
        else:
            self.driver.set_window_size(0,0)

        for url in __urls__:
            try:
                if (None != url):
                    logging.debug("url : %s ", url)
                    # Configuration browser
                    try :
                        self.driver.implicitly_wait(self.fineTune)
                        logging.debug(" page reached ");
                        #time.sleep(2)
                        cookies = self.driver.manage().getCookies();
                        self.driver.manage().getCookieNamed(cookies);
                        self.driver.manage().addCookie(cookies);
                        self.driver.get(url)
                        page_results = self._getPotentialStreamers()
                        print("Printed immediately.")
                        #time.sleep(31.4)
                    except:
                        print(" page unreachable ...");
                        continue;
                        pass;
            except Exception as e:
                logging.debug(" error : %s", e)
                self.driver.close()
                if (self.visibility):
                    self.display.close()

