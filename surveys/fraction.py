from sympy.solvers import solve
from sympy import Symbol
import random

def fraction(reliability):
    x = Symbol('x')
    denominator = 0
    numerator = 0.1
    while True:
        denominator = random.randint(50,200)
        solution = solve((reliability*denominator) - x, x)
        if solution[0] % 1 == 0:
            numerator = solution[0]
            break
    errors = int(denominator-numerator)
    return errors, denominator
