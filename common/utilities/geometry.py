import math
import random
from collections import namedtuple

def euclidean_distance(pos1, pos2):
    (x1, y1) = pos1[0], pos1[1]
    (x2, y2) = pos2[0], pos2[1]

    #return the distance to another object
    (dx, dy) = (x2 - x1, y2 - y1)
    return math.sqrt(dx ** 2 + dy ** 2)


class Point2(namedtuple('Point2', 'x y')):
    """ Point with 2 coordinates. """
    __slots__ = ()

    def add(self, other):
        return Point2(self.x + other[0], self.y + other[1])

    @property
    def coords(self):
        return (self.x, self.y)

class Point3(namedtuple('Point3', 'x y z')):
    """ Point with 3 coordinates. """

    __slots__ = ()

    @staticmethod
    def copy(other):
        return Point3(other[0], other[1], other[2])

    def add(self, other):
        return Point3(self.x + other[0], self.y + other[1], self.z + other[2])

    @property
    def coords(self):
        return (self.x, self.y, self.z)


class Rect(object):
    #a rectangle on the map. used to characterize a room.
    def __init__(self, x, y, w, h):
        self.tleft = Point2(x, y)
        self.bright = Point2(x + w, y + h)

    @property
    def top_left(self):
        return self.tleft

    @property
    def bottom_right(self):
        return self.bright

    @property
    def center(self):
        center_x = (self.tleft.x + self.bright.x) / 2
        center_y = (self.tleft.y + self.bright.y) / 2
        return Point2(center_x, center_y)
 
    @property
    def width(self):
        return self.bright.x - self.tleft.x

    @property
    def height(self):
        return self.bright.y - self.tleft.y

    def get_random_point(self):
        x = random.randint(self.top_left.x + 1, self.bottom_right.x - 1)
        y = random.randint(self.top_left.y + 1, self.bottom_right.y - 1)

        return Point2(x, y)

    def x_distance_to_rect(self, other):
        s1x, s2x = self.tleft.x, self.bright.x
        o1x, o2x = other.tleft.x, other.bright.x

        if ((s1x >= o1x and s1x <= o2x) or (s2x >= o1x and s2x <= o2x)):
            return 0

        if s2x < o1x:
            return o1x - s2x

        return s1x - o2x

    def y_distance_to_rect(self, other):
        s1y, s2y = self.tleft.y, self.bright.y
        o1y, o2y = other.tleft.y, other.bright.y

        if ((s1y >= o1y and s1y <= o2y) or (s2y >= o1y and s2y <= o2y)):
            return 0

        if s2y < o1y:
            return o1y - s2y

        return s1y - o2y

    def intersects(self, other):
        """ Check if this square intersects with other.
            Returns a boolean. """
        return (self.x_distance_to_rect(other) <= 1 and
                self.y_distance_to_rect(other) <= 1)

    def distance_to_rect(self, other):
        if self.intersects(other):
            return 1

        dx = self.x_distance_to_rect(other)
        dy = self.y_distance_to_rect(other)

        return math.sqrt(dx ** 2 + dy ** 2)

