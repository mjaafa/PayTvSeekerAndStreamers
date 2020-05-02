import requests
import json
import logging
import Colorer
from bs4 import BeautifulSoup
## main program emerald hack ###
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import socket
#from goto import goto, label
import time
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from pyvirtualdisplay import Display
import pickle
import os
desired_capabilities = DesiredCapabilities.FIREFOX.copy()
desired_capabilities['acceptInsecureCerts'] = True
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

class censys():

    predefined_syntax_basic_url      = "https://censys.io/ipv4?q="
    predefined_filter_443_code       = "+443.http.get.status_code%3A+200+"
    predefined_filter_80_code        = "80.http.get.status_code%3A200+"
    predefined_filter_443_line       = "443.http.get.status_line%3A+200+"
    predefined_filter_80_line        = "80.http.get.status_line%3A200"
    use_rest_api                     = False;
    visibility                       = False;
    expolit_bug                      = False;

    def __init__( self, __api_key__, __models__):
        __api_key = str(__api_key__).split(",")[1]
        logging.info(" api key : %s ", __api_key.split("@")[1])
        self.api_key = __api_key.split("@")[1]
        self.secret  = __api_key.split("@")[2]
        logging.debug(" API KEY : %s ", self.api_key)
        logging.debug(" secret KEY : %s ", self.secret)
        if (None == self.api_key or None == self.secret):
            self.use_rest_api = False;

        logging.info(" censys api init")
        self.api_keywords = __models__
        logging.info(" >> decrypted models key :: %s ", __models__)

    def _build_urls(self):
        url_built = []
        for __keyword__ in self.api_keywords.split(','):
            logging.info(" models search = %s", __keyword__)
            url = self.predefined_syntax_basic_url  + __keyword__.replace(" ","+")  + \
                  self.predefined_filter_443_code  +  self.predefined_filter_80_code  + \
                  self.predefined_filter_443_line + self.predefined_filter_80_line
            logging.debug(" url :: %s ", url);
            url_built.append(url)

        logging.debug(" url :: %s ", url_built);
        return url_built

    def _getPotentialStreamers(self):
        line  = []
        logging.info("Check Potential Streamers :")
        next_page = self.driver.find_elements_by_css_selector(".hover > a:nth-child(1)")
        try :
            while None != next_page:
                results = self.driver.find_elements_by_css_selector("#resultset");
                logging.debug("Search info : %s ", results)
                if(results.find("selenium.webdriver").isdigit):
                    logging.info(" reset cookies :");

                for line in results[0].text.split('\n'):
                    logging.debug("Search info : %s ", line)

                next_page = self.driver.find_elements_by_css_selector(".hover > a:nth-child(1)")
                if None == next_page:
                    self.driver.close()
                    return line
                self.driver.find_element_by_css_selector('.hover > a:nth-child(1)').click()
        except :
            logging.error("error page ")
        return line

    def search(self):
        __urls__ = self._build_urls()
        logging.info(" urls : %s ", __urls__)
        page_results = []

        for self.url in __urls__:
            try:
                if (None != self.url):
                    logging.debug("url : %s ", self.url)
                    self.display = Display(visible=self.visibility, size=(800, 600))
                    self.display.start()

                    # Configuration browser
                    self.profile = webdriver.FirefoxProfile()
                    self.profile.accept_untrusted_certs = True
                    self.driver = webdriver.Firefox(firefox_profile=self.profile)
                    self.desired_capabilities = DesiredCapabilities.FIREFOX.copy()
                    self.desired_capabilities['acceptInsecureCerts'] = True
                    self.driver.set_window_size(1024, 768)
                    try :
                        self.driver.implicitly_wait(20)
                        logging.debug(" page reached ");
                        time.sleep(20.4)
                        if (True == self.expolit_bug):
                            pickle.dump(self.driver.get_cookies(), open("cookies.pkl", "wb"))
                        self.driver.get(self.url)
                        if (True == self.expolit_bug):
                            cookies = pickle.load(open("cookies.pkl", "rb"))
                            for cookie in cookies:
                                self.driver.add_cookie(cookie)
                        page_results = self._getPotentialStreamers()
                        print("Printed immediately.")
                        time.sleep(2.4)

                    except:
                        print(" page unreachable ...");
                        self.driver.close()
                        continue;
                        pass;
            except Exception as e:
                logging.debug(" error : %s", e)

