
# Local HackaGame:
from . import interprocess
from tqdm import tqdm

class AbsGame():
    # Constructor
    def __init__(self, numberOfPlayers= 1 ):
        self._numberOfPlayers= numberOfPlayers

    # Game interface :
    def numberOfPlayers(self):
        return self._numberOfPlayers

    # Game interface :
    def initialize(self):
        # Initialize a new game
        # Return the game configuration (as a PodInterface)
        # the returned Pod is given to player's wake-up method
        pass

    def playerHand( self, iPlayer ):
        # Return the game elements in the player vision (an AbsGamel)
        pass

    def applyPlayerAction( self, iPlayer, action ):
        # Apply the action choosen by the player iPlayer. return a boolean at True if the player terminate its actions for the current turn.
        pass

    def tic( self ):
        # called function at turn end, after all player played its actions. 
        pass

    def isEnded( self ):
        # must return True when the game end, and False the rest of the time.
        pass

    def playerScore( self, iPlayer ):
        # return the player score for the current game (usefull at game ending)
        pass
    
    # Process :
    def start(self, numberOfGames= 1, port=1400 ):
        dealer= interprocess.Dealer(port)
        self.startWithDealer(dealer, numberOfGames)
    
    def testPlayer(self, player, numberOfGames= 1, oponents=[] ):
        players= [player]
        players+= oponents
        result= self.launch( players, numberOfGames )
        return result[0]
    
    def test2Players(self, player1, player2, numberOfGames= 1 ):
        return self.launch( [player1, player2], numberOfGames )
    
    def launch(self, players, numberOfGames= 1 ):
        print( f" local games ({numberOfGames})" )
        assert( len(players) == self._numberOfPlayers )
        dealer= interprocess.Local( players )
        self.startWithDealer(dealer, numberOfGames)
        return dealer.results()

    def startWithDealer(self, dealer, numberOfGames):
        print( f'HackaGame: wait for {self._numberOfPlayers} players' )
        dealer.waitForPlayers( self._numberOfPlayers )
        print( f'HackaGame: process {numberOfGames} games' )
        for i in tqdm(range(numberOfGames)) :
            self.play(dealer)
            dealer.changePlayerOrder()
        print( f'HackaGame: stop player-clients' )
        for i in range(1, self._numberOfPlayers+1) :
            dealer.stopPlayer( i )
    
    def play(self, aDealer):
        # Depend on how the players are handled: cf. AbsSequentialGame and AbsSimultaneousGame
        pass

class AbsSequentialGame(AbsGame):
    def play(self, aDealer):
        gameConf= self.initialize()
        aDealer.wakeUpPlayers( gameConf )
        iPlayer= 1
        # player take turns :
        while not self.isEnded() :
            action= aDealer.activatePlayer( iPlayer, self.playerHand(iPlayer) )
            # give a chance to propose a better action :
            while not self.applyPlayerAction( iPlayer, action ) :
                action= aDealer.activatePlayer( iPlayer, self.playerHand(iPlayer) )
            # switch player :
            iPlayer+= 1
            if iPlayer > self._numberOfPlayers :
                self.tic()
                iPlayer= 1
        # conclude the game :
        iPlayer= 1
        while iPlayer <= self._numberOfPlayers :
            aDealer.sleepPlayer( iPlayer, self.playerHand(iPlayer), self.playerScore(iPlayer) )
            iPlayer+= 1

class AbsSimultaneousGame(AbsGame):
    pass
