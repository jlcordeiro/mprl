class Borg(object):
    """ Derived classes will be a borg. """

    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state


def reduce_map(map_object):
    """ Reduces the size of a map, to be sent across the wire. 
        Converts [[True, False, False], [False, False, False]]
        to [\"100\", \"000\"] """
    return ["".join([str(int(b)) for b in row]) for row in map_object]

def expand_map(reduced_object):
    """ Expands a reduced object back to its 2D boolean format.
        Converts [\"100\", \"000\"]
        to [[True, False, False], [False, False, False]] """
    return  [[bool(int(v)) for v in list(row)] for row in reduced_object]


if __name__ == '__main__':
    print reduce_map([[True, False, False], [False, False, False]])
    print expand_map(["100", "000"])
