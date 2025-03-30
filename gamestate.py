from grid import SquareGrid, ConnGrid
import numpy as np
from utils import *
from random import choice
from time import perf_counter as perf

class Gamestate:
    def __init__(self, player_positions = []):
        self.player_up = 0
        self.player_positions = player_positions
        self.grid = SquareGrid()
        # self.cg = ConnGrid()
        for player_position in self.player_positions:
            self.grid.add_pawn(player_position)     
        self.open_placements = self.get_start_placements()
        self.goals = self.get_goals()

    def play_move(self, move):
        if len(move) == 3:
            self.play_wall(move)
        else:
            self.move_pawn(move)
        # self.player_up = (self.player_up + 1) % len(self.player_positions)

    def play_wall(self, move):
        self.grid.add_wall(move)
        self.remove_physicals(move)
        self.remove_illegals(move)

    def get_wall_neighbors(self, seg):
        x, y, r = seg
        if r == 1 and y < 8:
            candidates = (
                (x, y, 2), (x-1, y, 2), (x-1, y, 1),
                (x-1, y+1, 2), (x, y+1, 2), (x+1, y, 1)
            )
        elif r == 2 and x < 8:
            candidates = (
                (x, y, 1), (x, y+1, 2), (x+1, y, 1),
                (x+1, y-1, 1), (x, y-1, 2), (x, y-1, 1)
            )
        else:
            candidates = ()

        return [
            (nx, ny, nr)
            for nx, ny, nr in candidates
            if 0 <= nx < 9 and 0 <= ny < 9
    ]
    
    
    def get_adjacent_placements(self, move):
     
        start_x, start_y, start_r = move

        to_search = {(start_x, start_y, start_r + 1)}
        searched = set()
        empties = []


        while to_search:
            current = to_search.pop()
            searched.add(current)
            for neighbor in self.get_wall_neighbors(current):
                if neighbor in searched or neighbor in to_search:
                    continue
                nx, ny, nr = neighbor
                if self.grid.has_wall(nx, ny, nr):
                    to_search.add(neighbor)
                else:
                    empties.append(neighbor)

        placements = []

        for ex, ey, er in empties:
            new_r = er - 1
            candidate = (ex, ey, new_r)
            if candidate in self.open_placements:
                placements.append(candidate)
            

            if new_r == 0 and ex > 0:
                alt_candidate = (ex - 1, ey, new_r)
                if alt_candidate in self.open_placements:
                    placements.append(alt_candidate)
            elif ey > 0:
                alt_candidate = (ex, ey - 1, new_r)
                if alt_candidate in self.open_placements:
                    placements.append(alt_candidate)
                    
        return placements

    def get_candidates(self, move):
        placements = self.get_adjacent_placements(move)
        news = []
        for placement in placements:
            if self.grid.touches_two(placement):
                news.append(placement)

        return news
    
    def remove_illegals(self, move):
        candidates = self.get_candidates(move)
        illegals = self.get_illegals(candidates)
        for illegal in illegals:
            self.grid.mark_illegal(illegal)
            self.open_placements.discard(illegal)
        
    def get_illegals(self, candidates):
        illegals = []
        for placement in candidates:
            self.grid.set_up_uf(placement)
            for i, position, in enumerate(self.player_positions):
                if not self.grid.connected_to_goal(position, self.goals[i]):
                    illegals.append(placement)
        return illegals

    def move_pawn(self, move):
        pass

    def get_start_placements(self):
        return {(x, y, r) for r in range(2) for x in range(8) for y in range(8)}

    def __repr__(self):
        return get_display_string_pl(self.grid.arr, self.player_positions, 0)    
    
    def remove_physicals(self, move):
        x, y, r = move
        if r == 0:
            for dx in (-1, 0, 1):
                nx = x + dx
                if 0 <= nx < 8:
                    self.open_placements.discard((nx, y, r))
        else:
            for dy in (-1, 0, 1):
                ny = y + dy
                if 0 <= ny < 8:
                    self.open_placements.discard((x, ny, r))
    
        if 0 <= x < 8 and 0 <= y < 8:
            self.open_placements.discard((x, y, 1 - r))

    def get_goals(self):
        return [
        [(i,8) for i in range(9)],
        [(i,0) for i in range(9)],
        [(8,i) for i in range(9)],
        [(0,i) for i in range(9)],
        ]
    
    def check_position_legal(self):

        for i, position in enumerate(self.player_positions):
            conn = self.grid.are_connected(position, self.goals[i])
            if not conn:
                return False
        return True

    



    
if __name__ == "__main__":
    # g = Gamestate(
    #     [(4,0), (4,8), (0,4), (8,4)]
    #     )
    # # print(g)

    for r in range(50):

        
        g = Gamestate(
        [(4,0), (4,8), (0,4), (8,4)]
        )
        for i in range(20):
            tup = choice(tuple(g.open_placements))
            g.play_move(tup)
            # if not g.check_position_legal():
            #     print("fail!!!!!!!!")
            #     print(g)
        print(g)
    #     # for i in range(1):
    #     #     # print(g)
            
    #     #     tup = choice(tuple(g.open_placements))
            
    #     #     g.play_wall(tup)
            
    #     # print(g)
    #     g.play_move((0,4,0))
    #     g.play_move((2,4,0))
    #     g.play_move((4,4,0))
    #     g.play_move((6,4,0))
    #     # print(g)
    #     # print(g.grid)
  
        
    #     g.play_move((7,5,0))
    #     # print(g)
    #     # print(g.grid)
  

    #     g.play_move((4,5,1))
    #     # print(g)
    #     # print(g.grid)
    # print(g)
  
        
        


        # is_legal = g.check_position_legal()

    # for i in range(5000):
    #     g.check_position_legal()
    
    
    

    
    
