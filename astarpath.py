# A* Pathfinding Algorithm
# taken from: https://github.com/mazubieta/A-Star-Pathfinder

import sys, math, heapq


num_cells = 70 # Adjust the size of the board and the cells

class APath:
    def __init__(self, start, walls):
        self.cells = {}      # Dictionary of Cells where a tuple (immutable set) of (x,y) coordinates is used as keys

        for x in range(num_cells):
            for y in range(num_cells):
                self.cells[(x,y)]= {'state':None,   # None, Wall, Goal, Start Are the possible states. None is walkable 
                                    'f_score':None, # f() = g() + h() This is used to determine next cell to process
                                    'h_score':None, # The heuristic score, We use straight-line distance: sqrt((x1-x0)^2 + (y1-y0)^2)
                                    'g_score':None, # The cost to arrive to this cell, from the start cell
                                    'in_path':False,
                                    'parent':None}  # In order to walk the found path, keep track of how we arrived to each cell

        # Place Walls
        for w in walls:
            self.cells[w]['state']='Wall'

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


    def __calc_h(self, node, goal, heuristic):
        x1, y1 = goal
        x0, y0 = node

        if heuristic == 'manhattan':
            self.cells[node]['h_score'] = (abs(x1-x0)+abs(y1-y0))*10 # multiplied by 1- to avoid diagonals
        elif heuristic == 'crow':
            self.cells[node]['h_score'] = math.sqrt( (x1-x0)**2 + (y1-y0)**2 )*10
        else:
            self.cells[node]['h_score'] = 0


    def __on_board(self, node):
        x, y = node
        return x >= 0 and x < num_cells and y >= 0 and y < num_cells


    def __orthoganals(self, current):
        x, y = current
        directions = [(x-1, y), (x, y+1), (x+1, y), (x, y-1)]
        return [x for x in directions if self.__on_board(x) and self.cells[x]['state'] != 'Wall' and not x in self.closed_list]


    # Check if diag is blocked by a wall, making it unwalkable from current
    def __blocked_diagnol(self, current, diag):
        x, y = current
        
        N = x-1, y
        E = x, y+1
        S = x+1, y
        W = x, y-1
        NE = x-1, y+1
        SE = x+1, y+1
        SW = x+1, y-1
        NW = x-1, y-1
        
        if diag == NE:
            return self.cells[N]['state'] == 'Wall' or self.cells[E]['state'] == 'Wall'
        elif diag == SE:
            return self.cells[S]['state'] == 'Wall' or self.cells[E]['state'] == 'Wall'
        elif diag == SW:
            return self.cells[S]['state'] == 'Wall' or self.cells[W]['state'] == 'Wall'
        elif diag == NW:
            return self.cells[N]['state'] == 'Wall' or self.cells[W]['state'] == 'Wall'
        else:
            return False # Technically, you've done goofed if you arrive here.


    # Return a list of adjacent diagonal walkable cells
    def __diagonals(self, current):
        x, y = current
        
        NE = x-1, y+1
        SE = x+1, y+1
        SW = x+1, y-1
        NW = x-1, y-1
        
        directions = [NE, SE, SW, NW]
        return [x for x in directions if self.__on_board(x) and self.cells[x]['state'] != 'Wall' and not x in self.closed_list and not self.__blocked_diagnol(current,x)]


    # Update a child node with information from parent, such as g_score and the parent's coords
    def update_child(self, parent, child, cost_to_travel):
        self.cells[child]['g_score'] = self.cells[parent]['g_score'] + cost_to_travel
        self.cells[child]['parent'] = parent


    # Display the shortest path found
    def unwind_path(self, coord):
        if self.cells[coord]['parent'] != None:
            self.unwind_path(self.cells[coord]['parent'])
            self.cells[coord]['in_path'] = True


    # Recursive function to process the current node, which is the node with the smallest f_score from the list of open nodes
    def process_node(self, coord, goal, heuristic):
        if coord == goal:
            print "Cost %d\n" % self.cells[goal]['g_score']
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
            self.__calc_h(x, goal, heuristic)
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
    
        self.process_node(node, goal, heuristic)


    # Start the search for the shortest path from start to goal
    def find_path(self, goal, heuristic):
        if self.start != None and goal != None:
            self.cells[self.start]['g_score'] = 0
            self.cells[self.start]['state']='Start'
            self.cells[goal]['state']='Goal'
            self.__calc_h(self.start, goal, heuristic)
            self.__calc_f(self.start)
            
            self.closed_list[self.start]=True
            self.process_node(self.start, goal, heuristic)


# Clean up code a little bit: This function draws a cell at (x,y)        

HEURISTIC = 'crow' # Can be 'manhattan' or 'crow' anything else is assumed to be 'zero'
START = (5, 3)
GOAL  = (7, 3)
WALLS = ((6, 2),
         (6, 3),
         (6, 4),
         (6, 5),
         (7, 2),
         (7, 4))

A = APath(START, WALLS)
A.find_path(GOAL, HEURISTIC)

for y in range(num_cells):
    print
    for x in range(num_cells):
        state = A.cells[(x, y)]['state'],
        in_path = A.cells[(x, y)]['in_path'],

        if 'Wall' in state:
            print "#",
        elif "Start" in state:
            print "@",
        elif "Goal" in state:
            print "o",
        elif True in in_path:
            print "+",
        else:
            print ".",
