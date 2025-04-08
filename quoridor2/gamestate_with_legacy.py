from grid import SquareGrid
import numpy as np
from utils import *
from random import choice

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
        if self.wall_count == 0:
            self.open_placements = set()
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


#################  LEGACY?   #################
    # def get_adjacent_placements(self, move):
     
    #     start_x, start_y, start_r = move

    #     to_search = {(start_x, start_y, start_r + 1)}
    #     searched = set()
    #     empties = []


    #     while to_search:
    #         current = to_search.pop()
    #         searched.add(current)
    #         for neighbor in self.get_wall_neighbors(current):
    #             if neighbor in searched or neighbor in to_search:
    #                 continue
    #             nx, ny, nr = neighbor
    #             if self.grid.has_wall(nx, ny, nr):
    #                 to_search.add(neighbor)
    #             else:
    #                 empties.append(neighbor)

    #     placements = []

    #     for ex, ey, er in empties:
    #         new_r = er - 1
    #         candidate = (ex, ey, new_r)
    #         if candidate in self.open_placements:
    #             placements.append(candidate)
            

    #         if new_r == 0 and ex > 0:
    #             alt_candidate = (ex - 1, ey, new_r)
    #             if alt_candidate in self.open_placements:
    #                 placements.append(alt_candidate)
    #         elif ey > 0:
    #             alt_candidate = (ex, ey - 1, new_r)
    #             if alt_candidate in self.open_placements:
    #                 placements.append(alt_candidate)
                    
    #     return placements
    
    # def get_touch_twos(self, candidates):
    #     touch_twos = []
    #     for placement in candidates:
    #         if self.grid.touches_two(placement):
    #             touch_twos.append(placement)
    #     return touch_twos

    # def get_candidates(self, move):
    #     placements = self.get_adjacent_placements(move)
    #     placements = self.get_touch_twos(placements)
    #     return placements

