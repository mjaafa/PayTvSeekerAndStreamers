import sqlite3
import logging, pprint
import os.path
import hashlib

class database():
    # init database holding
    def __init__(self, __database_name__, __table_definition__):
        # Each rocket has an (x,y) position.
        logging.debug("Init Database : %s", __database_name__)

        try :
            self.conn = sqlite3.connect(__database_name__)
        except Exception as err:
            logging.error("database [%s] error %s  ", __database_name__, str(err));
            return err;

        cur = self.conn.cursor()
        #conn.commit()
        # build query :
        logging.info(" >> %s | %s | %s ", __table_definition__, __database_name__, os.path.isfile(__database_name__))
        if (os.path.isfile(__database_name__)):
            logging.debug("datbase create : [%s] %s", __database_name__, __table_definition__)
            query = 'CREATE TABLE IF NOT EXISTS ' + str(__table_definition__) + '';
            logging.warning(" Query %s :", query)
            cur.execute(query)
            self.conn.commit()
        else:
            logging.debug("datbase already exsits")
        self.conn.close()

    def database_insert_raw_data(self, __object__, __query_elements__):
        logging.info("[DATABASE] ");
        logging.debug("datbase create : [%s] %s", __object__)

        __element__=0
        while (__element__ < __query_elements__):
            __element__ = __element__ + 1
            logging.info(">> %s",__object__[__element__]);

        query = 'INSERT INTO SEARCH_API (KEY1 BLOB NOT NULL, KEY2 BLOB NOT NULL, TOKEN_HASH TEXT, SEARCH_KEYS TEXT';
        logging.warning(" Query %s : ", query)
        self.conn.execute(query)
        self.conn.commit()


