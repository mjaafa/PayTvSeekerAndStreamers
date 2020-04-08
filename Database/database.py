import sqlite3
import logging, pprint
from cryptography.fernet import Fernet, MultiFernet
import socket, ssl
import os.path
import re
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class remote_credentials_data:
    CredTag         = 15
    Name            = 17
    EncryptionTag   = 18
    Version         = 20
    Method          = 29
    Password        = 22
    Algorithm       = 23
    token           = 25
    backend         = 25


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

    def crypto_genKey(self):
        logging.debug("Generate Key");
        return Fernet(Fernet.generate_key())

    def __init_server_connection(self):
        # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # SET VARIABLES
        packet, reply = " GET https://127.0.0.1/credentials.json HTTPS/1.1 \r\nHost: 127.0.0.1\r\nConnection: close\r\n\r\n ", ""
        HOST, PORT = '127.0.0.1', 443
        URL_PATTERN = re.compile("^(.*://)?([A-Za-z0-9\-\.]+)(:[0-9]+)?(.*)$")
        HEADER_END = re.compile("\r\n\r\n")

        INPUT_URL = "https://127.0.0.1/credentials.json"

        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)

        URL_DATA = re.match(URL_PATTERN, INPUT_URL)
        PROTOCOL = URL_DATA.groups()[0][:-3]
        HOSTNAME = URL_DATA.groups()[1]
        PATHNAME = URL_DATA.groups()[3] if URL_DATA.groups()[3] != "" else "/"

        server_cert = 'nginx-selfsigned.crt'
        client_cert = 'client.crt'
        client_key = 'client.key'
        server_sni_hostname = '127.0.0.1'
        BUFFER_SIZE = 1024

        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=server_cert)
        context.load_cert_chain(certfile=client_cert, keyfile=client_key)
        context.verify_mode = ssl.CERT_REQUIRED
        context.check_hostname = False

        # CREATE SOCKET
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)

        # WRAP SOCKET
        wrappedSocket = context.wrap_socket(sock,
                                            server_side=False,
                                            server_hostname=server_sni_hostname)

        # CONNECT AND PRINT REPLY
        wrappedSocket.connect((HOST, PORT))
        message = "GET " + PATHNAME + " HTTP/1.1\r\nHost: " + HOSTNAME + "\r\nConnection: close\r\n\r\n"

        wrappedSocket.send(message.encode('UTF-8'))
        self.serverReply = bytearray()

        while True:
            part = wrappedSocket.recv(BUFFER_SIZE)
            if not part:
                break
            self.serverReply += part

        logging.debug(" server reply : %s ",  str(self.serverReply.decode('utf-8')))
        self.credential  = str(self.serverReply.decode('utf-8')).splitlines()
        logging.debug(" data [] %s ", self.credential[remote_credentials_data.CredTag])
        logging.debug(repr(wrappedSocket.getpeername()))
        logging.debug(wrappedSocket.cipher())
        logging.debug(pprint.pformat(wrappedSocket.getpeercert()))
#        logging.info(" parser %s ", self.credential[remote_credentials_data.backend].split(':')[1])
        wrappedSocket.close()

    def crypto_init(self):
        serverKey = self.__init_server_connection()
        __function_call = getattr(hashes, 'SHA256')
        hash_name       = str(self.credential[remote_credentials_data.Algorithm].split(':')[1].split('.')[1]).split(',')[0].strip('"')
        ### The same name :: class definition for the getattr cannot be really found tricky stuff dude .
        #backend_name    = str(self.credential[remote_credentials_data.backend].split(':')[1]).strip('"')
#        logging.info(" function caller %s ", _database__function_call)
        __hash_func__       = getattr(hashes,           hash_name)
        #__backend_func__    = getattr(default_backend,  backend_name)
        kdf = PBKDF2HMAC(
                        algorithm   = __hash_func__(),
                        length      = 32,
                        salt        = bytes(self.credential[remote_credentials_data.token], 'utf-8'),
                        iterations  = 100000,
                        backend     = default_backend()
                        )

        logging.debug(" >>>>>> PASWWORD =  %s ", str(self.credential[remote_credentials_data.Password].split(':')[1]).split(',')[0].strip('"'))
        password_bytes = str(self.credential[remote_credentials_data.Password].split(':')[1]).split(',')[0].strip('"').encode('utf-8')
        self.remoteKey  = base64.urlsafe_b64encode(kdf.derive(bytes(password_bytes)))
        masterKey       = Fernet(Fernet.generate_key())
        self.sessionToken = MultiFernet([self.remoteKey, masterKey])

#    def crypto_encrypt(self, __object__):


