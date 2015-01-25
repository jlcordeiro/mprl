"""
Module that wraps JSON communication.

Messages are sent in json, prefixed by the message length.

Example:
The dictionary:
{'msg': 'hello'}

Is sent as:
16 {"msg": "hello"}
"""


import socket
import select
import json


def read_json_message(sock):
    """ Read a full message from the socket.
        Only returns the message object, not the length. """
    data_expected = None
    all_data = None
    while all_data is None or len(all_data) < data_expected:
        size = 16 if data_expected is None else data_expected - len(all_data)
        new_data = sock.recv(size)

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
    """ Convert an object to json and send through a socket. """
    send_data = json.dumps(message)
    sock.send(str(len(send_data)) + " " + send_data)


class TCPServer(object):
    """ TCP server.
        Sends and receives messages formatted as json. """
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('localhost', 4446))
        self.sock.listen(5)

        self.client_fds = []

    def broadcast(self, data):
        """ Convert data to json and send to all clients. """
        for client_fd in self.client_fds:
            send_json(client_fd, data)

    def receive(self, put_queue):
        """ Check all the sockets.
            Accept new clients and read messages from existing ones.
            Also removes file descriptors from clients that leave.
        """
        input_fds, _, _ = select.select(self.client_fds + [self.sock], [], [])
        for in_fd in input_fds:
            if in_fd == self.sock:
                csock, _ = self.sock.accept()
                self.client_fds.append(csock)
                put_queue.put({'new-user': None})
            else:
                data = read_json_message(in_fd)
                if data is not None:
                    put_queue.put(data)
                else:
                    in_fd.close()
                    self.client_fds.remove(in_fd)

    def close(self):
        """ Close connection to all clients and close socket. """
        for client_fd in self.client_fds:
            client_fd.close()
        self.sock.close()


class TCPClient(object):
    """ TCP client.
        Sends and receives messages formatted as json. """
    def __init__(self, host, port):
        self.server_address = (host, port)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.server_address)

    def close(self):
        """ Close socket. """
        self.sock.close()

    def recv(self):
        """ Receive json from server. """
        return read_json_message(self.sock)

    def send(self, what):
        """ Convert what to json and send it to the server. """
        send_json(self.sock, what)
