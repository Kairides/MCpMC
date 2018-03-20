from typing import NewType

State = NewType('State', int)

class TransProba:
    source=0
    dest=0
    proba=0.0
    def __init__(self,s:State,p:float,d:State):
        self.source=s
        self.dest=d
        self.proba=p

class TransParam:
    source=0
    dest=0
    proba=0.0
    def __init__(self,s:State,p,d:State):
        self.source=s
        self.dest=d
        self.proba=p

class PMC:
    
    def __init__(self,nbstates,param):
        self.nbStates=nbstates                      #nombre d'etat
        self.trans=[[]]*nbstates                    #list of list of transitions
        self.paramters=param                        #list of all parameters
    
    def addProbTrans(self,t:TransProba):
        if t.source<self.nbStates:
            self.trans[t.source]=list(self.trans[t.source])+[t]
        else:
            print("wrong id (greater than number of states) for probabilist trans")
            1/0

    def addParamTrans(self,t:TransParam):
        if t.source<self.nbStates:
            self.trans[t.source]=[t]+list(self.trans[t.source])
        else:
            print("wrong id (greater than number of param states) for param trans")
            1/0

    def setInitial(self,s):
        self.initial=s

    def setTarget(self,t):
        self.target=t

