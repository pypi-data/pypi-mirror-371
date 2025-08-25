"""
HackaGame - Game - Connect4 
"""
import sys, random

sys.path.insert(1, __file__.split('gameConnect4')[0])
from ... import py as hk
from . import grid

Grid= grid.Grid

class GameConnect4( hk.AbsSequentialGame ) :
    
    # Initialization:
    def __init__(self, nbColumns=7, nbLines=6) :
        super().__init__( numberOfPlayers=2 )
        self._nbColumns= nbColumns
        self._nbLines= nbLines
    
    # Game interface :
    def initialize(self):
        self._grid= Grid( self._nbColumns, self._nbLines )
        return hk.Pod().fromLists( ['Connect4'], [ self._nbColumns, self._nbLines ] )
        
    def playerHand( self, iPlayer ):
        # Return the game elements in the player vision (an AbsGamel)
        return self._grid.asPod()

    def applyPlayerAction( self, iPlayer, action ):
        options= self._grid.possibilities()
        if not action in options :
            action= random.choice( options )
        self._grid.playerPlay( iPlayer, action )
        return True

    def isEnded( self ):
        # must return True when the game end, and False the rest of the time.
        return (self._grid.possibilities() == [] or self._grid.winner() != 0)
    
    def playerScore( self, iPlayer ):
        if self._grid.winner() == iPlayer :
            return 1
        elif self._grid.winner() == 0 :
            return 0
        return -1
