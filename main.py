#!/usr/bin/env python
# Package  import
import logging
from logging.config import fileConfig
from Seeker.seeker import seeker
from Database.database import database


# package configuration
fileConfig('configuration/log_conf.ini')
logger = logging.getLogger()

# clas definition and global variables definition

######### MAIN #########

def __boot__():
    print(" ")
    print("    MMMMMMMMMMMMMMMMMMMMMMMMMMMMMM")
    print("    MMMMMMMMMMMWXXNNXXNMMMMMMMMMMM")
    print("    MMMMMMMMMMXXWMMMMWNKMMMMMMMMMM")
    print("    MMMMMMMMMXNMMMMMMMMNXMMMMMMMMM")
    print("    MMMMMMMMMXWWWWWWWWWWKMMMMMMMMM")
    print("    MMMMMMNXXNWWWWWWWWWWNXXXWMMMMM")
    print("    MMMMMXNWWWWWWWWWWWWWWWWWKMMMMM")
    print("    MMMMMWXXXNWWWWWWWWWWWNXXNMMMMM")
    print("    MMMMMMMMWKOXXXKXXXX00XWMMMMMMM")
    print("    MMMMMMMMMMKNXXNNNXN0WMMMMMMMMM")
    print("    MMMMMMMMMN0NWWWWWWWKXMMMMMMMMM")
    print("    MMMMMMMWNXKNNWWWWNNX0NMMMMMMMM")
    print("    MMMMWXKXXNWWKNNNNKNWNXXXXWMMMM")
    print("    MMMNKWWWWWWWXXWWNXWWWWWWNXKWMM")
    print("    MMMNKNWWWWWWWKNWKNWWWWWWWXXWMM")
    print("    MMMMMXXNWWWWWNXXNWWWWWNKXWMMMM")
    print("    MMMMMMMNXKXNWWXXWWWNXXXWMMMMMM")
    print("    MMMMMMMMMMNXXXXXXXXXWMMMMMMMMM")
    print("    MMMMMMMMMMMMMMMMMMMMMMMMMMMMMM")
    print("    MMMMMMMMMMMMMMMMMMMMMMMMMMMMMM")

    logging.info(" # Booting The modules # ");
    logging.info(" * Booting Seeker module : ")
    __seeker__instance__ = seeker()
    seeker.set_browser_visibilty(__seeker__instance__, True);
    logging.info("    |->  Booting  component seeker browser : %s ",
                 ("Hidden", "Visible") [bool(seeker.get_browser_visibilty(__seeker__instance__)) == True] )
    seeker.init_config(__seeker__instance__);
    logging.info("    |->  Booting  component Seeker configuration ")

def main():
    logging.info(" *** PayTV BlackMamba seeker ***")
    __boot__();

if __name__ == "__main__":
    main()



