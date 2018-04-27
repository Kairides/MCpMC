""" Define pMC with modules """
import sympy


def copy_dict(dic):
    """ copy a dictionary """
    return {**dic}


def exp_to_fun(exp):
    try:
        free_var = exp.free_symbols
        b = True
    except:
        b = False
    if b:
        f = sympy.lambdify(free_var, exp, modules={'And': all, 'Or': any})

        def g(dic):
            eval = list(map(lambda x: dic[x], free_var))
            return f(*eval)
        return g
    else:
        return lambda *x: exp


def mysub(exp, dic):
    """ sympy subs but filtering local dictionary with only variables in exp"""
    try:
        free_var = exp.free_symbols
    except:
        free_var = []
    reduced_dic = {x: dic[x] for x in free_var if x in dic}
    if reduced_dic:
        return exp.subs(reduced_dic)
    return exp


class Module:
    """ module of a pMC with modules """
    def __init__(self, name):
        self.name = name
        self.initial_value_state = {}
        self.trans = []
        self.current_value_state = {}
        self.alph = {}

    def add_state(self, state, min_value, max_value, ini=None):
        """ add a state """
        if ini is None:
            init = min_value
        else:
            init = ini
        self.initial_value_state[state] = init
        self.current_value_state[state] = init

    def add_transition(self, name, cond, outcom):
        """ add a transition """
        self.alph[name] = True
        self.trans += [[name, cond, outcom, exp_to_fun(cond)]]

    def reinit(self):
        """ reinitialize all state to their initial value """
        self.current_value_state = copy_dict(self.initial_value_state)

    def eval(self, exp, global_substitution):
        """ evaluate an expression with the current value of the states
            given the current values of the global variables"""
        return mysub(exp, {**self.current_value_state, **global_substitution})

    def get_possible_transitions(self, global_substitution):
        """ return the transition doable given the current value of the global variable """
        return [[name, cond, outcom]
                for name, cond, outcom, funcond in self.trans
                if funcond({**global_substitution, **self.current_value_state})]

    def copy(self, name):
        """ return a copy of the module """
        mod = Module(name)
        mod.initial_value_state = copy_dict(self.initial_value_state)
        mod.current_value_state = copy_dict(self.current_value_state)
        mod.alph = copy_dict(self.alph)
        mod.trans = []

        for i in range(0, len(self.trans)):
            namet = self.trans[i][0]
            cond = self.trans[i][1]
            outcom = self.trans[i][2]

            mod.add_transition(namet, cond, outcom)

        return mod

    def replace(self, name1, name2):
        """ replace name1 with name2 in the module """
        if name1 in self.initial_value_state:
            self.initial_value_state[name2] = self.initial_value_state[name1]
            del self.initial_value_state[name1]
            self.current_value_state[name2] = self.current_value_state[name1]
            del self.current_value_state[name1]
        substitution = {name1: name2}
        new_trans = []
        for i in range(0, len(self.trans)):
            namet = self.trans[i][0]
            cond = self.trans[i][1]
            outcom = self.trans[i][2]
            if namet == name1:
                new_name = name2
                self.alph[name2] = True
                del self.alph[name1]
            else:
                new_name = namet
            new_outcom = []
            for var, update in outcom:
                new_outcom += [[mysub(var, substitution),
                                {mysub(state, substitution): mysub(state_up, substitution)
                                 for state, state_up in update.items()}]]
            new_trans += [[new_name, mysub(cond, substitution), new_outcom]]
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


class PmcModules:
    """ pMC with modules """
    param = []
    varGlobalInit = {}
    # varGlobalMin = {}
    # varGlobalMax = {}
    current_value_global = {}
    modules = []
    reward = []

    def __init__(self):
        pass

    def add_parameter(self, param):
        """ add a parameter """
        self.param += [param]

    def add_global_variable(self, state, min_value, max_value, ini=None):
        """ add a global variable with initial value"""
        if ini is None:
            init = min_value
        else:
            init = ini
        self.varGlobalInit[state] = init
        self.current_value_global[state] = init

    def add_module(self, mod):
        """ add a module """
        self.modules += [mod]

    def reinit(self):
        """ reinit all module and global variables to their initial values"""
        self.current_value_global = copy_dict(self.varGlobalInit)
        for mod in self.modules:
            mod.reinit()

    def get_possible_transitions(self):
        """ return the doable transitions """

        # All the possible transitions in the chain
        res = [m.get_possible_transitions(self.current_value_global) for m in self.modules]
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

    def get_valuation(self):
        """ return the current value of all variable (globale+sates in modules)"""
        return {**dict(i for mod in self.modules
                       for i in mod.current_value_state.items()), **self.current_value_global}
