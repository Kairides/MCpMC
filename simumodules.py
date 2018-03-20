import modules
import random

def typennotexp(e):
    return type(e)==int or type(e)==float

def sim(l,pmc):# l =length of exec, pmc = pmc to simulate
    pmc.reinit()
    end=False
    step=0
    r=0
    prob=1
    while step<l and not end :
        step+=1
        t=pmc.getPos()
        for i in range(0,len(t)):
            if len(t[i])>1:
                raise Exception("several action possible")
            elif len(t[i])>0:
                tr=t[i][0]
                name,cond,outcom=tr
                norma=sum(not typennotexp(e[0]) for e in outcom)
                if norma>0:
                    np=1/norma
                threshold=random.random()
                c=0
                j=0
                while j<len(outcom) and c<threshold:
                    v=outcom[j][0]
                    if typennotexp(v):
                        c+=v
                    else:
                        c+=np
                    j+=1
                j-=1
                realprob=outcom[j][0]
                if typennotexp(realprob):
                    unifprob=realprob
                else:
                    unifprob=np
                prob*=realprob/unifprob
#TODO metre a jour les etats
                
                r+=pmc.rewardAct(name)
                r+=pmc.rewardState()
            else:
                end=True

    return prob*r



def simu(l,n,pmc): # l = length of exec, n = number of simu, pmc = pmc to simulate
    r=0
    v=0
    for i in range(0,n):
        print(i)
        y=sim(l,pmc)
        r+=y
        v+=y*y

    estespy=r/n
    estvar=(v/(n-1)-n/(n-1)*estespy**2)**(1/2)
    return [estespy,estvar]
