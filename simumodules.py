""" Simulation of pMC with modules"""
from random import random
import random as rand
from modules import mysub, reevaluation_const
from copy import deepcopy
import re
# import time


def typennotexp(expr):
    """return true if type is int or float"""
    return isinstance(expr, (int, float))


def parameterize(pmc):

    """define a valuation for the parameters of the pMC"""

    non_init = deepcopy(pmc.param)

    if pmc.get_pmc_type() == "ctmc":

        while len(non_init) > 0:
            parameter = non_init.pop()
            if type(parameter) == "int":
                alea = rand.randint(0, 100)
                pmc.value_param[str(parameter)] = (pmc.value_param[str(parameter)][0], alea)
            else:
                pmc.value_param[str(parameter)] = (pmc.value_param[str(parameter)][0], random())
    else:

        while len(non_init) > 0:
            parameter = non_init.pop()

            # If the parameter is a an integer, its value will be between 0 and 9
            if type(parameter) == "int":
                alea = rand.randint(0, 10)
                pmc.value_param[str(parameter)] = (pmc.value_param[str(parameter)][0], alea)

            # If it's not an integer, it's either a float or a double
            else:
                # the maximum probability is set at 1
                proba_max = 1

                # we go through every equation
                for eq in pmc.equation_system:

                    # we check if the parameter is used in the equation
                    if parameter in pmc.equation_system[eq][1]:
                        proba_temp = (1 - pmc.equation_system[eq][0]) / pmc.equation_system[eq][1][parameter]

                        # If the maximum probability is less than the current maximum probability,
                        if proba_temp < proba_max:
                            # The maximum probability is changed
                            proba_max = proba_temp

                # The value of the parameter is then determined by the maximum probability
                alea = rand.uniform(0, proba_max)
                pmc.value_param[str(parameter)] = (pmc.value_param[str(parameter)][0], alea)


def correction_parameters(pmc):
    """Determine a valid valuation"""

    for eqa in pmc.equation_system:
        total_probability = pmc.equation_system[eqa][0]

        for par in pmc.equation_system[eqa][1]:
            print(par, type(par), "c'est le param ?")
            if str(par) in pmc.value_param:
                total_probability += (pmc.equation_system[eqa][1][par] * pmc.value_param[str(par)][1])
            else:
                for mod in pmc.modules:
                    if par in mod.current_value_state:
                        total_probability += pmc.equation_system[eqa][1][par] * mod.current_value_state[par]

        print('proba', total_probability)

        if len(pmc.equation_system[eqa][1]) == 0 and pmc.equation_system[eqa][0] < 1:
            max = 0
            equation = ""
            for i in range(len(pmc.equation_system[eqa][2])):
                if len(str(pmc.equation_system[eqa][2][i])) >= max:
                    max = len(str(pmc.equation_system[eqa][2][i]))
                    equation = str(pmc.equation_system[eqa][2][i])
            # print(equation, "c'est elle")
            for i in range(len(pmc.equation_system[eqa][2])):
                nb_in = 0
                if str(pmc.equation_system[eqa][2][i]) in equation:
                    nb_in += 1
                else:
                    raise Exception("Wat ??")
                if nb_in >= len(pmc.equation_system[eqa][2]):
                    total_probability = 1
                else:
                    raise Exception("Some equations are not in the final equation")

        # If the probability is greater than 1, the parameter used in the "equation" with the highest value
        # is recalculated based on the values of the other parameters (and their frequency in the "equation")
        # and on the numerical probability of the "equation", all that divided by the parameter's frequency
        if total_probability >= 1 and len(pmc.equation_system[eqa][1]) > 1:

            # The parameter with the highest probability is determined
            proba_max = 0
            max_parameter = ""
            for par in pmc.equation_system[eqa][1]:

                if pmc.value_param[str(par)][1] >= proba_max:
                    proba_max = pmc.value_param[str(par)][1]
                    max_parameter = par

            # print(max_parameter, pmc.value_param[str(max_parameter)][1])

            aux_proba = pmc.equation_system[eqa][0]
            for par in pmc.equation_system[eqa][1]:
                aux_proba += pmc.equation_system[eqa][1][par] * pmc.value_param[str(par)][1]

            if aux_proba >= 1:
                new_value = 0
            else:
                new_value = rand.uniform(0, (1 - aux_proba) / pmc.equation_system[eqa][1][max_parameter])

            parameter_type = pmc.value_param[str(max_parameter)][0]

            pmc.value_param[str(max_parameter)] = (parameter_type, new_value)


