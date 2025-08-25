#!env python3
"""
HackaGame - Game - TicTacToe 
"""
from . import GameTTT
from ...py.command import Command, Option

# script :
if __name__ == '__main__' :
    # Commands:
    cmd= Command(
            "start-server",
            [
                Option( "port", "p", default=1400 ),
                Option( "number", "n", 2, "number of games" )
            ],
            (
                "star a server fo gameTicTactoe on the machin. "
                "ARGUMENTS refers to game mode: classic or ultimate."
            )
        )
    cmd.process()

    if cmd.ready() :
        if cmd.argument() == "ultimate" :
            game= GameTTT( "ultimate" )
        else :
            game= GameTTT( "classic" )
    else :
        print( cmd.help() )
        exit()

    game.start( cmd.option("number"), cmd.option("port") )
