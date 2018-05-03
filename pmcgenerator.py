import random


# Function that chooses the next state for a transition
def state_transition(reached_states, average_degree):
    new_state = random.randint(0, average_degree)
    while reached_states.count(new_state) >= 1:
        new_state = random.randint(0, average_degree)

    return new_state


# Function writing parameters in the file
def param_writing(file, parameters):

    for i in range(0, len(parameters)):
        file.write("const double" + parameters[i] + "; \n")

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
def module_writing(file, pmc_type, nb_state, average_degree, parameters):

    if nb_state == 1:
        raise Exception("Number of state too small")
    else:
        file.write("const int N = " + str(nb_state) + ";" + "\n \n")

        file = param_writing(file, parameters)

        file.write("module main" + "\n")
        file.write("\t" + "s:[0..N];" + "\n")
        file.write("\n")

        for i in range(0, nb_state):

            reached_states = []

            if pmc_type == "ctmc":
                for j in range(0, average_degree):
                    transition_rate = random.randint(0, 100)
                    new_state = state_transition(reached_states, nb_state - 1)
                    trans = "\t"+"[] s="+str(i)+" -> "+str(transition_rate)+": (s' = "+str(new_state)+");\n"
                    reached_states += new_state
                    reached_states.append(new_state)
                    file.write(trans)
            else:
                proba_state = 0
                j = 1
                while proba_state < 1 and j < average_degree:
                    transition = random.random()
                    new_state = state_transition(reached_states, nb_state - 1)

                    if proba_state + transition > 1:
                        transition = (1 - proba_state)
                    elif proba_state + transition < 1 and j == average_degree - 1:
                        transition = (1 - proba_state)

                    trans = "\t"+"[] s="+str(i)+" -> "+str(transition)+": (s' = "+str(new_state)+");\n"
                    reached_states.append(new_state)

                    file.write(trans)
                    proba_state += transition
                    j += 1

        file.write("endmodule \n")

    return file


# Main function
def pmc_constructor(nom, pmc_type, nb_state, average_degree, *parameters):

    if pmc_type == "dtmc":
        nom += ".pm"
    elif pmc_type == "ctmc":
        nom += ".sm"
    else:
        raise Exception("Unknown pmc type")

    my_file = open(nom, "w")

    my_file = type_writing(my_file, pmc_type)

    my_file = module_writing(my_file, pmc_type, nb_state, average_degree, parameters)

    my_file.close()


pmc_constructor("test", "dtmc", 10, 10)
