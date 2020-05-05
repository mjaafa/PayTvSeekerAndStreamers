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
from dns import reversename
import ipaddress
import sys

class alexa_api():
    predefined_syntax_basic_url      = "https://www.alexa.com/siteinfo"
    use_rest_api                     = False;
    visibility                       = False;

    def __init__( self, __api_name__):
        self.api_name = __api_name__
        logging.info(" api key")

    def _build_urls(self):
         return self.predefined_syntax_basic_url

    def _getPotentialStreamers(self, results):
        search_traffic  = []
        logging.info("Check Potential Streamers :")
        try :
            search_traffic = self.driver.find_element_by_css_selector("#card_topkeywords > section:nth-child(3) > div:nth-child(2) > div:nth-child(2) > div:nth-child(2)")
            logging.info(" >> search traffic  = %s %", search_traffic)
        except :
            logging.error("error page ")
        return search_traffic

    def search(self, results):
        page_results = []
        urls = self._build_urls()
        if(self.api_name != "censys"):
            return

        try:
            if (None != self.url):
                #response = requests.get(url, timeout=30, verify=False)  # To execute get request
                #logging.debug("http code ", response.status_code)  # To logging.error http response code
                #logging.debug(" response : %s", BeautifulSoup(response.content))  # To logging.error http response code
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
                    time.sleep(2.4)
                    pickle.dump(self.driver.get_cookies(), open("cookies.pkl", "wb"))
                    self.driver.get(self.url)
                    search = self.driver.find_element_by_xpath("//input[starts-with(@class, '.InputAutocomplete-singlesite-0')]")
                    search.clear()
                    for result in results:
                        try :
                            ip = ipaddress.ip_address(result)
                            domain_address = reversename.from_address(ip)
                            search.send_keys(domain_address)
                            auto_complete = self.driver.find_elements_by_xpath("//li[starts-with(@class, '.InputAutocomplete-singlesite-0')]")
                            auto_complete[0].click()

                            cookies = pickle.load(open("cookies.pkl", "rb"))
                            for cookie in cookies:
                                self.driver.add_cookie(cookie)
                                page_results = self._getPotentialStreamers()
                                logging.info("Printed immediately.")
                                time.sleep(2.4)
                        except:
                            logging.info('%s is a correct IP%s address.', (ip, ip.version))
                except:
                    print(" page unreachable ...");
                    self.driver.close()
                    pass;

        except Exception as e:
            logging.debug(" error : %s", e)


