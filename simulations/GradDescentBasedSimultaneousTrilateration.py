from math import *
import random


# ======================================================================================================================
# Distance functions
# ======================================================================================================================

def d2(p0, p1):
    """
    Returns the magnitude of the vector p0-p1, given two vectors p0, p1 in R^n.
    """
    return fsum([(v_p0 - v_p1) ** 2 for v_p0, v_p1 in zip(p0, p1)])


def d(p0, p1):
    """
    Returns Euclidean distance between two vectors in R^n. Might be a little
    numerically unstable and overflow sensitive etc.
    """
    return sqrt(d2(p0, p1))


# ======================================================================================================================
# Gradient descent algorithm
# ======================================================================================================================
def GradDescent(X0, stepSize, maxIters, precision, Func, GradFunc):
    """
    returns an estimate Xn such that Func(X_n) is minimal, or
    maxIters has been reached, or "Func(X_n)-Func(X_{n-1})" is
    within precision bounds.

    Assumes
        X0 is a reasonable starting value
        Func:       (R^k)^n -> R            is a scalar valued function
        GradFunc:   (R^k)^n -> (R^k)^n      is the gradient of Func

    Returns a pair (X,report) where report is a string with information about
    the result of function call, and X is the estimate
    """
    n = len(X0)
    if n == 0:
        return X0, "empty list won't descent that well"
    k = len(X0[0])

    prevXValue = Func(X0)
    currPrecision = 0  # (won't be checked before it's set to an actual value)
    for i in range(maxIters):
        gradX = GradFunc(X0)
        X0 = [[X0[s][t] - stepSize * gradX[s][t] for t in range(k)] for s in range(n)]

        nextXValue = Func(X0)
        currPrecision = abs(prevXValue - nextXValue)
        prevXValue = nextXValue

        print("------------------------------")
        # print("gradX: {0}".format(gradX))
        print("prevXValue: {0}, nextXValue: {1}, currPrecision: {2}".format(prevXValue, nextXValue, currPrecision))
        print("Next estimate for the points X0:")
        for x in X0:
            print(x)

        if currPrecision < precision:
            return X0, "precision reached:{0} after {1} iterations".format(currPrecision, i)

    return X0, "maximum number of iterations reached. precision: {0}".format(currPrecision)


# ======================================================================================================================
# Definition of target function and gradient
# ======================================================================================================================

def e(p0, p1, m):
    """
    Returns the difference between the magnitude between p0,p1 and m.
    Where p0, p1 are vectors in R^k and m is a scalar.
    """
    return d2(p0, p1) - m


def e_ij(X, M, i, j):
    """
    Indicator version of e, that takes a list of size n containing lists of size k
    and returns the square of the difference in magnitude between X[i],X[j] and M[i][j].
    """
    return e(X[i], X[j], M[i][j]) ** 2


def e_ij_partial_st(X, M, i, j, s, t):
    """
    Partial derrivative of e_ij with respect to the variable X[s][t], evaluated at X.
    """
    if s == i:
        # nice feature that e_ij is part of the factorization, huh :-)
        # too bad that we only use the value once per gradient computation
        # it would've been a candidate for caching otherwise.
        return 4 * (X[i][t] - X[j][t]) * e_ij(X, M, i, j)
    if s == j:
        # it happens to be a stupidly symmetric function, in this case swapping i with j
        # and multiplying by -1 yields the right result
        return -1 * e_ij_partial_st(X, M, j, i, s, t)
    # if s not in [i,j], the partial derrivative vanishes. No computation required.
    return 0


def IndexPairs(n):
    """
    Returns an iterable list containing all pairs (i, j) such that
    i and j in [0,...,n-1] and i<j.

    This is summed over in E and its gradient to prevent duplicates
    because (i,j) and (j,i) yield the same results and trivial
    comparisons where i==j.
    """
    return [(i, j) for i in range(n) for j in range(n) if i < j]


def E(X, M):
    """
    Takes as input a list of size n containing lists of size k.
    Returns the sum of squared errors of all possible pairs in this list.

    k is the dimension of the space the crownstones are modeled in (2, 3)
    n is the number of crownstones that are simultaneously trilaterated.
    X is a candidate bundle of position vectors for the n crownstones\
    M is a symmetric nxn matrix containing the target *magnitudes* of the trilateration.
    """
    n = len(X)
    return fsum([e_ij(X, M, i, j) for i, j in IndexPairs(n)])


