import numpy as np
from utils import get_display_string, get_display_string_pl
from union_find import init_union_find, find, union, grid_index, display_uf
import heapq

# N = 1     # 00000001   a wall is disconnecting me from northern..
# E = 2     # 00000010   eastern...
# S = 4     # 00000100   southern...
# W = 8     # 00001000   ...western neighbor
# H = 16    # 00010000   h wall placement is illegal (blocking a pawn, not physical)
# V = 32    # 00100000   v wall placement is illegal (blocking a pawn, not physical)
# oc = 64   # 01000000   a player pawn (who not specified) is occupying this square (for jumping)
#mark = 128 # 10000000   this square has been marked for some debugging reason and will show up as an "x"

#array is rotated 90 degrees clockwise so that x and y can be input in that order

class SquareGrid:
    def get_clone(self):
        clone = SquareGrid()
        clone.arr = np.copy(self.arr)
        return clone
    
    def set_up_from_start(self):
        self.arr = self.get_empty_grid()

    def is_illegal(self, placment):
        
        x, y, r = placment

        if r:
            return self.arr[x, y] & 32
        return self.arr[x, y] & 16

    def mark_illegal(self, placement):
        

        x, y, r = placement
        if r:
            self.arr[x, y] |= 32
        else:
            self.arr[x, y] |= 16
        # self.mark((x,y))

    def unmark_illegal(self, placement):
        x, y, r = placement
        if r:
            self.arr[x, y] &= ~32
        else:
            self.arr[x, y] &= ~16
        # self.clear((x,y))

    def add_wall(self, placement):
        x, y, r = placement
        if r:
            self.arr[x, y] |= 2
            self.arr[x+1, y] |= 8 
            self.arr[x+1, y+1] |= 8 
            self.arr[x, y+1] |= 2
        else:
            self.arr[x, y] |= 1
            self.arr[x+1, y] |= 1
            self.arr[x+1, y+1] |= 4 
            self.arr[x, y+1] |= 4
        

    def remove_wall(self, placement):
        x, y, r = placement
        if r == 0:
            self.arr[x, y]     &= ~1
            self.arr[x+1, y]   &= ~1
            self.arr[x+1, y+1] &= ~4
            self.arr[x, y+1]   &= ~4
        else:
            self.arr[x, y]     &= ~2
            self.arr[x+1, y]   &= ~8
            self.arr[x+1, y+1] &= ~8
            self.arr[x, y+1]   &= ~2

    def has_wall(self, x, y, face):
        return self.arr[x, y] & face
    
    def remove_pawn(self, coords):
        self.arr[coords[0], coords[1]] &= ~64

    def add_pawn(self, coords):
        self.arr[coords[0], coords[1]] |= 64
    
    def mark(self,coords):
        x, y =coords
        self.arr[x, y] |= 128

    def is_occupied(self, coord):
        x,y = coord
        return self.arr[x,y] & 64
    

    
    def touches_two(self, placement):
        x, y, r = placement
        touches = 0
        if r == 0:
            groups = [
                [(x, y, 8), (x, y+1, 8)] + ([(x-1, y, 1)] if x > 0 else []),
                [(x, y+1, 2), (x, y, 2)],
                [(x+1, y, 2), (x+1, y+1, 2)] + ([(x+2, y, 1)] if x < 7 else [])
            ]
        else:
            groups = [
                [(x, y, 4), (x+1, y, 4)] + ([(x, y-1, 2)] if y > 0 else []),
                [(x, y, 1), (x+1, y, 1)],
                [(x, y+1, 1), (x+1, y+1, 1)] + ([(x, y+2, 2)] if y < 7 else [])
            ]

        for check in groups:
            for t in check:
                if self.has_wall(t[0], t[1], t[2]):
                    touches += 1
                    break
            if touches == 2:
                return True
        return False

            


    def clear(self, coords):
        x, y =coords
        self.arr[x, y] &= 127
    
    def clear_all(self):
        self.arr &= 127

    def get_blocked_pairs(self, placement):
        x, y, r = placement
        if r:
            return [((x, y), (x+1, y)), ((x, y+1), (x+1, y+1))]
        return [((x, y), (x, y+1)), ((x+1, y), (x+1, y+1))]

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
        cell_value = self.arr[x, y]  
        
        return [
            (nx, ny) for i, (dx, dy) in enumerate([(0, 1), (1, 0), (0, -1), (-1, 0)])
            if 0 <= (nx := x + dx) < 9 and 0 <= (ny := y + dy) < 9 and not (cell_value & barriers[i])
        ]
    
    def build_connectivity(self):
        parent, rank = init_union_find(81)
        # print(parent, rank)
        for i in range(9):
            for j in range(9):
                current_index = grid_index(i, j)
                cell_value = self.arr[i, j]
                if not (cell_value & np.uint8(1)):
                    north_index = grid_index(i, j+1)
                    union(parent, rank, current_index, north_index)

                if not (cell_value & np.uint8(2)):
                    east_index = grid_index(i+1, j)
                    union(parent, rank, current_index, east_index)
        return parent, rank

    def set_up_uf(self, placement):
        self.add_wall(placement)
        self.parent, self.rank= self.build_connectivity()
        self.remove_wall(placement)
        
    def coords_connected_uf(self, p1, p2):
        return find(self.parent,grid_index(p1[0],p1[1])) == find(self.parent,grid_index(p2[0],p2[1]))
        
    def connected_to_goal(self, p1, pset):
        player_root = find(self.parent,grid_index(p1[0],p1[1]))
        for square in pset:
            if find(self.parent,grid_index(square[0],square[1])) == player_root:
                return True
        return False

    # def are_connected(self, p1, pset):
        # #does a greedy search from destination set to player location (reverse so that the greedy heuristic can be simpler and more efficient)
        # p1x, p1y = p1
        # open_set = []
        # visited = set()
        # for goal in pset:
        #     heapq.heappush(open_set, (abs(goal[0] - p1x) + abs(goal[1] - p1y), goal))
        # while open_set:
        #     _, curr = heapq.heappop(open_set)
        #     # self.mark(curr)
        #     if curr == p1:
        #         return True
        #     if curr in visited:
        #         continue
        #     visited.add(curr)

        #     for neighbor in self.get_neighbors(curr):
        #         if neighbor in visited:
        #             continue
                
        #         heapq.heappush(open_set, (abs(neighbor[0] - p1x) + abs(neighbor[1] - p1y), neighbor))
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

