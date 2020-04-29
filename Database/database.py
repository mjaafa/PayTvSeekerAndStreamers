import sqlite3
import logging, pprint
import Colorer

import os.path
import hashlib
import pickle
import os
import sys

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
        # build query :
        logging.debug(" >> %s | %s | %s ", __table_definition__, __database_name__, os.path.isfile(__database_name__))
        if (os.path.isfile(__database_name__)):
            logging.debug("datbase create : [%s] %s", __database_name__, __table_definition__)
            query = 'CREATE TABLE IF NOT EXISTS ' + str(__table_definition__) + '';
            logging.debug(" Query %s :", query)
            cur.execute(query)
            self.conn.commit()
        else:
            logging.debug("datbase already exsits")
            return None;
        self.conn.close()

    def checkEncryption(self, __database_name__, __hashToken__):
        try :
            self.conn = sqlite3.connect(__database_name__)
        except Exception as err:
            logging.error("database [%s] error %s  ", __database_name__, str(err));
            return err;

        cur = self.conn.cursor()
        cur.execute(" SELECT TOKEN_HASH FROM SEARCH_API; ")
        self.conn.commit()
        result = cur.fetchall()
        logging.debug(">> result %s ", result)
        if (result != 0):
            for hash in result:
                if (str(hash[0]).strip() == str(__hashToken__).strip()):
                    logging.debug(" keys already generated ")
                    cur.close()
                    return self;
        else:
            cur.close()
            return None;

    def database_insert_raw_data_fromFile(self, __database_name__,  __fileName__, __query__, __api_key__, __sample_key__, __version__):
        logging.debug("datbase create : [%s] :: %s", __fileName__, __database_name__)

        try :
            self.conn = sqlite3.connect(__database_name__)
        except Exception as err:
            logging.error("database [%s] error %s  ", __database_name__, str(err));
            return err;

        cur = self.conn.cursor()
        file = open(__fileName__, "rt")
        #file.read()
        Lines = file.readlines()
        count=0
        keys=[]
        for line in Lines:
            count+=1
            keys.append(line.strip())
            if (count == 1 ):
                cur.execute(" SELECT TOKEN_HASH FROM SEARCH_API; ")
                self.conn.commit()
                result = cur.fetchall()
                logging.debug(">> result %s ", result)
                if (result != 0):
                    for hash in result:
                        if (str(hash[0]).strip() == str(keys[0]).strip()):
                            logging.debug(" the same entry do not insert ")
                            cur.close()
                            return self;
                else:
                    cur.close()
                    return None;

        keys.append(__api_key__);
        keys.append((__sample_key__))
        keys.append((__version__))
        cur = self.conn.cursor()
        cur.execute(__query__, keys)
        self.conn.commit()
        cur.close()
        return self

    def getApiKey(self, __database_name__ , __index__):
        try :
            self.conn = sqlite3.connect(__database_name__)
        except Exception as err:
            logging.error("database [%s] error %s  ", __database_name__, str(err));
            return err;

        cur = self.conn.cursor()
        query = "SELECT API_KEY FROM SEARCH_API WHERE TOKEN_HASH == \"" + str(__index__) +"\""
        cur.execute(query)
        self.conn.commit()
        result = cur.fetchone()
        logging.info(" >> api key :: %s ", result)
        logging.info(" >> api key :: %s ", result[0].strip())
        cur.close()
        return result[0].strip()

    def getSearchKeys(self, __database_name__, __index__):
        try :
            self.conn = sqlite3.connect(__database_name__)
        except Exception as err:
            logging.error("database [%s] error %s  ", __database_name__, str(err));
            return err;

        cur = self.conn.cursor()
        query = "SELECT SEARCH_KEY FROM SEARCH_API WHERE TOKEN_HASH == \"" + str(__index__) +"\""
        cur.execute(query)
        self.conn.commit()
        result = cur.fetchone()
        logging.info(" >> search key :: %s ", result[0].strip())
        cur.close()
        return result[0].strip()

    def getEncryptKey(self, __database_name__, __index__):
        try :
            self.conn = sqlite3.connect(__database_name__)
        except Exception as err:
            logging.error("database [%s] error %s  ", __database_name__, str(err));
            return err;

        cur = self.conn.cursor()
        query = "SELECT KEY1 FROM SEARCH_API WHERE TOKEN_HASH == \"" + str(__index__) +"\""
        cur.execute(query)
        self.conn.commit()
        result = cur.fetchone()
        cur.close()
        return result[0].strip()

    def getDecryptKey(self, __database_name__, __index__):
        try:
            self.conn = sqlite3.connect(__database_name__)
        except Exception as err:
            logging.error("database [%s] error %s  ", __database_name__, str(err));
            return err;

        cur = self.conn.cursor()
        query = "SELECT KEY2 FROM SEARCH_API WHERE TOKEN_HASH == \"" + str(__index__) + "\""
        cur.execute(query)
        self.conn.commit()
        result = cur.fetchone()
        cur.close()
        return result[0].strip()
