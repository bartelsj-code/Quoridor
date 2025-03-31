from grid import SquareGrid
import numpy as np
from utils import *
from random import choice
from time import perf_counter as perf

class Gamestate:
    def set_up_as_start(self, player_count, total_walls = 20):
        self.over = False
        self.player_up = 0
        self.player_positions = [(4,0), (4,8), (0,4), (8,4)][:player_count]
        self.player_walls = [total_walls//player_count]*player_count
        self.grid = SquareGrid()
        self.grid.set_up_from_start()
        for player_position in self.player_positions:
            self.grid.add_pawn(player_position)
        self.open_placements = self.get_start_placements()
        self.goals = self.get_goals()
        self.wall_count = total_walls
        self.walls_remain = True
        self.winner = None

    def get_clone(self):
        clone = Gamestate()
        clone.over = self.over
        clone.player_up = self.player_up
        clone.player_positions = self.player_positions[:]
        clone.player_walls = self.player_walls[:]
        clone.grid = self.grid.get_clone()
        clone.open_placements = self.open_placements.copy()
        clone.goals = clone.get_goals()
        clone.wall_count = sum(clone.player_walls)
        clone.walls_remain = self.walls_remain
        clone.winner = self.winner
        return clone

    def skip_turn(self):
        self.player_up = (self.player_up + 1) % len(self.player_positions)

    def play_move(self, move):
        if len(move) == 3 and type(move[2]) == int:
            self.play_wall(move)
        else:
            self.play_pawn(move)
        if self.has_won(self.player_up):
            self.over = True
            self.winner = self.player_up
        self.player_up = (self.player_up + 1) % len(self.player_positions)

    def get_legal_moves(self):
        return self.get_legal_placements() + self.get_legal_pawn_moves()

    def get_legal_placements(self):
        if self.player_walls[self.player_up] > 0:
            return list(self.open_placements)
        return []

    def play_wall(self, move):
        if move not in self.get_legal_placements():
            raise Exception(f"Illegal placement {move} requested")
        self.grid.add_wall(move)
        self.remove_physicals(move)
        self.remove_illegals(move)
        self.player_walls[self.player_up] -= 1
        if self.walls_remain and self.wall_count == 0:
            self.open_placements = set()
            self.walls_remain = False


    def get_legal_pawn_moves(self):
        start = self.player_positions[self.player_up]
        options = []
        neighbors = self.grid.get_neighbors(start)

        for neighbor in neighbors:
            if self.grid.is_occupied(neighbor):
                one_beyond = (2 * neighbor[0] - start[0], 2 * neighbor[1] - start[1])

                n2s = self.grid.get_neighbors(neighbor)
                n2s.remove(start)
                if one_beyond in n2s:
                    options.append((neighbor,one_beyond))
                    continue
                for n in n2s:
                    options.append((neighbor,n))
            else:
                options.append(neighbor)
        return options

    def play_pawn(self, move):
        
        if move not in self.get_legal_pawn_moves():
            raise Exception(f"Illegal pawn move {move} requested:\n{self}")
        start_coords = self.player_positions[self.player_up]
        move_components = [start_coords, move] if type(move[0]) == int else [start_coords] + list(move)
        # print(self.grid)
        self.grid.remove_pawn(move_components[0])
        self.grid.add_pawn(move_components[-1])
        
        self.player_positions[self.player_up] = move_components[-1]
        if self.walls_remain:
            all_cands = []
            for i in range(len(move_components)-1):
                square1, square2 = move_components[i], move_components[i+1]
                delta = (square2[0] - square1[0], square2[1] - square1[1])
                x,y = square1
                candidates = []
                if delta == (1,0):
                    #East
                    if y < 8:

                        candidates.append((x, y, 1))
                    if y > 0:
                        candidates.append((x, y-1, 1))
                
                if delta == (-1,0):
                    #West
                    if y < 8:
                        candidates.append((x-1, y, 1))
                        
                    if y > 0:
                        candidates.append((x-1, y-1, 1))
                        
                if delta == (0,1):
                    #North
                    if x < 8:
                        candidates.append((x, y, 0))
                    if x > 0:
                        candidates.append((x-1, y, 0))
                if delta == (0,-1):
                    #South
                    if x < 8:
                        candidates.append((x,y-1,0))
                    if x > 0:
                        candidates.append((x-1, y-1, 0))
                
                all_cands += candidates

            self.update_illegals(all_cands)


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

    def update_illegals(self, candidates):
        marked_illegal = []
        marked_legal = []
        for candidate in candidates:
            if self.grid.is_illegal(candidate):
                marked_illegal.append(candidate)
            elif candidate in self.open_placements:
                marked_legal.append(candidate)

        illegals = self.get_illegals(marked_illegal)
        for c in marked_illegal:
            if c not in illegals:
                self.grid.unmark_illegal(c)
                self.open_placements.add(c)

        new_illegals = self.get_illegals(marked_legal)

        for c in marked_legal:
            if c in new_illegals:
                self.grid.mark_illegal(c)
                self.open_placements.discard(c)

    def has_won(self, player):
        t = (8, 0)
        if player < 2:
            return self.player_positions[player][1] == t[player%2]
        return  self.player_positions[player][0] == t[player%2]
    

        

    
    def get_start_placements(self):
        return {(x, y, r) for r in range(2) for x in range(8) for y in range(8)}

    def __str__(self):
        symbs = ("•","○","∆","◇")
        return get_display_string_pl(self.grid.arr, self.player_positions, 0) + f"player {symbs[self.player_up]}"  
    
    def remove_physicals(self, move):
        x, y, r = move
        if r == 0:
            for dx in (-1, 0, 1):
                nx = x + dx
                if 0 <= nx < 8:
                    self.open_placements.discard((nx, y, r))
                    self.grid.unmark_illegal((nx, y, r))
        else:
            for dy in (-1, 0, 1):
                ny = y + dy
                if 0 <= ny < 8:
                    self.open_placements.discard((x, ny, r))
                    self.grid.unmark_illegal((x, ny, r))
    
        if 0 <= x < 8 and 0 <= y < 8:
            self.open_placements.discard((x, y, 1 - r))
            self.grid.unmark_illegal((x, y, 1 - r))

    def get_goals(self):
        return [
        [(i,8) for i in range(9)],
        [(i,0) for i in range(9)],
        [(8,i) for i in range(9)],
        [(0,i) for i in range(9)],
        ]
    
    # def check_position_legal(self):

    #     for i, position in enumerate(self.player_positions):
    #         conn = self.grid.are_connected(position, self.goals[i])
    #         if not conn:
    #             return False
    #     return True

    



    
if __name__ == "__main__":
    print("running incorrect file")
    # g = Gamestate(
    #     [(4,0), (4,8), (0,4), (8,4)]
    #     )
    # # # print(g)

    # for r in range(1):

        
    #     g = Gamestate(
    #     [(4,0), (4,8)]
    #     )
    #     # print(g)
    #     for i in range(600):
    #         move_options = g.get_legal_moves()
    #         tup = choice(move_options)
    #         # print(tup)
    #         g.play_move(tup)
    #         # print(g)
    #         if g.over:
    #             print(f"game over after {i} random moves")
    #             break
    #     print(g)



        # is_legal = g.check_position_legal()

    # for i in range(5000):
    #     g.check_position_legal()
    
    
    

    
    
