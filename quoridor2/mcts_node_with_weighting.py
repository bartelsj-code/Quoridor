from gamestate import Gamestate
from random import choice,shuffle
import multiprocessing

import math

# def rollout_simulation(args, cut_depth=20, min_depth = 15):
#     # gamestate, player = args
#     # rollie = gamestate.get_clone()
#     # depth = 0
#     # while not rollie.over:
#     #     if not rollie.walls_remain:
#     #         m = rollie.get_fastest_moves()
#     #     if not m is None:
#     #         move = m
#     #     else:
#     #         move = choice(rollie.get_legal_moves())
#     #     rollie.play_move(move)
#     #     if (depth > min_depth and not rollie.walls_remain) or depth > cut_depth:
#     #         rollie.evaluate_early()
#     #     depth += 1

#     # return 1 if rollie.winner == player else 0



class MctsNodeWeighted:
    def __init__(self, gamestate, player, reached_by=None, parent = None, depth = 0):
        self.depth = depth
        self.gamestate = gamestate.get_clone()
        self.reached_by = reached_by
        self.player = player
        self.parent = parent
        self.children = []
        self.wins = 0
        self.visits = 0
        self.fully_expanded = False

    def get_moves(self):
        self.untried_moves = self.gamestate.get_legal_moves()
        # shuffle(self.untried_moves)
        
    def select_child(self, parent_visits, c):        
        def utc_value(child):
            if child.visits == 0:
                return float('inf')
            win_rate = child.wins / child.visits
            exploration = c * math.sqrt(math.log(parent_visits)/child.visits)
            return win_rate + exploration
        shuffle(self.children)
        
        return max(self.children, key=utc_value)

    
    def spawn_child(self):
        move = self.untried_moves.pop()
        if len(self.untried_moves) == 0:
            self.fully_expanded = True
        child = MctsNodeWeighted(self.gamestate, self.player, move, self, self.depth+1)
        
        child.gamestate.play_move(move)
        child.get_moves()
        # print("self", self)
        # print("child", child)
        self.children.append(child)
        
        return child

    # def rollout_multi(self, num_rollouts = None):
    #     if num_rollouts is None:
    #         num_rollouts = multiprocessing.cpu_count()//2
    #     args = [(self.gamestate.get_clone(), self.player) for _ in range(num_rollouts)]
    #     with multiprocessing.Pool(processes=num_rollouts) as pool:
    #         results = pool.map(rollout_simulation, args)
    #     # Sum the wins (each result is 1 for win, 0 for loss)
    #     return results
    def get_player(self):
        return self.gamestate.player_up

    def rollout_single(self):
        
        rollie = self.gamestate.get_clone()
        moves = []
        rollout_depth = 0
        while not rollie.over:
            # print('hi', rollie.wall_count, rollie.player_walls)
     
            move = rollie.get_rollout_move()
            moves.append(move)
            
      
            if move == None:
                rollie.skip_turn()
                continue
            
            rollie.play_move(move)
            rollie.try_early_eval()


            rollout_depth += 1
    
        reward = 2 / ( 1+ self.depth + rollout_depth)

        return [reward] if rollie.winner == self.player else [0]


    

        
    def __repr__(self):
        return f"Wins: {self.wins}\nTotal: {self.visits}\n" + str(self.gamestate) + "\n"

