import random, pathlib

"""
HackaGame - Game - Risky 
"""
from ... import py as hk

class Cell():
    # Constructor :
    #--------------
    def __init__(self, population= 1):
        self._population= population
        self._virus= 0

    def copy(self):
        cpy= Cell()
        cpy._population = self._population
        cpy._virus= self._virus
        return cpy

    def initialize(self, population, virus):
        self._population= population
        self._virus= virus
        return self


    def population(self):
        return self._population
    
    def virus(self):
        return self._virus
    
    def setPopulation(self, pop):
        self._population= pop
        return self
    
    def setVirus(self, vir):
        self._virus= vir
        return self
    
    def __str__(self):
        return f"[{self._population}, {self._virus}]"
    
class Engine( hk.AbsSequentialGame ) :

    # Constructor :
    #--------------
    def __init__(self):
        super().__init__(1)
        # Grid:
        self._grid= [[ Cell() ]]
        # Time:
        self._duration= 10
        self._counter= 0

    def copy(self):
        cpy= Engine()
        cpy._grid= []
        for line in self._grid : 
            cpy._grid.append(
                [ c.copy() for c in line ]
            )
        return cpy

    # Pod interface :
    #-----------------
    def asPod( self ):
        # Return the engine elements as Pod
        gamePod= hk.Pod( "Pandemic", str(self._duration), [self._counter] )
        i= 0
        for line in self._grid: 
            linePod= hk.Pod( "Line" )
            for c in line :
                linePod.append( hk.Pod( "Cell", str(i), [c._population, c._virus] ) )
            gamePod.append( linePod )
        return gamePod

    def fromPod( self, enginePod ):
        # rebuilt self from enginePod elements
        self._counter= enginePod.flag(1)
        self._grid= []
        for linePod in enginePod.children() : 
            self._grid.append(
                [ Cell().initialize( c.flag(1), c.flag(2) ) for c in linePod ]
            )
        return self
    # Grid initialization :
    #----------------------
    def initGridFull( self, nbOfLine, lineSize, population= 10 ):
        self._grid= []
        for iLine in range(nbOfLine) : 
            self._grid.append(
                [ Cell(population) for ICell in range(lineSize) ]
            )
        return self
    
    # Game interface :
    #-----------------
    def initialize(self):
        # Initialize a new game (returning the game setting as Pod, a game elements shared with player wake-up)
        self._counter= self._duration
        return  self.asPod()

    def playerHand( self, iPlayer=1 ):
        return self.asPod()

    def applyPlayerAction( self, iPlayer, action ):
        #r= self._applyPlayerAction(iPlayer, action)
        #for i in range( self.size()) :
        #    if self.tileIsArmy(i) and self.tileArmyForce(i) == 0 :
        #        print( f"> What ?\n{self.playerHand(iPlayer)}\n{self.searchMetaActions(iPlayer)}\n{self.actionList}\n{self.playerHand(iPlayer)}>" )
        return True

    def tic( self ):
        # called function at turn end, after all player played its actions. 
        self._counter= max( self._counter-1, 0 )

    def isEnded( self ):
        return (self._counter == 0)
    
    def playerScore( self, iPlayer ):
        return 0

    # Player access :
    #----------------
    def grid(self):
        return self._grid
    
    # Printing :
    #-----------
    def __str__(self):
        lineStrs= [ "|"+ ", ".join( [ str(c) for c in line ] ) +"|" for line in self._grid ]
        return "\n".join( lineStrs )

    # Graph :
    #--------
    def cell( self, line, col ):
        return self._grid[line-1][col-1]
    
    def neighbor( self, line, col ):
        sidecol= col
        if line%2 == 1 :
            sidecol+= -1
        
        return [ [(line-1, sidecol), (line-1, sidecol+1)],
                [(line, col-1), (line, col+1)],
                [(line+1, sidecol), (line+1, sidecol+1)] ]
    
    # Draw :
    #-------
    def draw(self):
        return ""

    def drawSupport(self):
        nbLine= len( self._grid )
        lineSize= len( self._grid[0] )
        support= [ "          0" + "      0".join( str(i+1) for i in range(lineSize) ) ]
        support.append("    ┏━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━┓")
        return support