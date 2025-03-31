from player import Player
from random import choice
from mcts_node import MctsNode as MN

class Bot(Player):
    def choose_move(self, gamestate):
        root = MN(gamestate, gamestate.player_up)
        root.get_moves()
        curr = root
        calcs = 600
        bar_length = 25
        bar_character = "#"
        for i in range(calcs):
            

            #selection
            while curr.fully_expanded:
                curr = curr.select_child(curr.visits, 1.03)
                
            #expansion
            
            if not curr.gamestate.over:
                child = curr.spawn_child()
                # print(child)
                # simulation
                results = child.rollout()
                contrib = sum(results)
                num = len(results)
            else:
                contrib = 1 if curr.gamestate.winner == gamestate.player_up else 0
                num = 1
            


            #backprop
            while True:
                curr.visits += num
                curr.wins += contrib
                if curr == root:
                    break
                curr = curr.parent

            best_child = max(root.children, key=lambda child: child.visits)
            print(f"[{bar_character*int((i/calcs)*bar_length)}{(bar_length-int((i/calcs)*bar_length))*' '}] {i}/{calcs} ---- win_confidence: {100*root.wins/max(root.visits,1):.2f}%       best: {best_child.reached_by}  ", end='\r')
        
        
        return best_child.reached_by
