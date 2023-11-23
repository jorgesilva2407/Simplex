import sys
import numpy as np
from simplex import simplex
from linear_parser import parse

matrix, sub_rules, variables, type_obj = parse(sys.argv[1])

decision, solution, certificate, z = simplex(matrix, type_obj)
certificate = certificate.astype(np.float64)

out_file = 'out.txt'
for i in range(len(sys.argv)):
    if sys.argv[i] == '-o':
        out_file = sys.argv[i+1]

with open(out_file, 'w') as f:
    if decision == 'ilimitado':
        f.write('Status: ilimitado\n')
        f.write('Certificado:\n')
        for i in range(certificate.size):
            f.write(f'{certificate[i]:.4f} ')
    elif decision == 'inviavel':
        f.write('Status: inviavel\n')
        f.write('Certificado:\n')
        for i in range(certificate.size):
            f.write(f'{certificate[i]:.4f} ')
    elif decision == 'otimo':
        f.write('Status: otimo\n')
        f.write(f'Objetivo: {z:.4f}\n')
        f.write('Solucao:\n')
        for i in range(solution.size):
            f.write(f'{solution[i]:.4f} ')
        f.write('\nCertificado:\n')
        for i in range(certificate.size):
            f.write(f'{certificate[i]:.4f} ')