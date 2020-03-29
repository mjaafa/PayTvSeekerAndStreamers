import sqlite3

class streamerDBInit():
    # init database holding

    def __init__(self):
        # Each rocket has an (x,y) position.
        conn = sqlite3.connect('stbs_db.sqlite')
        cur = conn.cursor()
        cur.execute('CREATE TABLE STBS_List (IP_ADDR VARCHAR, ECM_SENDING TEXT, SNAPSHOT_STREAMER_WITNESS)')
        conn.commit()
        conn.close()

    def addStreamer():
