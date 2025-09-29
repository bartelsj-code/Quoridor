from grid import SquareGrid
import numpy as np
from utils import *
from random import choice, random, seed, randint
from union_find import *
import cProfile
import pstats
from gamestate import Gamestate


import random
R = random.Random(0x9E3779B97F4A7C15)  # any fixed 64-bit seed

GRID_SIZE = 9
N_SQUARES = GRID_SIZE * GRID_SIZE
MAX_PLAYERS = 4
MAX_WALLS = 100
HASH_MASK = 0x7F    # ignore 'mark' bit; consider also ignoring transient bits

def r64(): return R.getrandbits(64)

Z_GRID  = [[r64() for _ in range(256)] for _ in range(N_SQUARES)]
Z_POS   = [[r64() for _ in range(N_SQUARES)] for _ in range(MAX_PLAYERS)]
Z_TURN  = [r64() for _ in range(MAX_PLAYERS)]
Z_WALLS = [[r64() for _ in range(MAX_WALLS + 1)] for _ in range(MAX_PLAYERS)]

class Calcstate(Gamestate):
    '''Gamestate class expansion with more calculation-related methods'''
    def import_gamestate(self, gamestate):
        self.player_count = gamestate.player_count
        self.over = gamestate.over
        self.player_up = gamestate.player_up
        self.player_positions = gamestate.player_positions[:]
        self.player_walls = gamestate.player_walls[:]
        self.grid = gamestate.grid.get_clone()
        self.open_placements = gamestate.open_placements.copy()
        self.goals = gamestate.goals[:]
        self.wall_count = gamestate.wall_count
        self.paths = [path[:] for path in gamestate.paths]
        self.blockers = [b.copy() for b in gamestate.blockers]
        self.winner = gamestate.winner

    def try_early_eval(self):
        if self.wall_count == 0:
            self.evaluate_early(3)

    def evaluate_early(self, degree):
        lengths = [len(self.paths[i]) for i in range(self.player_count)]

        lowest = second = float("inf")
        winner = -1

        for i, val in enumerate(lengths):
            if val < lowest:
                second = lowest
                lowest = val
                winner = i
            elif val < second:
                second = val

        if lowest <= second - degree:
            self.winner = winner
            self.over = True





    def get_directist_pawn_move(self):
        path_move = self.paths[self.player_up][1]
        legal_moves = self.get_legal_pawn_moves()
        if path_move in legal_moves:
            return path_move
        jump_move = self.paths[self.player_up][2]
        for move in legal_moves:
            if move[1] == jump_move:
                return move
        return None
    
    def get_rollout_move(self):
        return self.get_random_move()
    
    def get_random_move(self):
        return choice(self.get_legal_moves())
    

    def _square_index(x, y):
        return y * 9 + x
    
    def _rehash(self) -> int:
        h = 0
        arr = self.grid.arr
        for y in range(9):
            for x in range(9):
                s = self._square_index(x, y)
                v = int(arr[x, y]) & HASH_MASK
                h ^= Z_GRID[s][v]
        # 2) player positions
        for pid, (x, y) in enumerate(self.player_positions):
            s = self._square_index(x, y)
            h ^= Z_POS[pid][s]
        # 3) side to move
        h ^= Z_TURN[self.player_up]
        # 4) walls remaining
        for pid, w in enumerate(self.player_walls):
            h ^= Z_WALLS[pid][w]
        self._zhash = h
        return h
    
    def play_move(self, move):
        super().play_move(move)
        self._zhash ^= Z_TURN[self.player_up]

    def get_hash(self):
        if not hasattr(self, "_zhash"):
            return self._rehash()
        return self._zhash


if __name__ == "__main__":
    seed("bagel")
    profiler = cProfile.Profile()
    profiler.enable()  

    for i in range(2000):
        
        g  = Calcstate()
        g.set_up_as_start(2)

        j = 0
        while not g.over:
            move = g.get_rollout_move()
            g.play_move(move)
            g.try_early_eval()
            j += 1
        i += 1
            
    profiler.disable()  
    stats = pstats.Stats(profiler).sort_stats('cumulative')
    stats.print_stats(25)



    # def get_favorable_placement(self):
    #     block_others = {}
    #     for i in range(self.player_count):
    #         if i == self.player_up:
    #             continue
    #         for blocker in self.blockers[i]:
    #             if blocker not in block_others:
    #                 block_others[blocker] = 0
    #             if blocker in self.blockers[self.player_up]:
    #                 block_others[blocker] -= 1
    #             elif blocker in self.open_placements:
    #                 block_others.add(blocker)
    #     if len(block_others) > 0:
    #         return choice(list(block_others))
    #     else:
    #         return choice(list(self.open_placements))