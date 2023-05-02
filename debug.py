import sys

try:
    """
    Tenta redefinir a funcao de impressao do python para ela só funcionar quando o modo de debug estiver ativado

    Returns:
        function: a nova funcao de impressao que sera usada
    """
    import builtins
    def print(*args, **kwargs):
        if '-d' in sys.argv:
            type(__builtins__)
            builtins.print(*args, **kwargs)
except:
    pass