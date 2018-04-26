from collections import defaultdict
from ply import lex, yacc
from sympy.parsing.sympy_parser import parse_expr as rea
from sympy import Function, Symbol
from modules import PmcModules, Module
# from memory_profiler import profile


# used to define multiple parameters in one go of the form param int p{0..N}; utilise apres p{x}
paramnameglob = ""


class MyFunc(Function):
    @classmethod
    def eval(cls, exp):
        global paramnameglob
        if exp.is_Number:
            return Symbol(paramnameglob + str(exp))


# @profile
def myparse(filepath):
    # associate to string their expression
    dic = {}
    # associate to string their type (or default when variable are not yet define) !! float are treated as int
    type = defaultdict(lambda: "default")
    
    # The pmc we are building
    pmc = PmcModules()
    
    # The module that is currently built
    curentMod = None


# ----------------------- @ LEXER ----------------------------@
    tokens = (
        'DOUBLE',
        'FLOAT',

        # basic operators
        'PLUS', 'MINUS', 'MULT', 'DIV',
        'EQUAL',
        'AND', 'NOT', 'OR',
        'LEQ', 'GEQ', 'GS', 'LS',

        # type of the parsed file
        'DTMC', 'CTMC', 'MDP',

        # keywords
        'MODULE', 'ENDMODULE', 'REWARDS', 'ENDREWARDS', 'INIT', 'ENDINIT',
        'PARAM', 'CONST', 'LABEL', 'GLOBALL', 'FORMULA',

        # string for variable names
        'NAME',

        # special char
        'DDOT', 'LCROCHET', 'RCROCHET', 'POINTPOINT', 'LPAR', 'RPAR',
        'FLECHE', 'NEW', 'SC', 'VIRGULE', 'QUOTE', 'LACCO', 'RACCO',

        # types
        'INT', 'TYPEFLOAT', 'BOOL', 'INTEGER',

        # boolean
        'TRUE', 'FALSE',
    )

    def t_ccode_comment(t):
        r'//.*\n'
        pass

    def t_POINTPOINT(t):
        r'\.\.'
        return t

    def t_FLECHE(t):
        r'->'
        return t

    def t_LEQ(t):
        r'<='
        return t

    def t_GEQ(t):
        r'>='
        return t

    def t_GS(t):
        r'>'
        return t

    def t_LS(t):
        r'<'
        return t

    def t_NOT(t):
        r'!'
        return t

    def t_FLOAT(t):
        r"""(\d+(\.\d+)?)([eE][-+]? \d+)?"""
        return t

    def t_INTEGER(t):
        r'\d+'
        return t

    def t_MDP(t):
        r"(mdp)|(nondeterministic)"
        return t

    def t_CTMC(t):
        r"(ctmc)|(stochastic)"
        return t

    def t_DTMC(t):
        r"(probabilistic)|(dtmc)"
        return t

    def t_PARAM(t):
        r"param"
        return t

    def t_CONST(t):
        r"const"
        return t

    def t_FORMULA(t):
        r"formula"
        return t

    def t_INT(t):
        r"int"
        return t

    def t_BOOL(t):
        r"bool"
        return t

    def t_TYPEFLOAT(t):
        r"float"
        return t

    def t_DOUBLE(t):
        r"double"
        return t

    def t_GLOBALL(t):
        r"global"
        return t

    def t_INIT(t):
        r"init"
        return t

    def t_ENDINIT(t):
        r"endinit"
        return t

    def t_MODULE(t):
        r"module"
        return t

    def t_ENDMODULE(t):
        r"endmodule"
        return t

    def t_REWARDS(t):
        r"rewards"
        return t

    def t_ENDREWARDS(t):
        r"endrewards"
        return t

    def t_TRUE(t):
        r"true"
        return t

    def t_FALSE(t):
        r"false"
        return t

    def t_LABEL(t):
        r'label'
        return t

    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_DIV = r'/'
    t_MULT = r'\*'
    t_NAME = r'[a-zA-Z_][a-zA-Z_0-9]*'
    t_EQUAL = r'='
    t_DDOT = r':'
    t_LCROCHET = r'\['
    t_RCROCHET = r'\]'
    t_LACCO = r'\{'
    t_RACCO = r'\}'
    t_LPAR = r'\('
    t_RPAR = r'\)'
    t_NEW = r'\''
    t_SC = r';'
    t_AND = r'&'
    t_VIRGULE = r','
    t_QUOTE = r'\"'
    t_OR = r'\|'


