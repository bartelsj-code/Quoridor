from grid import SquareGrid
import numpy as np
from utils import *
from random import choice, random, seed, randint
from union_find import *
import cProfile
import pstats
from copy import deepcopy


class Gamestate:
    
    ###############################  Overview  ##################################
    '''
    This class stores a Quoridor game position and some additional data and is written to be flexible so it can be used in a variety of simulations and in the base game

    Important Variables:
        self.grid: a SquareGrid object containing a 9x9 numpy array storing the walls, occupation, and adjacencies of each square in the position.
        self.open_placements: a set of all legal wall placement tuples for the current position (gets updated as game progresses but avoids re-evaluation)

        self.player_up: an int indicating which player is "at bat"
        self.over: indicates whether the game has reached an end state
        self.winner: indicates which player has won if the game has reached an end state

        The following lists are indexed 0 to 3 to access specific player's data often using self.player_up.
            self.player_positions: a list of tuples, each of which has an x and a y coordinate
            self.player_walls: a list of ints tracking how many walls each player has remaining to them
            self.goals: a list of sets of coordinates which are the goals for each respective player
            self.paths: a list of lists of coordinates. Each sublist is the shortest path from the player's coordinates to a goal square
            self.blockers: a list of sets of placement tuples. Placments in player i's set intersect player i's path.
    '''


    ##########################  Instance Initiations  ###########################

    def set_up_as_start(self, player_count, total_walls = 20):
        '''
        Sets up a gamestate to standard starting position.   

        Args:
            player_count: the number of players playing the game
            total_walls:  the number of walls to be evenly distributed to the players
        '''

        #win flag and identifier
        self.over = False
        self.winner = None 

        ###### set up players #######
        self.player_up = 0  
        self.player_count = player_count  
        self.player_positions = [(4,0), (4,8), (0,4), (8,4)][:player_count]  

        ###### set up walls  #######
        self.player_walls = [total_walls//player_count]*player_count  
        self.wall_count = sum(self.player_walls)

        ###### set up grid  #######
        self.grid = SquareGrid()  
        self.grid.set_up_from_start()

        for player_position in self.player_positions:  
            self.grid.add_pawn(player_position)  

        #  Set of all legal wall placements (updated over time)
        self.open_placements = self.get_start_placements()  
        
        # List of Sets of goal coordinates for each player
        self.goals = self.get_starting_goals()  

        #  Shortest path from each player to a goal coord as list of coord tuples
        self.paths = [self.grid.astar_full_path(self.player_positions[i], self.goals[i]) for i in range(self.player_count)]  
        self.blockers = [self.get_blockers(self.paths[i]) for i in range(self.player_count)]

    def get_clone(self):
        '''
        Creates a clone of this gamestate with all attributes matching (to be used in game tree traversal)
        Faster than deepcopy because some data can be shallow

        Returns:
            Gamestate object that matches self 
        '''
        clone = type(self)()
        clone.player_count = self.player_count
        clone.over = self.over
        clone.player_up = self.player_up
        clone.player_positions = self.player_positions[:]
        clone.player_walls = self.player_walls[:]
        clone.grid = self.grid.get_clone()
        clone.open_placements = self.open_placements.copy()
        clone.goals = self.goals[:]
        clone.wall_count = self.wall_count
        clone.paths = [path[:] for path in self.paths]
        clone.blockers = [b.copy() for b in self.blockers]
        clone.winner = self.winner
        return clone
    
    
    ############################  Move Execution  ############################

    def play_move(self, move):
        '''
        Takes in a move tuple and executes move on gamestate.

        Args:
            Move - Can take the following forms: 
                (x, y, r)            | A wall placement centered at the north-east corner of the square at x, y. Horizontal if r == 0 and Vertical if r == 1
                (x, y)               | Indicates a pawn move from the current square to the square at x, y.
                ((x1, y1),(x2, y2))  | Indicates a pawn move that involves a jump over another pawn. Ends at x2, y2. 
        '''

        if self.move_is_placement(move):
            self.play_wall(move)
        else:
            self.play_pawn(move)
            #check if the pawn move led the current player to a win.
            if self.has_won(self.player_up):
                self.over = True
                self.winner = self.player_up
        self.update_player()
    
    def play_wall(self, move):
        '''
        Plays wall on gamestate and updates relevant metadata
        
        Args:
            Move: A tuple of the form (x, y, r)            
        '''

        if move not in self.open_placements:
            raise Exception(f"Illegal placement {move} requested:\n{self}")
        
        #add wall
        self.grid.add_wall(move)

        #update remaining wall info
        self.player_walls[self.player_up] -= 1
        self.wall_count-=1

        #update shortest path 
        self.update_paths_after_placement(move)

        # if no more walls, empty open_placements
        if self.wall_count == 0 :
            self.open_placements = set()
            return 
        
        #remove unplayable moves from open_placements
        self.remove_physicals(move)
        self.remove_illegals(move)

    def play_pawn(self, move):
        '''
        Plays a pawn move and updates relevant metadata

        Args:
            move: a pawn move tuple (either a pair of coords, or a two pairs of coord tuples)
        '''
        if move not in self.get_legal_pawn_moves():
            raise Exception(f"Illegal pawn move {move} requested:\n{self}")
        
        start_coords = self.player_positions[self.player_up]
        move_components = [start_coords, move] if type(move[0]) == int else [start_coords] + list(move)
        self.grid.remove_pawn(move_components[0])
        self.grid.add_pawn(move_components[-1])
        self.player_positions[self.player_up] = move_components[-1]
        self.update_paths_after_pawn(move)
        if self.wall_count > 0:
            self.update_illegals(self.get_blockers(move_components))

    def skip_turn(self):
        # in some 3 and 4 player games one can encounter a position with no legal moves (very rare)
        self.update_player()

    ############################### Path Caching ##################################

    '''The gamestate stores the current shortest path and the placements that intersect it. 
    This has value in narrowing illegal move candidates and making good moves in rollout.'''

    def update_path(self, player):
        #sets the path for a player to the shortest currently available path
        self.paths[player] = self.grid.astar_full_path(self.player_positions[player], self.goals[player])

    def update_paths_after_placement(self, move):
        #updates the path after a placement is played, only updating the path for those player's whose existing path is blocked by the placement. 
        for i in range(self.player_count):
            blockers = self.blockers[i]
            if move in blockers:
                self.update_path(i)               
                self.blockers[i] = self.get_blockers(self.paths[i])
    
    def update_paths_after_pawn(self, move):
        #updates the current player's path after their pawn is moved. 

        if self.paths[self.player_up][1] == self.player_positions[self.player_up]:
            path = self.paths[self.player_up][1:]
            # path1 = self.grid.astar_full_path(self.player_positions[self.player_up], self.goals[self.player_up])
            # if path != path1:
            #     print(path,"\n", path1)

            self.paths[self.player_up] = path
            #ToDo, possibly change how blockers work: storing them in dict with number of uses so that blockers can be removed
            #rather than completely re-evaluating the set.
            self.blockers[self.player_up] = self.get_blockers(path)
        else:
            path = self.grid.astar_full_path(self.player_positions[self.player_up], self.goals[self.player_up])
            self.paths[self.player_up] = path
            self.blockers[self.player_up] = self.get_blockers(path)

    def get_blockers(self, path):
        '''
        gets a set of placements that impede path (including impossible placements)

        Args:
            path: List of coord tuples

        Returns:
            blockers: Set of placement tuples 
        '''
        blockers = set()
        for j in range(len(path)-1):
            a = path[j]
            b = path[j+1]
            if a > b:
                a, b = b, a
            ax, ay = a
            bx, by = b
            if ax == bx:
                for placement in ((ax, ay, 0), (ax-1, ay, 0)):
                    blockers.add(placement)
            if ay == by:
                for placement in ((ax, ay-1, 1), (ax, ay, 1)):
                    blockers.add(placement)

        return blockers

    ############################  Legal move queries  ##############################

    def get_legal_moves(self):
        '''
        Returns List of legal moves
        '''
        # returns a list of all legal moves combined
        return self.get_legal_placements() + self.get_legal_pawn_moves()
    
    def get_legal_pawn_moves(self):
        '''
        Determines legal pawn moves for player_up

        Returns:
            options: A list of move tuples
        '''
        start = self.player_positions[self.player_up]
        options = []
        neighbors = self.grid.get_neighbors(start)

        for neighbor in neighbors:
            # jumping moves
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
        #returns a list of legal wall placements
        if self.player_walls[self.player_up] > 0:
            return list(self.open_placements)
        return []
    
    ################## Remove Placements from Open Placements  ################=

    def remove_physicals(self, placement):
        '''
        Removes placements that intersect with the played move from open_placements
        Only called after a placement is played
        
        Args:
            move:  The placement that was just played
        '''
        x, y, r = placement
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

    def remove_illegals(self, placement):
        '''
        removes all moves made illegal by placement from open_placements

        Args:
            Placement: Placment tuple
        '''
        candidates = self.narrow_candidates(placement)
        length = len(candidates)
        if length == 0:
            return
        
        candidate_dict = self.narrow_paths(candidates)
        
        for illegal in self.get_illegals_greedy_targeted(candidate_dict):
            self.remove_illegal(illegal)

    def update_illegals(self, candidates):
        '''
        Handles additions to illegal set from set of candidates'''
        marked_illegal = []
        marked_legal = []

        # One loop: classify candidates
        for candidate in candidates:
            if self.grid.is_illegal(candidate):
                marked_illegal.append(candidate)
            elif candidate in self.open_placements:
                marked_legal.append(candidate)

        # Get all new illegal statuses in one go, if you can
        check_set = marked_illegal + marked_legal
        new_illegals = self.get_illegals_greedy(check_set)
        new_illegals_set = set(new_illegals)

        for c in marked_illegal:
            if c not in new_illegals_set:
                self.grid.unmark_illegal(c)
                self.open_placements.add(c)

        for c in marked_legal:
            if c in new_illegals_set:
                self.remove_illegal(c)

    def remove_illegal(self, placement):

        ''' Sets a placement's status to legal again '''
        self.open_placements.remove(placement)
        self.grid.mark_illegal(placement)

    def update_player(self):
        self.player_up = (self.player_up + 1) % self.player_count

###############################  Finding Candidates for illegal placements  #####################################
    
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

            placements.add(candidate)
            if new_r == 0 and ex > 0:
                alt_candidate = (ex - 1, ey, new_r)

                placements.add(alt_candidate)
            elif ey > 0:
                alt_candidate = (ex, ey - 1, new_r)
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
            placements.add(candidate)
            if new_r == 0 and ex > 0:
                alt_candidate = (ex - 1, ey, new_r)
                placements.add(alt_candidate)
            elif ey > 0:
                alt_candidate = (ex, ey - 1, new_r)
                placements.add(alt_candidate)

        return list(placements)
    
    def get_path_overlaps(self):
        overlaps = {}
        for i in range(self.player_count):
            blockers = self.blockers[i]
            for blocker in blockers:
                if blocker not in overlaps:
                    overlaps[blocker] = []
                overlaps[blocker].append(i)
        return overlaps
    
    def narrow_paths(self, candidates):
        overlaps = self.get_path_overlaps()
        cands = {cand: overlaps[cand] for cand in candidates if
                 cand in overlaps}
        return cands
                
    def narrow_candidates(self, move):
        touches = self.grid.get_touches(move)
        if touches == 0:
            return []
        elif touches == 1:
            cands = self.get_immediate_placements(move)
        else:
            cands = self.get_connected_placements(move)
        cands = [cand for cand in cands if
                 cand in self.open_placements
                 and self.grid.get_touches(cand) == 2]
        return cands
    
    def get_illegals_greedy_targeted(self, candidates):
        '''goes through all candidates with additional criteria of the players that may be affected'''
        illegals = []
        for candidate, players in candidates.items():
            self.grid.add_wall(candidate)
            for player in players:
                position = self.player_positions[player]
                if not self.grid.are_connected_greedy(position, self.goals[player]):
                    illegals.append(candidate)
                    break
            self.grid.remove_wall(candidate)
        return illegals

    def get_illegals_greedy(self, candidates):
        illegals = []
        for candidate in candidates:
            self.grid.add_wall(candidate)
            for i, position in enumerate(self.player_positions):
                if not self.grid.are_connected_greedy(position, self.goals[i]):
                    illegals.append(candidate)
                    break
            self.grid.remove_wall(candidate)
        return illegals

    def has_won(self, player):
        t = (8, 0)
        if player < 2:
            return self.player_positions[player][1] == t[player%2]
        return  self.player_positions[player][0] == t[player%2]

    def get_start_placements(self):
        return {(x, y, r) for r in range(2) for x in range(8) for y in range(8)}

    def get_starting_goals(self):
        return [
        set([(i,8) for i in range(9)]),
        set([(i,0) for i in range(9)]),
        set([(8,i) for i in range(9)]),
        set([(0,i) for i in range(9)]),
        ][:self.player_count]
    
    
    
    ############################  Misc  #################################

    def __str__(self):
        symbs = ("•","○","∆","◇")
        return get_display_string_pl(self.grid.arr, self.player_positions, 0, player_walls=self.player_walls) + f"player {symbs[self.player_up]} Winner: {symbs[self.winner] if self.winner is not None else 'N/A'}"  
    
    def move_is_placement(self, move):
        return len(move) == 3 and type(move[2]) == int
    
    def show_path(self, path):
        # debugging method for visualizing paths
        for square in path:
            self.grid.mark(square)
        print(self)
        self.grid.clear_all()
    
        

    


