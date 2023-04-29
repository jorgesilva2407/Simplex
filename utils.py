from fractions import Fraction
from typing import NamedTuple
import re

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
    coefs['__CONST__'] = 0
    var = '__CONST__'
    val = Fraction(1,1)
    i = 0
    
    while i < len(norm_exp):
        if norm_exp[i] == '+':
            coefs[var] = val
            var = '__CONST__'
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
    
    right['__CONST__'] -= left['__CONST__']
    left.pop('__CONST__')
    
    for var in right:
        if var == '__CONST__':
            continue
        elif var in left:
            left[var] -= right[var]
        else:
            left[var] = right[var]

    right = {const: right['__CONST__'] for const in right if const == '__CONST__'}

    if right['__CONST__'] < Fraction(0,1):
        if op == '<=':
            op = '>='
        elif op == '>=':
            op = '<='
        
        for var in left:
            left[var] = 0 - left[var]
        
        right['__CONST__'] = 0 - right['__CONST__']
    
    return ExprCoefs(left, op, right)
