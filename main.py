import sys
from simplex import simplex
from linear_parser import parse

matrix, sub_rules, variables, type_obj = parse(sys.argv[1])

result, partial_solution, partial_certification = simplex(matrix, type_obj)