def transition_recalculation(pmc):
    """calculate the probability of transition based on the valuation"""

    for mod in pmc.get_modules():
        for tr in mod.get_transition():
            prob = tr[2][0]
            if str(prob).isdigit():
                print()
            else:
                copy_point = str(prob).split('.')
                copy_slash = str(prob).split('/')
                if (copy_point[0].isdigit() and copy_point[1].isdigit()) or (copy_slash[0].isdigit() and copy_slash[1].isdigit()):
                    print()
                elif re.compile(r'([0-9]*[a-zA-Z]*)*').fullmatch(str(prob)):
                    tr[2][0] = pmc.value_param[str(prob)][1]
                else:

                    tr[2][0] = prob.evalf()

                    dic = {}
                    for param in pmc.param:
                        if str(param) in str(prob):
                            dic[param] = pmc.value_param[str(param)][1]

                    tr[2][0] = prob.evalf(subs=dic)


def sim(length, pmc, value=None):
    """simulate pMC once for at most length step
        return the accumulated reward"""
    pmc.reinitialization()

    end = False
    step = 0
    cumu_reward = 0
    prob = 1
    # Simulation for dtmc and probabilistic MC
    if pmc.get_pmc_type() == "dtmc" or pmc.get_pmc_type() == "probabilistic":

        while step < length and not end:
            print('step', step)
            step += 1
            numb_mod_deadlocked = 0
            for trans_mod in pmc.get_possible_transitions():
                if trans_mod:
                    proba_trans = 0
                    trans_list = []
                    for trans in trans_mod:
                        proba_trans += trans[2][0]
                        trans_list += [trans[2]]

                    if proba_trans > 1:
                        raise Exception("several actions possible")
                    else:
                        if value is None:
                            name, cond, outcome = trans_mod[0]
                            print("name:", name, "cond :", cond, "outcome :", outcome)
                            norma = sum(not typennotexp(e[0]) for e in trans_list)
                            threshold = random()
                            y = 0

                            print('trans_list', trans_list, len(trans_list))

                            while y < len(trans_list) and threshold > 0:
                                if typennotexp(trans_list[y][0]):
                                    threshold -= trans_list[y][0]
                                else:
                                    threshold -= 1/norma
                                y += 1
                            y -= 1

                            realprob = trans_list[y][0]
                            print(trans_list[y])
                            if typennotexp(realprob):
                                print("realprob", realprob)
                                prob *= mysub(realprob, pmc.get_valuation())/realprob
                                print("prob", prob)
                            else:
                                prob *= mysub(realprob, pmc.get_valuation())*norma
                            pmc.maj(trans_list[y][1])
                            cumu_reward += pmc.get_reward(name)
                        else:
                            name, _, outcome = trans_mod[0]
                            threshold = random()
                            y = 0
                            while y < len(trans_list) and threshold > 0:
                                threshold -= mysub(mysub(trans_list[y][0], value), pmc.get_valuation())
                                y += 1
                            y -= 1
                            realprob = trans_list[y][0]
                            prob *= mysub(realprob, pmc.get_valuation())/mysub(mysub(trans_list[y][0], value), pmc.get_valuation())
                            pmc.maj(trans_list[y][1])
                            cumu_reward += pmc.get_reward(name)
                else:
                    numb_mod_deadlocked += 1
                end = (numb_mod_deadlocked == len(pmc.modules))
            # if end:

    elif pmc.get_pmc_type() == "ctmc":  # Simulation for ctmc
        while step < length and not end:
            step += 1
            numb_mod_deadlocked = 0

            for trans_mod in pmc.get_possible_transitions():
                exit_rate = 0
                if trans_mod:
                    if len(trans_mod) > 1:
                        raise Exception("This model does not support mutli-lines transition")
                    else:
                        if value is None:
                            name, cond, outcome = trans_mod[0]
                            norma = sum(not typennotexp(e[0]) for e in outcome)
                            threshold = random()
                            y = 0

                            for i in range(len(outcome)):
                                print("je sais plus")

                            while y < len(outcome) and threshold > 0:
                                if typennotexp(outcome[y][0]):
                                    threshold -= outcome[y][0]
                                else:
                                    threshold -= 1 / norma
                                y += 1
                            y -= 1

                            realprob = outcome[y][0]
                            if typennotexp(realprob):
                                prob *= mysub(realprob, pmc.get_valuation()) / realprob
                            else:
                                prob *= mysub(realprob, pmc.get_valuation()) * norma
                            pmc.maj(outcome[y][1])
                            cumu_reward += pmc.get_reward(name)
                        else:
                            name, _, outcome = trans_mod[0]
                            threshold = random()
                            y = 0
                            while y < len(outcome) and threshold > 0:
                                threshold -= mysub(mysub(outcome[y][0], value), pmc.get_valuation())
                                y += 1
                            y -= 1
                            realprob = outcome[y][0]
                            prob *= mysub(realprob, pmc.get_valuation()) / mysub(mysub(outcome[y][0], value),
                                                                                 pmc.get_valuation())
                            pmc.maj(outcome[y][1])
                            cumu_reward += pmc.get_reward(name)
                    numb_mod_deadlocked += 1
                end = (numb_mod_deadlocked == len(pmc.modules))

    # print("end at l = "+str(step))
    # print(cumu_reward)
    return prob*cumu_reward


