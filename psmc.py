from pmc import *
import random
import math

from sympy import *
########################### Simulation ###################

def simuValu(pmc:PMC,               #the pmc
         t:State,               #target state
         l:int,                 #lenght left to explore
         valu):                 #valuation of the parameters for unification
    s=pmc.initial
    y=1
    while l>=0 and not (s==t):
        l-=1
        r=random.random()
        trans=pmc.trans[s]
        candidate=0
        v=valu(trans[candidate].proba)
        while v<r:
            candidate+=1
            v+=valu(trans[candidate].proba)
        s=trans[candidate].dest
        pa=trans[candidate].proba
        y*=pa/valu(pa)
    if l>=0:
        return y
    else:
        return 0


def simulValu(pmc:PMC,length:int,valu):
    return simuValu(pmc,pmc.target,length,valu)


def monteCarlo(pmc:PMC,                                # the pmc
               length:int,                             # length of execution
               valu,                                   # valuation of parameters for uniformization
               z,                                      # required precision typicaly 1.96 => 95%
               w,                                       # interval width required
               min                                     #minimun number of run
               ):
    minrun=min
    run=0
    numofpos=0
    acury=0
    acurvary=0
    while run<minrun:
        run+=1
        y=simulValu(pmc,length,valu)
        if y!=0:
            acury+=y
            acurvary+=y*y
    estprob=numofpos/run
    estvar=math.sqrt(run*estprob*(1-estprob)/(run-1))
    rw=z*estvar/math.sqrt(run)
    while rw>w:
        for _ in xrange(100):                           # to change if slow
            run+=1
            y=simulValu(pmc,length,valu)
            if y!=0:
                acury+=y
                acurvary+=y*y
        estprob=numofpos/run
        estvar=math.sqrt(run*estprob*(1-estprob)/(run-1))
        rw=z*estvar/math.sqrt(run)
    return [acury,acurvary,run]


def evalProbaParam(pmc:PMC,length,z,w,canoVal,min):
    res=[]
    for valu in canoVal:
        ny,nvar,nbrun=monteCarlo(pmc,length,valu,z,w,min)
        esty=ny/nbrun
        estvar=(nvar/(nbrun-1)-nbrun/(nbrun-1)*esty*esty)**(1/2)
        intConfW=2*z*estvar*(nbrun**(-1/2))
        res+=[[lambdify(pmc.paramters,intConfW),lambdify(pmc.paramters,esty)]]
    def result(x1,x2):
        by=0
        beicw=float("inf")
        for icw,y in res:
            eicw=icw(x1,x2)
            if eicw<beicw:
                beicw=eicw
                by=y(x1,x2)
        return [beicw,by]
    return result

