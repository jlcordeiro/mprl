import math
from utils import euclidean_distance


class ObjectController(object):
    def __init__(self):
        raise NotImplementedError("not_implemented")

    def move(self, dx = None, dy = None, new_pos = None):
        if new_pos is None:
            self._model.x += dx
            self._model.y += dy
        else:
            self._model.x = new_pos[0]
            self._model.y = new_pos[1]

    @property
    def position(self):
        return (self._model.x, self._model.y)

    @position.setter
    def position(self, value):
        self._model.x = value[0]
        self._model.y = value[1]

    @property
    def blocks(self):
        return self._model.blocks

    @property
    def name(self):
        return self._model.name

    def distance_to(self, obj2):
        return euclidean_distance(self.position,
                                  obj2.position)

    def draw_ui(self, con):
        self._view.draw(con)

    def clear_ui(self, con):
        self._view.clear(con)

