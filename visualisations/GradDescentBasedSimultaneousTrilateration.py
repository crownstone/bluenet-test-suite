from math import *
import random

# for visualisation purposes
import pygame
pygame.init()

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# some output modifiers
VISUALIZE = 10  # set to 0 for no visualisation, set to positive integer value for inter-frame delay
PRINT = False

if VISUALIZE:
    # Set the height and width of the screen
    screen_size = (1000, 1000)
    mid_screen = [screen_size[i] / 2.0 for i in range(2)]
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption("Gradient Descent Visualisation")


def pointToScreen(point2d, boundaries):
    """
    Returns a 2d coordinate in screenspace, representing the 2dpoint
    such that (0,0) ends up in the middle, (boundaries[0],0) ends up
    in the middle of the upper edge of the screen etc.
    """
    return [int(mid_screen[i] + point2d[i] * mid_screen[i]/boundaries[i]) for i in range(2)]

def pointCloudCenter(points):
    """
    Returns the average of the points.
    Assumes that points is a homogeneous list of lists of floats with all list sizes positive.
    """
    return [sum([points[i][j] for i in range(len(points))]) / 3.0 for j in range(len(points[0]))]


def pointdiff(v0, v1):
    return [v0[i]-v1[i] for i in range(len(v0))]


def translatePointCloudAverageTo0(points):
    """
    Subtracts the average of the points from each point.
    Assumes that points is a homogeneous list of lists of floats
    """
    avg = pointCloudCenter(points)
    return [pointdiff(point, avg) for point in points]

def updateFrame(targetTriangle, estimateTriangle, bounds):
    """
    Keeps the estimate triangle on the same place as
    """
    # targetTriangle = translatePointCloudAverageTo0(targetTriangle)
    # estimateTriangle = translatePointCloudAverageTo0(estimateTriangle)

    screen.fill(WHITE)
    pygame.draw.circle(screen, BLACK, pointToScreen([0, 0], bounds), 3)

    pygame.draw.polygon(screen, BLACK, [pointToScreen(targetTriangle[i], bounds) for i in range(3)], 5)
    pygame.draw.polygon(screen, RED, [pointToScreen(estimateTriangle[i], bounds) for i in range(3)], 5)
    pygame.display.flip()

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
def GradDescent(X0, stepSize, maxIters, precision, Func, GradFunc, targetTriangle = None):
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

    targetTriangle: this is the actual value we are trying to optimize for.
      must be valid bunch of points when visualizing.
    """
    n = len(X0)
    if n == 0:
        return X0, "empty list won't descent that well"
    k = len(X0[0])

    if VISUALIZE:
        # set the bounds to twice the size of the target triangle
        bounds = [2*max([targetTriangle[i][j] for i in range(n)]) for j in range(k)]
        # wait a bit so you have time to open the window if it doesn't pop up in the right place
        # pygame.time.wait(2000)

    prevXValue = Func(X0)
    currPrecision = 0  # (won't be checked before it's set to an actual value)
    result = None
    for i in range(maxIters):
        gradX = GradFunc(X0)
        X0 = [[X0[s][t] + stepSize * gradX[s][t] for t in range(k)] for s in range(n)]

        # optimization with regards to numeric stability:
        # maybe subtract the average of all points in X0 from all points in X0.
        # as the function is translation invariant it may need an artificial measure like that
        # Warning: this is NOT vanilla gradient descent anymore when you apply this.
        X0 = translatePointCloudAverageTo0(X0)

        # Similarly we could optimize so that volume is kept equal to 1 and allow for a scalar.

        nextXValue = Func(X0)
        currPrecision = abs(prevXValue - nextXValue)
        prevXValue = nextXValue

        if VISUALIZE:
            updateFrame(targetTriangle, X0, bounds)

            while True:
                # only run while space is pressed, so delay until it is down
                keys_mods = pygame.key.get_mods()
                pygame.time.wait(VISUALIZE)
                pygame.event.pump()  # process event queue
                if keys_mods & pygame.KMOD_SHIFT:
                    break

        if PRINT:
            print("------------------------------")
            # print("gradX: {0}".format(gradX))
            print("prevXValue: {0}, nextXValue: {1}, currPrecision: {2}".format(prevXValue, nextXValue, currPrecision))
            print("Next estimate for the points X0:")
            for x in X0:
                print(x)

        if currPrecision < precision:
            result = X0, "precision reached:{0} after {1} iterations".format(currPrecision, i)
            break

    pygame.quit()

    if result:
        return result

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

# for numeric stability, prescale and move center to 0.0:
points = translatePointCloudAverageTo0(points)

for i in range(n):
    for j in range(k):
        points[i][j] *= 0.1

# matrix of actual (post-prescaled) magnitudes. I.e.:
#    dists[i][j] == d2(points[i],points[j])
actual_magnitudes = [[
    d2(p_i, p_j)
    for p_i in points]
    for p_j in points]

print("magnitudes:")
max_magnitude = max([max(magn) for magn in actual_magnitudes])
for x in actual_magnitudes:
    print(x)

# perturb magnitudes to emulate rssi measure error:
magnitude_errors = errormatrix(n, 0.05)
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
estimate_error_bound = sqrt(max_magnitude)
X0 = [[
    points[i][j] + random.uniform(-estimate_error_bound, estimate_error_bound)
    for j in range(k)]
    for i in range(n)]

print("initial points tuple (X0)")
for x in X0:
    print(x)

# perform gradient descent to trilaterate the perturbed valu         es.
precision = 0
perturbed_result = GradDescent(X0, 0.001, 500, precision,
                               lambda X: E(X, perturbed_magnitudes),
                               lambda X: Grad_E(X, perturbed_magnitudes),
                               points)

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
