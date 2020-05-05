from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet, MultiFernet
import base64
import logging, pprint
import socket, ssl
import re
import hashlib
from binascii import unhexlify
from Colorer import colorer

class remote_credentials_data:
    CredTag         = 14
    Name            = 16
    EncryptionTag   = 18
    Version         = 19
    Method          = 29
    Password        = 21
    backend         = 24
    Algorithm       = 22
    token           = 23
    keywords        = 25
    apikey          = 26

class crypto():
    generateKeys = True;
    def __init__(self, __server_url__, __server_ip__, __server_port__):
        HOST, PORT =  __server_ip__, __server_port__
        URL_PATTERN = re.compile("^(.*://)?([A-Za-z0-9\-\.]+)(:[0-9]+)?(.*)$")
        HEADER_END = re.compile("\r\n\r\n")

        INPUT_URL = __server_url__ + "/credentials.json"

        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)

        URL_DATA = re.match(URL_PATTERN, INPUT_URL)
        PROTOCOL = URL_DATA.groups()[0][:-3]
        HOSTNAME = URL_DATA.groups()[1]
        PATHNAME = URL_DATA.groups()[3] if URL_DATA.groups()[3] != "" else "/"

        server_cert = 'server-nginx-configuration/client-conf/nginx-selfsigned.crt'
        client_cert = 'server-nginx-configuration/client-conf/client.crt'
        client_key  = 'server-nginx-configuration/client-conf/client.key'
        server_sni_hostname = __server_ip__
        BUFFER_SIZE = 2048

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
        try:
            wrappedSocket.connect((HOST, PORT))
            message = "GET " + PATHNAME + " HTTP/1.1\r\nHost: " + HOSTNAME + "\r\nConnection: close\r\n\r\n"

            wrappedSocket.send(message.encode('UTF-8'))
            self.serverReply = bytearray()

            while True:
                part = wrappedSocket.recv(BUFFER_SIZE)
                if not part:
                    break
                self.serverReply += part

            logging.debug("[Crypto] server reply    : %s ", str(self.serverReply.decode('utf-8')))
            self.credential = str(self.serverReply.decode('utf-8')).splitlines()
            logging.debug("[Crypto] check           : %s ", self.credential[remote_credentials_data.CredTag])
            logging.debug("[Crypto] peer name : %s", repr(wrappedSocket.getpeername()))
            logging.debug("[Crypto] Cypher : %s ", wrappedSocket.cipher())
            logging.debug(pprint.pformat(wrappedSocket.getpeercert()))
            logging.debug("[Crypto] backend         :  %s ",
                          self.credential[remote_credentials_data.backend].split(':')[1])
            wrappedSocket.close()
        except :
            logging.error(" Remote Server Error : cannot retrieve credential");



    def crypto_fetchServerToken(self):
        try:
            hash_name = str(self.credential[remote_credentials_data.Algorithm].split(':')[1].split('.')[1]).split(',')[
            0].strip('"')
        except:
            logging.error(" error no credential retrieved")
            return None;

        __hash_func__ = getattr(hashes, hash_name)
        kdf = PBKDF2HMAC(
            algorithm=__hash_func__(),
            length=32,
            salt=bytes(self.credential[remote_credentials_data.token], 'utf-8'),
            iterations=100000,
            backend=default_backend()
        )

        logging.debug("[Crypto] Remote component name =  %s ",
                      str(self.credential[remote_credentials_data.Name].split(':')[1]).split(',')[0].strip('"'))
        logging.debug("[Crypto] Remote component password =  %s ",
                      str(self.credential[remote_credentials_data.Password].split(':')[1]).split(',')[0].strip('"'))
        logging.debug("[Crypto] Remote component version =  %s ",
                      str(self.credential[remote_credentials_data.Version].split(':')[1]).split(',')[0].strip('"'))
        password_bytes = str(self.credential[remote_credentials_data.Password].split(':')[1]).split(',')[0].strip(
            '"').encode('utf-8')
        self.remoteKeyRAW   = base64.urlsafe_b64encode(kdf.derive(bytes(password_bytes)))
        self.remoteKey      = Fernet(self.remoteKeyRAW)
        self.remoteKeyHash  = hashlib.sha512(self.remoteKeyRAW).hexdigest()
        ## to make it less decryptable use the token too ()
        return self;

    def crypto_getremoteHashIndex(self):
        logging.debug(" >> hash retrieve ");
        return self.remoteKeyHash

    def crypto_set_generateKeys(self, __enable__, __encryption_key__, __decryption_key__):
        self.generateKeys       = __enable__
        if (False == __enable__):
            logging.debug("[Crypto] stored keys : %s ", __encryption_key__);
            logging.debug("[Crypto] stored keys : %s ", __decryption_key__);
            self.encryptionKeyRAW   = __encryption_key__
            self.decryptionKeyRAW   = __decryption_key__

    def crypto_genEncryptionKey(self):
        if(True == self.generateKeys):
            self.encryptionKeyRAW = Fernet.generate_key()
            logging.debug("[Crypto] Generate EncryptionKey %s", self.encryptionKeyRAW.decode());

        self.encryptionKey = Fernet(self.encryptionKeyRAW)
        self.sessionEncryptionToken = MultiFernet([self.remoteKey, self.encryptionKey])
        logging.debug("[Crypto] Generate EncryptionKey : %s", self.sessionEncryptionToken);

    def crypto_genDecryptionKey(self):
        if(True == self.generateKeys):
            self.decryptionKeyRAW = Fernet.generate_key()
            logging.debug("[Crypto] Generate DecryptionKey %s", self.decryptionKeyRAW.decode());

        self.decryptionKey = Fernet(self.decryptionKeyRAW)
        self.remoteKey     = Fernet(self.remoteKeyRAW)
        self.sessionDecryptionToken = MultiFernet([self.remoteKey, self.encryptionKey, self.decryptionKey])
        logging.debug("[Crypto] Generate EncryptionKey : %s ", self.encryptionKey);
        logging.debug("[Crypto] Generate DecryptionKey : %s ", self.sessionDecryptionToken);

    def crypto_encrypt(self, __object__):
        logging.debug("[Crypto] Encrypt instance        : %s ", __object__);
        return self.sessionEncryptionToken.encrypt(bytes(__object__))

    def crypto_decrypt(self, __object__):
        logging.debug("[Crypto] Decrypt instance        : %s ", __object__);
        return self.sessionDecryptionToken.decrypt(bytes(__object__))

    def crypto_getClient(self):
        return str(self.credential[remote_credentials_data.Name].split(':')[1]).split(',')[0].strip('"')

    def crypto_getStoringKeys(self, __session_key_file__):
        if(True == self.generateKeys):
            file = open(__session_key_file__, 'w')
            file.write(str(self.remoteKeyHash) + '\n')
            logging.info("encryption Key %s ", str(self.encryptionKeyRAW.decode()))
            file.write(str(self.encryptionKeyRAW.decode()) + '\n')
            logging.info("decryption Key %s ", str(self.decryptionKeyRAW.decode()))
            file.write(str(self.decryptionKeyRAW.decode()))
            file.close()

    def crypto_getMiscDataModels(self):
        logging.debug("[Crypto] Remote component keyword list =  %s ",
                      str(self.credential[remote_credentials_data.keywords].split(':')[1]).strip('"').strip("'"))
        __list = str(self.credential[remote_credentials_data.keywords].split(':')[1]).strip('"').strip("'")
        return self.crypto_encrypt(__list.encode())

    def crypto_getMiscDataApiKey(self):
        logging.debug("[Crypto] Remote component API key list =  %s ",
                      str(self.credential[remote_credentials_data.apikey].split(':')[1]).strip('"').strip("'"))
        logging.debug("[Crypto] Remote component API key list =  %s ",
                      str(self.credential[remote_credentials_data.apikey].split(':')[1]).strip('"').strip("'"))
        __apiKey = str(self.credential[remote_credentials_data.apikey].split(':')[1]).strip('"').strip("'")
        return self.crypto_encrypt(__apiKey.encode())

    def crypto_getVersion(self):
        return str(self.credential[remote_credentials_data.Version].split(':')[1]).split(',')[0].strip('"')
