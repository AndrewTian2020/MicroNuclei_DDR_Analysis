# ===================================================================================================
# Date: July 11, 2025
# Author: Andrew Tian
# Functions for performing mathematical calculations
# I.e. multivariate ANOVA, manual integration

# ===================================================================================================
# Importing libraries
import numpy as np
from statistics import stdev
from scipy.stats import norm

# ===================================================================================================
# integrate() performs trapezoidal approximation of custom sine function from 0 to 144 hours
# a, b, c, and k are all parameters of the function (should be optimized)
# n is the number of partitions, ideally higher is better but not fully necessary either
# This function only applies to ONE well, keep looping this for all wells and store in a list
def integrate(a, b, c, k, n):
    dx = 144/n
    i = 1
    area = 0.0

    y1 = 0.0
    y2 = 0.0

    x1 = 0.0
    x2 = 0.0

    while i <= n:
        x1 = dx * i
        x2 = dx * (i + 1)

        y1 = a * np.sin(x1 * np.pi / 72 - b + c * np.sin(x1 * np.pi / 72 - b)) + k
        y2 = a * np.sin(x2 * np.pi / 72 - b + c * np.sin(x2 * np.pi / 72 - b)) + k

        area += (y2 + y1)/2 * dx

        i += 1

    return area

# derivate() just finds the "max" value of a function by manually calculating
# "n" values of the function (equally partitioned) to find the maximum
def derivate(a, b, c, k, n):
    max = 0.0

    dx = 144/n
    i = 1

    x = 0.0
    y = 0.0

    while i <= n:
        x = dx * i
        y = a * np.sin(x * np.pi / 72 - b + c * np.sin(x * np.pi / 72 - b)) + k
        if y > max:
            max = y
        i += 1
    return max

# derivate2() just finds the "max" value of a function by manually calculating
# "n" values of the function (equally partitioned) to find the maximum
# and also returns the x value at which the maximum mn ratio occurs
def derivate2(a, b, c, k, n):
    max = 0.0

    dx = 144/n
    i = 1

    x = 0.0
    xmax = 0.0
    y = 0.0

    while i <= n:
        x = dx * i
        y = a * np.sin(x * np.pi / 72 - b + c * np.sin(x * np.pi / 72 - b)) + k
        if y > max:
            max = y
            xmax = x
        i += 1
    return [xmax, max]

# take z score for a list of data given a population
def zscore(data, pop):
    i = 0
    m = sum(pop) / len(pop)
    s = stdev(pop)
    z_vals = []
    while i < len(data):
        z_vals.append((data[i] - m)/s)
        i += 1
    return z_vals

# take p values for a list of data given a population
def right_p_vals(z_vals):
    p_vals = []
    for z in z_vals:
        p_vals.append(1 - norm.cdf(z))
    return p_vals