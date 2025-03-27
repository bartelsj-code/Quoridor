class GSSquare:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.occupant = None
        self.neighbors = []

    def repr(self):
        if self.occupant == None:
            return " "
        
        