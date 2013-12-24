import math

def euclidean_distance(pos1, pos2):
    (x1, y1) = pos1
    (x2, y2) = pos2

    #return the distance to another object
    (dx, dy) = (x2 - x1, y2 - y1)
    return math.sqrt(dx ** 2 + dy ** 2)
