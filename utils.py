from fractions import Fraction
from typing import NamedTuple
import re
import numpy as np
from debug import *
np.set_printoptions(precision=2, linewidth=200)

class Expr(NamedTuple):
    """
    Classe que agrupa o lado direito e esquerdo de uma expressao representados na forma de tokens

    Args:
        NamedTuple (list, str, list): uma lista com o lado esquerdo da expressao e outra lista com o lado direito e a operacao que envolve os dois lados

    Raises:
        RuntimeError: None

    Returns:
        None: Nenhum
    """
    left: list
    op: str
    right: list

    def __str__(self) -> str:
        """
        Transforma o objeto Expr em uma string

        Returns:
            str: string que descreve o objeto Expr
        """
        exp = ''
        for token in self.left:
            exp += token + ' '
        exp += self.op + ' '
        for token in self.right:
            exp += token + ' '
        return exp

class ExprCoefs(NamedTuple):
    """
    Classe que agrupa o lado direito e esquerdo de uma na forma de dicionarios que associam variaveis e coeficientes

    Args:
        NamedTuple (dict, str, dict): um dicionario com o conteudo do lado esquerdo da expressao e outro com o lado direito e a comparacao entre os dois lados

    Returns:
        None: Nenhum
    """
    left: dict
    op: str
    right: dict

    def __str__(self) -> str:
        """
        Tranasforma o objeto ExprCoefs em uma strings

        Returns:
            str: string que descreve o objeto ExprCoefs
        """
        exp = ''
        left_vars = list(self.left.keys())
        right_vars = list(self.right.keys())
        for i in range(len(left_vars)-1):
            exp += f'{self.left[left_vars[i]]} * {left_vars[i]} + '
        exp += f'{self.left[left_vars[-1]]} * {left_vars[-1]}'
        exp += ' ' + self.op + ' '
        for i in range(len(right_vars)-1):
            exp += f'{self.right[right_vars[i]]} * {right_vars[i]} + '
        try: 
            exp += f'{self.right[right_vars[-1]]} * {right_vars[-1]}'
        except:
            exp = 'Objetive function: ' + exp
        return exp

def get_tokens(exp):
    """
    Separa uma string que representa uma expressao aritmetica linear
    em operadores, constantes e variaveis 

    Args:
        exp (str): a expressao a ser desmembrada

    Returns:
        list: lista com os elementos da expressao
    """
    normalized_exp = re.sub('(MAX)|(MIN)|( )','',exp)
    funcs = [
        lambda x: re.sub('\+', ' + ', x),
        lambda x: re.sub('-', ' - ', x),
        lambda x: re.sub('\*', ' * ', x),
        lambda x: re.sub('/', ' / ', x)
    ]

    acc = normalized_exp

    for f in funcs:
        acc = f(acc)

    return acc.split()

def is_variable(exp):
    """
    Retorna se um valor eh variavel ou nao

    Args:
        exp (str): o valor a ser avaliado

    Returns:
        bool: se eh uma variavel ou nao
    """
    return True if re.match(r'([0-9]+)|(\+)|(\*)|/|-', exp) is None else False

def get_variables(expr):
    """
    Retorna um set com todas as variaveis da expressao

    Args:
        expr (list of strings): a expressao separada em tokens

    Returns:
        set: o conjunto de variaveis da expressao
    """
    variables = set()
    for token in expr:
        if is_variable(token):
            variables.add(token)
    
    return variables

def add_one_before_variable(exp):
    """
    Em uma lista de tokens, substitui adiciona um elemento '1' antes da ocorrencia da variavel

    Args:
        exp (list of strings): lista com os tokens de uma expressao

    Returns:
        list of strings: a versao extendida da expressao avaliada
    """
    norm_expr = []
    for token in exp:
        if is_variable(token):
            norm_expr.append('1')
            norm_expr.append('*')
            norm_expr.append(token)
        else:
            norm_expr.append(token)
    return norm_expr

