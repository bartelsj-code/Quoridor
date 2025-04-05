from board import Board
from player import Player
from bot1 import Bot


class Game:
    def __init__(self):
        self.players = [
            Bot(),
            Bot(),
            Bot(),
            # Player(),
            # Player(),
        ] 
        self.board = Board(len(self.players))

    def play(self):
        done = False
        for i in range(100):
            for player in self.players:
                move = player.choose_move(self.board.state)
                if self.board.execute_move(move):
                    done = True
                    break
                
            if done:
                print(f"game over after {i} turns")
                break
        print(self.board)
        

        pass


if __name__ == "__main__":
    for i in range(1):
        g = Game()
        g.play()