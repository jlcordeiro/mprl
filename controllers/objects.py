import math
from utils import euclidean_distance


class ObjectController(object):
    def __init__(self):
        raise NotImplementedError("not_implemented")

    def move(self, dx, dy):
        self.model.x += dx
        self.model.y += dy

    @property
    def position(self):
        return (self.model.x, self.model.y)

    @property
    def blocks(self):
        return self.model.blocks

    @property
    def name(self):
        return self.model.name

    def distance_to(self, obj2):
        return euclidean_distance(self.position,
                                  obj2.position)

    def draw_ui(self, con):
        self.view.draw(con)

    def clear_ui(self, con):
        self.view.clear(con)