def remove_op_minus(exp):
    """
    Remove a operacao de subtracao da expressao e a substitui pela soma com a negacao do proximo termo

    Args:
        exp (list of strings): lista com os tokens da expressao 

    Returns:
        list of strings: a versao extendida da expressao avaliada
    """
    norm_expr = []
    buffer = ''
    for token in exp:
        if buffer != '':
            norm_expr.append(buffer+token)
            buffer = ''
            continue
        
        if token == '-':
            norm_expr.append('+')
            buffer = '-'
        else:
            norm_expr.append(token)
    return norm_expr

def remove_op_mult(exp):
    """
    Remove o token associado a operacao de multiplicacao da expressao, uma vez que eh redundante

    Args:
        exp (list of strings): lista com os tokens da expressao 

    Returns:
        list of strings: a versao condensada da expressao avaliada
    """
    return list(filter(lambda x: x != '*', exp))

def make_association(norm_exp):
    """
    Recebe uma expressao que foi normalizada e recupera as constantes associadas a cada variavel

    Args:
        norm_exp (list of strings): lista com os tokens da expressao 

    Returns:
        dict: dicionario em que as chaves sao variaveis da expressao e os valores sao as constantes associadas a cada variavel
    """
    coefs = {variable: Fraction(0,1) for variable in get_variables(norm_exp)}
    coefs['__ONE__'] = 0
    var = '__ONE__'
    val = Fraction(1,1)
    i = 0
    
    while i < len(norm_exp):
        if norm_exp[i] == '+':
            coefs[var] = val
            var = '__ONE__'
            val = Fraction(1,1)
            i += 1
            continue
        
        if is_variable(norm_exp[i]):
            var = norm_exp[i]
        elif norm_exp[i] == '/':
            i += 1
            val *= Fraction(1,int(norm_exp[i]))
        else:
            val *= Fraction(int(norm_exp[i]),1)

        i += 1
    
    coefs[var] = val

    return coefs

def get_coeficients(expr):
    """
    Calcula os coeficientes associadas a cada variavel em uma expressao
    
    Args:
        expr (list of strings): a lista com os tokens da expressao

    Returns:
        dict: dicionario que associa uma variavel a seu coeficiente
    """
    funcs = [
        add_one_before_variable,
        remove_op_minus,
        remove_op_mult,
        make_association
    ]

    coefs = expr

    for f in funcs:
        coefs = f(coefs)

    return coefs

def simplify(expr):
    """
    Passa todas as variáveis para o lado esquerdo da expressao e as constantes para o lado direito e torna a constante do lado direito em positiva

    Args:
        expr (ExprCoefs): expressao na forma de coeficientes

    Returns:
        ExprCoefs: expressao simplificada na forma de coeficientes
    """
    left = expr.left
    op = expr.op
    right =  expr.right
    
    right['__ONE__'] -= left['__ONE__']
    left.pop('__ONE__')
    
    for var in right:
        if var == '__ONE__':
            continue
        elif var in left:
            left[var] -= right[var]
        else:
            left[var] = 0 - right[var]

    right = {const: right['__ONE__'] for const in right if const == '__ONE__'}

    if right['__ONE__'] < Fraction(0,1):
        if op == '<=':
            op = '>='
        elif op == '>=':
            op = '<='
        
        for var in left:
            left[var] = 0 - left[var]
        
        right['__ONE__'] = 0 - right['__ONE__']
    
    return ExprCoefs(left, op, right)


