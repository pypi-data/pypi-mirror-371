"""
HackaGame - Game - Hello 
"""
from . import GameConnect4
from ...py.command import Command, Option

# script :
if __name__ == '__main__' :
    # Define a command interpreter: 2 options: host address and port:
    cmd= Command(
            "start-server",
            [
                Option( "port", "p", default=1400 ),
                Option( "number", "n", 2, "number of games" )
            ],
            (
                "star a server fo gameConnect4 on your machine. "
                "gameConnect4 do not take ARGUMENT."
            ))
    # Process the command line: 
    cmd.process()
    if not cmd.ready() :
        print( cmd.help() )
        exit()

    # Start the player the command line: 
    game= GameConnect4()

    game.start( cmd.option("number"), cmd.option("port") )