def E_partial_st(X, M, s, t):
    """
    The partial derrivative of E(*,M), considering it as a
    function of (R^k)^n -> R with respect to the variable X[s][t],
    evaluated at X.

    note:
    returns 0 if len(X) = 0,
    must suffice s < n and t < k, and s,t >= 0
    """
    n = len(X)
    return fsum([e_ij_partial_st(X, M, i, j, s, t) for i, j in IndexPairs(n)])


def Grad_E(X, M):
    """
    Returns the value of gradient of E(*,M), considering it as a
    function of (R^k)^n -> R, evaluated at X.
    This result is a vector in (R^k)^n, i.e. a list of size n,
    containing lists of size k.
    """
    n = len(X)
    if n == 0:
        return []
    k = len(X[0])

    return [[E_partial_st(X, M, s, t) for t in range(k)] for s in range(n)]


# ======================================================================================================================
# Definition of test scenario
# ======================================================================================================================
def errormatrix(n, epsilon):
    """
    Returns a list of size n containing lists of size n, where all the entries
    are samples of independent uniformly distributed random variables in the range
    (-epsilon,epsilon)
    """
    Errs = [[None] * n for unused in range(n)]  # [[]*n]*n doesn't do what you want...
    for i in range(n):
        for j in range(n):
            if i > j:
                Errs[i][j] = Errs[j][i]
            else:
                Errs[i][j] = random.uniform(-epsilon, epsilon)
    return Errs


# actual crownstone locations
points = [
    [0.0, 0.0],
    [0.0, 3.75],
    [2.2, 2.5]
]

# short hand variables
n = len(points)
k = len(points[0])
print("Working in (R^{0})^{1}".format(k, n))

# for numeric stability, prescale:
for i in range(n):
    for j in range(k):
        points[i][j] *= 0.05

# matrix of actual (post-prescaled) magnitudes. I.e.:
#    dists[i][j] == d2(points[i],points[j])
actual_magnitudes = [[
    d2(p_i, p_j)
    for p_i in points]
    for p_j in points]

print("magnitudes:")
for x in actual_magnitudes:
    print(x)

# perturb magnitudes to emulate rssi measure error:
magnitude_errors = errormatrix(n, 0.005)
perturbed_magnitudes = [[
    actual_magnitudes[i][j] + magnitude_errors[i][j]
    for i in range(n)]
    for j in range(n)]

print("introduced magnitude errors:")
for x in magnitude_errors:
    print(x)

# setup starting conditions for descent
# careful about the starting condition.. setting all values equal
# happens to be a local maximum of the method, trapping the algorithm.
# For now we use a pertubation of the original (post-prescaled) points
# which is reasonable whence whe have a guesstimate for the crownstone positions.
estimate_error_bound = 0.5
X0 = [[
    points[i][j] + random.uniform(-estimate_error_bound, estimate_error_bound)
    for j in range(k)]
    for i in range(n)]

print("initial points tuple (X0)")
for x in X0:
    print(x)

# perform gradient descent to trilaterate the perturbed values.
perturbed_result = GradDescent(X0, 0.0001, 500, 0.00001,
                               lambda X: E(X, perturbed_magnitudes),
                               lambda X: Grad_E(X, perturbed_magnitudes))

# the value of the objective function at the found minimum
perturbed_error = E(perturbed_result[0], perturbed_magnitudes)

# then check how well the perturbed triangulation result does using
# Error function of the original values:
actual_error = E(perturbed_result[0], actual_magnitudes)

# report:
print(perturbed_result[1])
print("value of perturbed sq.error function at found minimum: {0}".format(perturbed_error))
print("value of actual sq.error function at found minimum: {0}".format(actual_error))
print("found minimum:")
for x in perturbed_result[0]:
    print(x)

print("Distances:")
for i in range(n):
    for j in range(n):
        if i < j:
            dist = d(points[i], points[j])
            dist_ = d(perturbed_result[0][i], perturbed_result[0][j])
            print("d[{3}][{4}]: {0:.2f}, d'[{3}][{4}]: {1:.2f}, diff: {2:.2f}".format(
                dist, dist_, dist - dist_, i, j))