def sub_variables(obj, restrictions, variables):
    """
    Substitui as variaveis do programa por outras que podem ser processadas usando programacao linear

    Args:
        obj (dict): a funcao objetivo na forma de um dicionario
        restrictions (list of ExprCoefs): as restricoes do problema na forma de ExprCoefs
        variables (set of strings): as variaveis originais do problema

    Returns:
        dict, list of ExprCoefs, set, list of dicts: funcoes objetivo, restricoes e conjunto de variaveis
                                                     apos alteracao e as transformacoes de variaveis que foram feitas
    """
    variables_domain = []
    valid_restrictions = []

    #* encontra restricoes que definem o dominio de variaveis
    for i in range(len(restrictions)):
        if len(restrictions[i].left) == 1:
            variables_domain.append((i, restrictions[i]))
        else:
            valid_restrictions.append((i, restrictions[i]))
    
    #* junta as variaveis da funcao objetivo as das restricoes
    all_vars = set(obj.keys()).union(variables)
    all_vars.discard('__ONE__')

    sub_list = []
    keep_restriction = []

    #* define como serao feitas as substituicoes no problema
    for restriction in variables_domain:
        var = list(restriction[1].left.keys())[0]
        op = restriction[1].op
        const = restriction[1].right['__ONE__']/restriction[1].left[var]
        
        if const < 0:
            const = 0 - const
            if op == '<=':
                op = '>='
            elif op == '>=':
                op = '<='

        #* var na forma ideal
        if op == '>=' and const == Fraction(0,1):
            continue
        #* var menor ou igual a zero
        elif op == '<=' and const == Fraction(0,1):
            sub_list.append({'original': var, 
                             'new': '__INV__' + var,
                             'type': 'inv'})
        #* var limitada inferiormente 
        elif op == '>=' and const > Fraction(0,1):
            sub_list.append({'original': var, 
                             'new': '__SUM__' + var,
                             'type': 'sum',
                             'const': const})
        #* var limitada superiormente eh tratada como retricao do problema
        elif op == '<=' and const > Fraction(0,1):
            keep_restriction.append(restriction[0])

    #* encontra variaveis livres do programa
    free_vars = []
    for var in all_vars:
        is_free = True
        
        for va_d in variables_domain:
            if var in va_d[1].left:
                is_free = False
        
        if is_free:
            free_vars.append(var)

    #* define como serao feitas as substituicoes de variaveis livres
    for var in free_vars:
        sub_list.append({'original': var,
                         'new1': '__FREE1__'+var,
                         'new2': '__FREE2__'+var,
                         'type': 'free'})

    #* mantem certos indicadores de dominio como se fossem restricoes
    for i in keep_restriction:
        valid_restrictions.append((i, restrictions[i]))

    print('Valid Restrictions:')
    for rest in valid_restrictions:
        print(rest[1])

    print('*'*50)

    print('Substitutions:')
    for sub in sub_list:
        print(sub)
    
    print('*'*50)

    #* faz as substituicoes
    new_obj = sub_vars_obj(obj, sub_list)
    new_restrictions = [sub_vars_restriction(restriction, sub_list) for restriction in valid_restrictions]

    return new_obj, new_restrictions, sub_list

def sub_vars_obj(obj, sub_list):
    """
    Faz as substituicoes de variaveis na funcao objetivo

    Args:
        obj (dict): a funcao objetivo na forma de um dicionario
        sub_list (list of dicts): regras de substituicao

    Returns:
        dict: nova funcao objetivo
    """
    for i in range(len(sub_list)):
        if sub_list[i]['original'] in obj:
            if sub_list[i]['type'] == 'inv':
                obj[sub_list[i]['new']] = (0 - obj[sub_list[i]['original']])
                obj.pop(sub_list[i]['original'])
            elif sub_list[i]['type'] == 'sum':
                obj[sub_list[i]['new']] = obj[sub_list[i]['original']]
                if '__ONE__' in obj:
                    obj['__ONE__'] -= obj[sub_list[i]['original']]*sub_list[i]['const']
                else:
                    obj['__ONE__'] = 0 - obj[sub_list[i]['original']]*sub_list[i]['const']
                obj.pop(sub_list[i]['original'])
            elif sub_list[i]['type'] == 'free':
                obj[sub_list[i]['new1']] = obj[sub_list[i]['original']]
                obj[sub_list[i]['new2']] = 0 - obj[sub_list[i]['original']]
                obj.pop(sub_list[i]['original'])

    return obj

