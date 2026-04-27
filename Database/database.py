import logging
import os.path
import re
import sqlite3


_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _validate_identifier(name):
    if not _IDENTIFIER.match(str(name)):
        raise ValueError(f"Invalid SQL identifier: {name!r}")
    return str(name)


class database:
    def __init__(self, __database_name__, __table_definition__):
        logging.debug("Init Database: %s", __database_name__)
        self.conn = sqlite3.connect(__database_name__)
        try:
            cur = self.conn.cursor()
            query = "CREATE TABLE IF NOT EXISTS " + str(__table_definition__)
            cur.execute(query)
            self.conn.commit()
        finally:
            self.conn.close()

    def _fetch_one_value(self, __database_name__, column, __index__):
        column = _validate_identifier(column)
        with sqlite3.connect(__database_name__) as conn:
            cur = conn.cursor()
            cur.execute(
                f"SELECT {column} FROM SEARCH_API WHERE TOKEN_HASH = ?",
                (str(__index__),),
            )
            result = cur.fetchone()
        if not result:
            raise KeyError(f"No SEARCH_API row for TOKEN_HASH={__index__!r}")
        return result[0].strip() if isinstance(result[0], str) else result[0]

    def checkEncryption(self, __database_name__, __hashToken__):
        with sqlite3.connect(__database_name__) as conn:
            cur = conn.cursor()
            cur.execute("SELECT TOKEN_HASH FROM SEARCH_API WHERE TOKEN_HASH = ?", (str(__hashToken__).strip(),))
            result = cur.fetchone()
        return self if result else None

    def database_insert_element(self, __database_name__, __table_name__, __primary_key__, __key__, __value__):
        table = _validate_identifier(__table_name__)
        primary_key = _validate_identifier(__primary_key__)
        with sqlite3.connect(__database_name__) as conn:
            cur = conn.cursor()
            cur.execute(f"SELECT 1 FROM {table} WHERE {primary_key} = ?", (__key__,))
            if cur.fetchone():
                return self
            # Kept for backward compatibility; callers should prefer explicit insert methods.
            logging.warning("database_insert_element has no column map; nothing inserted for %s", table)
        return self

    def database_insert_raw_data_fromFile(self, __database_name__, __fileName__, __query__, __api_key__, __sample_key__, __version__):
        logging.debug("Database insert from %s into %s", __fileName__, __database_name__)
        with open(__fileName__, "rt", encoding="utf-8") as file:
            keys = [line.strip() for line in file.readlines()]

        if not keys:
            raise ValueError("Session key file is empty")

        with sqlite3.connect(__database_name__) as conn:
            cur = conn.cursor()
            cur.execute("SELECT TOKEN_HASH FROM SEARCH_API WHERE TOKEN_HASH = ?", (keys[0],))
            if cur.fetchone():
                logging.debug("Search key entry already exists; updating encrypted API/search material")
                cur.execute(
                    "UPDATE SEARCH_API SET KEY1 = ?, KEY2 = ?, API_KEY = ?, SEARCH_KEY = ?, VERSION = ? WHERE TOKEN_HASH = ?",
                    (keys[1], keys[2], __api_key__, __sample_key__, __version__, keys[0]),
                )
                conn.commit()
                return self
            keys.extend([__api_key__, __sample_key__, __version__])
            cur.execute(__query__, keys)
            conn.commit()
        return self

    def getApiKey(self, __database_name__, __index__):
        return self._fetch_one_value(__database_name__, "API_KEY", __index__)

    def getSearchKeys(self, __database_name__, __index__):
        return self._fetch_one_value(__database_name__, "SEARCH_KEY", __index__)

    def getEncryptKey(self, __database_name__, __index__):
        return self._fetch_one_value(__database_name__, "KEY1", __index__)

    def getDecryptKey(self, __database_name__, __index__):
        return self._fetch_one_value(__database_name__, "KEY2", __index__)
