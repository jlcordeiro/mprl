import textwrap
import libtcodpy as libtcod
from config import *


class MessagesBorg:
    __shared_state = {}
    messages = []

    def __init__(self):
        pass

    def add(self, new_msg):
        #split the message if necessary, among multiple lines
        new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)

        for line in new_msg_lines:
            #if the buffer is full, remove the first line
            if len(self.messages) == MSG_HEIGHT:
                del self.messages[0]

            self.messages.append(line)
        print self.messages

    def get_all(self):
        return self.messages
