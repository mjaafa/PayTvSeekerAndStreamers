#!/usr/bin/env python
# Package  import
import logging
from logging.config import fileConfig
from Seeker.seeker import seeker
from Database.database import database
from NetworkHoppingManager.vpnHopper import vpnHopper


# package configuration
fileConfig('configuration/log_conf.ini')
logger = logging.getLogger()

# clas definition and global variables definition

######### MAIN #########

def __boot__():
    print(" ")
#    print("    MMMMMMMMMMMMMMMMMMMMMMMMMMMMMM")
#    print("    MMMMMMMMMMMWXXNNXXNMMMMMMMMMMM")
#    print("    MMMMMMMMMMXXWMMMMWNKMMMMMMMMMM")
#    print("    MMMMMMMMMXNMMMMMMMMNXMMMMMMMMM")
#    print("    MMMMMMMMMXWWWWWWWWWWKMMMMMMMMM")
#    print("    MMMMMMNXXNWWWWWWWWWWNXXXWMMMMM")
#    print("    MMMMMXNWWWWWWWWWWWWWWWWWKMMMMM")
#    print("    MMMMMWXXXNWWWWWWWWWWWNXXNMMMMM")
#    print("    MMMMMMMMWKOXXXKXXXX00XWMMMMMMM")
#    print("    MMMMMMMMMMKNXXNNNXN0WMMMMMMMMM")
#    print("    MMMMMMMMMN0NWWWWWWWKXMMMMMMMMM")
#    print("    MMMMMMMWNXKNNWWWWNNX0NMMMMMMMM")
#    print("    MMMMWXKXXNWWKNNNNKNWNXXXXWMMMM")
#    print("    MMMNKWWWWWWWXXWWNXWWWWWWNXKWMM")
#    print("    MMMNKNWWWWWWWKNWKNWWWWWWWXXWMM")
#    print("    MMMMMXXNWWWWWNXXNWWWWWNKXWMMMM")
#    print("    MMMMMMMNXKXNWWXXWWWNXXXWMMMMMM")
#    print("    MMMMMMMMMMNXXXXXXXXXWMMMMMMMMM")
#    print("    MMMMMMMMMMMMMMMMMMMMMMMMMMMMMM")
#    print("    MMMMMMMMMMMMMMMMMMMMMMMMMMMMMM")
    logging.debug( " testing vpn hopper ")
    __vpn_instance___ = vpnHopper()
    ifname = "enp0s20f0u5"
#    ifname = "lo"
    mac_address = vpnHopper.get_mac_address(__vpn_instance___, ifname)
    socket = vpnHopper.setup_if_conf_urllib3(__vpn_instance___, ifname)
    logging.debug(" get mac address %s : %s ", ifname, mac_address)
    logging.info(" # Booting The modules # ");
    logging.info(" * Booting Seeker module : ")
    __seeker__instance__ = seeker()
    seeker.set_browser_visibilty(__seeker__instance__, False);
    logging.info("    |->  Booting  component seeker browser        : %s ",
                 ("Hidden", "Visible") [bool(seeker.get_browser_visibilty(__seeker__instance__)) == True] )
    if (None != seeker.init_config(__seeker__instance__)):
        logging.info("    |->  Booting  component Seeker configuration : Done")
        return __seeker__instance__;
    else:
        logging.info("    |->  Booting  component Seeker configuration : NOK ")
        return None;

def main():
    logging.info(" *** PayTV BlackMamba seeker ***")
    seeker__ = __boot__();
    if (None == seeker__):
        return None;
    seeker.search(seeker__)

if __name__ == "__main__":
    main()
