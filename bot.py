from player import Player
from random import choice
from mcts_node import MctsNode as MN

class Bot(Player):
    def choose_move(self, gamestate):
        root = MN(gamestate, gamestate.player_up)
        root.get_moves()
        curr = root
        calcs = 1500
        bar_length = 80
        bar_character = "#"
        for i in range(calcs):
            print(f"[{bar_character*int((i/calcs)*bar_length)}{(bar_length-int((i/calcs)*bar_length))*' '}] {i}/{calcs} ---- win_confidence: {100*root.wins/max(root.visits,1):.2f}%", end='\r')

            #selection
            while curr.fully_expanded:
                curr = curr.select_child(curr.visits, 1.4)
                
            #expansion
            
            if not curr.gamestate.over:
                child = curr.spawn_child()
                # print(child)
                # simulation
                was_win = child.rollout()
            else:
                was_win = curr.gamestate.winner == gamestate.player_up


            #backprop
            while True:
                curr.visits += 1
                if was_win:
                    curr.wins += 1
                if curr == root:
                    break
                curr = curr.parent
                
        
        best_child = max(root.children, key=lambda child: child.visits)
        return best_child.reached_by
