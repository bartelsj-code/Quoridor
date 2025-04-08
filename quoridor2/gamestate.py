from grid import SquareGrid
import numpy as np
from utils import *
from random import choice, random, seed
from union_find import find, grid_index
import cProfile
import pstats

seed('bagel')

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
        self.goals = self.get_starting_goals()
        self.wall_count = total_walls
        self.winner = None

    def get_clone(self):
        clone = Gamestate()
        clone.over = self.over
        clone.player_up = self.player_up
        clone.player_positions = self.player_positions[:]
        clone.player_walls = self.player_walls[:]
        clone.grid = self.grid.get_clone()
        clone.open_placements = self.open_placements.copy()
        clone.goals = [goals.copy() for goals in self.goals]
        clone.wall_count = self.wall_count
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
        
    def get_legal_placements(self):
        if self.player_walls[self.player_up] > 0:
            return list(self.open_placements)
        return []
    
    def play_wall(self, move):
        if move not in self.get_legal_placements():
            raise Exception(f"Illegal placement {move} requested")
        self.grid.add_wall(move)
        self.player_walls[self.player_up] -= 1
        self.wall_count-=1
        if self.wall_count == 0 :
            self.open_placements = set()
        # self.update_goals()
        self.remove_physicals(move)
        self.remove_illegals(move)
        

    

    def play_pawn(self, move):
        if move not in self.get_legal_pawn_moves():
            raise Exception(f"Illegal pawn move {move} requested:\n{self}")
        start_coords = self.player_positions[self.player_up]
        move_components = [start_coords, move] if type(move[0]) == int else [start_coords] + list(move)
        # print(self.grid)
        self.grid.remove_pawn(move_components[0])
        self.grid.add_pawn(move_components[-1])
        
        self.player_positions[self.player_up] = move_components[-1]
        if self.wall_count > 0:
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

    def get_immediate_placements(self, move):
        start_x, start_y, start_r = move
        if start_r == 0:
            components = ((start_x, start_y, start_r+1), (start_x+1, start_y, start_r+1))
        if start_r == 1:
            components = ((start_x, start_y, start_r+1), (start_x, start_y+1, start_r+1))
        segs = []
        seen = set()
        for component in components:
            for seg in self.get_wall_neighbors(component):
    
                x, y, r = seg
                if not self.grid.has_wall(x, y, r ) and seg not in components:
                    segs.append(seg)
        
        segs = list(set(segs))
        placements = set()
        for ex, ey, er in segs:
            new_r = er - 1
            candidate = (ex, ey, new_r)
            if candidate in self.open_placements:
                placements.add(candidate)
            

            if new_r == 0 and ex > 0:
                alt_candidate = (ex - 1, ey, new_r)
                if alt_candidate in self.open_placements:
                    placements.add(alt_candidate)
            elif ey > 0:
                alt_candidate = (ex, ey - 1, new_r)
                if alt_candidate in self.open_placements:
                    placements.add(alt_candidate)
                    
        return list(placements)
        # for neighbor in self.get_wall_neighbors((start_x, start_y, start_r + 1)):


    def get_connected_placements(self, move):

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


        empties = list(set(empties))


        placements = set()

        for ex, ey, er in empties:
            new_r = er - 1
            candidate = (ex, ey, new_r)
            if candidate in self.open_placements:
                placements.add(candidate)
            if new_r == 0 and ex > 0:
                alt_candidate = (ex - 1, ey, new_r)
                if alt_candidate in self.open_placements:
                    placements.add(alt_candidate)
            elif ey > 0:
                alt_candidate = (ex, ey - 1, new_r)
                if alt_candidate in self.open_placements:
                    placements.add(alt_candidate)

                    
        return list(placements)

    
    def get_path_overlaps(self):
        overlaps = set()
        for i, position in enumerate(self.player_positions):
            path = self.grid.astar_full_path(position, self.goals[i])
            for j in range(len(path)-1):
                a = path[j]
                b = path[j+1]
                if a > b:
                    a, b = b, a
                ax, ay = a
                bx, by = b
                if ax == bx:
                    for placement in ((ax, ay, 0), (ax-1, ay, 0)):
                        if placement in self.open_placements:
                            overlaps.add(placement) 
                if ay == by:
                    for placement in ((ax, ay-1, 1), (ax, ay, 1)):
                        if placement in self.open_placements:
                            overlaps.add(placement)
        return overlaps

                

    def narrow_candidates(self, move):
        touches = self.grid.get_touches(move)
        if touches == 0:
            return []
        elif touches == 1:
            cands = self.get_immediate_placements(move)
        else:
            cands = self.get_connected_placements(move)


        overlaps = self.get_path_overlaps()
        # cands = [cand for cand in cands if cand in overlaps]
    
        cands = [cand for cand in cands if cand in overlaps
                 and not self.grid.is_illegal(cand)
                 and self.grid.get_touches(cand) == 2]
        
        

       

        
        return cands
      
    
    

    def remove_illegals(self, move):
        candidates = self.narrow_candidates(move)
        illegals = self.get_illegals_greedy(candidates)
        self.grid.add_wall(move)
        # print(self.open_placements)
        for illegal in illegals:
            
            self.open_placements.remove(illegal)
            self.grid.mark_illegal(illegal)

    def get_illegals_uf(self, candidates):
        illegals = []
        for placement in candidates:
            self.grid.set_up_uf(placement)
            for i, position, in enumerate(self.player_positions):
                if not self.grid.connected_to_goal(position, self.goals[i]):
                    illegals.append(placement)
                    break
        return illegals

    def get_illegals_greedy(self, candidates, single_player = False):
        illegals = []
        if single_player:
            for candidate in candidates:
                self.grid.add_wall(candidate)
                position = self.player_positions[self.player_up]
                goals = self.goals[self.player_up]
                if not self.grid.are_connected_greedy(position, goals):
                    illegals.append(candidate)
                self.grid.remove_wall(candidate)
            return illegals
        else:
            for candidate in candidates:
                self.grid.add_wall(candidate)
                for i, position, in enumerate(self.player_positions):
                    if not self.grid.are_connected_greedy(position, self.goals[i]):
                        illegals.append(candidate)
                        break
                self.grid.remove_wall(candidate)
            return illegals

    def update_goals(self):
        self.grid.set_up_uf()
        for i, position in enumerate(self.player_positions):
            r = find(self.grid.parent, grid_index(position[0], position[1]))
            self.goals[i] = {spot for spot in self.goals[i] if find(self.grid.parent, grid_index(spot[0], spot[1])) == r}
        # print([len(g) for g in self.goals])
        pass
    
    def update_illegals(self, candidates):
        marked_illegal = []
        marked_legal = []
        for candidate in candidates:
            if self.grid.is_illegal(candidate):
                marked_illegal.append(candidate)
            elif candidate in self.open_placements:
                marked_legal.append(candidate)

        illegals = self.get_illegals_greedy(marked_illegal)
        for c in marked_illegal:
            if c not in illegals:
                self.grid.unmark_illegal(c)
                self.open_placements.add(c)

        new_illegals = self.get_illegals_greedy(marked_legal)

        for c in marked_legal:
            if c in new_illegals:
                self.grid.mark_illegal(c)
                self.open_placements.discard(c)

    def has_won(self, player):
        t = (8, 0)
        if player < 2:
            return self.player_positions[player][1] == t[player%2]
        return  self.player_positions[player][0] == t[player%2]

    def try_early_eval(self):
        if self.wall_count == 0:
            self.evaluate_early()

    

    def evaluate_early(self):
        degree = 2#len(self.player_positions)
        l = -1
        lowest = float("inf")
        second = float("inf")
        for i, coords in enumerate(self.player_positions):
            goals = self.goals[i]
            curr = self.grid.astar_distance(coords, goals)
            if curr < lowest:
                second = lowest
                lowest = curr
                l = i
            elif curr < second:
                second = curr

        if lowest <= second-degree:
            self.winner = l
            # print("cut off early")
            self.over = True

    def get_move_weighted(self, weighting):
        if self.player_walls[self.player_up] > 0 :
            if random() > weighting:
                try:
                    return choice(list(self.open_placements))
                except:
                    self.wall_count = 0
        return choice(self.get_legal_pawn_moves())


    def get_fastest_move(self):
        move_candidate = self.grid.astar_first_move(self.player_positions[self.player_up], self.goals[self.player_up])
        if move_candidate in self.get_legal_pawn_moves():
            return move_candidate
        return choice(self.get_legal_pawn_moves())
    
    def get_rollout_move(self, weight):
        if self.player_walls[self.player_up] > 0:
            move = self.get_move_weighted(weight)
        else:
            move = g.get_fastest_move()
        return move
        
    
    def get_start_placements(self):
        return {(x, y, r) for r in range(2) for x in range(8) for y in range(8)}


    def __str__(self):
        symbs = ("•","○","∆","◇")
        return get_display_string_pl(self.grid.arr, self.player_positions, 0) + f"player {symbs[self.player_up]} Winner: {symbs[self.winner]}"  
    
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

    def get_starting_goals(self):
        return [
        set([(i,8) for i in range(9)]),
        set([(i,0) for i in range(9)]),
        set([(8,i) for i in range(9)]),
        set([(0,i) for i in range(9)]),
        ][:len(self.player_positions)]
    
    
    
        
if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()  
    
    for i in range(1000):
        g = Gamestate()
        g.set_up_as_start(2)
        # print(g)    
        j = 0
        while not g.over:
            move = g.get_rollout_move(0.3)
            # print(move)
            # print(move)
            g.play_move(move)

            g.try_early_eval()
            j += 1
            
            # print(g)

    profiler.disable()  
    stats = pstats.Stats(profiler).sort_stats('cumulative')
    stats.print_stats(5)

    # g.play_move((0,5,0))
    
    
    # g.play_move((4,5,0))
    # g.play_move((2,5,0))
    # g.play_wall((6,5,0))
    
    # g.play_wall((7,5,1))
    # # print(g)
    # # print(g.finds)
    # g.play_wall((5,4,1))
    # # print(g)
    # # print(g.finds)
    # g.play_wall((7,1,0))
    # g.play_wall((5,3,0))
    # g.play_wall((5,1,0))
    # g.play_wall((3,1,0))
    
    # # print(g)
    # # print(g.finds)
    # g.play_move((6,1,1))
    # g.play_wall((2,2,1))
    # g.play_move((0,4,1))

    # g.play_move((7,7,0))

    # g.play_wall((2,5,0))
    # print(g)
    # print(g.finds)
