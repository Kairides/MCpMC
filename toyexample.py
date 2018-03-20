from pmc import *
from sympy import *
######################### pMC used #####################

### les parametres ###

p=Symbol('p')
q=Symbol('q')

## le pmc ##
apmc=PMC(5,[p,q])

#3 etats proba
spr0=State(0)
spr1=State(1)
spr2=State(2)

#2 etats param
spa0=State(3)
spa1=State(4)

#trans proba
apmc.addProbTrans(TransProba(spr1,1.0,spr1))
apmc.addProbTrans(TransProba(spr2,1.0,spr2))
apmc.addProbTrans(TransProba(spr0,0.5,spa0))
apmc.addProbTrans(TransProba(spr0,0.5,spa1))

#trans param
apmc.addParamTrans(TransParam(spa0,p,spr0))
apmc.addParamTrans(TransParam(spa0,q,spa0))
apmc.addParamTrans(TransParam(spa0,1-p-q,spr2))
apmc.addParamTrans(TransParam(spa1,p,spr2))
apmc.addParamTrans(TransParam(spa1,q,spr1))
apmc.addParamTrans(TransParam(spa1,1-p-q,spa1))


#initial and target state
apmc.setInitial(spr0)
apmc.setTarget(spr1)

def toyexample():
    return apmc
