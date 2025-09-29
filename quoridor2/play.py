from gamestate import Gamestate
from game import Game
import cProfile
import pstats
from random import seed

if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()  
    seed('bagel')
    
    g= Game()
    g.play()
    profiler.disable()  
    stats = pstats.Stats(profiler).sort_stats('cumulative')
    stats.print_stats(20)