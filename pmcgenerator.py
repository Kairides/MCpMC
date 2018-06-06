import random

# TODO: Créer un affichage permetant de choisir le nom du fichier, le type de MC, le nombre d'état, le nombre moyen de transition, le nombre de parametre et le taux de parametrage


# Function that chooses the next state for a transition
def state_transition(reached_states, nb_state):
    new_state = random.randint(0, nb_state - 1)
    while reached_states.count(new_state) >= 1:
        print("il est deja dedans", new_state)
        new_state = random.randint(0, nb_state - 1)
        print("nouvel etat choisit", new_state)

    return new_state


def random_rate(pmc_type, parameters=None, rate=None):
    if pmc_type == 'ctmc':
        if parameters and rate:
            val = random.random()
            if val <= rate:
                index = random.randint(1, parameters)
                return "p" + str(index)

            else:
                return random.randint(0, 100)
        else:
            return random.randint(0, 100)

    else:
        raise Exception("How did you get here ?")


# Function writing parameters in the file
def param_writing(file, parameters, pmc_type):
    if pmc_type == "dtmc":
        for i in range(1, parameters + 1):
            file.write("const double p" + str(i) + "; \n")

        file.write("\n")
    else:
        for i in range(1, parameters + 1):
            file.write("const int p" + str(i) + "; \n")

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
# The transitions of each states are written on a single line
def module_writing(file, pmc_type, nb_state, maximum_degree, parameters=None, rate=None):

    if nb_state == 1:
        raise Exception("Number of state too small")
    else:
        file.write("const int N = " + str(nb_state) + ";" + "\n \n")

        if parameters and rate:
            file = param_writing(file, parameters, pmc_type)

        # Main module, only one module in this model
        file.write("module main" + "\n")
        file.write("\t" + "s:[0..N];" + "\n")
        file.write("\n")

        # In this model, every state will have at most maximum_degre transition
        for i in range(0, nb_state):

            # In this model, a state can only be reach once by another state.
            # If a state s is reached, it will be stored in this array and for every new transition,
            # we check the array to see if the state has already been reached
            # if so, a new one is selected
            reached_states = []
            trans = ""

            if pmc_type == "ctmc":
                max_degre = random.randint(1, maximum_degree)

                for j in range(0, max_degre):
                    trans = "\t [] s=" + str(i) + "-> "
                    if j <= max_degre:
                        transition_rate = random_rate(pmc_type, parameters, rate)
                        new_state = state_transition(reached_states, nb_state)
                        trans += str(transition_rate)+" : (s' = "+str(new_state)+" ) + "
                        reached_states.append(new_state)
                    transition_rate = random_rate(pmc_type, parameters, rate)
                    new_state = state_transition(reached_states, nb_state - 1)
                    trans += str(transition_rate) + " : (s' = " + str(new_state) + " ); \n"
                file.write(trans)
            else:
                proba_state = 0  # total transition probability for state i
                param_state = []  # parameters used for transitions for state i
                j = 0

                trans = "\t [] s=" + str(i) + " -> "

                while proba_state < 1 and j < maximum_degree:

                    # If there is parameters and a rate, parameters can be used for transitions
                    if parameters and rate:
                        new_state = state_transition(reached_states, nb_state)
                        reached_states.append(new_state)
                        # If the total probability is not 1 but the last transition is reached
                        # the resulting probability will be:
                        # "1 -(the parameters used + the total probability)" as a string
                        if proba_state < 1 and j >= maximum_degree - 1:

                            if param_state:
                                transition = "1-("
                                for k in range(0, len(param_state)):
                                    transition += param_state[k] + "+"
                                transition += str(proba_state) + ")"
                            else:
                                transition = 1 - proba_state
                                proba_state += transition

                            trans += str(transition) + ": (s' = " + str(new_state) + "); \n"
                        else:
                            val = random.random()
                            if val <= rate:
                                index = random.randint(1, parameters)
                                transition = "p" + str(index)
                                param_state.append(transition)
                                trans += str(transition) + ": (s' = " + str(new_state) + ") + "
                            else:
                                transition = float("{0:.3f}".format(random.random()))
                                if proba_state + transition > 1:
                                    if param_state:
                                        transition = "1-("
                                        for k in range(0, len(param_state)):
                                            transition += param_state[k] + "+"
                                        transition += str(proba_state) + ")"
                                        proba_state = 1
                                    else:
                                        transition = (1 - proba_state)
                                        proba_state += transition
                                    trans += str(transition) + ": (s' = " + str(new_state) + "); \n "
                                else:
                                    proba_state += transition
                                    trans += str(transition) + ": (s' = " + str(new_state) + ") + "
                    else:
                        new_state = state_transition(reached_states, nb_state - 1)
                        transition = float("{0:.3f}".format(random.random()))
                        if proba_state + transition > 1:
                            transition = (1 - proba_state)
                            trans += str(transition) + ": (s' = " + str(new_state) + ");\n "
                        elif proba_state + transition < 1 and j == maximum_degree - 1:
                            transition = (1 - proba_state)
                            trans += str(transition) + ": (s' = " + str(new_state) + ");\n "
                        else:
                            trans += str(transition) + ": (s' = " + str(new_state) + ") + "
                        proba_state += transition

                        reached_states.append(new_state)
                    j += 1
                file.write(trans)

        file.write("endmodule \n \n")

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
#     -If you want to generate a pMC, parameters should be send with a rate, if send without,
#      a regular MC will be generated
pmc_constructor("exemple_rapport", "dtmc", 4, 3, 2, 0.5)