def simu(length, num_simu, pmc, value=None):

    """length = length of exec, num_simu = number of simu, pmc = pmc to simulate"""

    accu_reward = 0
    accu_var = 0

    parameterize(pmc)
    if pmc.get_pmc_type() == "dtmc":
        correction_parameters(pmc)

    reevaluation_const(pmc.value_param, pmc.get_valuation())
    for mod in pmc.modules:
        pmc.reevaluation(mod)

    transition_recalculation(pmc)

    if pmc.get_pmc_type() == "ctmc":
        for _ in range(0, num_simu):
            # print("sim #"+str())
            for i in pmc.value_param:
                if pmc.value_param[i][1]:
                    print("Already initialized")
                else:
                    pmc.value_param[i] = (pmc.value_param[i][0], rand.randint(1, 10))

            reevaluation_const(pmc.value_param, pmc.get_valuation())
            for i in pmc.get_modules():
                pmc.reevaluation(i)
            random_var_y = sim(length, pmc, value)
            accu_reward += random_var_y
            accu_var += random_var_y*random_var_y
            for par in pmc.value_param:
                pmc.value_param[par] = (pmc.value_param[par][0], None)
            pmc.equation_system = {}
            pmc.expression = ""
    else:

        # This block's purpose is to correct any problems with the parameters' value
        # It starts by checking the total probability of each "equation"
        # print("debut correction")

        for _ in range(0, num_simu):
            # print("sim #"+str(i))
            random_var_y = sim(length, pmc, value)
            accu_reward += random_var_y
            accu_var += random_var_y*random_var_y

        for par in pmc.value_param:
            pmc.value_param[par] = (pmc.value_param[par][0], None)
        # pmc.equation_system = {}
        # pmc.expression = ""
    estespy = accu_reward/num_simu
    estvar = (accu_var/(num_simu-1)-num_simu/(num_simu-1)*estespy**2)**(1/2)
    return [estespy, estvar]
