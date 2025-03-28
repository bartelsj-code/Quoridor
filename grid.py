import numpy as np
from utils import get_display_string, get_display_string_pl
import heapq

# N = 1     # 00000001   a wall is disconnecting me from northern..
# E = 2     # 00000010   eastern...
# S = 4     # 00000100   southern...
# W = 8     # 00001000   ...western neighbor
# H = 16    # 00010000   a horizontal wall cannot be added that is centered at the top right corner of this square
# V = 32    # 00100000   a vertical wall cannot be added that is centered at the top right corner of this square
# oc = 64   # 01000000   a player pawn (not identified) is occupying this square
# mark = 128 #10000000   this square has been marked for some debugging reason

#array is rotated 90 degrees clockwise so that x and y can be input in that order

class SquareGrid:
    def __init__(self):
        self.arr = self.get_empty_grid()

    def add_wall(self, x, y, r):
        if r == 0:
            if self.arr[x, y] & 16:
                return False
            self.arr[x, y] |= 49 # 1 + 16 + 32 
            self.arr[x+1, y] |= 17 # 1 + 16
            self.arr[x+1, y+1] |= 4 
            self.arr[x, y+1] |= 4
            if x > 0:
                self.arr[x-1, y]  |= 16
        else:
            if self.arr[x, y] & 32:
                return False
            self.arr[x, y] |= 50 # 2 + 16 + 32
            self.arr[x+1, y] |= 8 
            self.arr[x+1, y+1] |= 8 
            self.arr[x, y+1] |= 34 # 2 + 32
            if y > 0:
                self.arr[x, y-1] |= 32
        return True

    def add_pawn(self, coords):
        self.arr[coords[0], coords[1]] += 64

    def get_open_wall_moves(self):
        legal_moves = []
        for x in range(8):
            for y in range(8):
                num = self.arr[x, y]
                if not num & 16:
                    legal_moves.append((x, y, 0))
                if not num & 32:
                    legal_moves.append((x, y, 1))
        return legal_moves
    
    def mark(self,coords):
        x, y =coords
        self.arr[x, y] |= 128

    def clear(self, coords):
        x, y =coords
        self.arr[x, y] &= 127
    
    def clear_all(self):
        self.arr &= 127


    def get_empty_grid(self):
        return np.array(
                [
                [12, 8, 8, 8, 8, 8, 8, 8, 9],
                [ 4, 0, 0, 0, 0, 0, 0, 0, 1],
                [ 4, 0, 0, 0, 0, 0, 0, 0, 1],
                [ 4, 0, 0, 0, 0, 0, 0, 0, 1],
                [ 4, 0, 0, 0, 0, 0, 0, 0, 1],
                [ 4, 0, 0, 0, 0, 0, 0, 0, 1],
                [ 4, 0, 0, 0, 0, 0, 0, 0, 1],
                [ 4, 0, 0, 0, 0, 0, 0, 0, 1],                
                [ 6, 2, 2, 2, 2, 2, 2, 2, 3]
                ], dtype=np.uint8)
    
    def get_neighbors(self, p):
        x, y = p
        barriers = (1, 2, 4, 8)
        cell_value = self.arr[x, y]  # Avoid multiple lookups
        
        return [
            (nx, ny) for i, (dx, dy) in enumerate([(0, 1), (1, 0), (0, -1), (-1, 0)])
            if 0 <= (nx := x + dx) < 9 and 0 <= (ny := y + dy) < 9 and not (cell_value & barriers[i])
        ]
    
    def are_connected(self, p1, pset):
        
        pset = set(pset)
        to_visit = []  
        g_cost = {p1: 0} 
        
        
        def heuristic(p):
            return min(abs(p[0] - goal[0]) + abs(p[1] - goal[1]) for goal in pset)
        
        heapq.heappush(to_visit, (heuristic(p1), 0, p1)) 
        
        while to_visit:
            _, g, curr = heapq.heappop(to_visit)
            
            self.mark(curr) 
            
            if curr in pset:
                return True 
            
            for neighbor in self.get_neighbors(curr):
                new_g = g + 1 
                if neighbor not in g_cost or new_g < g_cost[neighbor]:
                    g_cost[neighbor] = new_g
                    f_score = new_g + heuristic(neighbor)
                    heapq.heappush(to_visit, (f_score, new_g, neighbor))  
                    
        return False  
    


        # pset = set(pset)
        # visited = set()
        # to_visit = []
        # g_cost = {p1: 0}

        # def heuristic(p):
        #     return min(abs(p[0] - goal[0]) + abs(p[1] - goal[1]) for goal in pset) if pset else 0
        # heapq.heappush(to_visit, (heuristic(p1), p1))
        
        # while to_visit:
        #     _, curr = heapq.heappop(to_visit)
        #     self.mark(curr)
        #     if curr in pset:
        #         return True
        #     if curr in visited:
        #         continue
        #     visited.add(curr)
            
        #     for neighbor in self.get_neighbors(curr):
        #         if neighbor in visited:
        #             continue
        #         new_g = g_cost[curr] + 1
        #         if neighbor not in g_cost or new_g < g_cost[neighbor]:
        #             g_cost[neighbor] = new_g
        #             f_score = new_g + heuristic(neighbor)
        #             heapq.heappush(to_visit, (f_score, neighbor))
        # return False

        
    
    def __repr__(self):
        return str(self.arr)
    

#N = 1
#E = 2
#S = 4
#W = 8
#NA = 16
#EA = 32
#SA = 64
#WA = 128  

class ConnGrid:
    def __init__(self):
        self.arr = self.get_empty_grid()
    
    def get_empty_grid(self):
        return np.array([
            [12, 8, 8, 8, 8, 8, 8, 8, 8, 9],
            [ 4, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [ 4, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [ 4, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [ 4, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [ 4, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [ 4, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [ 4, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [ 4, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [ 4, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [ 6, 2, 2, 2, 2, 2, 2, 2, 2, 3]]
        )
    
    # def add_wall(self, x, y, r):
    #     x += 1
    #     y += 1
    #     if r == 0:

            
    #         sub = self.arr[x-1:x+2, y]
    #         # g = np.bitwise_or.reduce(self.arr[x-1:x+2, y], dtype=np.int8)
    #         # for x1 in range(x-1,x+2):
    #         #     self.arr[x1,y] = g
    #     if r == 1:
    #         # g = np.bitwise_or.reduce(self.arr[x, y-1:y+2], dtype=np.int8)
    #         # for y1 in range(y-1,y+2):
    #         #     self.arr[x,y1] = g



            
        
        

    def __repr__(self):
        return str(self.arr)
    


if __name__ == "__main__":
    g = ConnGrid()
    print(g)
    # g.add_wall(0, 0, 0)
    # g.add_wall(1,0,1)
    # g.add_wall(1,2,1)
    # g.add_wall(2,3,0)
    # print(g)
 