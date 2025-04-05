from gamestate import Gamestate
from game import Game
import cProfile
import pstats

if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()  
    
    g= Game()
    g.play()
    profiler.disable()  
    stats = pstats.Stats(profiler).sort_stats('cumulative')
    stats.print_stats(10)