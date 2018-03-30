import bee
import functions
import t_test

import numpy as np
import math

# attempt to detect usage of scipy-functions where the behaviour
# does not seem to match the formula in the paper

def test_rosen_integers():
    X = [2,4,6,8]
    y = 100*((4 - 2**2)**2) + (2 - 1)**2 \
      + 100*((6 - 4**2)**2) + (4 - 1)**2 \
      + 100*((8 - 6**2)**2) + (6 - 1)**2

    assert functions.Rosenbrock(X) == y

def test_rosen_decimals():
    X = [0.5, 0.1]
    y = 100*((0.1 - 0.5**2)**2) + (0.5 - 1)**2

    assert functions.Rosenbrock(X) == y

def test_schwefel_naive():
    # schwefel as implemented seems to not be 0 at the minimum specified,
    # as the paper mentions it should.
    c = 418.9829
    x = 420.96
    D = 100

    sin = math.sin
    sqrt = math.sqrt
    #as in paper
    y1 = c*D - sum([-x*sin(sqrt(abs(x))) for i in range(D)])
    #as adapted from paper + guess
    y2 = c*D - sum([x*sin(sqrt(abs(x))) for i in range(D)])

    expected_y = functions.Schwefel.miny
    s = "Schwefel as in paper f(x) of x={x} expects {expect}: {actual}"
    print(s.format(x=x, expect=expected_y, actual=y1))
    s = "Schwefel as modified f(x) of x={x} expects {expect}: {actual}"
    print(s.format(x=x, expect=expected_y, actual=y2))
    print("\n")

def assert_epsilon(expected_y, actual_y, epsilon):
    try:
        assert abs(actual_y - expected_y) < epsilon
    except AssertionError:
        print(" FAILED:")
        print("  Expected: {}".format(expected_y))
        print("  Got: {}".format(actual_y))
        print("  (epsilon: {})".format(epsilon))
    else:
        print(" OK")

def test_minimal_values():
    """Tests that the specified minimal value in the paper actually occurs in
       the location specified in the paper
    """
    dim = 100
    epsilon = 0.0001
    for func in functions.FUNCTIONS:
        print("Testing known min of {} [D={}]...".format(func.__name__, dim), end='')
        X = np.array([func.minx for i in range(dim)])
        expected_y = func.miny
        actual_y = func(X)
        assert_epsilon(expected_y, actual_y, epsilon)

        print("  also testing range of dimensions: ")
        failures = 0
        for ddim in range(1, dim+1):
            X = np.array([func.minx for i in range(ddim)])
            actual_y = func(X)
            if abs(actual_y - expected_y) >= epsilon:
                failures += 1
        print("    {} failures".format(failures), end='')
        if failures > 0:
            print(", FAILED\n")
        else:
            print(", OK\n")


def test_sampling():
    """quick verification that the proportions sampled using the cumulative
       distribution makes sense given the probabilities below"""
    print("Manual review: The proportions sampled below more or less match"
          " what is expected from the given weights: ...")
    weights = [0.1, 0.8, 0.01, 0.09]
    f = lambda: bee.Bee.sample("self", weights)
    L = [0 for i in weights]
    N = 25000
    for i in range(N):
        choice = f()[0]
        L[choice] += 1
    print("  Weights: ", weights)
    print("  Sample (N={}): ".format(N), [x/sum(L) for x in L])
    print("")

def test_ttest():
    """Test that both the scipy and the manual t-test gives the same result"""
    print("\n=====\nTesting the t-test implementation")
    epsilon = 0.0001

    pop1 = [1,5,7,10,13, 3, 1, 3, 3, 3, 3, 1, 2]
    pop2 = [0, 0, 2, 1, 8, 4, 4, 10, 4]

    paper_runs = len(pop1)
    this_runs = len(pop2)

    t,v,p,insig = t_test.manual_t_test(paper_mean=np.mean(pop1),
                                       this_mean=np.mean(pop2),
                                       paper_std=np.std(pop1),
                                       this_std=np.std(pop2),
                                       paper_runs=paper_runs,
                                       this_runs=this_runs)
    t2,p2 = t_test.scipy_t_test(pop1,pop2)

    print("Scipy t-test: t:{t},  p:{p}".format(t=t2,p=p2))
    if abs(t-t2) < epsilon and abs(p-p2) < epsilon:
        print("OK")
    else:
        print("FAILED")
    print("=====\n")

test_rosen_integers()
test_rosen_decimals()
test_schwefel_naive()
test_minimal_values()
test_sampling()

test_ttest()