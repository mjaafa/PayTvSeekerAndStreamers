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
import pickle
import os
#trick n' tweak the browser
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
import ipaddress

class censys():

    predefined_syntax_basic_url      = "https://censys.io/ipv4?q="
    predefined_filter_443_code       = "+443.http.get.status_code%3A+200+"
    predefined_filter_80_code        = "80.http.get.status_code%3A200+"
    predefined_filter_443_line       = "443.http.get.status_line%3A+200+"
    predefined_filter_80_line        = "80.http.get.status_line%3A200"
    use_rest_api                     = False;
    visibility                       = False;
    expolit_bug                      = True;
    should_activates_cookies         = True;
    fineTune                         = 10;

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
        clients  = []
        logging.info("Check Potential Streamers :")

        next_page = self.driver.find_elements_by_css_selector(".hover > a:nth-child(1)")
        index = 0
        try :
            while None != next_page:
                results = self.driver.find_elements_by_css_selector("#resultset");
                logging.debug("Search info : %s ", results[0].text)
                for line in results[0].text.split('\n'):
                    try:
                        __ip__ = line.split()[0]
                        ip = ipaddress.ip_address(__ip__);
                        clients.append(ip);
                        next_page = self.driver.find_elements_by_css_selector(".hover > a:nth-child(1)")

                        if None == next_page:
                            self.driver.close()

                            if (self.visibility):
                                self.display.close()
                        return clients

                        self.driver.find_element_by_css_selector('.hover > a:nth-child(1)').click()
                    except:
                        logging.debug(" not ip address %s ", __ip__)
                        continue;
                        pass;

        except :
            logging.error("error page ")
            self.driver.quit()
            if (self.visibility):
                self.display.close()
            return clients

        return clients

    def search(self):
        __urls__ = self._build_urls()
        logging.info(" urls : %s ", __urls__)
        page_results = []
        self.desired_capabilities = DesiredCapabilities.CHROME.copy()
        self.desired_capabilities['acceptInsecureCerts'] = True
        self.profile = webdriver.ChromeOptions()
        self.profile.add_argument('--ignore-certificate-errors')
        self.profile.add_argument('headless')
        self.driver = webdriver.Chrome(chrome_options=self.profile)
        if (self.visibility):
            self.display = Display(visible=self.visibility, size=(800, 600))
            self.display.start()
        else:
            self.driver.set_window_size(0,0)

        for self.url in __urls__:
            try:
                if (None != self.url):
                    logging.debug("url : %s ", self.url)

                    # Configuration browser
                    try :
                        self.driver.implicitly_wait(self.fineTune)
                        logging.debug(" page reached ...");
                        time.sleep(20.4)
                        if (True == self.expolit_bug):
                            pickle.dump(self.driver.get_cookies(), open("cookies.pkl", "wb"))

                        logging.debug(" get url !: %s", self.url)
                        self.driver.get(self.url)
                        if (True == self.expolit_bug):
                            cookies = pickle.load(open("cookies.pkl", "rb"))
                            for cookie in cookies:
                                self.driver.add_cookie(cookie)
                        page_results = self._getPotentialStreamers()

                        print("Printed immediately.")

                        time.sleep(2.4)
                        self.driver.close()

                        if (self.visibility):
                            self.display.close()


                    except:
                        print(" page unreachable ...");
                        self.driver.close()
                        if (True == self.visibility):
                            self.display.close()
                        continue;
                        pass;
            except Exception as e:
                logging.debug(" error : %s", e)
                self.driver.close()
                if (self.visibility):
                    self.display.close()
                if(self.expolit_bug):
                    os.remove("cookies.pkl")

        return page_results