def sub_vars_restriction(restriction, sub_list):
    """
    Faz as substituicoes de variaveis nas restricoes

    Args:
        restriction (ExprCoefs): restricao na forma ExprCoefs
        sub_list (list of dicts): regras de substituicao

    Returns:
        ExprCoefs: nova restricao
    """
    new_restriction = restriction[1]
    
    for i in range(len(sub_list)):
        if sub_list[i]['original'] in new_restriction.left:
            if sub_list[i]['type'] == 'inv':
                new_restriction.left[sub_list[i]['new']] = (0 - new_restriction.left[sub_list[i]['original']])
                new_restriction.left.pop(sub_list[i]['original'])
            elif sub_list[i]['type'] == 'sum':
                new_restriction.left[sub_list[i]['new']] = new_restriction.left[sub_list[i]['original']]
                new_restriction.right['__ONE__'] += new_restriction.left[sub_list[i]['original']]*sub_list[i]['const']
                new_restriction.left.pop(sub_list[i]['original'])
            elif sub_list[i]['type'] == 'free':
                new_restriction.left[sub_list[i]['new1']] = new_restriction.left[sub_list[i]['original']]
                new_restriction.left[sub_list[i]['new1']] = 0 - new_restriction.left[sub_list[i]['original']]
                new_restriction.left.pop(sub_list[i]['original'])

    left = new_restriction.left
    op = new_restriction.op
    right = new_restriction.right

    if new_restriction.right['__ONE__'] < 0:
        for var in new_restriction.left:
            left[var] = 0 - new_restriction.left[var]
        
        right['__ONE__'] = 0 - new_restriction.right['__ONE__']

        if new_restriction.op == '<=':
            op = '>='
        elif new_restriction.op == '>=':
            op = '<='

    return ExprCoefs(left, op, right)

def to_normal_form(restrictions):
    """
    Coloca o problema na forma normal

    Args:
        restrictions (list of ExprCoefs): lista de restricoes na forma ExprCoefs

    Returns:
        list of ExprCoefs: lista com as restricoes do problema na forma padrao
    """
    norm_restrictions = []
    counter = 0
    for restriction in restrictions:
        left = restriction.left
        op = restriction.op
        right = restriction.right
        if op == '==':
            norm_restrictions.append(ExprCoefs(left, op, right))
        elif op == '<=':
            left[f'__EXTRA{counter}__'] = Fraction(1,1)
            norm_restrictions.append(ExprCoefs(left, '==', right))
        elif op == '>=':
            left[f'__EXTRA{counter}__'] = Fraction(-1,1)
            norm_restrictions.append(ExprCoefs(left, '==', right))
        counter += 1
    return norm_restrictions

def to_array(obj, restrictions):
    variables = set()
    for rest in restrictions:
        variables = variables.union(set(rest.left.keys()))
    variables = sorted(list(variables))

    print('Variables:')
    print(variables)

    line_obj = np.zeros(len(variables) + 1)
    for i in range(len(variables)):
        if variables[i] in obj:
            line_obj[i] = obj[variables[i]]

    if '__ONE__' in obj:
        line_obj[-1] = obj['__ONE__']

    print(line_obj)

    A = np.zeros((len(restrictions),len(variables)+1))
    for i in range(len(restrictions)):
        if '__ONE__' in restrictions[i].right:
            A[i,-1] = restrictions[i].right['__ONE__']
        
        for j in range(len(variables)):
            if variables[j] in restrictions[i].left:
                A[i,j] = restrictions[i].left[variables[j]]
    
    fmt = '%-10s '*(len(variables) + 1)
    print(fmt % tuple(variables + ['B']))
    print(fmt % tuple(['-'*10 for i in range(len(variables)+1)]))
    print(fmt % tuple(line_obj))
    for row in A:
        print(fmt % tuple(row))

    return None