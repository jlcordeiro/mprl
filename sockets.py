import socket
import select
from Queue import Queue

class TCPServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('localhost', 4446))
        self.socket.listen(5)

        self.client_fds = []

    def broadcast(self, data):
        print " >> ", data, " << "
        for fd in self.client_fds:
            fd.send(data)

    def receive(self, put_queue):
        input_fds, _, _ = select.select(self.client_fds + [self.socket], [], [])
        for x in input_fds:
            if x == self.socket:
                print "NEW CLIENT JOINED!"
                csock, _ = self.socket.accept()
                self.client_fds.append(csock)
            else:
                data = x.recv(1024)
                if data:
                    put_queue.put(data)
                else:
                    x.close()
                    self.client_fds.remove(x)

    def close(self):
        for fd in self.client_fds:
            fd.close()
        self.socket.close()

