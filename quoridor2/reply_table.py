from collections import OrderedDict

class OppReplyTable:
    def __init__(self, cap_states = 100000, per_state_cap=6):
        self.cap_states = cap_states
        self.k = per_state_cap
        self.store = OrderedDict()

    def get(self, h):
        '''returns entry for calcstate hash'''
        d = self.store.get(h)
        if d is not None:
            self.store.move_to_end(h)
        return d
    
    def update(self, h, move, R):
        '''updates table entry for calcstate hash and move made based on result'''
        d = self.get(h)
        if d is None:
            if len(self.store) >= self.cap_states:
                self.store.popitem(last=False)
            d = self.store[h] = {}
        n, mu = d.get(move, (0, 0.0))
        n = min(65535, n+1)
        mu = mu + (R - mu) / n
        d[move] = (n, mu)

        if len(d) > self.k:
            worst = sorted(d.items(), key=lambda kv: kv[1][1])[:self.k]
            self.store[h] = dict(worst)