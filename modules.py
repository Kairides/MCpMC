from sympy import *

def copyDict(d):
    nd={}
    for a,b in d.items():
        nd[a]=b
    return nd


class Module:
    stateInit={}
    stateMin={}
    stateMax={}
    trans=[]
    
    stateValu={}
    
    subs={}
    
    def __init__(self,name):
        self.name=name

    def addStateInit(self,s,min,max,init):
        self.stateMin[s]=min
        self.stateMax[s]=max
        self.stateInit[s]=init
        self.stateValu[s]=init

    def addState(self,name,min,max):
        self.addStateInit(name,min,max,min)

    def addTrans(self,name,cond,outcom):
        self.trans+=[[name,cond,outcom]]

    def reinit(self):
        self.stateValu=copyDict(self.stateInit)
    
    def eval(self,e,subGlobal):
        sub={}
        e.evalf(subs=self.stateValu).evalf(subs=subGlobal)

    def getPos(self,subGlobal):
        res=[]
        for i in range(0,len(self.trans)):
            name,cond,outcom=self.trans[i]
            if cond.subs(subGlobal).subs(self.stateValu):
                res+=[[name,cond,outcom]]
        return res

    def copy(self,name):
        mod=Module(name)
        mod.stateInit=copyDict(self.stateInit)
        mod.stateMin=copyDict(self.stateMin)
        mod.stateMax=copyDict(self.stateMax)
        mod.stateValu=copyDict(self.stateValu)
        mod.trans=[]
        


        for i in range(0,len(self.trans)):
            name,cond,outcom=self.trans[i]
            mod.addTrans(name,cond,list(outcom))
        return mod

    def replace(self,n1,n2):
        if n1 in self.stateInit:
            self.stateInit[n2]=self.stateInit[n1]
            del self.stateInit[n1]
            self.stateValu[n2]=self.stateValu[n1]
            del self.stateValu[n1]
            self.stateMin[n2]=self.stateMin[n1]
            del self.stateMin[n1]
            self.stateMax[n2]=self.stateMax[n1]
            del self.stateMax[n1]
        nt=[]
        for i in range(0,len(self.trans)):
            name,cond,outcom=self.trans[i]
            if name==n1:
                nm=n2
            else:
                nm=name
            no=[]
            for j in range(0,len(outcom)):
                p,up=outcom[j]
                nup={}
                for a,b in up.items():
                    try:
                        na=a.subs(n1,n2)
                    except:
                        na=a
                    try:
                        nb=b.subs(n1,n2)
                    except:
                        nb=b
                    nup[na]=nb
                try:
                    no+=[[p.subs(n1,n2),nup]]
                except:
                    no+=[[p,nup]]
            try:
                nt+=[[nm,cond.subs(n1,n2),no]]
            except:
                nt+=[[nm,cond,no]]
        self.trans=nt

    def setInit(self,n,v):
        if n in self.stateInit:
            self.stateInit[n]=v
            self.stateInit[n]=v







class PmcModules:
    
    param=[]
    varGlobalInit={}
    varGlobalMin={}
    varGlobalMax={}
    varGlobalValu={}
    modules=[]
    
    rewA={}

    def __init__(self):
        pass

    def addParam(self,param):
        self.param+=[param]

    def addGlobalInit(self,s,min,max,init):
        self.varGlobalInit[s]=init
        self.varGlobalValu[s]=init
        self.varGlobalMin[s]=min
        self.varGlobalMax[s]=max

    def addGlobal(self,name,min,max):
        self.addGlobalInit(name,min,max,min)

    def addModule(self,mod):
        self.modules+=[mod]

    def reinit(self):
        self.varGlobalValu=copyDict(self.varGlobalInit)
        for mod in self.modules:
            mod.reinit()

    def getPos(self):
        res=[]
        for mod in self.modules:
            res+=[mod.getPos(self.varGlobalValu)]
        return res

    def getModule(self,name):
        for mod in self.modules:
            if mod.name==name:
                return mod

    def setInit(self,n,v):
        if n in self.varGlobalValu:
            self.varGlobalValu[n]=v
        else:
            for mod in self.modules:
                mod.setInit(n,v)

    def rewardAct(self,name):
        if name in self.rewA:
            return self.rewA[name]
        else:
            return 0

    def rewardState(self):
        return 0
