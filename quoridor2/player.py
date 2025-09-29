from gamestate import Gamestate
from utils import get_display_string_pl
from random import choice

class Player:
    def get_move(self, gamestate):
        move = self.choose_move(gamestate)
        return move
        
    def choose_move(self, gamestate):
        move = choice(gamestate.get_legal_moves())
        return move
    
        