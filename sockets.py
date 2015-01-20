import socket
import select
import json
from Queue import Queue

def recv_json(sock):
    data_expected = None
    all_data = None
    while all_data is None or len(all_data) < data_expected:
        new_data = sock.recv(16)

        if data_expected is None:
            data_expected = int(new_data.split(' ')[0])
            all_data = " ".join(new_data.split(' ')[1:])
        else:
            all_data += new_data

    print all_data
    return json.loads(all_data)

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
                print "a"
                data = recv_json(x)
                if data:
                    print "b"
                    put_queue.put(data)
                else:
                    print "c"
                    x.close()
                    self.client_fds.remove(x)

    def close(self):
        for fd in self.client_fds:
            fd.close()
        self.socket.close()

