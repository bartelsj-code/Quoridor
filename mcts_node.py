from gamestate import Gamestate
from random import choice,shuffle
import multiprocessing

import math

def rollout_simulation(args):
    gamestate, player = args
    rollie = gamestate.get_clone()
    while not rollie.over:
        move = choice(rollie.get_legal_moves())
        rollie.play_move(move)
    return 1 if rollie.winner == player else 0



class MctsNode:
    def __init__(self, gamestate, player, reached_by=None, parent = None):
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
        shuffle(self.untried_moves)
        
    def select_child(self, parent_visits, c):        
        def utc_value(child):
            if child.visits == 0:
                return float('inf')
            win_rate = child.wins / child.visits
            exploration = c * math.sqrt(math.log(parent_visits)/child.visits)
            return win_rate + exploration
        
        return max(self.children, key=utc_value)

    
    def spawn_child(self):
        move = self.untried_moves.pop()
        if len(self.untried_moves) == 0:
            self.fully_expanded = True
        child = MctsNode(self.gamestate, self.player, move, self)
        
        child.gamestate.play_move(move)
        child.get_moves()
        # print("self", self)
        # print("child", child)
        self.children.append(child)
        
        return child

    def rollout(self, num_rollouts = None):
        if num_rollouts is None:
            num_rollouts = multiprocessing.cpu_count()
        args = [(self.gamestate.get_clone(), self.player) for _ in range(num_rollouts)]
        with multiprocessing.Pool(processes=num_rollouts) as pool:
            results = pool.map(rollout_simulation, args)
        # Sum the wins (each result is 1 for win, 0 for loss)
        return results
    

        
    def __repr__(self):
        return f"Wins: {self.wins}\nTotal: {self.visits}\n" + str(self.gamestate) + "\n"

