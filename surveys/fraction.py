from sympy.solvers import solve
from sympy import Symbol
import random

# Generates a reliability fraction and returns denominator and numerator
def reliatbilityFraction(reliability):
    x = Symbol('x')
    # Initialize denominator and numerator
    denominator = None
    numerator = None
    while True:
        # Choose random denominator
        denominator = random.randint(50,200)
        # Solve equation to match reliability
        solution = solve((reliability*denominator) - x, x)
        # Check if solution is whole number
        if solution[0] % 1 == 0:
            numerator = solution[0]
            break
    return int(numerator), denominator
