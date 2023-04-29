from utils import *

def parse(file):
    """
    Transforma a entrada do arquivo em matrizes do numpy

    Args:
        file (str): nome do arquivo de entrada

    Raises:
        AssertionError: Mais de uma funcao objetivo no arquivo de entrada

    Returns:
        tuple: matrizes do numpy geradas a partir da entrada
    """

    with open(file) as f:
        lines = f.readlines()
        obj = lines[0]
        restrictions = lines[1:]
        parsed_obj = parse_obj(obj)
        parsed_restrictions = parse_restrictions(restrictions)
        
    return None

def parse_obj(obj):
    """
    Interpreta a funcao objetivo do programa

    Args:
        line (str): linha da funcao que possui a funcao objetivo

    Returns:
        dict(): dicionario que associa as variaveis da funcao objetivo e suas constantes associadas
    """
    obj_type = 'MAX' if 'MAX' in obj else 'MIN'

    tokens = get_tokens(obj)

    coefs = get_coeficients(tokens)
    return obj_type, coefs

def parse_restrictions(restrictions):
    """
    Recebe uma lista com restricoes na forma de strings e faz o parsing delas

    Args:
        restrictions (list of strings): lista contendo as restricoes a serem interpretadas

    Raises:
        RuntimeError: alguma restricao foi mal especificada

    Returns:
        dict: dicionario com os coeficientes associados a cada variavel em cada restricao
    """
    ste_exprs = []

    for restriction in restrictions:
        if '==' in restriction:
            #* Exemplo: A restricao x1 + x2 = x3 eh equivalente a x1 + x2 <= x3 e x1 + x2 >= x3, e a segunda destas eh equivalente a x3 <= x1 + x2
            left, right = restriction.strip().split(sep='==')
            left, right = get_tokens(left), get_tokens(right)
            ste_exprs += [Expr(left, '<=', right)]
            ste_exprs += [Expr(left, '>=', right)]
        
        elif '>=' in restriction:
            #* A restricao x1 + x2 >= x3 eh equivalente a x3 <= x1 + x2
            left, right = restriction.strip().split(sep='>=')
            ste_exprs += [Expr(get_tokens(right), '>=', get_tokens(left))]
        
        elif '<=' in restriction:
            #* A restricao x1 + x2 <= x3 eh representada por ela propria no contexto em questao
            left, right = restriction.strip().split(sep='<=')
            ste_exprs += [Expr(get_tokens(left), '<=', get_tokens(right))]
        
        elif len(restriction) <= 1:
            #* caso em que existe uma linha extra no arquivo
            continue
        
        else:
            #* Caso em que nenhuma das operacoes validas foi invocada
            raise RuntimeError('Restricao impropria')

    #* registra as variaveis do problema em um set
    variables = set()
    for expr in ste_exprs:
        variables = variables.union(get_variables(expr.left))
        variables = variables.union(get_variables(expr.right))

    coefs = [simplify(ExprCoefs(get_coeficients(expr.left), expr.op, get_coeficients(expr.right))) for expr in ste_exprs]

    

    return coefs