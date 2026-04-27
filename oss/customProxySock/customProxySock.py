import logging
import select
import socket
import struct
from socketserver import StreamRequestHandler, TCPServer, ThreadingMixIn

try:
    from NetworkHoppingManager.vpnHopper import vpnHopper
except Exception:  # pragma: no cover - optional Linux-only helper
    vpnHopper = None


SOCKS_VERSION = 5


class ThreadingTCPServer(ThreadingMixIn, TCPServer):
    allow_reuse_address = True
    daemon_threads = True


class SocksProxy(StreamRequestHandler):
    def handle(self):
        remote = None
        try:
            if not self._negotiate_authentication():
                return
            cmd, address, port, address_type = self._read_request()
            if cmd != 1:  # CONNECT only
                self.connection.sendall(self.generate_failed_reply(address_type, 7))
                return

            remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._bind_to_interface_if_requested(remote)
            remote.connect((address, port))
            bind_address = remote.getsockname()
            logging.debug("SOCKS connected to %s:%s", address, port)
            self.connection.sendall(self._success_reply(bind_address, address_type))
            self.exchange_loop(self.connection, remote)
        except Exception as err:
            logging.error("SOCKS proxy error: %s", err)
            try:
                self.connection.sendall(self.generate_failed_reply(1, 5))
            except Exception:
                pass
        finally:
            if remote:
                remote.close()

    @staticmethod
    def _byte_value(value):
        return value if isinstance(value, int) else ord(value)

    def _recv_exact(self, size):
        data = self.connection.recv(size)
        if len(data) != size:
            raise ConnectionError("Unexpected end of SOCKS client data")
        return data

    def _negotiate_authentication(self):
        header = self._recv_exact(2)
        version, nmethods = struct.unpack("!BB", header)
        if version != SOCKS_VERSION or nmethods <= 0:
            return False
        methods = list(self._recv_exact(nmethods))
        requires_auth = bool(self.server.username or self.server.password)
        selected = 2 if requires_auth else 0
        if selected not in methods:
            self.connection.sendall(struct.pack("!BB", SOCKS_VERSION, 0xFF))
            return False
        self.connection.sendall(struct.pack("!BB", SOCKS_VERSION, selected))
        return self.verify_credentials() if requires_auth else True

    def verify_credentials(self):
        version = self._byte_value(self._recv_exact(1)[0])
        if version != 1:
            return False
        username_len = self._byte_value(self._recv_exact(1)[0])
        username = self._recv_exact(username_len).decode("utf-8")
        password_len = self._byte_value(self._recv_exact(1)[0])
        password = self._recv_exact(password_len).decode("utf-8")
        valid = username == self.server.username and password == self.server.password
        self.connection.sendall(struct.pack("!BB", 1, 0 if valid else 0xFF))
        return valid

    def _read_request(self):
        version, cmd, _, address_type = struct.unpack("!BBBB", self._recv_exact(4))
        if version != SOCKS_VERSION:
            raise ValueError("Invalid SOCKS version")
        if address_type == 1:  # IPv4
            address = socket.inet_ntoa(self._recv_exact(4))
        elif address_type == 3:  # Domain name
            domain_length = self._byte_value(self._recv_exact(1)[0])
            address = self._recv_exact(domain_length).decode("utf-8")
        elif address_type == 4:  # IPv6
            address = socket.inet_ntop(socket.AF_INET6, self._recv_exact(16))
        else:
            raise ValueError("Unsupported SOCKS address type")
        port = struct.unpack("!H", self._recv_exact(2))[0]
        return cmd, address, port, address_type

    def _bind_to_interface_if_requested(self, remote_socket):
        if not self.server.ifname:
            return
        if vpnHopper is None:
            logging.warning("Interface binding requested but vpnHopper is unavailable")
            return
        vpn_instance = vpnHopper()
        vpnHopper.setup_if_conf_socket(vpn_instance, remote_socket.fileno(), self.server.ifname)

    def _success_reply(self, bind_address, address_type):
        addr = struct.unpack("!I", socket.inet_aton(bind_address[0]))[0]
        port = bind_address[1]
        return struct.pack("!BBBBIH", SOCKS_VERSION, 0, 0, 1 if address_type != 4 else address_type, addr, port)

    def generate_failed_reply(self, address_type, error_number):
        return struct.pack("!BBBBIH", SOCKS_VERSION, error_number, 0, 1, 0, 0)

    def exchange_loop(self, client, remote):
        while True:
            readable, _, _ = select.select([client, remote], [], [])
            if client in readable:
                data = client.recv(4096)
                if not data or remote.send(data) <= 0:
                    break
            if remote in readable:
                data = remote.recv(4096)
                if not data or client.send(data) <= 0:
                    break


class customProxySock:
    def __init__(self, port=1080, __username__="", __password__="", __ifname__=""):
        self.port = int(port)
        self.__username__ = __username__ or ""
        self.__password__ = __password__ or ""
        self.__ifname__ = __ifname__ or ""
        self.server = None

    def launchProxySock(self):
        with ThreadingTCPServer(("127.0.0.1", self.port), SocksProxy) as server:
            self.server = server
            self.server.ifname = self.__ifname__
            self.server.username = self.__username__
            self.server.password = self.__password__
            logging.info("SOCKS proxy listening on 127.0.0.1:%s", self.port)
            self.server.serve_forever()

    def getNotificationError(self):
        return getattr(self.server, "error", None)

    def shutdownProxySock(self):
        if self.server is not None:
            self.server.shutdown()
