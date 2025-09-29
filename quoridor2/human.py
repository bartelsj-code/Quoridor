from player import Player

class Human(Player):
    def get_move(self, gamestate):

        move = self.choose_move(gamestate)
        return move
        
    def choose_move(self, gamestate):
        confirmed = False
        while not confirmed:
            while True:
                choice = str_to_move(input("enter move: "))
                if choice == "o":
                    print(gamestate.get_legal_moves())
                else:
                    if choice in gamestate.get_legal_moves():
                        break
                    print(f"{choice} is not a legal move. For options enter \"o\" ")
            g = gamestate.get_clone()
            g.play_move(choice)
            print(g)
            i = input("to confirm, hit enter, otherwise anything else")
            if i == "":
                break
        return choice

def str_to_move(str1):
    try:
        if str1 == "o":
            return str1
        components = str1.split(";")
        g = []

        for comp in components:
            g.append(tuple([int(val) for val in comp.split(",")]))
        if len(g) > 1:
            return tuple(g)
        return g[0]
    except:
        return None
    
