import numpy as np
from debug import *
from utils import print_iter
from fractions import Fraction
import time

def simplex(matrices, type_obj):
    A, B, obj = matrices
    if type_obj == 'MIN':
        obj = -obj
    n_rest = A.shape[0]
    n_var = A.shape[1]

    right = np.eye(n_rest, dtype=np.object_)
    # left = np.eye(n_rest, dtype=np.object_)
    left = np.zeros((n_rest,1), dtype=np.object_)

    for i in range(n_rest):
        for j in range(n_rest):
            right[i,j] = Fraction(right[i,j])
            # left[i,j] = Fraction(left[i,j])
        left[i] = Fraction(0,1)

    for i in range(n_rest):
        if B[i] < 0:
            right[i,i] = -right[i,i]

    aux = np.concatenate((left,A,right,B), axis=1)
    # aux_obj = np.zeros(2*n_rest+n_var+1, dtype=np.object_)
    aux_obj = np.zeros(n_rest+n_var+2, dtype=np.object_)
    aux_obj[n_var+1:-1] = np.ones(n_rest)
    # aux_obj[n_rest+n_var:-1] = np.ones(n_rest)
    aux_obj[0] = Fraction(1,1) # tableau simples
    # ext_obj = np.zeros(2*n_rest+n_var+1, dtype=np.object_)
    ext_obj = np.zeros(n_rest+n_var+2, dtype=np.object_)
    ext_obj[1:n_var+1] = obj
    # ext_obj[n_rest:n_rest+n_var] = obj
    ext_obj[0] = Fraction(1,1)

    for i in range(n_rest+n_var+2):
    # for i in range(2*n_rest+n_var+1):
        aux_obj[i] = Fraction(aux_obj[i])
        ext_obj[i] = Fraction(ext_obj[i])

    print_iter(n_var, n_rest, ext_obj, aux_obj, aux)

    for i in range(n_rest):
        # aux[i,n_rest:] /= aux[i,n_rest+n_var+i]
        aux[i,1:] /= aux[i,1+n_var+i]
        ext_obj -= aux[i,:]
        aux_obj -= aux[i,:]

    print_iter(n_var, n_rest, ext_obj, aux_obj, aux)
    aux, ext_obj, base, is_feasible = tableau_first_phase(n_var, n_rest, ext_obj.copy(), aux_obj, aux.copy())
    if is_feasible:
        aux, ext_obj, base, is_unlimited = tableau_second_phase(n_var, n_rest, ext_obj.copy(), aux.copy(), base)
        if is_unlimited:
            print('unlimited')
        else:
            print('optimal')
    else:
        print('unfeasible')
    return None, None, None

def tableau_first_phase(n_var, n_rest, ext_obj, aux_obj, aux):
    base = np.zeros(n_rest, dtype=np.int64)
    for i in range(n_rest):
        # base[i] = n_rest+n_var+i
        base[i] = 1+n_var+i
    # indexes = np.where(aux_obj[n_rest:-1] < 0)[0]+n_rest
    indexes = np.where(aux_obj[1:-1] < 0)[0]+1
    print(indexes)
    while len(indexes) > 0:
        print('current base = ', base)
        found = False
        for col in indexes:
            if aux_obj[col] >= 0:
                break
            pivot_line = find_pivot_line(aux, col)
            if pivot_line == None:
                continue
            else:
                found = True
                base[pivot_line] = col
                print('new base = ', base)
                aux, aux_obj, ext_obj = pivot_matrix(aux, aux_obj, ext_obj, col, pivot_line, n_rest, n_var)
                break
        if not found:
            break
        # indexes = np.where(aux_obj[n_rest:-1] < 0)[0]+n_rest
        indexes = np.where(aux_obj[1:-1] < 0)[0]+1
    # print('certificate verification = ', -(aux_obj[:n_rest]*aux[:,-1]).sum())
    print('optimal value found in this phase = ', aux_obj[-1])
    print('*'*150)
    return aux, ext_obj, base, (aux_obj[-1] == 0)

def tableau_second_phase(n_var, n_rest, ext_obj, aux, base):
    # indexes = np.where(aux_obj[n_rest:-1] < 0)[0]+n_rest
    indexes = np.where(ext_obj[1:-1] < 0)[0]+1
    while len(indexes) > 0:
        print('current base = ', base)
        for col in indexes:
            if np.all(aux[:,col] <= 0):
            # if np.all(aux[:,col] <= 0) and np.any(aux[:,col] < 0):
                return aux, ext_obj, base, True
            if ext_obj[col] >= 0:
                break
            pivot_line = find_pivot_line(aux, col)
            if pivot_line == None:
                continue
            else:
                base[pivot_line] = col
                print('new base = ', base)
                aux, _, ext_obj = pivot_matrix(aux, None, ext_obj, col, pivot_line, n_rest, n_var, phase=2)
                break
        # indexes = np.where(aux_obj[n_rest:-1] < 0)[0]+n_rest
        indexes = np.where(ext_obj[1:-1] < 0)[0]+1
    # print('certificate verification = ', -(aux_obj[:n_rest]*aux[:,-1]).sum())
    print('optimal value found in this phase = ', ext_obj[-1])
    print('*'*150)
    return aux, ext_obj, base, False

def find_pivot_line(aux, col):
    n_rest = aux.shape[0]
    ratios = np.zeros(n_rest, dtype=np.object_)
    for i in range(n_rest):
        if aux[i,col] == 0:
            ratios[i] = Fraction(-1,1)
        else:
            ratios[i] = aux[i,-1]/aux[i,col]
    # ratios = aux[:,-1]/(aux[:,col]+Fraction(1,10**12))
    sorted_ratios = np.argsort(ratios)
    # print(ratios)
    # print(np.sort(ratios))
    # print(sorted_ratios)
    for i in sorted_ratios:
        if ratios[i] <= 0:
            continue
        if aux[i,col] == 0:
            continue
        return i
    for i in sorted_ratios:
        if ratios[i] == 0:
            return i
    return None

def pivot_matrix(aux, aux_obj, ext_obj, pivot_col, pivot_line, n_rest, n_var, phase=1):
    print(f'pivoting column {pivot_col} in line {pivot_line}')
    aux[pivot_line,:] /= aux[pivot_line, pivot_col]
    ext_obj -= ext_obj[pivot_col]*aux[pivot_line,:]
    if phase == 1:
        aux_obj -= aux_obj[pivot_col]*aux[pivot_line,:]
    for i in range(n_rest):
        if i == pivot_line:
            continue
        else:
            aux[i,:] -= aux[i,pivot_col]*aux[pivot_line,:]
    print_iter(n_var, n_rest, ext_obj, aux_obj, aux, phase)
    return aux, aux_obj, ext_obj