#!/usr/bin/env python
#
# shodan_ips.py
# Search SHODAN and print a list of IPs matching the query
#
# Author: achillean


from time import sleep
import shodan
import sys

import json
from pprint import pprint

Weak_user=False

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class findStreamer():
    # Rocket simulates a rocket ship for a game
    #  or a physics simulation.

    def __init__(self):
        # Each rocket has an (x,y) position.
        conn = sqlite3.connect('stbs_db.sqlite')
        cur = conn.cursor()
        cur.execute('CREATE TABLE STBS_List (IP_ADDR VARCHAR, ECM_SENDING TEXT, SNAPSHOT_STREAMER_WITNESS)')
        conn.commit()

        conn.close()
        self.
        self.y = y

    def move_up(self):
        # Increment the y-position of the rocket.
        self.y += 1

def checkIfTargetusesTorrent():
    print "Check if Target uses torrent :"
    results = driver.find_elements_by_class_name('torrent_files');
    for torrentFiles in results:
        print "Torrent ::", torrentFiles.text


display = Display(visible=0, size=(800, 600))
display.start()
# Configuration
API_KEY = "PSG9x9oZM83aEaLdkA4KfwYkNpP1jDdH"

profile = webdriver.FirefoxProfile()
profile.accept_untrusted_certs = True

driver = webdriver.Firefox(firefox_profile=profile)

api = shodan.Shodan(API_KEY)

# Perform the search
query = ' '.join(sys.argv[1:])
result = api.search("")

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