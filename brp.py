from pmc import *
from sympy import *

### les parametres ###

global nbstate,targets
nbstate=0
target=State(nbstate)
pK=Symbol('p')
pL=Symbol('q')
def brp(N,MAX):
    global nbstate,targets
    HState={}
    nbstate=0
    target=State(nbstate)
    nbstate+=1



    def getState(s,srep,nrtr,i,bs,s_ab,fs,ls,r,rrep,fr,lr,br,r_ab,recv,T,k,l):
        global nbstate,targets
        statev=HState.get((s,srep,nrtr,i,bs,s_ab,fs,ls,r,rrep,fr,lr,br,r_ab,recv,T,k,l),None)
        if statev!=None:
            return statev
        elif s==5:
            return target
        else:
            ns=State(nbstate)
            nbstate+=1
            HState[(s,srep,nrtr,i,bs,s_ab,fs,ls,r,rrep,fr,lr,br,r_ab,recv,T,k,l)]=ns
            return ns

    todo=set()
    initial=(0,0,0,0,false,false,false,false,0,0,false,false,false,false,false,false,0,0)
    todo.add(initial)
    done=set()
    transparam=[]
    transprob=[]
    while len(todo)>0:
        elem=todo.pop()
        (s,srep,nrtr,i,bs,s_ab,fs,ls,r,rrep,fr,lr,br,r_ab,recv,T,k,l)=elem
        done.add(elem)
        cs=getState(*elem)
        #new file
        if (s==0 and not T):
            nextelem=(1,0,nrtr,1,bs,s_ab,fs,ls,r,rrep,fr,lr,br,r_ab,recv,true,k,l)
            ns=getState(*nextelem)
            transprob+=[TransProba(cs,1.0,ns)]
            if nextelem not in done:
                todo.add(nextelem)
        #aF 1
        if s==1 and k==0:
            nextelem1=(2,srep,0,i,s_ab,s_ab,i==1,i==N,r,rrep,fr,lr,br,r_ab,recv,T,1,l)
            nextelem2=(2,srep,0,i,s_ab,s_ab,i==1,i==N,r,rrep,fr,lr,br,r_ab,recv,T,2,l)
            ns1=getState(*nextelem1)
            ns2=getState(*nextelem1)
            transparam+=[TransParam(cs,pK,ns1),TransParam(cs,1-pK,ns2)]
            if nextelem1 not in done:
                todo.add(nextelem1)
            if nextelem2 not in done:
                todo.add(nextelem2)

        #aB
        if s==2 and l==1:
            nextelem=(4,srep,nrtr,i,bs,not s_ab,fs,ls,r,rrep,fr,lr,br,r_ab,recv,T,k,0)
            ns=getState(*nextelem)
            transprob+=[TransProba(cs,1.0,ns)]
            if nextelem not in done:
                todo.add(nextelem)

        #TO_Msg
        if s==2 and k==2:
            nextelem=(3,srep,nrtr,i,bs,s_ab,fs,ls,r,rrep,fr,lr,br,r_ab,recv,T,0,l)
            ns=getState(*nextelem)
            transprob+=[TransProba(cs,1.0,ns)]
            if nextelem not in done:
                todo.add(nextelem)

        #TO_Ack
        if s==2 and l==2:
            nextelem=(3,srep,nrtr,i,bs,s_ab,fs,ls,r,rrep,fr,lr,br,r_ab,recv,T,k,0)
            ns=getState(*nextelem)
            transprob+=[TransProba(cs,1.0,ns)]
            if nextelem not in done:
                todo.add(nextelem)

        #aF 2
        if s==3 and nrtr<MAX and k==0:
            nextelem1=(2,srep,nrtr+1,i,s_ab,s_ab,i==1,i==N,r,rrep,fr,lr,br,r_ab,recv,T,1,l)
            nextelem2=(2,srep,nrtr+1,i,s_ab,s_ab,i==1,i==N,r,rrep,fr,lr,br,r_ab,recv,T,2,l)
            ns1=getState(*nextelem1)
            ns2=getState(*nextelem1)
            transparam+=[TransParam(cs,pK,ns1),TransParam(cs,1-pK,ns2)]
            if nextelem1 not in done:
                todo.add(nextelem1)
            if nextelem2 not in done:
                todo.add(nextelem2)

        #[] sender 1
        if s==3 and nrtr==MAX and i<N:
            nextelem=(5,1,nrtr,i,bs,s_ab,fs,ls,r,rrep,fr,lr,br,r_ab,recv,T,k,l)
            ns=getState(*nextelem)
            transprob+=[TransProba(cs,1.0,ns)]
            if nextelem not in done:
                todo.add(nextelem)

        #[] sender 2
        if s==3 and nrtr==MAX and i==N:
            nextelem=(5,2,nrtr,i,bs,s_ab,fs,ls,r,rrep,fr,lr,br,r_ab,recv,T,k,l)
            ns=getState(*nextelem)
            transprob+=[TransProba(cs,1.0,ns)]
            if nextelem not in done:
                todo.add(nextelem)

        #[] sender 3
        if s==4 and i<N:
            nextelem=(1,srep,nrtr,i+1,bs,s_ab,fs,ls,r,rrep,fr,lr,br,r_ab,recv,T,k,l)
            ns=getState(*nextelem)
            transprob+=[TransProba(cs,1.0,ns)]
            if nextelem not in done:
                todo.add(nextelem)

        #[] sender 4
        if s==4 and i==N:
            nextelem=(0,3,nrtr,i,bs,s_ab,fs,ls,r,rrep,fr,lr,br,r_ab,recv,T,k,l)
            ns=getState(*nextelem)
            transprob+=[TransProba(cs,1.0,ns)]
            if nextelem not in done:
                todo.add(nextelem)

        #aG 1
        if r==0 and k==1:
            nextelem=(s,srep,nrtr,i,bs,s_ab,fs,ls,1,rrep,fs,ls,bs,r_ab,T,T,0,l)
            ns=getState(*nextelem)
            transprob+=[TransProba(cs,1.0,ns)]
            if nextelem not in done:
                todo.add(nextelem)

        #aG 2
        if r==4 and k==1:
            nextelem=(s,srep,nrtr,i,bs,s_ab,fs,ls,2,rrep,fs,ls,bs,r_ab,T,T,0,l)
            ns=getState(*nextelem)
            transprob+=[TransProba(cs,1.0,ns)]
            if nextelem not in done:
                todo.add(nextelem)

        #[] receiver 1
        if r==1:
            nextelem=(s,srep,nrtr,i,bs,s_ab,fs,ls,2,rrep,fr,lr,br,br,recv,T,k,l)
            ns=getState(*nextelem)
            transprob+=[TransProba(cs,1.0,ns)]
            if nextelem not in done:
                todo.add(nextelem)

        #[] receiver 2
        if r==2 and r_ab==br and fr and not lr:
            nextelem=(s,srep,nrtr,i,bs,s_ab,fs,ls,3,1,fr,lr,br,r_ab,recv,T,k,l)
            ns=getState(*nextelem)
            transprob+=[TransProba(cs,1.0,ns)]
            if nextelem not in done:
                todo.add(nextelem)
        
        #[] receiver 3
        if r==2 and r_ab==br and not fr and not lr:
            nextelem=(s,srep,nrtr,i,bs,s_ab,fs,ls,3,2,fr,lr,br,r_ab,recv,T,k,l)
            ns=getState(*nextelem)
            transprob+=[TransProba(cs,1.0,ns)]
            if nextelem not in done:
                todo.add(nextelem)

        #[] receiver 4
        if r==2 and r_ab==br and not fr and lr :
            nextelem=(s,srep,nrtr,i,bs,s_ab,fs,ls,3,3,fr,lr,br,r_ab,recv,T,k,l)
            ns=getState(*nextelem)
            transprob+=[TransProba(cs,1.0,ns)]
            if nextelem not in done:
                todo.add(nextelem)
        #aA 1
        if r==2 and not (r_ab==br) and l==0:
            nextelem1=(s,srep,nrtr,i,bs,s_ab,fs,ls,4,rrep,fr,lr,br,r_ab,recv,T,k,1)
            nextelem2=(s,srep,nrtr,i,bs,s_ab,fs,ls,4,rrep,fr,lr,br,r_ab,recv,T,k,2)
            ns1=getState(*nextelem1)
            ns2=getState(*nextelem1)
            transparam+=[TransParam(cs,pL,ns1),TransParam(cs,1-pL,ns2)]
            if nextelem1 not in done:
                todo.add(nextelem1)
            if nextelem2 not in done:
                todo.add(nextelem2)
        #aA 2
        if r==3 and l==0:
            nextelem1=(s,srep,nrtr,i,bs,s_ab,fs,ls,4,rrep,fr,lr,br,not r_ab,recv,T,k,1)
            nextelem2=(s,srep,nrtr,i,bs,s_ab,fs,ls,4,rrep,fr,lr,br,not r_ab,recv,T,k,2)
            ns1=getState(*nextelem1)
            ns2=getState(*nextelem1)
            transparam+=[TransParam(cs,pL,ns1),TransParam(cs,1-pL,ns2)]
            if nextelem1 not in done:
                todo.add(nextelem1)
            if nextelem2 not in done:
                todo.add(nextelem2)

        #SyncWait
        if ( s==6) and (r==0 or r==5 or r==4):
            if s==5:
                news=6
                news_ab=s_ab
            else:
                news=0
                news_ab=false
            if r==0:
                newr=0
                newrrep=rrep
            elif r==5:
                newr=0
                newrrep=0
            elif ls:
                newr=5
                newrrep=rrep
            else:
                newr=5
                newrrep=4
            nextelem=(news,srep,nrtr,i,bs,news_ab,fs,ls,newr,newrrep,fr,lr,br,r_ab,recv,T,k,l)
            ns=getState(*nextelem)
            transprob+=[TransProba(cs,1.0,ns)]
            if nextelem not in done:
                todo.add(nextelem)

    pmc=PMC(nbstate,[pL,pK])
    pmc.setInitial(getState(*initial))
    pmc.setTarget(target)
    for trans in transparam:
        pmc.addParamTrans(trans)
    for trans in transprob:
        pmc.addProbTrans(trans)

    return pmc


