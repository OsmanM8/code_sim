import sympy as sp 
import random
from sympy import factor, Rational



x = sp.Symbol('x') #turns x into a symbolic variable

def generate_qfactor(difficulty = "easy"):
    if difficulty == "easy":
        a = random.randint(1,10)
        b = random.randint(1,10)

        factor = ((x + a) * (x + b))
        formula = sp.expand(factor)
        return formula, factor      # returns the problem(formula) and solution(factor)
    
    elif difficulty == "medium":
        a = random.randint(1,20)
        b = random.randint(1,20)

        factor = ((x + a) * (x + b))
        formula = sp.expand(factor)
        return formula, factor      # returns the problem(formula) and solution(factor)
    
    elif difficulty == "hard":
        a = random.randint(1,10)
        b = random.randint(1,10)        #these 2 combine to make the fraction ^
        c = random.randint(1,10)

        d = Rational(a, b)      # a/b is a fraction

        factor = ((x + d) * (x + c))
        formula = sp.expand(factor)
        return formula, factor      # returns the equation(formula) and solution(factor)


def generate_quad(difficulty = "easy"):
    if difficulty == "easy":
        a = random.randint(1,10)
        b = random.randint(1,10)

        equation = ((x ** 2) + (a * x) + b)
        solution = sp.solve(equation)           #return the roots of the quadratic
        return equation, solution               #function returns the equation and solution
     
    elif difficulty == "medium":
        a = random.randint(1,20)
        b = random.randint(1,20)

        equation = ((x ** 2) + (a * x) + b)
        solution = sp.solve(equation)           #return the roots of the quadratic
        return equation, solution               #function returns the equation and solution
    
    elif difficulty == "hard":
        a = random.randint(1,10)
        b = random.randint(1,10)            #^ these two variables will combine to form a fraction
        c = random.randint(1,10)

        d = Rational(a,b)               # a/b becomes the fraction

        equation = ((x ** 2) + (d * x) + c)
        solution = sp.solve(equation)           #return the roots of the quadratic
        return equation, solution               #function returns the equation and solution

def generate_quad_problem1(problem_type = "factoring", difficulty = "easy"):
    if problem_type == "factoring":
        return generate_qfactor(difficulty)
    elif problem_type == "quadratic":
        return generate_quad(difficulty)
    
def check_answer(input ,answer, problem_type = "factoring"):
    if problem_type == "factoring":
        user_ans = sp.expand(input)
        solution = sp.expand(answer)
        if (user_ans - solution == 0):
            return True
        else: return False
    
    if problem_type == "quadratic":
        return set(sp.solve(input)) == set(answer)
    
def generate_problem_dict(problem_type = "factoring", difficulty = "easy"):      # JSON output
    problem, solution = generate_quad_problem1(problem_type, difficulty)

        # if the quadratic solution are roots, turn them to strings here 
        
    return{
        "Problem: ": str(problem),
        "Solution: ": str(solution),
        "Problem Type: ": problem_type,             
        "Difficulty: ": difficulty                  #returns a set of data for each problem
    }

def test_generator():
    for _ in range(5):
        p = generate_problem_dict("factoring")
        print(p)

#print(generate_problem_dict())
