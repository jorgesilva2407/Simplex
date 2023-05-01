import sys
import global_variables

if '-d' in sys.argv:
    global_variables.debug = True
else:
    global_variables.debug = False

from simplex import simplex, build_solution, build_certification
from parser import parse

matrix, sub_rules, variables, type_obj = parse(sys.argv[1])

if type_obj == 'MIN':
    matrix[0,:] = 0 - matrix[0,:]

result, partial_solution, partial_certification = simplex(matrix)

solution = build_solution(partial_solution, sub_rules)
certification = build_certification(partial_certification, sub_rules)