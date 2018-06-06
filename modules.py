""" Define pMC with modules """
import sympy

from copy import deepcopy


def copy_dict(dic):
    """ copy a dictionary """
    return {**dic}


def exp_to_fun(exp, param):
    free_var = exp.free_symbols
    if free_var:
        f = sympy.lambdify(free_var, exp, modules={'And': all, 'Or': any})

        def g(dic):
            evaluation = []
            for i in free_var:
                if i in dic:
                    evaluation += [dic[i]]
                elif str(i) in param:
                    evaluation += [param[str(i)][1]]
                else:
                    raise Exception("Unknown variable", i)
            # eval = list(map(lambda x: dic[x], free_var))
            return f(*evaluation)
        return g
    else:
        return lambda *x: exp


def mysub(exp, dic):
    """ sympy subs but filtering local dictionary with only variables in exp"""

    free_var = exp.free_symbols

    if free_var:
        reduced_dic = {x: dic[x] for x in free_var if x in dic}
        if reduced_dic:
            return exp.subs(reduced_dic)
    return exp


def reevaluation_const(value_param, dic):

    non_init = []
    for i in dic:
        if type(dic[i]) == 'sympy.core.symbol.Symbol':
            non_init += [i]
    while len(non_init) > 0:
        for i in range(0, len(non_init)):
            if str(i) in value_param:
                dic[i] = value_param[str(i)][1]
            elif dic[i] in dic and dic[dic[i]] != 'sympy.core.symbol.Symbol':
                dic[i] = dic[dic[i]]
            else:
                print("Unknown or uninitialized value")


class Module:
    """ module of a pMC with modules """
    def __init__(self, name):
        self.name = name
        self.initial_value_state = {}
        self.trans = []
        self.current_value_state = {}
        self.maximum_value_state = {}
        self.alph = {}
        self.pmc = PmcModules()

    def add_state(self, state, min_value, max_value, ini=None):
        """ adds a state """
        if ini is None:
            init = min_value
        else:
            init = ini
        self.initial_value_state[state] = init
        self.current_value_state[state] = init
        self.maximum_value_state[state] = max_value

    def remove_state(self, state):
        """ deletes a state"""
        if state in self.current_value_state:
            del self.initial_value_state[state]
            del self.current_value_state[state]
            del self.maximum_value_state[state]
        else:
            raise Exception("State not in module")

    def get_states(self):
        """returns the states"""
        state = []
        for i in self.initial_value_state:
            state.append(i)
        return state

    def num_state(self):
        """returns the number of state"""
        num = 0
        for _ in self.get_states():
            num += 1
        return num

    def add_transition(self, name, cond, outcome):
        """ add a transition """
        self.alph[name] = True
        self.trans += [[name, cond, outcome, exp_to_fun(cond, self.pmc.value_param)]]

    def reinitialization(self):
        """ reinitialize all state to their initial value """
        self.current_value_state = copy_dict(self.initial_value_state)

    def eval(self, exp, global_substitution):
        """ evaluate an expression with the current value of the states
            given the current values of the global variables"""
        return mysub(exp, {**self.current_value_state, **global_substitution})

    def get_possible_transitions(self, global_substitution):
        """ return the transition doable given the current value of the global variable """

        for name, _, _, funcond in self.trans:
            print(name, funcond({**global_substitution, **self.current_value_state}))

        return [[name, cond, outcome]
                for name, cond, outcome, funcond in self.trans
                if funcond({**global_substitution, **self.current_value_state})]

    def copy(self, name):
        """ return a copy of the module """
        mod = Module(name)
        mod.initial_value_state = copy_dict(self.initial_value_state)
        mod.current_value_state = copy_dict(self.current_value_state)
        mod.maximum_value_state = copy_dict(self.maximum_value_state)
        mod.alph = copy_dict(self.alph)
        mod.trans = []
        for i in range(0, len(self.trans)):
            name_transition = self.trans[i][0]
            cond = self.trans[i][1]
            outcome = self.trans[i][2]

            mod.add_transition(name_transition, cond, outcome)
        '''for namet, cond, outcome, _ in self.trans:
        mod.add_transition(namet, cond, list(outcome))'''

        return mod

    def replace(self, name1, name2):
        """ replace name1 with name2 in the module """
        if name1 in self.initial_value_state:
            self.initial_value_state[name2] = self.initial_value_state[name1]
            del self.initial_value_state[name1]
            self.current_value_state[name2] = self.current_value_state[name1]
            del self.current_value_state[name1]
            self.maximum_value_state[name2] = self.maximum_value_state[name1]
            del self.maximum_value_state[name1]
        substitution = {name1: name2}
        new_trans = []
        for i in range(0, len(self.trans)):
            name = self.trans[i][0]
            cond = self.trans[i][1]
            outcome = self.trans[i][2]

            if name == name1:
                new_name = name2
                self.alph[name2] = True
                del self.alph[name1]
            else:
                new_name = name
            new_outcome = []

            for var, update in outcome:
                new_outcome += [[mysub(var, substitution),
                                {mysub(state, substitution): mysub(state_up, substitution)
                                 for state, state_up in update.items()}]]
            new_trans += [[new_name, mysub(cond, substitution), new_outcome, exp_to_fun(mysub(cond, substitution), self.pmc.value_param)]]
        self.trans = new_trans

    def set_init_value(self, state, value):
        """ declare a new initial value for a state """
        if state in self.initial_value_state:
            self.initial_value_state[state] = value
            self.initial_value_state[state] = value

    def maj(self, update, global_valu):
        """ update the current states values according to up """
        temp = copy_dict(self.current_value_state)
        for k in self.current_value_state:
            if k in update:
                self.current_value_state[k] = mysub(update[k], {**temp, **global_valu})
            else:
                self.current_value_state[k] = self.current_value_state[k]
        return temp

    def set_pmc(self, pmc):
        self.pmc = pmc

    def get_pmc(self):
        return self.pmc

    def get_param(self):
        return (self.get_pmc()).get_param()

    def get_transition(self):
        return self.trans


