""" Simulation of pMC with modules"""
from random import random
from modules import mysub


def typennotexp(expr):
    """return true if type is int or float"""
    return isinstance(expr, (int, float))


def sim(length, pmc, value=None):
    """simulate pMC once for at most length step
        return the accumulated reward"""
    pmc.reinit()
    end = False
    step = 0
    cumu_reward = 0
    prob = 1
    if pmc.get_pMCtype() == "dtmc" or pmc.get_pMCtype() == "probabilistic":  # Simulation for dtmc and probabilistic MC
        while step < length and not end:
            step += 1
            numb_mod_deadlocked = 0
            for trans_mod in pmc.get_possible_transitions():
                if trans_mod:
                    # print(len(trans_mod))
                    if len(trans_mod) > 1:
                        raise Exception("several actions possible")
                    else:
                        if value is None:
                            name, _, outcome = trans_mod[0]
                            norma = sum(not typennotexp(e[0]) for e in outcome)
                            threshold = random()
                            j = 0
                            while j < len(outcome) and threshold > 0:
                                if typennotexp(outcome[j][0]):
                                    threshold -= outcome[j][0]
                                else:
                                    threshold -= 1/norma
                                j += 1
                            j -= 1
                            realprob = outcome[j][0]
                            if typennotexp(realprob):
                                prob *= mysub(realprob, pmc.get_valuation())/realprob
                            else:
                                prob *= mysub(realprob, pmc.get_valuation())*norma
                            pmc.maj(outcome[j][1])
                            cumu_reward += pmc.get_reward(name)
                        else:
                            name, _, outcome = trans_mod[0]
                            threshold = random()
                            j = 0
                            while j < len(outcome) and threshold > 0:
                                threshold -= mysub(mysub(outcome[j][0], value), pmc.get_valuation())
                                j += 1
                            j -= 1
                            realprob = outcome[j][0]
                            prob *= mysub(realprob, pmc.get_valuation())/mysub(mysub(outcome[j][0], value), pmc.get_valuation())
                            pmc.maj(outcome[j][1])
                            cumu_reward += pmc.get_reward(name)
                else:
                    numb_mod_deadlocked += 1
                end = (numb_mod_deadlocked == len(pmc.modules))
            # if end:

    elif pmc.get_pMCtype() == "ctmc":  # Simulation for ctmc
        while step < length and not end:
            step += 1
            numb_mod_deadlocked = 0
            for trans_mod in pmc.get_possible_transitions():
                if trans_mod:
                    time_unit = 1
                    if len(trans_mod) > 1:
                        print("race condition")

                    else:
                        print("hein ?")

                else:
                    numb_mod_deadlocked += 1
                end = (numb_mod_deadlocked == len(pmc.modules))

    # print("end at l = "+str(step))
    # print(cumu_reward)
    return prob*cumu_reward


def simu(length, num_simu, pmc, valu=None):
    """length = length of exec, num_simu = number of simu, pmc = pmc to simulate"""
    accu_reward = 0
    accu_var = 0
    for _ in range(0, num_simu):
        # print("sim #"+str(i))
        random_var_y = sim(length, pmc, valu)
        accu_reward += random_var_y
        accu_var += random_var_y*random_var_y

    estespy = accu_reward/num_simu
    estvar = (accu_var/(num_simu-1)-num_simu/(num_simu-1)*estespy**2)**(1/2)
    return [estespy, estvar]
