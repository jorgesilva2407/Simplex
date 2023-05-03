import numpy as np
from utils import print_iter
from fractions import Fraction

def simplex(matrices, phase=1):
    A, B, obj = matrices
    n_rest = A.shape[0]
    n_var = A.shape[1]

    if phase == 1:
        left = np.eye(n_rest, dtype=np.object_)
        for i in range(n_rest):
            for j in range(n_rest):
                left[i,j] = Fraction(left[i,j])

        ext_A = np.concatenate((left.astype(Fraction),A.copy()),axis=1)

        right = np.eye(n_rest, dtype=np.object_)
        for i in range(n_rest):
            if B[i,0] < 0:
                right[i,i] = -right[i,i]
            for j in range(n_rest):
                right[i,j] = Fraction(right[i,j])

        aux = np.concatenate((ext_A,right,B.copy()), axis=1)

        aux_obj = np.zeros((1,2*n_rest+n_var+1), dtype=np.object_)
        aux_obj[0,n_rest+n_var:-1] = np.ones((1,n_rest))

        true_obj = np.zeros((1,2*n_rest+n_var+1), dtype=np.object_)
        true_obj[0,n_rest:n_rest+n_var] = obj

        for i in range(2*n_rest+n_var+1):
            aux_obj[0,i] = Fraction(aux_obj[0,i])
            true_obj[0,i] = Fraction(true_obj[0,i])

        for i in range(n_rest):
            # true_obj -= aux[i,:]
            # print_iter(n_var, n_rest, true_obj, aux_obj, aux)
            print_iter(n_var, n_rest, true_obj, aux_obj, aux)
            aux_obj -= aux[i,:]


        print_iter(n_var, n_rest, true_obj, aux_obj, aux)

        base = np.zeros(n_rest)
        for i in range(n_rest):
            base[i] = n_rest+n_var+i
        
        while True:
            indexes = np.where(aux_obj[0, n_rest:n_rest+n_var] < 0)[0]
            if indexes.size == 0:
                break
            did_something = False
            for i  in indexes:
                line = 0
                col = n_rest+i
                for j in range(1,n_rest):
                    if aux[j,col] == 0:
                        continue
                    elif aux[line,col] == 0:
                        line = j
                    elif aux[j,-1]/aux[j,col] < aux[line,-1]/aux[line,col]:
                        line = j
                if aux[line,col] == 0:
                    continue
                elif aux[line,-1]/aux[line,col] <= 0:
                    continue
                did_something = True
                print('old base: ',base)
                base[line] = col
                print('new base: ',base)
                aux[line,:] /= aux[line,col]
                aux_obj -= aux[line,col]*aux_obj[0,col]*aux[line,:]
                true_obj -= aux[line,col]*true_obj[0,col]*aux[line,:]
                for rest in  range(n_rest):
                    if rest == line:
                        continue
                    else:
                        aux[rest,:] -= aux[line,col]*aux[rest,col]*aux[line,:]
                print_iter(n_var, n_rest, true_obj, aux_obj, aux)
                break
            if not did_something:
                break
    return None, None, None

def build_solution(solution, sub_rules):
    return None

def build_certification(certification, sub_rules):
    return None