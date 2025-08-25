#!env python3
"""
HackaGame - Game - Single421 
"""
import sys

from ... import py as hkpy
from . import engine as ge

# Modes:
#Game2Players= mode2players.Game

class GameSolo( hkpy.AbsSequentialGame ) :

    def __init__(self):
        super().__init__(1)
    
    # Game interface :
    def initialize(self):
        # Initialize a new game (not returning anything)
        self.engine= ge.Engine421()
        self.engine.initialize()
        self.score= 0
        return hkpy.Pod().fromLists( ['Game', '421-Solo'] )
    
    def playerHand( self, iPlayer ):
        # Return the game elements in the player vision (an AbsGamel)
        gameElements= hkpy.Pod().fromLists( ['Game', '421-Solo'] )
        gameElements.append( hkpy.Pod().fromLists( ['Horizon'], [ self.engine.turn() ] ) )
        gameElements.append( hkpy.Pod().fromLists( ['Dices'],
                                        self.engine.dices(),
                                        [ self.engine.currentScore() ] ) )
        return gameElements

    def applyPlayerAction( self, iPlayer, action ):
        # Apply the action choosen by the player iPlayer. return a boolean at True if the player terminate its actions for the current turn.
        self.score= self.engine.step( action )
        return True

    def isEnded( self ):
        # must return True when the game end, and False the rest of the time.
        return self.engine.isEnded()

    def playerScore( self, iPlayer ):
        # return the player score for the current game (usefull at game ending)
        return self.score


class GameDuo( hkpy.AbsSequentialGame ) :

    # Constructor: 
    def __init__(self):
        super().__init__(2)
        self._startHorizon= 3
        self._refDices= [0, 0 ,0]
        self._lastPlayer= 0

    # Accessors: 
    def refDices(self) :
        return self._refDices

    def initialize(self):
        # Initialize a new game (not returning anything)
        self.engine= ge.Engine421()
        self.engine.initialize(self._startHorizon)
        self._refDices= [0, 0 ,0]
        self._lastPlayer= 0
        return hkpy.Pod().fromLists( ['Game', '421-Duo'] )

    def playerHand( self, iPlayer ):
        if (self._lastPlayer == 0 and iPlayer == 1) or (self._lastPlayer != 0 and iPlayer == 2) :
            return self.currentPlayerHand()
        else :
            return self.opponentPlayerHand()

    def currentPlayerHand( self ):
        # Return the game elements in the player vision (an AbsGamel)
        gameElements= hkpy.Pod().fromLists( ['Game', '421-Duo'] )
        gameElements.append( hkpy.Pod().fromLists( ['Horizon'], [ self.engine.turn() ] ) )
        gameElements.append( hkpy.Pod().fromLists( ['Dices'],
                                        self.engine.dices(),
                                        [ self.engine.currentScore() ] 
                                    )
                            )
        gameElements.append( hkpy.Pod().fromLists( ['Opponent'],
                                       self.refDices(),
                                       [ self.engine.scoreDices( self.refDices() ) ]
                                    )
                            )
        return gameElements
    
    def opponentPlayerHand( self ):
        # Return the game elements in the player vision (an AbsGamel)
        gameElements= hkpy.Pod().fromLists( ['Game', '421-Duo'] )
        gameElements.append( hkpy.Pod().fromLists( ['Horizon'], [ 0 ] ) )
        gameElements.append( hkpy.Pod().fromLists( ['Dices'],
                                       self.refDices(),
                                       [ self.engine.scoreDices( self.refDices() ) ]
                                    )
                            )
        gameElements.append( hkpy.Pod().fromLists( ['Opponent'],
                                        self.engine.dices(),
                                        [ self.engine.currentScore() ] 
                                    )
                            )
        return gameElements
    
    def applyPlayerAction( self, iPlayer, action ):
        # Apply the action choosen by the player iPlayer. return a boolean at True if the player terminate its actions for the current turn.
        self.engine.step( action )
        if iPlayer == 1 and self.engine.isEnded() :
            self._refDices= [ d for d in self.engine.dices() ]
            self.engine.initialize( self._startHorizon-self.engine.turn() )
            self._lastPlayer= 1
            return True
        elif self.engine.isEnded() :
            self._lastPlayer= 2
            return True
        return False

    def isEnded( self ):
        # must return True when the game end, and False the rest of the time.
        return self._lastPlayer == 2 and self.engine.isEnded()

    def playerScore( self, iPlayer ):
        # Get appropriate combinaison:
        if iPlayer == 1: 
            ipCombi= self.refDices()
            opCombi= self.engine.dices()
        else :
            ipCombi= self.engine.dices()
            opCombi= self.refDices()
        
        # Compute scores:
        ipScore= self.engine.score( { "D1": ipCombi[0], "D2": ipCombi[1], "D3": ipCombi[2] } )
        opScore= self.engine.score( { "D1": opCombi[0], "D2": opCombi[1], "D3": opCombi[2] } )

        # Compare:
        if ipScore > opScore :
            return 1
        elif ipScore < opScore :
            return -1
        else :
            return 0
