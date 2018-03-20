import simumodules
import modules
from parser import myparse


pmc=myparse('example/zeroconf.pm')


pmc.rewA['a']=1
pmc.rewA['b']=9

estR,estVar=simumodules.simu(3,3,pmc)

print(estR.subs({pmc.param[0]:0.3,pmc.param[1]:0.3}))
print()



print("salut")
