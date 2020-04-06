#!/usr/bin/env python
#
# shodan_ips.py
# Search SHODAN and print a list of IPs matching the query
#
# Author: achillean

from time import sleep
import shodan
import sys
import logging
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyvirtualdisplay import Display
import Database

import json
from pprint import pprint

class seeker():
    # Rocket simulates a rocket ship for a game
    #  or a physics simulation.
    API_KEY = "PSG9x9oZM83aEaLdkA4KfwYkNpP1jDdH"
    visibility = 0

    def __init__(self):
        # init webdriver
        self.engine.display = Display(visible=self.visibility, size=(800, 600))
        self.engine.display.start()

        # Configuration browser
        self.engine.profile = webdriver.FirefoxProfile()
        self.engine.profile.accept_untrusted_certs = True
        self.engine.driver = webdriver.Firefox(firefox_profile=self.engine.profile)

        # configure Xengine
        self.engine.api = shodan.Shodan(self.API_KEY)

        # Each rocket has an (x,y) position.
        #conn = sqlite3.connect('stbs_db.sqlite')
        #cur = conn.cursor()
        #cur.execute('CREATE TABLE STBS_List (IP_ADDR VARCHAR, ECM_SENDING TEXT, SNAPSHOT_STREAMER_WITNESS)')
        #conn.commit()
        #conn.close()

    def set_browser_visibilty(self, __visible__):
        self.visibility = __visible__;

    def get_browser_visibilty(self, __visible__):
        return self.visibility;

    def __checkIfTargetusesTorrent(self):
        logging.debug("Check if Target uses torrent :");
        results = self.driver.find_elements_by_class_name('torrent_files');
        for torrentFiles in results:
            logging.info("Torrent ::", torrentFiles.text);

    def __init_load_searck_keys(self):
        self.engine.api.searchKeyDatabase = Database()

    def search(self):
        # Increment the y-position of the rocket.
        # Perform the search
        self.engine.query = ' '.join(sys.argv[1:])
        result = self.engine.api.search("")



driver_emby = webdriver.Firefox()

# Loop through the matches and print each IP
for service in result['matches']:
                print "**********************************"
                print service['ip_str'];
                print service['location'];
                print service['port']
                driver.implicitly_wait(10)
                #if "186.229.29.210" in str(service['ip_str']):
                #    continue;
                if "443" in str(service['port']):
                    url = "https://"+str(service['ip_str'])+":"+str(service['port'])+"/emby/users/public?format=json";
                    secured=True;
                else:
                    url = "http://"+str(service['ip_str'])+":"+str(service['port'])+"/emby/users/public?format=json";
                    secured=False;
                print url
               # print ("URL built is :", url.split(" ")[1])
                try:
                    driver.get(url);
                except:
                    continue;
                detectingWeakUser();
                torrentCheck="https://iknowwhatyoudownload.com/en/peer/?ip="+str(service['ip_str']);
                driver.get(torrentCheck);
                checkIfTargetusesTorrent();
                if(Weak_user==True):
                    if (True == secured):
                        urld = "https://"+str(service['ip_str'])+":"+str(service['port']);
                    else:
                        urld = "http://"+str(service['ip_str'])+":"+str(service['port']);
                    #driver_emby.set_window_size(1024, 768)
                    #driver_emby.get(urld)
                    Weak_user=False;
                    print("URL ", urld)
                #sleep(60);
                #

driver.close();