# ignore space tab and new line
    t_ignore = ' \n\t'

# error handeling in lexer
    def t_error(t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)
        raise Exception("Illegal char")

    lexer = lex.lex()

    # --------------------- PARSER ------------------------ #

    # PRECEDENCE of opreators
    precedence = (
                  ('left', 'OR'),
                  ('left', 'AND'),
                  ('nonassoc', 'GEQ', 'LEQ', 'LS', 'GS', 'EQUAL'),
                  ('left', 'PLUS', 'MINUS'),
                  ('left', 'MULT', 'DIV'),
                  ('right', 'NOT', 'UNMINUS'),
                  ('right', 'LACCO', 'LCROCHET', 'LPAR'),
                  ('left', 'RACCO', 'RCROCHET', 'RPAR'),
                  ('left', 'DDOT'),
                  ('left', 'PARAM', 'CONST', 'NAME'),
                  ('right', 'MODULE', 'REWARDS'),
                  ('left', 'ENDMODULE', 'ENDREWARDS'),
                  ('left', 'SC'),
                  )

    # STARTING rule
    start = 'def'

    # empty for list
    def p_empty(p):
        '''empty :'''

    def p_begining(p):
        'def : mdptype unfold'
        # print(p[1])

    def p_unfold(p):
        '''unfold : declParamList unfold
                  | declConstList unfold
                  | declGlobalList unfold
                  | moduleList unfold
                  | labelList unfold
                  | rewards unfold
                  | initdef unfold
                  | formulas unfold
                  | declParamList
                  | declConstList
                  | declGlobalList
                  | moduleList
                  | labelList
                  | rewards
                  | initdef
                  | formulas'''

    def p_formulas(p):
        '''formulas : formula SC
                    | formula SC formulas'''

    def p_formula(p):
        '''formula : FORMULA NAME EQUAL funexp'''

        t, e = p[4]
        dic[p[2]] = rea(e, dic)

    # type : MDP
    def p_mdptype(p):
        '''mdptype : MDP
                   | CTMC
                   | DTMC'''

        if p[1] not in ("dtmc", "probabilistic", "ctmc"):
            print(p[1])
            print(" WARNING !! only probabilistic model are supported yet")

    # list of PARAMETERS separted by a semicolon
    def p_decl_param_list(p):
        '''declParamList : declParam SC
                         | declParam SC declParamList'''

    def p_decl_paraml(p):
        '''declParam : PARAM type NAME DDOT LCROCHET funexp POINTPOINT funexp RCROCHET
                     | PARAM type NAME'''

        dic[p[3]] = rea(p[3], dic)
        type[p[3]] = "int"
        pmc.add_parameter(dic[p[3]])

    def p_decl_param_multiple(p):
        '''declParam : PARAM type NAME LACCO funexp POINTPOINT funexp RACCO'''

        global paramnameglob
        paramnameglob = p[3]
        dic[p[3]] = MyFunc
        t1, e1 = p[5]
        t2, e2 = p[7]
        for i in range(rea(e1, dic), rea(e2, dic) + 1):
            pmc.add_parameter(Symbol(p[3] + str(i)))

    def p_type(p):
        '''type : empty
                | INT
                | TYPEFLOAT
                | BOOL
                | DOUBLE'''

        if p[1] == "bool":
            p[0] = "bool"
        else:
            p[0] = "int"

    # list of CONSTANTS separated by a semicolon
    def p_decl_const_listl(p):
        '''declConstList : declConst SC
                         | declConst SC declConstList'''

    def p_decl_constl(p):
        '''declConst : CONST type NAME EQUAL funexp
                     | CONST type NAME'''

        if (len(p) == 5):
            t, e = p[5]
            if t == p[2]:
                dic[p[3]] = rea(e, dic)
                type[p[3]] = p[2]
            else:
                raise Exception("invalid type cons decl : " + p[3] + " " + t + " " + p[2])

    # list of GLOBAL VARIABLES separated by a semicolon
    def p_globall_list(p):
        '''declGlobalList : declGlobal SC
                          | declGlobal SC declGlobalList'''

    def p_globall(p):
        '''declGlobal : GLOBALL NAME DDOT LCROCHET funexp POINTPOINT funexp RCROCHET
                      | GLOBALL NAME DDOT LCROCHET funexp POINTPOINT funexp RCROCHET INIT funexp
                      | GLOBALL NAME DDOT BOOL'''

        dic[p[2]] = rea(p[2], dic)
        if len(p) > 10:
            type[p[2]] = "int"
            t1, e1 = p[5]
            t2, e2 = p[7]
            pmc.add_global_variable(dic[p[2]], rea(e1, dic), rea(e2, dic))
        elif len(p) > 6:
            t1, e1 = p[5]
            t2, e2 = p[7]
            t3, e3 = p[10]
            type[p[2]] = "int"
            pmc.add_global_variable(dic[p[2]], rea(e1, dic), rea(e2, dic), rea(e3, dic))
        else:
            type[p[2]] = "bool"
            pmc.add_global_variable(dic[p[2]], rea("true", dic), rea("false", dic))

    # list of MODULES
    def p_module_list(p):
        '''moduleList : MODULE module endmodule
                      | MODULE module endmodule moduleList'''

    # For a module either
    # 1 define a new module
    # 2 define a module as renaming a previous one
    def p_module(p):
        '''module : modName stateList transList
                  | reModName  LCROCHET listIdState RCROCHET '''

    def p_new_mod(p):
        '''modName : NAME'''

        nonlocal curentMod
        curentMod = Module(p[1])

    def p_renewmod(p):
        '''reModName : NAME EQUAL NAME'''

        nonlocal curentMod
        mod = pmc.get_module(p[3])
        curentMod = mod.copy(p[1])

    # renaming a module
    def p_list_id_state(p):
        '''listIdState : NAME EQUAL NAME
                       | NAME EQUAL NAME VIRGULE listIdState'''

        dic[p[3]] = rea(p[3], dic)
        type[p[3]] = type[p[1]]
        try:
            curentMod.replace(dic[p[1]], dic[p[3]])
        except:
            curentMod.replace(p[1], p[3])

    # when finished add the created module to pmc
    def p_endmodule(p):
        '''endmodule : ENDMODULE'''

        nonlocal curentMod
        pmc.add_module(curentMod)
        curentMod = None

    # list of declarition of states
    def p_state_list(p):
        '''stateList : stateDecl SC
                     | stateDecl SC stateList'''

    # state declaration with our without initial value
    def p_statedecl(p):
        '''stateDecl : NAME DDOT LCROCHET funexp POINTPOINT funexp RCROCHET
                     | NAME DDOT LCROCHET funexp POINTPOINT funexp RCROCHET INIT funexp
                     | NAME DDOT BOOL'''

        dic[p[1]] = rea(p[1], dic)
        if len(p) > 8:
            _, e1 = p[4]
            _, e2 = p[5]
            _, e3 = p[9]
            curentMod.add_state(dic[p[1]], rea(e1, dic), rea(e2, dic), rea(e3, dic))
            type[p[1]] = "int"
        elif len(p) > 5:
            type[p[1]] = "int"
            _, e1 = p[4]
            _, e2 = p[6]
            curentMod.add_state(dic[p[1]], rea(e1, dic), rea(e2, dic))
        else:
            type[p[1]] = "bool"
            curentMod.add_state(dic[p[1]], True, False)

    # list of transition
    def p_trans_list(p):
        '''transList : trans SC
                     | trans SC transList'''

    # transition without or with name
    def p_trans(p):
        '''trans : LCROCHET RCROCHET funexp FLECHE updatesProb
                 | LCROCHET NAME RCROCHET funexp FLECHE updatesProb'''

        if len(p) == 6:
            t, e = p[3]
            if t == "bool":
                curentMod.add_transition("", rea(e, dic), p[5])
            else:
                raise Exception('Not bool in cond' + e)
        else:
            t, e = p[4]
            if t == "bool":
                curentMod.add_transition(p[2], rea(e, dic), p[6])
            else:
                raise Exception('Not bool in cond'+e)

    def p_updates_prob(p):
        '''updatesProb : funexp DDOT updates PLUS updatesProb
                        | funexp DDOT updates
                        | updates'''

        if len(p) > 4:
            _, e = p[1]
            p[0] = p[5] + [[rea(e, dic), p[3]]]
        elif len(p) > 3:
            _, e = p[1]
            p[0] = [[rea(e, dic), p[3]]]
        else:
            p[0] = [[1, p[1]]]

    def p_updates(p):
        '''updates : upd
                   | upd AND updates'''

        if len(p) > 2:
            p[0] = {}
            for a in p[1]:
                p[0][a] = p[1][a]
            for b in p[3]:
                p[0][b] = p[3][b]
        else:
            p[0] = p[1]

    def p_upd(p):
        '''upd : LPAR NAME NEW EQUAL funexp RPAR'''

        _, e = p[5]
        p[0] = {rea(p[2], dic): rea(e, dic)}

    # list of LABELS separated by a semicolon
    def p_label_list(p):
        '''labelList : label SC
                     | label SC labelList'''


    def p_label(p):
        '''label : LABEL QUOTE NAME QUOTE EQUAL listCond'''

    def p_list_cond(p):
        '''listCond : NAME EQUAL funexp
                    | NAME EQUAL funexp AND listCond'''

    # REWARDS
    def p_rewards(p):
        '''rewards : REWARDS rew ENDREWARDS
                   | REWARDS rew ENDREWARDS rewards'''

    def p_rew(p):
        '''rew : QUOTE NAME QUOTE funexp DDOT funexp SC
               | LCROCHET NAME RCROCHET funexp DDOT funexp SC
               | LCROCHET RCROCHET funexp DDOT funexp SC
               | QUOTE NAME QUOTE funexp DDOT funexp SC rew
               | LCROCHET RCROCHET funexp DDOT funexp SC rew
               | LCROCHET NAME RCROCHET funexp DDOT funexp SC rew'''
        if p[1] == "[":
            if len(p) == 9:
                t, e = p[4]
                _, er = p[6]
                if t == 'bool':
                    pmc.add_reward(p[2], rea(e, dic), rea(er, dic))
                else:
                    raise Exception("Invalid type in condition of reward " + p[2])
            else:
                t, e = p[3]
                _, er = p[5]
                if t == 'bool':
                    pmc.add_reward('', rea(e, dic), rea(er, dic))
                else:
                    raise Exception("Invalid type in condition of reward " + p[2])

    # init def:
    def p_initdef(p):
        '''initdef : INIT initlist ENDINIT'''

    def p_inilist(p):
        '''initlist : ainit
                    | ainit AND initlist'''

    def p_ainit(p):
        '''ainit : NAME EQUAL funexp'''

        t1, e = p[3]
        t2 = type[p[1]]
        if t1 == t2:
            pmc.set_init_value(rea(p[1], dic), rea(e, dic))
        else:
            raise Exception("bad type in init :" + e + " = " + p[1])

    # EXPRESSION AS FUNCTION (with parameters and CONSTANTs

    def p_funexpbinop(p):
        '''funexp : funexp PLUS funexp
                  | funexp MINUS funexp
                  | funexp DIV funexp
                  | funexp MULT funexp'''

        t1, e1 = p[1]
        t2, e2 = p[3]
        if t1 == t2 or t1 == "default" or t2 == "default":
            p[0] = ["int", "(%s)" % (e1 + p[2] + e2)]
        else:
            raise Exception("Incompatible type in : " + e1 + p[2] + e2)

    def p_funexpbinopcomp(p):
        '''funexp : funexp GEQ funexp
                  | funexp GS funexp
                  | funexp LS funexp
                  | funexp LEQ funexp'''

        t1, e1 = p[1]
        t2, e2 = p[3]
        if t1 == t2 or t1 == "default" or t2 == "default":
            p[0] = ["bool", "(%s)" % (e1 + p[2] + e2)]
        else:
            raise Exception("Incompatible type in : " + e1 + p[2] + e2)

    def p_funexpequality(p):
        '''funexp : funexp EQUAL funexp'''

        t1, e1 = p[1]
        t2, e2 = p[3]
        if (t1 == t2 and (t1 == "bool" or t1 == "default")) or ("default" in (t1, t2) and "bool" in (t1, t2)):
            p[0] = ["bool", "(%s&%s)" % (e1, e2)]
        elif t1 == t2 or t1 == "default" or t2 == "default":
            p[0] = ["bool", "((%s >= 0)&(%s <= 0))" % (e1 + "-" + e2, e1 + "-" + e2)]
        else:
            raise Exception("Incompatible type in : " + e1 + p[2] + e2)

    def p_funexpand(p):
        '''funexp : funexp AND funexp
                  | funexp OR funexp'''

        t1, e1 = p[1]
        t2, e2 = p[3]
        if t1 == t2 or t1 == "default" or t2 == "default":
            p[0] = ["bool", "(%s)" % (e1 + p[2] + e2)]
        else:
            raise Exception("Incompatible type in : " + e1 + p[2] + e2)

    def p_funexpunary(p):
        '''funexp : LPAR funexp RPAR
                  | NOT funexp
                  | MINUS funexp %prec UNMINUS'''

        if len(p) > 3:
            t, e = p[2]
            p[0] = [t, "(%s)" % e]
        elif p[1] == '!':
            t, e = p[2]
            if t == "bool" or t == "default":
                p[0] = ["bool", "(~%s)" % e]
            else:
                raise Exception("incompatible type : ~" + e)
        else:
            t, e = p[2]
            if t == "int" or t == "default":
                p[0] = ["int", "(- %s)" % e]
            else:
                raise Exception("incompatible type : -" + e)

    def p_funexp_float(p):
        '''funexp : FLOAT'''
        p[0] = ["int", p[1]]


    def p_funexp_integer(p):
        '''funexp : INTEGER'''
        return p

    def p_funexp_true_false(p):
        '''funexp : TRUE
                  | FALSE'''

        p[0] = ["bool", p[1]]

    def p_funexp_var(p):
        '''funexp : NAME'''

        p[0] = [type[p[1]], p[1]]

    def p_funexp_param(p):
        '''funexp : NAME LACCO funexp RACCO'''

        _, e = p[3]
        p[0] = ["int", "%s(%s)" % (p[1], e)]

    def p_funexp_func(p):
        '''funexp : NAME LPAR funexp RPAR'''

        _, e = p[3]
        p[0] = ["int", "%s(%s)" % (p[1], e)]


# handeling error in parsing
    def p_error(p):
        print("Syntax error in input!")
        print(p)
        print(yacc.debug_file)
        raise Exception("Syntax error")

    parser = yacc.yacc()

    with open(filepath, 'r') as myfile:
        parser.parse(myfile.read())

    print("\nparsing OK\n")

    pmc.reinit()

    return pmc