#################################################################################################
    
    # def get_partner(self, single):
    #     coords, face = single
    #     if face == 1:
    #         return ((coords[0], coords[1]+1), 4)
    #     if face == 4:
    #         return ((coords[0], coords[1]-1), 1)
    #     if face == 2:
    #         return ((coords[0]+1, coords[1]), 8)
    #     if face == 8:
    #         return ((coords[0]-1, coords[1]), 2)

    # def placements_from_single(self, single):

    #     coords, face = single
    #     if face == 1:
    #         return ((coords[0]-1, coords[1], 0), (coords[0],coords[1], 0))
    #     if face == 4:
    #         return ((coords[0]-1, coords[1]-1, 0), (coords[0],coords[1]-1, 0))
    #     if face == 2:
    #         return ((coords[0], coords[1], 1), (coords[0],coords[1]-1, 1))
    #     if face == 8:
    #         return ((coords[0]-1, coords[1], 1), (coords[0]-1,coords[1]-1, 1))
    #     return []

    # def expand_and_clear_doubles(self, start, goals):
    #     seeked = set()
    #     goals = set(goals)
    #     seeking = set()
    #     visited = set()
    #     to_do = set()
    #     to_do.add(start)

    #     for i in range(80):
    #         while to_do:
                

    #             curr = to_do.pop()
    #             # self.grid.mark(curr)
    #             if curr in goals:
    #                 # print(self)
    #                 # print("goal_reached")
     
    #                 return
                
                
    #             lst = self.s_dict.get(curr)
    #             if lst is not None:
    #                 for single in lst:

    #                     partner = self.get_partner(single)
    #                     if partner in seeking:

    #                         # self.grid.unblock_single(partner[0], partner[1])

    #                         # self.grid.unblock_single(single[0], single[1])
    #                         seeking.remove(partner)
    #                         seeked.add(partner)
    #                         seeked.add(single)
    #                         # seeking.discard(single)
                            
    #                         pass
    #                         # remove wall and both from seeking
    #                     else:
                            
    #                         if single not in seeked:
    #                             # print(single)
    #                             seeking.add(single)
                
                            
        
    #             visited.add(curr)
                
                
                
    #             neighbors = self.grid.get_neighbors(curr)

    #             for neighbor in neighbors:
    #                 if neighbor not in visited and neighbor not in to_do:
    #                     to_do.add(neighbor)

    #             # print(self)
    #             # print(seeking)
    #         # print("section done")

    #         # print(self)
    #         # self.grid.clear_all()

    #         if len(seeking) == 2:
    #             # print(self)
    #             single = seeking.pop()
    #             partner1 = self.get_partner(single)
    #             seeked.add(single)
    #             seeked.add(partner1)
    #             placements1 = self.placements_from_single(single)
    #             single2 = seeking.pop()
    #             partner2 = self.get_partner(single2)

    #             seeked.add(single2)
    #             seeked.add(partner2)

    #             placements2 = self.placements_from_single(single2)
    #             shared = None
    #             for p in placements1:
    #                 if p in placements2:
    #                     self.finds.add(p)
    #                     # print(f"found illegal: {p}")
    #                     break
    #             to_do.add(partner1[0])
    #             to_do.add(partner2[0])

    #         elif len(seeking) == 1:
    #             # raise Exception("Implement")
    #             single = seeking.pop()
    #             partner = self.get_partner(single)
    #             seeked.add(single)
    #             seeked.add(partner)

    #             coords, face = partner
    #             to_do.add((coords))

    #         else:
    #             for s in seeking:
    #                 self.grid.mark(s[0])
    #             print(self)
    #             print(seeking)
    #             raise Exception(f"seeking had length: {len(seeking)}")
    #             single = seeking.pop()


    #     print(self)
    #     raise Exception("loop didn't exit")


                
            



            


    # def expand_and_clear_singles(self, start, goals):
    #     goals = set(goals)
    #     seeking = set()
    #     visited = set()
    #     to_do = set()
    #     to_do.add(start)
        
    #     while True:
    #         while to_do:
                
    #             # print(self)
    #             # print(to_do)
    #             curr = to_do.pop()
    #             # self.grid.mark(curr)
    #             if curr in goals:
    #                 # print(self)
    #                 # print("goal_reached")
    #                 return
                
    #             # print(self)
    #             lst = self.s_dict.get(curr)
    #             if lst is not None:
    #                 for single in lst:

    #                     partner = self.get_partner(single)
    #                     if partner in seeking:

    #                         # self.grid.unblock_single(partner[0], partner[1])

    #                         # self.grid.unblock_single(single[0], single[1])
    #                         seeking.remove(partner)
                            
    #                         pass
    #                         # remove wall and both from seeking
    #                     else:
    #                         if self.get_partner(single)[0] not in visited:
    #                             seeking.add(single)
                            
    #             visited.add(curr)
                
    #             neighbors = self.grid.get_neighbors(curr)

    #             for neighbor in neighbors:
    #                 if neighbor not in visited and neighbor not in to_do:
    #                     to_do.add(neighbor)


    #         # print(self)
    #         # print("segment done")
    #         # self.grid.clear_all()


    #         if len(seeking) == 1:
    #             single = seeking.pop()
    #             # print(single)
                
    #             # self.grid.mark(single[0])
    #             placements = self.placements_from_single(single)
    #             for placement in placements:
    #                 if placement in self.open_placements:
    #                     # print(999,"\n",self, single)
    #                     self.finds.add(placement)
    #                     # print(f"found illegal: {placement}")
    #                     # print(self.finds)
    #             self.grid.unblock_single(single[0], single[1])
                

    #             coords, face = self.get_partner(single)
    #             self.grid.unblock_single(coords, face)
                        
    #             to_do.add((coords))
    #         else:
    #             for s in seeking:
    #                 self.grid.mark(s[0])
    #             print(self)
    #             raise Exception("singles space")
                

    #             # self.grid.clear_all()



    # def record(self, single):
    #     self.s_blocks.add(single)
    #     coords = single[0]
    #     if not coords in self.s_dict:
    #         self.s_dict[coords] = []
    #     self.s_dict[coords].append(single)
    #     # print(self.s_dict)
        

    # def block_h_if_poss(self, a, b):
    #     if a[1]>b[1]:
    #         a, b, = b, a
        

    #     placements = ((a[0]-1, a[1], 0), (a[0], a[1], 0))


    #     if placements[0] in self.open_placements or placements[1] in self.open_placements:
            
    #         self.grid.block_single(a, 1)
    #         self.record((a,1))
            
    #         self.grid.block_single(b, 4)
    #         self.record((b,4))

    # def block_v_if_poss(self, a, b):
    #     if a[0]>b[0]:
    #         a, b, = b, a
        

    #     placements = ((a[0], a[1], 0), (a[0], a[1]-1, 0))
    #     if placements[0] in self.open_placements or placements[1] in self.open_placements:
            
    #         self.grid.block_single(a, 2)
    #         self.record((a,2))
            
    #         self.grid.block_single(b, 8)
    #         self.record((b,8))
         

    # def block_path_verticals(self, path):
    #     for i in range(len(path)-1):
    #         a = path[i]
    #         b = path[i+1]
    #         if a[1] == b[1]:

    #             self.block_v_if_poss(a, b)
        
    # def block_path_horizontals(self, path):
        
    #     for i in range(len(path)-1):
    #         a = path[i]
    #         b = path[i+1]
    #         if a[0] == b[0]:
    #             self.block_h_if_poss(a, b)

    # def mark_path(self, path):
    #     for square in path:
    #         self.grid.mark(square)

                

    # def find_blockers(self, start, goals):

    #     self.s_dict = {}
    #     # print("shortest general path")
    #     shortest_path = self.grid.astar_full_path(start, goals)
    #     if shortest_path == None:
    #         print(self)
    #         raise Exception("Illegal Position")
        
    #     # print("STARTING HORIZONTAL")
    #     # self.mark_path(shortest_path)
    #     # print(self)
    #     #Horizontal Portion
    #     # print("marking all horizontal segments used")
    #     self.block_path_horizontals(shortest_path)
    #     # print(self)
    #     # self.grid.clear_all()
        
    #     path = self.grid.astar_full_path(start, goals)
        
        
        
    #     # # print(path)
    #     if path == None:
    #         # print("2nd path was not found for horizontal")
    #     # #     pass
    #         self.expand_and_clear_singles(start, goals)
    #         # self.grid.clear_all()
            
    #         # print("New second path:")
    #         path = self.grid.astar_full_path(start, goals)
            
            

    #     # ######################################3
    #     # else:
    #     #     print("2nd path WAS good")
    #     # self.mark_path(path)
    #     # print(self)

    #     if path == None:
    #         print(self)
    #         raise Exception("path was none")
    #     self.block_path_horizontals(path)
    #     # print("second path blocked")
    #     # print(self)
    #     # self.grid.clear_all()

    #     # print("expand and clear doubles")
    #     self.expand_and_clear_doubles(start, goals) 
    #     # ################################################
        
    #     while self.s_blocks:
    #         coords, face = self.s_blocks.pop()
    #         self.grid.unblock_single(coords, face)
    #     self.grid.clear_all()

    #     # print("STARTING VERTICALS")
    #     # self.mark_path(shortest_path)
    #     # print(self)
        

    #     # vertical portion

    #     # print("blocking all vertical used connections")
    #     self.block_path_verticals(shortest_path)
    #     # print(self)
    #     # self.grid.clear_all()

    #     path = self.grid.astar_full_path(start, goals)

    #     if path == None:
    #         # print("2nd path was not found for vertical")
    #         self.expand_and_clear_singles(start, goals)

    #         # self.grid.clear_all()
    #         path = self.grid.astar_full_path(start, goals)
    #         # print("new 2nd path")
    #     # else:
    #     #     print("2nd path was good")
    #     # self.mark_path(path)
    #     # print(self)


    #     self.block_path_verticals(path)
    #     # print("blocked verticals roudn 2")
    #     # print(self)

    #     # self.grid.clear_all()
    #     self.expand_and_clear_doubles(start, goals)


    #     while self.s_blocks:
    #         coords, face = self.s_blocks.pop()
    #         self.grid.unblock_single(coords, face)

    #     self.grid.clear_all()
    #     # print("reset:")
    #     # print(self)


