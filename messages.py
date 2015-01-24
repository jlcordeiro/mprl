from config import MSG_HEIGHT, MSG_WIDTH
from collections import deque
from textwrap import wrap


class Messages():
    def __init__(self):
        self._messages = deque([], MSG_HEIGHT)

    def add(self, msg):
        self._messages.extend(wrap(msg, MSG_WIDTH))

    def toList(self):
        return list(self._messages)