# # class ConnGrid:
# #     def __init__(self):
# #         self.arr = self.get_empty_grid()
    
# #     def get_empty_grid(self):
# #         return np.array([
# #             [12, 8, 8, 8, 8, 8, 8, 8, 8, 9],
# #             [ 4, 0, 0, 0, 0, 0, 0, 0, 0, 1],
# #             [ 4, 0, 0, 0, 0, 0, 0, 0, 0, 1],
# #             [ 4, 0, 0, 0, 0, 0, 0, 0, 0, 1],
# #             [ 4, 0, 0, 0, 0, 0, 0, 0, 0, 1],
# #             [ 4, 0, 0, 0, 0, 0, 0, 0, 0, 1],
# #             [ 4, 0, 0, 0, 0, 0, 0, 0, 0, 1],
# #             [ 4, 0, 0, 0, 0, 0, 0, 0, 0, 1],
# #             [ 4, 0, 0, 0, 0, 0, 0, 0, 0, 1],
# #             [ 4, 0, 0, 0, 0, 0, 0, 0, 0, 1],
# #             [ 6, 2, 2, 2, 2, 2, 2, 2, 2, 3]]
# #         )
    
# #     # def add_wall(self, x, y, r):
# #     #     x += 1
# #     #     y += 1
# #     #     if r == 0:

            
# #     #         sub = self.arr[x-1:x+2, y]
# #     #         # g = np.bitwise_or.reduce(self.arr[x-1:x+2, y], dtype=np.int8)
# #     #         # for x1 in range(x-1,x+2):
# #     #         #     self.arr[x1,y] = g
# #     #     if r == 1:
# #     #         # g = np.bitwise_or.reduce(self.arr[x, y-1:y+2], dtype=np.int8)
# #     #         # for y1 in range(y-1,y+2):
# #     #         #     self.arr[x,y1] = g



            
        
        

#     def __repr__(self):
#         return str(self.arr)
    


# if __name__ == "__main__":
#     g = ConnGrid()
#     print(g)
#     # g.add_wall(0, 0, 0)
#     # g.add_wall(1,0,1)
#     # g.add_wall(1,2,1)
#     # g.add_wall(2,3,0)
#     # print(g)
 