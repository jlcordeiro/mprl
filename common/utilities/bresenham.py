def bresenham_fov(origin, target, blocks=None):
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

    point_x, point_y = origin
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

        if blocks and blocks(point):
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


MAP_SIZE = 20

floor = [[0 for _ in xrange(0, MAP_SIZE)] for _ in xrange(0, MAP_SIZE)]
visible = [[0 for _ in xrange(0, MAP_SIZE)] for _ in xrange(0, MAP_SIZE)]

blocked = [(5, 7), (6, 7), (7, 7), (8, 7),
           (5, 8),
           (5, 9),
           (5, 10),
           (9, 11), (10, 11)]

for b in blocked:
    floor[b[1]][b[0]] = 1


def print_map(l):
    for row in l:
        print "_".join(["#" if result is 1 else " " for result in row])


blocks = lambda p: floor[p[1]][p[0]]

player = (7, 9)
FOV = 4

xlo, xhi = player[0] - FOV, player[0] + FOV + 1
ylo, yhi = player[1] - FOV, player[1] + FOV + 1

limits = [(x, ylo) for x in xrange(xlo, xhi)] + \
         [(x, yhi) for x in xrange(xlo, xhi)] + \
         [(xlo, y) for y in xrange(ylo, yhi)] + \
         [(xhi, y) for y in xrange(ylo, yhi)]

for limit in limits:
    for block in bresenham_fov(player, limit, blocks):
        visible[block[1]][block[0]] = 1

print_map(floor)
print
print_map(visible)
