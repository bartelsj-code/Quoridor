from player import Player
from random import choice, shuffle
from mcts_node import MctsNode as MN

class Bot(Player):
    def choose_move(self, gamestate):
        root = MN(gamestate, gamestate.player_up)
        root.get_moves()
        print(root.get_player())
        shuffle(root.untried_moves)
        curr = root
        calcs = 1000
        bar_length = 30
        bar_character = "#"
        for i in range(calcs):
            chain = []
            

            #selection
            while curr.fully_expanded:
                curr = curr.select_child(curr.visits, 1.41)
                chain.append((curr.get_player(), curr.reached_by))
                
            #expansion
            
            if not curr.gamestate.over:
                child = curr.spawn_child()
                
                # print(child)
                # simulation
                results = child.rollout_single()

                contrib = sum(results)
                num = len(results)
            else:
                contrib = 1 if curr.gamestate.winner == gamestate.player_up else 0
                num = 1
            

            # print([(c.wins, c.visits) for c in root.children])
            #backprop
            curr = child
            chain.append((curr.get_player(), curr.reached_by))
            
            while True:
                curr.visits += num
                curr.wins += contrib
                if curr == root:
                    break
                curr = curr.parent

            if i % 50 == 0:
                best_child = max(root.children, key=lambda child: child.visits)
            print(f"[{bar_character*int((i/calcs)*bar_length)}{(bar_length-int((i/calcs)*bar_length))*' '}] {i}/{calcs} ---- win_confidence: {100*best_child.wins/max(best_child.visits,1):.2f}%       best: {best_child.reached_by}, {best_child.wins/best_child.visits:.2f} {chain[:min(len(chain),5)]}          ", end='\r')
        
        best_child = max(root.children, key=lambda child: child.visits)
        print(f"[{bar_character*int((calcs/calcs)*bar_length)}{(bar_length-int((i/calcs)*bar_length))*' '}] {calcs}/{calcs} ---- win_confidence: {100*root.wins/max(root.visits,1):.2f}%       best: {best_child.reached_by}, {best_child.wins/best_child.visits:.2f}                                                         ", end='\r')
        return best_child.reached_by
