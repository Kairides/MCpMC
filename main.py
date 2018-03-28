from math import sqrt
from random import random
#from sys import argv
from parser import myparse
#from modules import mysub
from simumodules import simu
import time
from memory_profiler import profile
#import re
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as colors
import matplotlib.cm as cmx
import sympy

@profile
def toy():
    file = 'example/toy.pm'
    time1 = time.time()
    pmc = myparse(file)
    time2 = time.time()
    print('parsing of %s took %0.3f ms' % (file, (time2-time1)*1000.0))
    num_of_run = 10000
    length_of_run = 100
    time1 = time.time()
    estimated_reward, estimated_variance = simu(length_of_run, num_of_run, pmc)
    time2 = time.time()
    print('the %d simulations took %0.3f ms' % (num_of_run, (time2-time1)*1000.0))
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    f=sympy.lambdify(pmc.param,estimated_reward)
    fv=np.vectorize(f)
    v=sympy.lambdify(pmc.param,estimated_variance)
    vv=np.vectorize(v)
    x = np.arange(0.05, 0.95, 0.01)
    y = np.arange(0.05, 0.95, 0.01)
    X1,Y1=np.meshgrid(x,y)
    X=X1[X1+Y1<0.95]
    Y=Y1[X1+Y1<0.95]
    Z=fv(X,Y)
    C=2*1.96*vv(X,Y)/sqrt(num_of_run)
    plot=ax.scatter(X,Y,Z,c=C)
    ax.set_xlabel('p')
    ax.set_ylabel('q')
    ax.set_zlabel('probability')
    cb=plt.colorbar(plot)
    cb.set_label("IC width")
    plt.savefig('toy_%d.png'%num_of_run)

def toym():
    file = 'example/toymul.pm'
    time1 = time.time()
    pmc = myparse(file)
    time2 = time.time()
    print('parsing of %s took %0.3f ms' % (file, (time2-time1)*1000.0))
    num_of_run = 10000
    length_of_run = 100
    time1 = time.time()
    estimated_reward, estimated_variance = simu(length_of_run, num_of_run, pmc)
    time2 = time.time()
    print('the %d simulations took %0.3f ms' % (num_of_run, (time2-time1)*1000.0))
    def random_val1(q,e):
        random_valuation = {}
        random_valuation[pmc.param[0]]=q
        for i in range(1,len(pmc.param)):
            param=pmc.param[i]
            random_valuation[param] = random()*(1-q)
        return e.subs(random_valuation)
    random_val=np.vectorize(random_val1)
    x=np.arange(0.05, 0.95, 0.05)
    y=random_val(x,estimated_reward)
    e=random_val(x,estimated_variance*1.96/sqrt(num_of_run))
    fig = plt.figure()
    ax=fig.add_subplot(111)
    ax.errorbar(x,y,yerr=e,fmt='o')
    ax.set_xlabel('q')
    ax.set_ylabel('probability for random valuation')
    plt.show()


def nand():
    file = 'example/nand.pm'
    time1 = time.time()
    pmc = myparse(file)
    time2 = time.time()
    print('parsing of %s took %0.3f ms' % (file, (time2-time1)*1000.0))
    num_of_run = 2
    length_of_run = 1000000
    time1 = time.time()
    estimated_reward, estimated_variance = simu(length_of_run, num_of_run, pmc)
    time2 = time.time()
    print('the %d simulations took %0.3f ms' % (num_of_run, (time2-time1)*1000.0))

def nand2():
    file = 'example/nand2.pm'
    time1 = time.time()
    pmc = myparse(file)
    time2 = time.time()
    print('parsing of %s took %0.3f ms' % (file, (time2-time1)*1000.0))
    num_of_run = 1000
    length_of_run = 1000000
    time1 = time.time()
    estimated_reward, estimated_variance = simu(length_of_run, num_of_run, pmc,{pmc.param[0]:0.02,pmc.param[1]:0.9})
    time2 = time.time()
    print('the %d simulations took %0.3f ms' % (num_of_run, (time2-time1)*1000.0))
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    f=sympy.lambdify(pmc.param,estimated_reward)
    fv=np.vectorize(f)
    v=sympy.lambdify(pmc.param,estimated_variance)
    vv=np.vectorize(v)
    x = np.arange(0.05, 0.95, 0.01)
    y = np.arange(0.05, 0.95, 0.01)
    X,Y=np.meshgrid(x,y)
    Z=fv(X,Y)
    C=2*1.96*vv(X,Y)/sqrt(num_of_run)
    plot=ax.scatter(X,Y,Z,c=C.ravel())
    ax.set_xlabel(str(pmc.param[0]))
    ax.set_ylabel(str(pmc.param[1]))
    ax.set_zlabel('probability')
    cb=plt.colorbar(plot)
    cb.set_label("IC width")
    plt.savefig('nand2_%d.png'%num_of_run)

