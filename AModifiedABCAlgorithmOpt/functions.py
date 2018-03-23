import numpy as np
from scipy.optimize import rosen

# Where possible, scipy implementations will be used for performance reasons
# A set of tests have been made for each such function in tests.py to check
# that the behaviour does not differ from the formulae in the paper


def Sphere(X):
    return np.sum(np.power(X,2))
Sphere.minx = 0
Sphere.miny = 0
Sphere.search_range = (-100, 100)
Sphere.init_range = (-100, 50)

#https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.rosen.html
def Rosenbrock(X):
    return rosen(X)
Rosenbrock.minx = 1
Rosenbrock.miny = 0
Rosenbrock.search_range = (-2.048, 2.048)
Rosenbrock.init_range = (-2.048, 2.048)

def Ackley(X):
    D = len(X)
    pi = np.pi
    sum1 = -0.2*np.sqrt(  (1.0/D)*np.sum(np.power(X,2))  )
    sum2 = (1.0/D)*np.sum(np.cos(2*pi*X))

    return -20*np.exp(sum1) - np.exp(sum2) + 20 + np.e
Ackley.minx = 0
Ackley.miny = 0
Ackley.search_range = (-32.768, 32.768)
Ackley.init_range = (-32.768, 16)

def Griewank(X):
    sum1 = np.sum(np.power(X,2))

    range = np.arange(1, X.size + 1)
    prod1 = np.product(  np.cos(X/np.sqrt(range))  )

    return (1/4000.)*sum1 - prod1 + 1
Griewank.minx = 0
Griewank.miny = 0
Griewank.search_range = (-600, 600)
Griewank.init_range = (-600, 200)

def Weierstrass(X):
    a = 0.5
    b = 3
    kmax = 20
    D = np.size(X)

    pi = np.pi
    K = np.arange(0, kmax + 1)
    AK = np.power(a, K)
    BK = 2*pi*np.power(b, K)

    total = 0
    for i,xi in enumerate(X, start=1):
        part1 = np.sum(AK*np.cos(BK*(xi + 0.5)))
        total += part1

    part2 = AK*np.cos(BK*0.5)
    total -= D*np.sum(part2)

    return total
Weierstrass.minx = 0
Weierstrass.miny = 0
Weierstrass.search_range = (-0.5, 0.5)
Weierstrass.init_range = (-0.5, 0.2)

def Rastrigin(X):
    pi = np.pi
    return np.sum(  np.power(X,2) - 10*np.cos(2*pi*X) + 10  )
Rastrigin.minx = 0
Rastrigin.miny = 0
Rastrigin.search_range = (-5.12, 5.12)
Rastrigin.init_range = (-5.12, 2)

def Noncontinuous_Rastrigin(X):
    pi = np.pi
    Y = np.where(np.abs(X) < 0.5, X, np.round(2*X)/2.0)
    return np.sum(  np.power(Y,2) - 10*np.cos(2*pi*Y) + 10  )
Noncontinuous_Rastrigin.minx = 0
Noncontinuous_Rastrigin.miny = 0
Noncontinuous_Rastrigin.search_range = (-5.12, 5.12)
Noncontinuous_Rastrigin.init_range = (-5.12, 2)

def Schwefel(X):
    D = np.size(X)
    return 418.9829*D - np.sum(X*np.sin(np.sqrt(np.abs(X))))
    #return 418.9829*D - np.sum(-X*np.sin(np.sqrt(np.abs(X))))
    #differs from paper, also see tests
Schwefel.minx = 420.96
Schwefel.miny = 0
Schwefel.search_range = (-500, 500)
Schwefel.init_range = (-500, 500)


FUNCTIONS = [Sphere, Rosenbrock, Ackley, Griewank, Weierstrass,
            Rastrigin, Noncontinuous_Rastrigin, Schwefel]
