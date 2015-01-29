# A* Pathfinding Algorithm
# taken from: https://github.com/mazubieta/A-Star-Pathfinder

import sys, math, heapq

class APath:
    def __init__(self, width, height, start, is_wall_func):
        self.width = width
        self.height = height
        self.cells = {}      # Dictionary of Cells where a tuple (immutable set) of (x,y) coordinates is used as keys
        self.path = []
        self.is_wall = is_wall_func

        for x in range(width):
            for y in range(height):
                self.cells[(x, y)] = {'f_score': None, # f() = g() + h() This is used to determine next cell to process
                                      'h_score': None, # The heuristic score
                                      'g_score': None, # The cost to arrive to this cell, from the start cell
                                      'parent': None}  # In order to walk the found path, keep track of how we arrived to each cell

        # Place Start
        self.start = start

        # The cell with the lowest f_score is of highest priority,
        # priority queue of opened cells' f_scores
        self.open_list = []

        # When we pop the highest priority f_score, we use this as a key to retreive the actual cell identifier
        self.pq_dict = {}

        # A dictionary of closed cells
        self.closed_list = {}


    def __calc_f(self, node):
        self.cells[node]['f_score'] = self.cells[node]['h_score'] + self.cells[node]['g_score']


    def __calc_h(self, node, goal):
        x1, y1 = goal
        x0, y0 = node
        self.cells[node]['h_score'] = math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2) * 10


    def __on_board(self, node):
        x, y = node
        return x >= 0 and x < self.width and y >= 0 and y < self.height


    def __orthoganals(self, current):
        x, y = current
        directions = [(x - 1, y), (x, y + 1), (x + 1, y), (x, y - 1)]
        return [x for x in directions if self.__on_board(x) and not self.is_wall(x) and not x in self.closed_list]


    # Check if diag is blocked by a wall, making it unwalkable from current
    def __blocked_diagnol(self, current, diag):
        x, y = current
        
        N = x - 1, y
        E = x, y + 1
        S = x + 1, y
        W = x, y - 1
        NE = x - 1, y + 1
        SE = x + 1, y + 1
        SW = x + 1, y - 1
        NW = x - 1, y - 1
        
        if diag == NE:
            return self.is_wall(N) or self.is_wall(E)
        elif diag == SE:
            return self.is_wall(S) or self.is_wall(E)
        elif diag == SW:
            return self.is_wall(S) or self.is_wall(W)
        elif diag == NW:
            return self.is_wall(N) or self.is_wall(W)
        else:
            return False # Technically, you've done goofed if you arrive here.


    # Return a list of adjacent diagonal walkable cells
    def __diagonals(self, current):
        x, y = current
        
        NE = x - 1, y + 1
        SE = x + 1, y + 1
        SW = x + 1, y - 1
        NW = x - 1, y - 1
        
        directions = [NE, SE, SW, NW]
        return [x for x in directions if self.__on_board(x) and not self.is_wall(x) and not x in self.closed_list and not self.__blocked_diagnol(current,x)]


    # Update a child node with information from parent, such as g_score and the parent's coords
    def update_child(self, parent, child, cost_to_travel):
        self.cells[child]['g_score'] = self.cells[parent]['g_score'] + cost_to_travel
        self.cells[child]['parent'] = parent


    # Display the shortest path found
    def unwind_path(self, coord):
        if self.cells[coord]['parent'] != None:
            self.unwind_path(self.cells[coord]['parent'])
            self.path.append((coord))


    # Recursive function to process the current node, which is the node with the smallest f_score from the list of open nodes
    def process_node(self, coord, goal):
        if coord == goal:
            self.unwind_path(self.cells[goal]['parent'])
            return
            
        # l will be a list of walkable adjacents that we've found a new shortest path to
        l = [] 
        
        # Check all of the diagnols for walkable cells, that we've found a new shortest path to
        for x in self.__diagonals(coord):
            # If x hasn't been visited before
            if self.cells[x]['g_score'] == None:
                self.update_child(coord, x, cost_to_travel=14)
                l.append(x)
            # Else if we've found a faster route to x
            elif self.cells[x]['g_score'] > self.cells[coord]['g_score'] + 14:
                self.update_child(coord, x, cost_to_travel=14)
                l.append(x)
        
        for x in self.__orthoganals(coord):
            # If x hasn't been visited before
            if self.cells[x]['g_score'] == None:
                self.update_child(coord, x, cost_to_travel=10)
                l.append(x)
            # Else if we've found a faster route to x
            elif self.cells[x]['g_score'] > self.cells[coord]['g_score'] + 10:
                self.update_child(coord, x, cost_to_travel=10)
                l.append(x)
        
        for x in l:
            # If we found a shorter path to x
            # Then we remove the old f_score from the heap and dictionary
            if self.cells[x]['f_score'] in self.pq_dict:
                if len(self.pq_dict[self.cells[x]['f_score']]) > 1:
                    self.pq_dict[self.cells[x]['f_score']].remove(x)
                else:
                    self.pq_dict.pop(self.cells[x]['f_score'])
                self.open_list.remove(self.cells[x]['f_score'])
            # Update x with the new f and h score (technically don't need to do h if already calculated)
            self.__calc_h(x, goal)
            self.__calc_f(x)
            # Add f to heap and dictionary
            self.open_list.append(self.cells[x]['f_score'])
            if self.cells[x]['f_score'] in self.pq_dict:
                self.pq_dict[self.cells[x]['f_score']].append(x)
            else:
                self.pq_dict[self.cells[x]['f_score']] = [x]
        
        heapq.heapify(self.open_list)
        
        if len(self.open_list) == 0:
            print 'NO POSSIBLE PATH!'
            return
        f = heapq.heappop(self.open_list)
        if len(self.pq_dict[f]) > 1:
            node = self.pq_dict[f].pop()
        else:
            node = self.pq_dict.pop(f)[0]
        
        heapq.heapify(self.open_list)
        self.closed_list[node]=True
    
        self.process_node(node, goal)


    # Start the search for the shortest path from start to goal
    def find_path(self, goal):
        if self.start != None and goal != None:
            self.cells[self.start]['g_score'] = 0
            self.__calc_h(self.start, goal)
            self.__calc_f(self.start)
            
            self.closed_list[self.start]=True
            self.process_node(self.start, goal)

if __name__ == '__main__':
    # Clean up code a little bit: This function draws a cell at (x,y)
    WIDTH = 40
    HEIGHT = 20

    START = (5, 3)
    GOAL  = (7, 3)
    WALLS = ((6, 2),
             (6, 3),
             (6, 4),
             (6, 5),
             (7, 2),
             (7, 4))

    is_wall = lambda x: x in WALLS

    import time
    start = time.clock()
    for _ in xrange(0, 1000):
        A = APath(WIDTH, HEIGHT, START, is_wall)
        A.find_path(GOAL)
    print time.clock() - start

    A = APath(WIDTH, HEIGHT, START, is_wall)
    A.find_path(GOAL)

    for y in range(HEIGHT):
        print
        for x in range(WIDTH):
            wall = (x, y) in WALLS
            path = (x, y) in A.path

            if (x, y) == START:
                print "@",
            elif (x, y) == GOAL:
                print 'T',
            elif wall:
                print "#",
            elif path:
                print "+",
            else:
                print ".",

    print
    print A.path
