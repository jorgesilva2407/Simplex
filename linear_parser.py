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

    type_obj, obj = parse_obj(lines[0])
    variables, restrictions = parse_restrictions(lines[1:])

    sub_obj, sub_restrictions, sub_rules = sub_variables(obj, restrictions, variables)

    print('Problem after substitution:')
    print(ExprCoefs(sub_obj, '', {}))
    for rest in sub_restrictions:
        print(rest)

    print('*'*150)

    normal_restrictions = to_normal_form(sub_restrictions)

    print('Restrictions in normal form:')
    for rest in normal_restrictions:
        print(rest)
    
    print('*'*150)

    all_variables = set()
    for rest in normal_restrictions:
        all_variables = all_variables.union(set(rest.left.keys()))

    all_variables = all_variables.union(sub_obj.keys())
    all_variables.discard('ONE')
    all_variables = sorted(list(all_variables))

    print('Variables:')
    print(all_variables)

    print('*'*150)

    matrices = to_array(sub_obj, normal_restrictions, all_variables)

    return matrices, sub_rules, all_variables, type_obj

def parse_obj(obj):
    """
    Interpreta a funcao objetivo do programa

    Args:
        obj (str): linha da funcao que possui a funcao objetivo

    Returns:
        str, set, dict: se o problema é maximo ou minimo, as variaveis e coeficientes da funcao objetivo
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
            left, right = restriction.strip().split(sep='==')
            left, right = get_tokens(left), get_tokens(right)
            ste_exprs += [Expr(left, '==', right)]
        
        elif '>=' in restriction:
            left, right = restriction.strip().split(sep='>=')
            ste_exprs += [Expr(get_tokens(left), '>=', get_tokens(right))]
        
        elif '<=' in restriction:
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

    print('Restrictions in Expr form:')
    for rest in ste_exprs:
        print(rest)

    print('*'*150)

    coefs = [ExprCoefs(get_coeficients(expr.left), expr.op, get_coeficients(expr.right)) for expr in ste_exprs]

    print('Restrictions in ExprCoefs form:')
    for exp in coefs:
        print(exp)

    print('*'*150)

    simp_coefs = [simplify(exp) for exp in coefs]

    print('Simplified Restrictions:')
    for exp in simp_coefs:
        print(exp)

    print('*'*150)

    return variables, simp_coefs