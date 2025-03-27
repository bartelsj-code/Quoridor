from grid import SquareGrid, ConnGrid
import numpy as np
from utils import *
from random import choice

class Gamestate:
    def __init__(self, player_positions = []):
        self.player_positions = player_positions
        self.grid = SquareGrid()
        self.cg = ConnGrid()
        for player_position in self.player_positions:
            self.grid.add_pawn(player_position)     
        self.open_placements = set(self.grid.get_open_wall_moves())
        self

    def __repr__(self):
        return get_display_string_pl(self.grid.arr, self.player_positions, 0)    
    
    def play_wall(self, move):
        print(len(self.open_placements))
        r = move[2]
        x = move[0]
        y = move[1]
        if self.grid.add_wall(x,y,r):
            print("added wall")

        if r == 0:
            for x2 in range(max(x-1, 0), x+2):
                self.open_placements.discard((x2,y,r))
            self.open_placements.discard((x, y,1))
        if r == 1:
            for y2 in range(max(y-1, 0), y+2):
                self.open_placements.discard((x,y2,r))
            self.open_placements.discard((x, y,0))

    def get_legal_moves(self):
        pass
        # self.grid.get_legal_wall_moves()
        # return self.grid.get_open_wall_moves()

        
        # self.grid.get_legal_pawn_moves():

    



    
if __name__ == "__main__":
    g = Gamestate(
        [(4,0), (4,8), (6,3), (3,3)]
        )
    # print(g)
    

    # print(g.grid.grid)
    # g.grid.add_wall(0,0,0)

    for i in range(20):
        print(g)
        
        tup = choice(tuple(g.open_placements))
        g.play_wall(tup)
    print(g)

    
    
