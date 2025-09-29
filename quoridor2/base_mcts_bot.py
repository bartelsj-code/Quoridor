from player import Player
from calcstate import Calcstate
import math, random

class BaseMCTSnode:
    def __init__(self, calcstate, parent, move_from_parent):
        self.state = calcstate
        self.parent = parent
        self.move_from_parent = move_from_parent
        self.N = 0
        self.W = 0.0
        self.children = {}
        self.untried = calcstate.get_legal_moves()
        

    @property
    def q(self):
        return 0.0 if self.N == 0 else self.W / self.N
    
    @property
    def fully_expanded(self):
        return len(self.untried) == 0
    

class BaseMCTSbot(Player):
    def __init__(self, expansions):
        self.expansion_count = expansions
        self.c_uct = 1.414
        self.rollout_cap = 256
        self.player_id = None

    def choose_move(self, gamestate):
        calcstate = Calcstate()
        calcstate.import_gamestate(gamestate)
        self.player_id = calcstate.player_up
        self.max_depth = 0

        root = BaseMCTSnode(calcstate, None, None)

        for iteration in range(self.expansion_count):

            print(f"({iteration}/{self.expansion_count}), {self.max_depth}", end="\r")
            node = root
            depth = 0
            while (not node.state.over) and node.fully_expanded:
                # print(node.state)
                # print(node.untried[-5:])
                depth += 1
                node = self._select_uct(node)
            if depth > self.max_depth:
                self.max_depth = depth
            
            if (not node.state.over) and node.untried:
                move = node.untried.pop(random.randrange(len(node.untried)))
                child_state = node.state.get_clone()
                child_state.play_move(move)
                
                
                child = BaseMCTSnode(child_state, node, move)
                node.children[move] = child
                node = child
                # print(node.state)
                # print(node.untried[-5:])

            value = 1 if self._rollout_to_terminal(node.state) else 0

            self._backprop(node, value)
            
        best_move = max(root.children.items(), key=lambda kv: kv[1].N)[0]


        return best_move
        



    def _select_uct(self, node):
        parent_N = node.N
        c = self.c_uct
        # argmax over Q + c * sqrt(ln(N_parent)/N_child)
        best_child, best_score = None, -1e100
        for move, child in node.children.items():
            q = child.q
            u = c * math.sqrt(max(1.0, math.log(parent_N))) / (1 + child.N)
            score = q + u
            if score > best_score:
                best_score, best_child = score, child
        return best_child


    def _rollout_to_terminal(self, state):
        s: Calcstate = state.get_clone()
        while not s.over:
            moves = s.get_legal_moves()
            if not moves:
                break
            m = random.choice(moves)
            s.play_move(m)
            s.try_early_eval()
        return s.winner == self.player_id
    
    def _backprop(self, node, value_from_me):
        n = node
        while n is not None:
            n.N += 1
            n.W += value_from_me
            n = n.parent
        
            