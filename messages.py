import textwrap
import libtcodpy as libtcod
from config import *


class MessagesBorg:
    __shared_state = {}
    messages = []

    def __init__(self):
        pass

    def add(self, new_msg, color=libtcod.white):
        #split the message if necessary, among multiple lines
        new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)

        for line in new_msg_lines:
            #if the buffer is full, remove the first line
            if len(self.messages) == MSG_HEIGHT:
                del self.messages[0]

            #add the new line as a tuple, with the text and the color
            self.messages.append((line, color))

    def get_all(self):
        return self.messages
