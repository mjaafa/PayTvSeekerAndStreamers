#!/usr/bin/env python
# Package  import
import logging
from logging.config import fileConfig
import Seeker

# package configuration
fileConfig('configuration/log_conf.ini')
logger = logging.getLogger()

# clas definition and global variables definition

######### MAIN #########

def main():
    logging.info("Welcome to the Pay Tv illigal STB seeker")

if __name__ == "__main__":
    main()



