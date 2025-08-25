"""
HackaGame player interface 
"""
import os
from ... import py as hk
from .grid import playerSymbols, Grid

# Script
def main() :
    player= Interface()
    player.takeASeat()

class Interface(hk.AbsPlayer) :

    def __init__(self):
        super().__init__()
        self.grid= Grid()
        self.playerId= 0
        
    # Player interface :
    def wakeUp(self, playerId, numberOfPlayers, gamePod):
        self.playerId= playerId
        assert( gamePod.word() == 'Connect4')
        # Reports:
        print( f'---\nwake-up player-{playerId} ({numberOfPlayers} players) - dimention: {gamePod.integer()}')

    def perceive(self, gameState):
        # update the game state:
        self.grid.initializeFrom( gameState )
        os.system("clear")
        print( self.grid )
        print( "You: " + playerSymbols[self.playerId] )

    def decide(self):
        action = input('Enter your action: ')
        return action
    
    def sleep(self, result):
        print( f'---\ngame end\nresult: {result}')

# Script :
if __name__ == '__main__' :
    main()