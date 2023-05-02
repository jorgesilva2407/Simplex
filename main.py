import sys
from simplex import simplex, build_solution, build_certification
from linear_parser import parse

matrix, sub_rules, variables, type_obj = parse(sys.argv[1])

result, partial_solution, partial_certification = simplex(matrix)

solution = build_solution(partial_solution, sub_rules)
certification = build_certification(partial_certification, sub_rules)