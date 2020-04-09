import sqlite3
import logging, pprint
import os.path

class database():
    # init database holding
    def __init__(selfi, __database_name__, __table_definition__):
        # Each rocket has an (x,y) position.
        logging.debug("Init Database : %s", __database_name__)

        try :
            conn = sqlite3.connect(__database_name__)
        except Exception as err:
            logging.error("databese [%s] error %s  ", __database_name__, str(err));
            return err;

        cur = conn.cursor()
        #cur.execute('CREATE TABLE STBS_List (IP_ADDR VARCHAR, ECM_SENDING TEXT, SNAPSHOT_STREAMER_WITNESS)')
        # build query :
        if (__table_definition__  != '' and not os.path.isfile(__database_name__)):
            logging.debug("datbase create : [%s] %s", __database_name__, __table_definition__)
            query = " " " CREATE TABLE " + str(__table_definition__) + " " " ";
            logging.warning(" Query %s :", query)
            cur.execute(query)
            conn.commit()
        else:
            logging.debug("datbase already exsits ")

        conn.close()

