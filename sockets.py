"""
Module that wraps JSON communication.

Messages are sent in json, prefixed by the message length.

Example:
The dictionary:
{'msg': 'hello'}

Is sent as:
16 {"msg": "hello"}
"""

import threading
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

    return json.loads(all_data)


def send_json(sock, message):
    """ Convert an object to json and send through a socket. """
    send_data = json.dumps(message)
    sock.send(str(len(send_data)) + " " + send_data)


class TCPServer(object):
    """ Thread safe, non-blocking TCP server.
        Sends and receives messages formatted as json. """
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('localhost', 4446))
        self.sock.listen(5)

        self.client_fds = []

        self.lock = threading.Lock()

    def broadcast(self, data):
        """ Convert data to json and send to all clients. """
        self.lock.acquire()
        for client_fd in self.client_fds:
            try:
                send_json(client_fd, data)
            except socket.error, _:
                client_fd.close()
                self.client_fds.remove(client_fd)
        self.lock.release()

    def receive(self, put_queue):
        """ Check all the sockets.
            Accept new clients and read messages from existing ones.
            Also removes file descriptors from clients that leave.
        """
        self.lock.acquire()
        input_fds, _, _ = select.select(self.client_fds + [self.sock], [], [])
        for in_fd in input_fds:
            if in_fd == self.sock:
                csock, _ = self.sock.accept()
                self.client_fds.append(csock)
                put_queue.put({'new-user': None})
            else:
                try:
                    data = read_json_message(in_fd)
                    if data is not None:
                        put_queue.put(data)
                    else:
                        raise socket.error()
                except socket.error, _:
                    in_fd.close()
                    self.client_fds.remove(in_fd)

        self.lock.release()

    def close(self):
        """ Close connection to all clients and close socket. """
        self.lock.acquire()
        for client_fd in self.client_fds:
            client_fd.close()
        self.sock.close()
        self.lock.release()


class TCPClient(object):
    """ Thread safe, non-blocking TCP client.
        Sends and receives messages formatted as json. """
    def __init__(self, host, port):
        self.server_address = (host, port)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.server_address)

        self.lock = threading.Lock()

    def close(self):
        """ Close socket. """
        self.lock.acquire()
        self.sock.close()
        self.lock.release()

    def recv(self):
        """ Receive json from server. Non-blocking. """
        data = None

        self.lock.acquire()
        input_fds, _, _ = select.select([self.sock], [], [])
        if len(input_fds) > 0:
            data = read_json_message(self.sock)
            if data is None:
                self.sock.close()

        self.lock.release()
        return data

    def send(self, what):
        """ Convert what to json and send it to the server. """
        self.lock.acquire()
        send_json(self.sock, what)
        self.lock.release()
