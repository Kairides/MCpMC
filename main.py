from math import sqrt
from random import random
from sys import argv
from parser import myparse
from modules import mysub
from simumodules import simu
import time
# from memory_profiler import profile
# import re
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
# import matplotlib.colors as colors
# import matplotlib.cm as cmx
import sympy


# @profile

# Auxiliary function used to parse the file in parameter and calculate how long it took
def parsing_aux(nom):

    time1 = time.time()  # First time
    pmc = myparse(nom)  # Parsing
    time2 = time.time()  # Second time
    print('parsing of %s took %0.3f ms' % (nom, (time2-time1)*1000.0))  # printing the time it took to parse
    return pmc


# function used to calculate the mean and variance
def estim_esp_var(length_of_run, num_of_run, pmc, value=None):

    time1 = time.time()
    accu = simu(length_of_run, num_of_run, pmc, value)
    time2 = time.time()
    print('the %d simulations took %0.3f ms' % (num_of_run, (time2 - time1)*1000.0))

    return accu


def vectorize_f(pcm, estim_reward):

    f = sympy.lambdify(pcm.param, estim_reward)

    return np.vectorize(f)


def vectorize_v(pmc, estim_variance):

    v = sympy.lambdify(pmc.param, estim_variance)

    return np.vectorize(v)


# Test function for toy
def toy():

    # File selection
    pmc = parsing_aux('example/toy.pm')

    # Number of runs and their length
    num_of_run = 10000
    length_of_run = 100

    # Mean and variance
    estimated_reward, estimated_variance = estim_esp_var(length_of_run, num_of_run, pmc)

    fig = plt.figure()

    ax = Axes3D(fig)
    # ax = fig.add_subplot(111, projection='3d')

    fv = vectorize_f(pmc, estimated_reward)

    vv = vectorize_v(pmc, estimated_variance)

    x = np.arange(0.05, 0.95, 0.01)

    big_x1, big_y1 = np.meshgrid(x, x)

    big_x = big_x1[big_x1+big_y1 < 0.95]
    big_y = big_y1[big_x1+big_y1 < 0.95]
    big_z = fv(big_x, big_y)
    big_c = 2 * 1.96 * vv(big_x, big_y) / sqrt(num_of_run)
    plot = ax.scatter(big_x, big_y, big_z, c=big_c)
    ax.set_xlabel('p')
    ax.set_ylabel('q')
    ax.set_zlabel('probability')
    cb = plt.colorbar(plot)
    cb.set_label("CI width")
    plt.savefig('toy_%d.png' % num_of_run)


# Test function for toymul
def toym():

    # File selection
    pmc = parsing_aux('example/toymul.pm')

    # Number of runs and their length
    num_of_run = 10000
    length_of_run = 100

    # Mean and variance
    estimated_reward, estimated_variance = estim_esp_var(length_of_run, num_of_run, pmc)

    def random_val1(q, e):
        random_valuation = dict()
        random_valuation[pmc.param[0]] = q
        for i in range(1, len(pmc.param)):
            param = pmc.param[i]
            random_valuation[param] = random() * (1 - q)
        return e.subs(random_valuation)

    random_val = np.vectorize(random_val1)
    x = np.arange(0.05, 0.95, 0.05)
    y = random_val(x, estimated_reward)
    e = random_val(x, estimated_variance * 1.96 / sqrt(num_of_run))
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.errorbar(x, y, yerr=e, fmt='o')
    ax.set_xlabel('q')
    ax.set_ylabel('probability for random valuation')
    plt.savefig('toymul_%d.png' % num_of_run)
    # plt.show()


'''def nand():  # nand.pm n'existe pas

    pmc = parsing_aux('example/nand.pm')

    num_of_run = 2
    length_of_run = 1000000

    estimated_reward, estimated_variance = estim_esp_var(length_of_run, num_of_run, pmc)'''


# Test function for nand2.pm
def nand2():

    # File selection
    pmc = parsing_aux('example/nand2.pm')

    # Number of runs and their length
    num_of_run = 1000
    length_of_run = 1000000

    # Mean and variance
    estimated_reward, estimated_variance = estim_esp_var(length_of_run, num_of_run, pmc, {pmc.param[0]: 0.02, pmc.param[1]: 0.9})

    # Plotting
    fig = plt.figure()

    ax = Axes3D(fig)
    # ax = fig.add_subplot(111, projection='3d')

    fv = vectorize_f(pmc, estimated_reward)

    vv = vectorize_v(pmc, estimated_variance)

    x, y = np.arange(0.05, 0.95, 0.01)
    big_x, big_y = np.meshgrid(x, y)

    big_z = fv(big_x, big_y)
    big_c = 2 * 1.96 * vv(big_x, big_y) / sqrt(num_of_run)
    plot = ax.scatter(big_x, big_y, big_z, c=big_c.ravel())
    ax.set_xlabel(str(pmc.param[0]))
    ax.set_ylabel(str(pmc.param[1]))
    ax.set_zlabel('probability')
    cb = plt.colorbar(plot)
    cb.set_label("CI width")
    plt.savefig('nand2_%d.png' % num_of_run)


