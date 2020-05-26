import socks

secured_socket=socks.socksocket() # Same API as socket.socket in the standard lib

secured_socket.set_proxy(socks.SOCKS5, "localhost") # SOCKS4 and SOCKS5 use port 1080 by default
# Or
secured_socket.set_proxy(socks.SOCKS4, "localhost", 4444)
# Or
secured_socket.set_proxy(socks.HTTP, "5.5.5.5", 8888)

# Can be treated identical to a regular socket object
secured_socket.connect(("www.somesite.com", 80))
secured_socket.sendall("GET / HTTP/1.1 ...")
print (" received data", secured_socket.recv(4096))