class PmcModules:
    """ pMC with modules """
    param = []

    # Dictionary storing every parameters, their name, their type and their value (None if not initialized)
    value_param = {}

    # Character string used to determine the transitions used for the same state
    expression = ""

    # Dictionary storing the total probability of the transitions of a state and the parameters used
    equation_system = {}

    # Stores the type of the pMC
    type = ""

    varGlobalInit = {}
    # varGlobalMin = {}
    # varGlobalMax = {}
    current_value_global = {}
    modules = []
    reward = []

    def __init__(self):
        pass

    def add_pmc_type(self, pmc_type):
        """ specify the type of pMC"""
        if pmc_type == "dtmc" or pmc_type == "ctmc" or pmc_type == "probabilistic":
            self.type = pmc_type
        else:
            print("pMC type not known", pmc_type)

    def get_pmc_type(self):
        """ return the type of the pMC"""
        if self.type:
            return self.type
        else:
            return False

    def add_parameter(self, param):
        """ add a parameter (or uninitialized constant) """
        self.param += [param]

    def add_global_variable(self, state, min_value, ini=None):
        """ add a global variable with initial value """
        if ini is None:
            init = min_value
        else:
            init = ini
        self.varGlobalInit[state] = init
        self.current_value_global[state] = init

    def add_module(self, mod):
        """ add a module """
        mod.set_pmc(self)
        self.modules += [mod]

    def reinitialization(self):
        """ reinit all module and global variables to their initial values"""
        self.current_value_global = copy_dict(self.varGlobalInit)
        for mod in self.modules:
            mod.reinitialization()

    def get_possible_transitions(self):
        """ return the doable transitions """
        res = []
        for m in self.modules:
            res += [m.get_possible_transitions(self.current_value_global)]
        # res = [m.get_possible_transitions(self.current_value_global) for m in self.modules]
        name = [[tr[0] for tr in t if tr[0] != ""] for t in res]

        def good_name(action):
            """ indicate whether the name is ok for all modules"""
            for i in range(0, len(res)):
                if (action in self.modules[i].alph) and (action not in name[i]):
                    return False
            return True
        name = [list(filter(good_name, na)) for i, na in enumerate(name)]
        res2 = [list(filter(lambda t: (t[0] in name[i]) or t[0] == "", a))
                for i, a in enumerate(res)]
        return res2

    def get_module(self, name):
        """ return the module corresponding to name"""
        for mod in self.modules:
            if mod.name == name:
                return mod
        raise Exception("moule "+name+" not found")

    def set_init_value(self, variable, value):
        """ set a new initial value for a global variable """
        if variable in self.current_value_global:
            self.current_value_global[variable] = value
        else:
            for mod in self.modules:
                mod.set_init_value(variable, value)

    def add_reward(self, name, cond, reward):
        """ add a reward """
        self.reward += [[name, cond, reward]]

    def get_reward(self, act):
        """ return the reward of a given action """
        # print(self.reward)
        cumu_reward = 0
        substitution = self.get_valuation()
        for rew_action, cond, reward in self.reward:
            if (rew_action == act or act == '') and mysub(cond, substitution):
                cumu_reward += mysub(reward, substitution)
        return cumu_reward

    def maj(self, update):
        """ update the globale variable and all modules according to up"""
        valuation = self.get_valuation()
        for mod in self.modules:
            mod.maj(update, self.current_value_global)
        temp = {}
        for k in self.current_value_global:
            if k in update:
                temp[k] = mysub(update[k], valuation)
            else:
                temp[k] = self.current_value_global[k]
        self.current_value_global = temp

    def get_param(self):
        return self.param

    def get_valuation(self):
        """ return the current value of all variable (globale+sates in modules)"""
        return {**dict(i for mod in self.modules
                       for i in mod.current_value_state.items()), **self.current_value_global}

    def get_states(self):
        """returns the states of all modules"""

        total_states = []

        for i in self.modules:
            total_states.append(i.get_states())
        return total_states

    def get_state(self, module, index):
        """returns a selected state from a module"""

        module_states = module.get_states()

        if not module_states:
            raise Exception("No states in the module")
        else:
            if len(module_states) >= index:
                return module_states[index]
            else:
                raise Exception("Not enough states in the module")

    def get_modules(self):
        """returns the modules"""

        """total_module = []

        for i in self.modules:
            total_module.append(i)"""
        return self.modules

    def reevaluation(self, module):
        """ reevaluates the value of variables"""
        non_init = {}
        for val in module.maximum_value_state:

            # If the variable's type isn't 'int', 'float', 'double' or 'bool', it's considered uninitialized
            # it's then stored in the list
            if type(module.maximum_value_state[val]) != 'int' \
                    or type(module.maximum_value_state[val]) != 'float' \
                    or type(module.maximum_value_state[val]) != 'double' \
                    or type(module.maximum_value_state[val]) != 'bool':
                non_init[val] = None

        while len(non_init) > 0:

            copy = deepcopy(non_init)

            for i in non_init:

                current = module.maximum_value_state[i]

                if str(current) in self.value_param:

                    if module.maximum_value_state[i] == current:
                        new_maxi = self.value_param[str(current)][1]
                    else:
                        new_maxi = module.maximum_value_state[i]
                    module.remove_state(i)
                    module.add_state(i, 0, new_maxi)

                elif module.current_value_state[i] in module.current_value_state:

                    new_mini = module.initial_value_state[i]

                    if module.maximum_value_state[i] == current:
                        new_maxi = module.maximum_value_state[i]
                    else:
                        new_maxi = module.maximum_value_state[i]
                    module.remove_state(i)
                    module.add_state(i, new_mini, new_maxi)
                del copy[i]
            non_init = copy

        # This list stores all the uninitialized variables
        non_init = {}
        for val in module.current_value_state:

            # If the variable's type isn't 'int', 'float', 'double' or 'bool', it's considered uninitialized
            # it's then stored in the list
            if type(module.current_value_state[val]) != 'int' \
                    or type(module.current_value_state[val]) != 'float' \
                    or type(module.current_value_state[val]) != 'double' \
                    or type(module.current_value_state[val]) != 'bool':
                non_init[val] = None

        while len(non_init) > 0:
            # print(len(non_init))

            copy = deepcopy(non_init)

            for i in non_init:
                # print(i)
                current = module.current_value_state[i]

                if str(current) in self.value_param:
                    # print("il est la")
                    new_mini = module.initial_value_state[i]

                    if module.maximum_value_state[i] == current:
                        new_maxi = self.value_param[str(current)][1]
                    else:
                        new_maxi = module.maximum_value_state[i]
                    new_init = self.value_param[str(current)][1]
                    # print(new_init)
                    module.remove_state(i)
                    module.add_state(i, new_mini, new_maxi, new_init)

                elif module.current_value_state[i] in module.current_value_state:
                    # print("ou ici")
                    new_mini = module.initial_value_state[i]

                    if module.maximum_value_state[i] == current:
                        new_maxi = module.maximum_value_state[i]
                    else:
                        new_maxi = module.maximum_value_state[i]
                    module.remove_state(i)
                    module.add_state(i, new_mini, new_maxi, self.value_param[str(i)][1])
                del copy[i]
            non_init = copy