# Test function for zeroconf
def zeroconf():

    # File selection
    pmc = parsing_aux('example/zeroconf.pm')

    # Number of runs and their length
    num_of_run = 10000
    length_of_run = 500

    # Mean and variance
    estimated_reward, estimated_variance = estim_esp_var(length_of_run, num_of_run, pmc)
    # ,{pmc.param[0]:0.3,pmc.param[1]:0.3})

    # Plotting
    fig = plt.figure()

    ax = Axes3D(fig)
    # ax = fig.add_subplot(111, projection='3d')

    fv = vectorize_f(pmc, estimated_reward)

    vv = vectorize_v(pmc, estimated_variance)

    x, y = np.arange(0.15, 0.55, 0.005)
    big_x, big_y = np.meshgrid(x, y)
    big_z = fv(big_x, big_y)
    big_c = 2*1.96*vv(big_x, big_y)/sqrt(num_of_run)
    plot = ax.scatter(big_x, big_y, big_z, c=big_c.ravel())
    ax.set_xlabel(str(pmc.param[0]))
    ax.set_ylabel(str(pmc.param[1]))
    ax.set_zlabel('Expected value')
    cb = plt.colorbar(plot)
    cb.set_label("CI width")
    plt.savefig('zeroconf_%d.png' % num_of_run)
    # plt.show()


# Test function for crowds
def crowd():

    # File selection
    pmc = parsing_aux('example/crowds.pm')

    # Number of runs and their length
    num_of_run = 10000
    length_of_run = 1000000

    # Mean and variance
    estimated_reward, estimated_variance = estim_esp_var(length_of_run, num_of_run, pmc)
    # ,{pmc.param[0]:0.8,pmc.param[1]:1/6})

    chain0 = 'the estimated probability for %s=0.8 and %s=1/6 is %0.3f with CI length %0.3f'
    chain1 = str(pmc.param[0])
    chain2 = str(pmc.param[1])

    param1 = estimated_reward.subs({pmc.param[0]: 0.8, pmc.param[1]: 1/6})
    param2 = 2*1.96*estimated_variance.subs({pmc.param[0]: 0.8, pmc.param[1]: 1/6})/sqrt(num_of_run)

    print(chain0 % (chain1, chain2, param1, param2))
    fig = plt.figure()

    ax = Axes3D(fig)
    # ax = fig.add_subplot(111, projection='3d')
    f = sympy.lambdify(pmc.param, estimated_reward)
    fv = np.vectorize(f)
    v = sympy.lambdify(pmc.param, estimated_variance)
    vv = np.vectorize(v)
    x = np.arange(0.05, 0.95, 0.01)
    y = np.arange(0.05, 0.95, 0.01)
    big_x, big_y = np.meshgrid(x, y)
    big_z = fv(big_x, big_y)
    big_c = 2*1.96*vv(big_x, big_y)/sqrt(num_of_run)
    plot = ax.scatter(big_x, big_y, big_z, c=big_c.ravel())
    ax.set_xlabel(str(pmc.param[0]))
    ax.set_ylabel(str(pmc.param[1]))
    ax.set_zlabel('probability')
    cb = plt.colorbar(plot)
    cb.set_label("CI width")
    plt.savefig('crowds_%d.png' % num_of_run)


def main():

    file = 'example/nand.pm'   # Selection du fichier nand.pm dans le dossier example, le fichier nand.pm n'existe pas
    if len(argv) > 1:
        file = argv[1]
    pmc = myparse(file)

    num_of_run = 10
    length_of_run = 100

    estimated_reward, estimated_variance = simu(length_of_run, num_of_run, pmc)
    # ,{pmc.param[0]:0.02,pmc.param[1]:0.9})
    print("\nsimu OK\n")
    print("random valuation:")
    random_valuation = {}
    for param in pmc.param:
        random_valuation[param] = 0.5-random() * 0.01
        print(param)
        print("=" + str(random_valuation[param]))

    print(estimated_reward)
    print(mysub(estimated_reward, random_valuation))
    print(3.92/sqrt(num_of_run)*mysub(estimated_variance, random_valuation))


# parsing_aux("example/toy.pm")

# nand2()
# toym()
# crowd()
# zeroconf()
toy()
