import sys
import global_variables

if '-d' in sys.argv:
    global_variables.debug = True
else:
    global_variables.debug = False

from simplex import simplex
from parser import parse


parse('input.txt')