import numpy as np
from utils import get_display_string

# N = 1     # 00000001
# E = 2     # 00000010
# S = 4     # 00000100
# W = 8     # 00001000
# H = 16    # 00010000
# V = 32    # 00100000
# oc = 64   # 01000000

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
    
    def add_wall(self, x, y, r):
        x += 1
        y += 1
        if r == 0:
            
            
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
 