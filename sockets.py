import socket
import select
import json
from Queue import Queue

def recv_json(sock):
    data_expected = None
    all_data = None
    while all_data is None or len(all_data) < data_expected:
        size_recv = 16 if data_expected is None else data_expected - len(all_data)
        new_data = sock.recv(size_recv)

        if data_expected is None:
            if len(new_data) is 0:
                return None

            data_expected = int(new_data.split(' ')[0])
            all_data = " ".join(new_data.split(' ')[1:])
        else:
            all_data += new_data

    print all_data
    return json.loads(all_data)

def send_json(sock, message):
    send_data = json.dumps(message) 
    sock.send(str(len(send_data)) + " " + send_data)

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
            send_json(fd, data)

    def receive(self, put_queue):
        input_fds, _, _ = select.select(self.client_fds + [self.socket], [], [])
        for x in input_fds:
            if x == self.socket:
                print "NEW CLIENT JOINED!"
                csock, _ = self.socket.accept()
                self.client_fds.append(csock)
            else:
                data = recv_json(x)
                if data is not None:
                    put_queue.put(data)
                else:
                    x.close()
                    self.client_fds.remove(x)

    def close(self):
        for fd in self.client_fds:
            fd.close()
        self.socket.close()

