import random


# Function that chooses the next state for a transition
def state_transition(reached_states, maximum_degree):
    new_state = random.randint(0, maximum_degree)
    while reached_states.count(new_state) >= 1:
        new_state = random.randint(0, maximum_degree)

    return new_state


def random_rate(pmc_type, parameters=None, rate=None):
    if pmc_type == 'ctmc':
        if parameters and rate:
            val = random.random()
            if val <= rate:
                index = random.randint(0, len(parameters)-1)
                return parameters[index]

            else:
                return random.randint(0, 100)
        else:
            return random.randint(0, 100)

    else:
        raise Exception("How did you get here ?")


# Function writing parameters in the file
def param_writing(file, parameters):

    for i in range(0, len(parameters)):
        file.write("const double " + str(parameters[i]) + "; \n")

    file.write("\n")
    return file


# Function writing the type of pMC in the file
def type_writing(file, pmc_type):

    if pmc_type == "ctmc" or pmc_type == "dtmc":
        file.write(pmc_type + "\n" + "\n")
    else:
        print(pmc_type)
        raise Exception("Unknown pmc type")

    return file


# Function writing the main module and the constant describing the number of states
def module_writing(file, pmc_type, nb_state, maximum_degree, parameters=None, rate=None):

    if nb_state == 1:
        raise Exception("Number of state too small")
    else:
        file.write("const int N = " + str(nb_state) + ";" + "\n \n")

        if parameters:
            file = param_writing(file, parameters)

        # Main module, only one module in this model
        file.write("module main" + "\n")
        file.write("\t" + "s:[0..N];" + "\n")
        file.write("\n")

        # In this model, every state will have at least a transition,
        # if the pMC is a ctmc, every state will have the same amount of transition
        for i in range(0, nb_state):

            # In this model, a state can only be reach once by another state.
            # If a state s is reached, it will be stored in this array and for every new transition,
            # we check the array to see if the state has already been reached
            # if so, a new one is selected
            reached_states = []

            if pmc_type == "ctmc":
                for j in range(0, maximum_degree):
                    transition_rate = random_rate(pmc_type, parameters, rate)
                    new_state = state_transition(reached_states, nb_state - 1)
                    trans = "\t"+"[] s="+str(i)+" -> "+str(transition_rate)+": (s' = "+str(new_state)+");\n"
                    reached_states.append(new_state)
                    file.write(trans)
            else:
                proba_state = 0  # total transition probability for state i
                param_state = []  # parameters used for transitions for state i
                j = 0

                while proba_state < 1 and j < maximum_degree:

                    # If there is parameters and a rate, parameters can be used for transitions
                    if parameters and rate:

                        # If the total probability is not 1 but the last transition is reached
                        # the resulting probability will be:
                        # "1 -(the parameters used + the total probability)" as a string
                        if proba_state < 1 and j >= maximum_degree - 1:

                            if param_state:
                                transition = "1 - ("
                                for k in range(0, len(param_state)):
                                    transition += param_state[k] + " + "
                                transition += str(proba_state) + ")"
                            else:
                                transition = 1 - proba_state
                                proba_state += transition
                        else:
                            val = random.random()
                            if val <= rate:
                                index = random.randint(0, len(parameters) - 1)
                                transition = parameters[index]
                                param_state.append(transition)
                            else:
                                transition = float("{0:.3f}".format(random.random()))
                                if proba_state + transition > 1:
                                    transition = (1 - proba_state)
                                proba_state += transition
                    else:
                        transition = float("{0:.3f}".format(random.random()))
                        if proba_state + transition > 1:
                            transition = (1 - proba_state)
                        if proba_state + transition < 1 and j == maximum_degree - 1:
                            transition = (1 - proba_state)
                        proba_state += transition

                    new_state = state_transition(reached_states, nb_state - 1)

                    trans = "\t"+"[] s="+str(i)+" -> "+str(transition)+": (s' = "+str(new_state)+");\n"
                    reached_states.append(new_state)

                    file.write(trans)
                    j += 1
        file.write("endmodule \n \n")

        # Initial state
        file.write("init \n \t" + "s = 0 \n" + "endinit")
    return file


# Main function
def pmc_constructor(nom, pmc_type, nb_state, maximum_degree, parameters=None, rate=None):

    # Change the extension based on the type of pMC
    if pmc_type == "dtmc":
        nom += ".pm"
    elif pmc_type == "ctmc":
        nom += ".sm"
    else:
        raise Exception("Unknown pmc type")

    my_file = open(nom, "w")

    my_file = type_writing(my_file, pmc_type)

    my_file = module_writing(my_file, pmc_type, nb_state, maximum_degree, parameters, rate)

    my_file.close()


# -The pMC type is either "ctmc" or "dtmc", anything else will cause an error
# -Don't add an extension to the file, the program does it automatically
# -Parameters and rate are optionals:
#     -If you want to generate a pMC, parameters should be send as a list of characters
#     -If you want to generate a pMC, parameters should be send with a rate, if send without,
#      a regular MC will be generated
pmc_constructor("test", "dtmc", 5, 2)
