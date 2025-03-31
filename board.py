from gamestate import Gamestate

class Board:
    def __init__(self, player_count):
        self.state = Gamestate()
        self.state.set_up_as_start(player_count)

    def execute_move(self, move):
        self.state.play_move(move)
        print(self)
        if self.state.over:
            return True
        

    def __str__(self):
        return "Board:\n" + str(self.state)
        