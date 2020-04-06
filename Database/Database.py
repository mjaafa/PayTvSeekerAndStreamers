import sqlite3
import logging

class DatabaseInit():
    # init database holding

    def __init__(selfi, __database_name__, __table_definition__):
        # Each rocket has an (x,y) position.
        logging.info("Init Database : ", __database_name__)
        conn = sqlite3.connect(__database_name__)
        cur = conn.cursor()
        #cur.execute('CREATE TABLE STBS_List (IP_ADDR VARCHAR, ECM_SENDING TEXT, SNAPSHOT_STREAMER_WITNESS)')
        # build query :
        query = "CREATE TABLE " + str(__table_definition__);
        cur.execute('%s', query)
        conn.commit()
        conn.close()

    def DatabaseAddElement(self, __elementInsert__):
        # insert streamer data.