def zeroconf():
    file = 'example/zeroconf.pm'
    time1 = time.time()
    pmc = myparse(file)
    time2 = time.time()
    print('parsing of %s took %0.3f ms' % (file, (time2-time1)*1000.0))
    num_of_run = 10000
    length_of_run = 500
    time1 = time.time()
    estimated_reward, estimated_variance = simu(length_of_run, num_of_run, pmc)#,{pmc.param[0]:0.3,pmc.param[1]:0.3})
    time2 = time.time()
    print('the %d simulations took %0.3f ms' % (num_of_run, (time2-time1)*1000.0))
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    f=sympy.lambdify(pmc.param,estimated_reward)
    fv=np.vectorize(f)
    v=sympy.lambdify(pmc.param,estimated_variance)
    vv=np.vectorize(v)
    x = np.arange(0.15, 0.55, 0.005)
    y = np.arange(0.15, 0.55, 0.005)
    X,Y=np.meshgrid(x,y)
    Z=fv(X,Y)
    C=2*1.96*vv(X,Y)/sqrt(num_of_run)
    plot=ax.scatter(X,Y,Z,c=C.ravel())
    ax.set_xlabel(str(pmc.param[0]))
    ax.set_ylabel(str(pmc.param[1]))
    ax.set_zlabel('Espected value')
    cb=plt.colorbar(plot)
    cb.set_label("IC width")
    plt.savefig('zeroconf_%d.png'%num_of_run)
    plt.show()

def crowd():
    file = 'example/crowds.pm'
    time1 = time.time()
    pmc = myparse(file)
    time2 = time.time()
    print('parsing of %s took %0.3f ms' % (file, (time2-time1)*1000.0))
    num_of_run = 10000
    length_of_run = 1000000
    time1 = time.time()
    estimated_reward, estimated_variance = simu(length_of_run, num_of_run, pmc)#,{pmc.param[0]:0.8,pmc.param[1]:1/6})
    time2 = time.time()
    print('the %d simulations took %0.3f ms' % (num_of_run, (time2-time1)*1000.0))
    print('the estimated proobability for %s=0.8 and %s=1/6 is %0.3f with IC length %0.3f'%(str(pmc.param[0]),str(pmc.param[1]),estimated_reward.subs({pmc.param[0]:0.8,pmc.param[1]:1/6}),2*1.96*estimated_variance.subs({pmc.param[0]:0.8,pmc.param[1]:1/6})/sqrt(num_of_run)))
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    f=sympy.lambdify(pmc.param,estimated_reward)
    fv=np.vectorize(f)
    v=sympy.lambdify(pmc.param,estimated_variance)
    vv=np.vectorize(v)
    x = np.arange(0.05, 0.95, 0.01)
    y = np.arange(0.05, 0.95, 0.01)
    X,Y=np.meshgrid(x,y)
    Z=fv(X,Y)
    C=2*1.96*vv(X,Y)/sqrt(num_of_run)
    plot=ax.scatter(X,Y,Z,c=C.ravel())
    ax.set_xlabel(str(pmc.param[0]))
    ax.set_ylabel(str(pmc.param[1]))
    ax.set_zlabel('probability')
    cb=plt.colorbar(plot)
    cb.set_label("IC width")
    plt.savefig('crowds_%d.png'%num_of_run)

def main():
    file = 'example/nand.pm'
    if len(argv) > 1:
        file = argv[1]
    pmc = myparse(file)


    num_of_run = 10
    length_of_run = 100


    estimated_reward, estimated_variance = simu(length_of_run, num_of_run, pmc)#,{pmc.param[0]:0.02,pmc.param[1]:0.9})
    print("\nsimu OK\n")
    print("random valuation:")
    random_valuation = {}
    for param in pmc.param:
        random_valuation[param] = 0.5-random()*0.01
        print(param)
        print("="+str(random_valuation[param]))

    print(estimated_reward)
    print(mysub(estimated_reward, random_valuation))
    print(3.92/sqrt(num_of_run)*mysub(estimated_variance, random_valuation))


toym()
