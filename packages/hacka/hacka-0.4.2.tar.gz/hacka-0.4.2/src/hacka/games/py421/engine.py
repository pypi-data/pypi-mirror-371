#!env python3
"""
HackaGame - Game - Single421 
"""
import sys, os, random

class Engine421() :

    def __init__( self ):
        self.initialize()

    def initialize(self, horizon=3):
        self.horizon= horizon
        dice= self.randomDice([1, 1, 1], ["roll", "roll", "roll"])
        self.state= { "H":self.horizon-1,  "D1":dice[0],  "D2":dice[1],  "D3":dice[2] }
        self.stop= False

    def allStates(self):
        allStates= []
        for h in range( self.horizon ) :
            for i1 in range(1, 7) :
                for i2 in range(1, i1+1) :
                    for i3 in range(1, i2+1) :
                        state= { "H":h,  "D1":i1,  "D2":i2,  "D3":i3 }
                        allStates.append( state )
        return allStates

    def allActions(self):
        allActions= []
        for i1 in [ "keep", "roll" ] :
            for i2 in [ "keep", "roll" ] :
                for i3 in [ "keep", "roll" ] :
                    action= { "A1":i1,  "A2":i2, "A3":i3 }
                    allActions.append( action )
        return allActions

    def allActionsStr(self):
        allActions= []
        for i1 in [ "keep", "roll" ] :
            for i2 in [ "keep", "roll" ] :
                for i3 in [ "keep", "roll" ] :
                    action= '-'.join( [i1, i2, i3] )
                    allActions.append( action )
        return allActions

    def stateDico(self):
        return self.state
    
    def turn(self):
        return self.state["H"]

    def dices(self):
        return [self.state["D1"],  self.state["D2"],  self.state["D3"]]

    def setOnStateDico(self, state):
        self.state= state

    def stateStr(self):
        return str(self.state["H"]) +"-"+ str(self.state["D1"]) +"-"+ str(self.state["D2"]) +"-"+ str(self.state["D3"])

    def setOnStateStr(self, state_str):
        values= [ int(x_str) for x_str in state_str.split("-") ]
        self.setOnStateDico({ "H":values[0],  "D1":values[1],  "D2":values[2],  "D3":values[3] })

    def isEnded(self):
        return self.stop or self.state["H"] == 0

    def actionFromStr(self, act_str):
        values= act_str.split("-")
        for i in [0, 1, 2] :
            values[i]= "keep" if values[i] in ["keep", "k"] else "roll"
        return { "A1":values[0],  "A2":values[1],  "A3":values[2] }

    def actionToStr(self, act):
        return act["A1"] +"-"+ act["A2"] +"-"+ act["A3"]

    def isActionStr(self, act_str):
        values= act_str.split("-")
        ok= len(values) == 3
        for a in values :
            if a not in ["keep", "k", "roll", "r"] :
                ok= False 
        return ok
    

    def scoreDices(self, dices):
        return self.score( { die:face for die, face in zip( ["D1", "D2", "D3"], dices ) } )

    def currentScore(self):
        return self.score( self.stateDico() )
    
    def score(self, state):
        if state["D1"] == 0 and state["D2"] == 0 and state["D3"] == 0 : 
            return 0
        
        if state["D1"] == 4 and state["D2"] == 2 and state["D3"] == 1 : 
            return 800

        if state["D1"] == 1 and state["D2"] == 1 and state["D3"] == 1 : 
            return 600

        if state["D2"] == 1 and state["D3"] == 1 : 
            return 400 +state["D1"]

        if state["D2"] == state["D1"] and state["D3"] == state["D1"] : 
            return 300 + state["D1"]

        if state["D2"] == state["D1"]-1 and state["D3"] == state["D1"]-2 : 
            return 200 + state["D1"]

        if state["D1"] == 2 and state["D2"] == 2 and state["D3"] == 1 : 
            return 0

        return 100 + state["D1"]

    def randomDice(self, dice, act):
        new_dice= []
        for die, act in zip(dice, act) :
            if act == "roll" or act == "r" :
                new_dice.append( random.choice( range(1,7) ) )
            else :
                new_dice.append(die)
        new_dice.sort(reverse=True)
        return new_dice

    def randomTransition(self, action):
        if action["A1"] == "keep" and  action["A2"] == "keep" and  action["A3"] == "keep" :
           self.stop= True
        if self.stop or self.state["H"] == 0 :
            self.state["H"]= 0
            return self.state
        dice=[ self.state["D1"], self.state["D2"], self.state["D3"] ]
        diceAct= [ action["A1"], action["A2"], action["A3"] ]
        dice= self.randomDice(dice, diceAct)
        return { "H":self.state["H"]-1,  "D1":dice[0],  "D2":dice[1],  "D3":dice[2] }

    def step(self, actionStr):
        action= { "A1": 'keep',  "A2": 'keep',  "A3": 'keep' }
        if self.isActionStr( actionStr ) :
            action= self.actionFromStr( actionStr )
        else :
            print('WARNING: default action')
        # Get a random transition
        horizon= self.state["H"]
        self.state= self.randomTransition(action)
        # Compute the associated reward
        if horizon != 0 and (self.stop or self.state["H"] == 0) :
            return self.score( self.state )
        else :
            return 0

# set-
if __name__ == '__main__' :
    main()
