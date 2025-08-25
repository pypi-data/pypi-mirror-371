#!env python3
"""
HackaGames - Game - TicTacToe
"""
import os, sys


from ... import py as hk
from . import engine

class GameTTT( hk.AbsSequentialGame ):

    # Constructor
    def __init__(self, mode="classic"):
        super().__init__(2)
        self.mode= mode

    # Game interface :
    def initialize(self):
        if self.mode == "ultimate" :
            self.grid= engine.Ultimate()
        else :
            self.grid= engine.Classic()
        self.count= 4
        return hk.Pod().fromLists( ["TicTacToe", self.grid.name()] )

    def playerHand( self, iPlayer ):
        # Return the game elements in the player vision (a POD)
        pod= self.grid.asPod()
        return pod

    def applyPlayerAction( self, iPlayer, action ):
        # Apply the action choosen by the player iPlayer. return a boolean at True if the player terminate its actions for the current turn.
        ok= self.grid.apply( iPlayer, action )
        if ok or self.count < 1 :
            self.count= 4
            return True
        self.count-= 1
        return False

    def isEnded( self ):
        # must return True when the game end, and False the rest of the time.
        return self.grid.isEnded()

    def playerScore( self, iPlayer ):
        # If winning
        if self.grid.isWinning(iPlayer) :
            return 1
        # get openent number
        iOponent= 1
        if iPlayer == 1 :
            iOponent= 2
        # if loosing
        if self.grid.isWinning(iOponent) :
            return -1
        # else
        return 0
