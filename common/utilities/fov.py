from geometry import euclidean_distance


def bresenham_fov(origin, target, radius, blocks=None):
    """
    Generate a list of points between origin and target that are visible,
    using the Bresenham Algorithm.

    Both origin and target must be a tuple with (point_x, point_y) coordinates.
    blocks is a function that receives a tuple with (point_x, point_y) coordinates,
    and returns True if that coordinate blocks vision. False otherwise.

    Returns a list of points starting at the origin and going until the first
    coordinate that blocks vision.

    Implementation based on:
    http://tech-algorithm.com/articles/drawing-line-using-bresenham-algorithm/
    """

    visible_points = []

    point_x, point_y = origin[0], origin[1]
    w, h = target[0] - point_x, target[1] - point_y

    longest = max(abs(w), abs(h))
    shortest = min(abs(w), abs(h))

    # get the sign (-1, 0, 1) of a value
    sign = lambda x: 0 if x == 0 else 1 if x > 0 else -1

    dx1 = sign(w)
    dy1 = sign(h)
    dx2 = 0 if (w == 0 or abs(h) > abs(w)) else (1 if w > 0 else -1)
    dy2 = 0 if (h == 0 or abs(w) > abs(h)) else (1 if h > 0 else -1)

    numerator = longest >> 1
    for _ in xrange(0, longest + 1):
        point = (point_x, point_y)

        if ((blocks and blocks(point)) or
                euclidean_distance(origin, point) > radius):
            return visible_points

        visible_points.append(point)

        numerator += shortest
        if numerator >= longest:
            numerator -= longest
            point_x += dx1
            point_y += dy1
        else:
            point_x += dx2
            point_y += dy2

    return visible_points


class Fov(object):
    """ Class to calculate 360 degrees field of view.
        Uses an external function to determine visibility.
    """

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.visible = [[0 for _ in xrange(0, width)]
                        for _ in xrange(0, height)]

    def update(self, pos, radius, blocks_visibility):
        """ Update the FOV map. """

        # get a square of positions around the player, for this radius
        xlo = max(0, pos[0] - radius)
        xhi = min(pos[0] + radius + 1, self.width - 1)
        ylo = max(0, pos[1] - radius)
        yhi = min(pos[1] + radius + 1, self.height - 1)

        limits = [(x, ylo) for x in xrange(xlo, xhi)] + \
                 [(x, yhi) for x in xrange(xlo, xhi)] + \
                 [(xlo, y) for y in xrange(ylo, yhi)] + \
                 [(xhi, y) for y in xrange(ylo, yhi)]

        # go point by point and get visible points between position and point
        for limit in limits:
            for block in bresenham_fov(pos, limit, radius, blocks_visibility):
                self.visible[block[1]][block[0]] = 1

    def contains(self, pos):
        """ Check if a pos is visible or not. """
        return self.visible[pos[1]][pos[0]]


if __name__ == '__main__':
    WIDTH, HEIGHT = 30, 20
    ### local variables
    FLOOR = [[0 for _ in xrange(0, WIDTH)] for _ in xrange(0, HEIGHT)]
    BLOCKED = [(5, 7), (6, 7), (7, 7), (8, 7),
               (5, 8),
               (5, 9),
               (5, 10),
               (9, 11), (10, 11)]
    for b in BLOCKED:
        FLOOR[b[1]][b[0]] = 1

    BLOCKS = lambda p: FLOOR[p[1]][p[0]]

    FOV = Fov(WIDTH, HEIGHT)

    FOV.update((7, 9), 7, BLOCKS)
    # make sure it doesn't crash for positions out of the map
    FOV.update((7, 9), 107, BLOCKS)
