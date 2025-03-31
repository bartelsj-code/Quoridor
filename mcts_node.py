from gamestate import Gamestate
from random import choice
import math

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

    def rollout(self):
        rollie = self.gamestate.get_clone()
        while not rollie.over:
            move = choice(rollie.get_legal_moves())
            rollie.play_move(move)
        if rollie.winner == self.player:
            return True
        return False
    

        
    def __repr__(self):
        return f"Wins: {self.wins}\nTotal: {self.visits}\n" + str(self.gamestate) + "\n"

    