###########################################################################################################
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

    

    def narrow_candidates(self, move):
        touches = self.grid.get_touches(move)
        if touches == 0:
            return []
        elif touches == 1:
            cands = self.get_immediate_placements(move)
        else:
            cands = self.get_connected_placements(move)

        cands = [cand for cand in cands if not self.grid.is_illegal(cand) and self.grid.get_touches(cand) == 2]
        return cands
      
    
    

    def remove_illegals(self, move):
        candidates = self.narrow_candidates(move)
        illegals = self.get_illegals(candidates)
        self.grid.add_wall(move)
        # print(self.open_placements)
        for illegal in illegals:
            
            self.open_placements.remove(illegal)
            self.grid.mark_illegal(illegal)


    #     pass
        # self.s_blocks = set()
        # self.finds = set()
        
        # illegals = []
        # for i, start in enumerate(self.player_positions):
        #     # print(f"player {i}")
        #     self.find_blockers(start, self.goals[i])
            
        # print(self.finds)
        # for placement in self.finds:
        #     self.open_placements.discard(placement)
        #     self.grid.mark_illegal(placement)

###########################################################################################################
        

    def get_illegals(self, candidates):
        illegals = []
        for candidate in candidates:
            self.grid.add_wall(candidate)
            for i, position, in enumerate(self.player_positions):
                if not self.grid.are_connected_greedy(position, self.goals[i]):
                    illegals.append(candidate)
                    break
            self.grid.remove_wall(candidate)
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

    def evaluate_early(self, degree = 2):
        l = -1
        lowest = float("inf")
        second = float("inf")
        for i, coords in enumerate(self.player_positions):
            goals = self.goals[i]
            curr = self.grid.get_path_distance(coords, goals)
            if curr < lowest:
                second = lowest
                lowest = curr
                l = i
            elif curr < second:
                second = curr

        if lowest <= second-degree:
            self.winner = l
            self.over = True

    def get_fastest_move(self):
        move_candidate = self.grid.astar_first_move(self.player_positions[self.player_up], self.goals[self.player_up])
        if move_candidate in self.get_legal_pawn_moves():
            return move_candidate
        return choice(self.get_legal_pawn_moves())
    
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
    
        
if __name__ == "__main__":
    
    for i in range(500):
        g = Gamestate()
        g.set_up_as_start(2)
        # print(g)    
        while not g.over:
            options = g.get_legal_moves()
            if g.wall_count > 0:
                move = choice(options)
            else:
                move = g.get_fastest_move()
        
            # print(move)
            g.play_move(move)
        print(g)

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
