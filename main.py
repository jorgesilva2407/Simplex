import sys
from simplex import simplex
import global_variables

if '-d' in sys.argv:
    global_variables.debug = True
else:
    global_variables.debug = False

from parser import parse
parse('input.txt')