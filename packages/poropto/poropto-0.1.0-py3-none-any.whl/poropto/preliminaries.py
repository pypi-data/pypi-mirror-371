# poropto/preliminaries.py

# --------------------------------------------------------------------------------------------------
# Libraries

import math
import os
import warnings
import ast
import scipy.integrate as integrate
import numpy as np
import pandas as pd
import pyomo.environ as pyo
import logging

# --------------------------------------------------------------------------------------------------

def satisfaction_degree(A):
    '''
    Calculate the satisfaction degree of an intuitionistic fuzzy set (IFS).

    Parameters:
    A (tuple): A tuple (x, mu, nu) where:
        - x: The element of the universe of discourse (not used in the current calculation).
        - mu: The membership degree of the fuzzy set (x).
        - nu: The non-membership degree of the fuzzy set (x).

    Returns:
    float: The satisfaction degree, rounded to the specified precision.

    Raises:
    ValueError: If any of the input values are invalid.
    '''
    # Unpack the IFS
    x, mu, nu = A

    # Validate membership and non-membership degrees
    if not (0 <= mu <= 1):
        raise ValueError(f'Invalid value for membership degree (mu): {mu}. It must be between 0 and 1 (inclusive).')

    if not (0 <= nu <= 1):
        raise ValueError(f'Invalid value for non-membership degree (nu): {nu}. It must be between 0 and 1 (inclusive).')

    pi = 1 - (mu + nu)

    # Validate hesitation degree
    if pi < 0:
        raise ValueError(f'Invalid combination of membership (mu) and non-membership (nu) degrees. The sum of mu and nu cannot exceed 1.')

    # Validate the denominator of the satisfaction degree
    if (nu + pi) == 0:
        raise ValueError('The sum of non-membership degree (nu) and hesitation degree (pi) cannot be zero.')

    # Calculate satisfaction degree
    satisfaction_degree = mu / (nu + pi)

    return satisfaction_degree

# --------------------------------------------------------------------------------------------------

def validate_tifn(A):
    '''
    Validate the input trapezoidal intuitionistic fuzzy number (TIFN).

    Parameters:
    A (list): A list [(a, b, c, d), mu, nu] representing the TIFN.

    Raises:
    ValueError: If any of the input values are invalid.
    '''
    # Unpack the TIFN
    (a, b, c, d), mu, nu = A

    # Validate membership and non-membership degrees
    if not (0 <= mu <= 1):
        raise ValueError(f'Invalid membership degree mu: {mu}. Must be in [0, 1].')

    if not (0 <= nu <= 1):
        raise ValueError(f'Invalid non-membership degree nu: {nu}. Must be in [0, 1].')

    if not (0 <= mu + nu <= 1):
        raise ValueError(f'Invalid combination: mu + nu = {round((mu + nu),2)}. Sum must be in [0, 1].')

    # Validate trapezoidal parameters for TIFN
    if not (a <= b <= c <= d):
        raise ValueError(f'Invalid trapezoidal parameters: Ensure a <= b <= c <= d. Received: a={a}, b={b}, c={c}, d={d}.')

# --------------------------------------------------------------------------------------------------

def tifn_degrees(x, A):
    '''
    Calculate both the membership and non-membership degrees for a trapezoidal intuitionistic fuzzy number (TIFN) based on its multi-rule functions.

    Parameters:
    x (float): The value at which to evaluate the functions.
    A (list): A list [(a, b, c, d), mu, nu] representing the TIFN.

    Returns:
    tuple: A tuple (mu_x, nu_x, pi_x) representing the membership, non-membership, and hesitation degrees of x.

    Raises:
    ValueError: If any of the input values are invalid.
    '''
    # Unpack the TIFN
    (a, b, c, d), mu, nu = A

    # Validate the TIFN
    validate_tifn(A)

    # Calculate mu_x
    if x < a or x > d:
        mu_x = 0
    elif a <= x < b:
        mu_x = mu * (x - a) / (b - a)
    elif b <= x <= c:
        mu_x = mu
    elif c < x <= d:
        mu_x = mu * (d - x) / (d - c)

    # Calculate nu_x
    if x < a or x > d:
        nu_x = 1
    elif a <= x < b:
        nu_x = (b - x + nu * (x - a)) / (b - a)
    elif b <= x <= c:
        nu_x = nu
    elif c < x <= d:
        nu_x = (x - c + nu * (d - x)) / (d - c)

    # Calculate pi_x
    pi_x = 1 - (mu_x + nu_x)

    return mu_x, nu_x, pi_x

# --------------------------------------------------------------------------------------------------

def add_tifns(A1, A2):
    '''
    Perform the addition operation on two trapezoidal intuitionistic fuzzy numbers (TIFNs).

    Parameters:
    A1 (list): A list [(a1, b1, c1, d1), mu1, nu1] representing the first TIFN.
    A2 (list): A list [(a2, b2, c2, d2), mu2, nu2] representing the second TIFN.

    Returns:
    list: A list [(a, b, c, d), mu, nu] representing the result of the addition.

    Raises:
    ValueError: If any of the input values are invalid.
    '''
    # Unpack both TIFNs
    (a1, b1, c1, d1), mu1, nu1 = A1
    (a2, b2, c2, d2), mu2, nu2 = A2

    # Validate both TIFNs
    for i, A in enumerate([A1, A2], start=1):
        try:
            validate_tifn(A)
        except ValueError as e:
            raise ValueError(f'Error in TIFN {i}: {str(e)}')

    # Calculate the new trapezoidal parameters
    a = a1 + a2
    b = b1 + b2
    c = c1 + c2
    d = d1 + d2

    # Calculate the new membership and non-membership degrees
    mu = mu1 + mu2 - (mu1 * mu2)
    nu = nu1 * nu2

    # Create the resulting TIFN
    result = [(a, b, c, d), mu, nu]

    # Validate the resulting TIFN
    try:
        validate_tifn(result)
    except ValueError as e:
        raise ValueError(f'Error in resulting TIFN: {str(e)}')

    return result

# --------------------------------------------------------------------------------------------------

def subtract_tifns(A1, A2):
    '''
    Perform the subtraction operation on two trapezoidal intuitionistic fuzzy numbers (TIFNs).

    Parameters:
    A1 (list): A list [(a1, b1, c1, d1), mu1, nu1] representing the first TIFN.
    A2 (list)): A list [(a2, b2, c2, d2), mu2, nu2] representing the second TIFN.

    Returns:
    list: A list [(a, b, c, d), mu, nu] representing the result of the subtraction.

    Raises:
    ValueError: If any of the input values are invalid.
    '''
    # Unpack both TIFNs
    (a1, b1, c1, d1), mu1, nu1 = A1
    (a2, b2, c2, d2), mu2, nu2 = A2

    # Validate both TIFNs
    for i, A in enumerate([A1, A2], start=1):
        try:
            validate_tifn(A)
        except ValueError as e:
            raise ValueError(f'Error in TIFN {i}: {str(e)}')

    # Calculate the new trapezoidal parameters
    a = a1 - d2
    b = b1 - c2
    c = c1 - b2
    d = d1 - a2

    # Calculate the new membership and non-membership degrees
    mu = mu1 + mu2 - (mu1 * mu2)
    nu = nu1 * nu2

    # Create the resulting TIFN
    result = [(a, b, c, d), mu, nu]

    # Validate the resulting TIFN
    try:
        validate_tifn(result)
    except ValueError as e:
        raise ValueError(f'Error in resulting TIFN: {str(e)}')

    return result

# --------------------------------------------------------------------------------------------------

def multiply_tifns(A1, A2):
    '''
    Perform the multiplication operation on two trapezoidal intuitionistic fuzzy numbers (TIFNs).

    Parameters:
    A1 (list): A list [(a1, b1, c1, d1), mu1, nu1] representing the first TIFN.
    A2 (list): A list [(a2, b2, c2, d2), mu2, nu2] representing the second TIFN.

    Returns:
    list: A list [(a, b, c, d), mu, nu] representing the result of the multiplication.

    Raises:
    ValueError: If any of the input values are invalid.
    '''
    # Unpack both TIFNs
    (a1, b1, c1, d1), mu1, nu1 = A1
    (a2, b2, c2, d2), mu2, nu2 = A2

    # Validate both TIFNs
    for i, A in enumerate([A1, A2], start=1):
        try:
            validate_tifn(A)
        except ValueError as e:
            raise ValueError(f'Error in TIFN {i}: {str(e)}')

    # Calculate the new trapezoidal parameters
    a = a1 * a2
    b = b1 * b2
    c = c1 * c2
    d = d1 * d2

    # Calculate the new membership and non-membership degrees
    mu = mu1 * mu2
    nu = nu1 + nu2 - (nu1 * nu2)

    # Create the resulting TIFN
    result = [(a, b, c, d), mu, nu]

    # Validate the resulting TIFN
    try:
        validate_tifn(result)
    except ValueError as e:
        raise ValueError(f'Error in resulting TIFN: {str(e)}')

    return result

# --------------------------------------------------------------------------------------------------

def divide_tifns(A1, A2):
    '''
    Perform the division operation on two trapezoidal intuitionistic fuzzy numbers (TIFNs).

    Parameters:
    A1 (list): A list [(a1, b1, c1, d1), mu1, nu1] representing the first TIFN.
    A2 (list): A list [(a2, b2, c2, d2), mu2, nu2] representing the second TIFN.

    Returns:
    list: A list [(a, b, c, d), mu, nu] representing the result of the division.

    Raises:
    ValueError: If any of the input values are invalid.
    '''
    # Unpack both TIFNs
    (a1, b1, c1, d1), mu1, nu1 = A1
    (a2, b2, c2, d2), mu2, nu2 = A2

    # Validate both TIFNs
    for i, A in enumerate([A1, A2], start=1):
        try:
            validate_tifn(A)
        except ValueError as e:
            raise ValueError(f'Error in TIFN {i}: {str(e)}')

    # Ensure no division by zero
    if d2 == 0 or c2 == 0 or b2 == 0 or a2 == 0:
        raise ValueError('Division by zero error: One of the trapezoidal parameters of A2 is zero.')

    # Calculate the new trapezoidal parameters
    a = a1 / d2
    b = b1 / c2
    c = c1 / b2
    d = d1 / a2

    # Calculate the new membership and non-membership degrees
    mu = mu1 * mu2
    nu = nu1 + nu2 - (nu1 * nu2)

    # Create the resulting TIFN
    result = [(a, b, c, d), mu, nu]

    # Validate the resulting TIFN
    try:
        validate_tifn(result)
    except ValueError as e:
        raise ValueError(f'Error in resulting TIFN: {str(e)}')

    return result

# --------------------------------------------------------------------------------------------------

def scale_tifn(A, lambda_):
    '''
    Perform the scaling operation on a trapezoidal intuitionistic fuzzy number (TIFN).

    Parameters:
    A (list): A list [(a, b, c, d), mu, nu] representing the TIFN.
    lambda_ (float): The scaling factor (λ), where λ ≥ 0.

    Returns:
    list: A list [(a, b, c, d), mu, nu] representing the result of the scaling.

    Raises:
    ValueError: If any of the input values are invalid.
    '''
    # Unpack the TIFN
    (a, b, c, d), mu, nu = A

    # Validate the TIFN
    validate_tifn(A)

    # Validate scaling factor
    if lambda_ < 0:
        raise ValueError(f'Invalid scaling factor λ: {lambda_}. It must be non-negative.')

    # Calculate the new trapezoidal parameters
    a = lambda_ * a
    b = lambda_ * b
    c = lambda_ * c
    d = lambda_ * d

    # Calculate the new membership and non-membership degrees
    mu = 1 - (1 - mu) ** lambda_
    nu = nu ** lambda_

    # Create the resulting TIFN
    result = [(a, b, c, d), mu, nu]

    # Validate the resulting TIFN
    try:
        validate_tifn(result)
    except ValueError as e:
        raise ValueError(f'Error in resulting TIFN: {str(e)}')

    return result

# --------------------------------------------------------------------------------------------------

def scale_tifn_exponentially(A, lambda_):
    '''
    Perform the scaling operation on a trapezoidal intuitionistic fuzzy number (TIFN)
    using an exponential scaling method.

    Parameters:
    A (list): A list [(a, b, c, d), mu, nu] representing the TIFN.
    lambda_ (float): The scaling factor (λ), where λ ≥ 0.

    Returns:
    list: A list [(a, b, c, d), mu, nu] representing the result of the scaling.

    Raises:
    ValueError: If any of the input values are invalid.
    '''
    # Unpack the TIFN
    (a, b, c, d), mu, nu = A

    # Validate the TIFN
    validate_tifn(A)

    # Validate scaling factor
    if lambda_ < 0:
        raise ValueError(f'Invalid scaling factor λ: {lambda_}. It must be non-negative.')

    # Calculate the new trapezoidal parameters
    a = a ** lambda_
    b = b ** lambda_
    c = c ** lambda_
    d = d ** lambda_

    # Calculate the new membership and non-membership degrees
    mu = mu ** lambda_
    nu = 1 - (1 - nu) ** lambda_

    # Create the resulting TIFN
    result = [(a, b, c, d), mu, nu]

    # Validate the resulting TIFN
    try:
        validate_tifn(result)
    except ValueError as e:
        raise ValueError(f'Error in resulting TIFN: {str(e)}')

    return result

# --------------------------------------------------------------------------------------------------

def negate_tifn(A):
    '''
    Perform the negation operation on a trapezoidal intuitionistic fuzzy number (TIFN).

    Parameters:
    A (list): A list [(a, b, c, d), mu, nu] representing the TIFN.

    Returns:
    list: A list [(a, b, c, d), mu, nu] representing the result of the negation.

    Raises:
    ValueError: If any of the input values are invalid.
    '''
    # Unpack the TIFN
    (a, b, c, d), mu, nu = A

    # Validate the TIFN
    validate_tifn(A)

    # Calculate the new trapezoidal parameters
    a = -d
    b = -c
    c = -b
    d = -a

    # The membership and non-membership degrees remain the same
    mu = mu
    nu = nu

# Create the resulting TIFN
    result = [(a, b, c, d), mu, nu]

    # Validate the resulting TIFN
    try:
        validate_tifn(result)
    except ValueError as e:
        raise ValueError(f'Error in resulting TIFN: {str(e)}')

    return result

# --------------------------------------------------------------------------------------------------

def reciprocal_tifn(A):
    '''
    Perform the reciprocal operation on a trapezoidal intuitionistic fuzzy number (TIFN).

    Parameters:
    A (list): A list [(a, b, c, d), mu, nu] representing the TIFN.

    Returns:
    list: A list [(a, b, c, d), mu, nu] representing the result of the reciprocal.

    Raises:
    ValueError: If any of the input values are invalid.
    '''
    # Unpack the TIFN
    (a, b, c, d), mu, nu = A

    # Validate the TIFN
    validate_tifn(A)

    # Calculate the new trapezoidal parameters (reciprocals)
    a = 1 / d
    b = 1 / c
    c = 1 / b
    d = 1 / a

    # The membership and non-membership degrees remain the same
    mu = mu
    nu = nu

    # Create the resulting TIFN
    result = [(a, b, c, d), mu, nu]

    # Validate the resulting TIFN
    try:
        validate_tifn(result)
    except ValueError as e:
        raise ValueError(f'Error in resulting TIFN: {str(e)}')

    return result

# --------------------------------------------------------------------------------------------------

def aggregate_tifns(tifns):
    '''
    Aggregate a collection of trapezoidal intuitionistic fuzzy numbers (TIFNs) into a single TIFN.

    Parameters:
    tifns (list): A list of lists [(a_i, b_i, c_i, d_i), mu_i, nu_i] representing the TIFNs.

    Returns:
    list: A list [(a, b, c, d), mu, nu] representing the aggregated TIFN.

    Raises:
    ValueError: If the input list is empty or any of the input values are invalid.
    '''
    if not tifns:
        raise ValueError('The list of TIFNs is empty.')

    # Initialize sums for trapezoidal parameters
    sum_a = sum_b = sum_c = sum_d = 0

    # Initialize products for membership and non-membership degrees
    prod_mu_complement = 1
    prod_nu = 1

    for tifn in tifns:
        (a, b, c, d), mu, nu = tifn

        # Validate TIFNs
        for i, tifn in enumerate(tifns, start=1):
            try:
                validate_tifn(tifn)
            except ValueError as e:
                raise ValueError(f'Error in TIFN {i}: {str(e)}')

        # Accumulate sums for trapezoidal parameters
        sum_a += a
        sum_b += b
        sum_c += c
        sum_d += d

        # Update products for membership and non-membership degrees
        prod_mu_complement *= (1 - mu)
        prod_nu *= nu

    # Calculate the aggregated membership and non-membership degrees
    aggregated_mu = 1 - prod_mu_complement
    aggregated_nu = prod_nu

    # Create the resulting TIFN
    result = [(sum_a, sum_b, sum_c, sum_d), aggregated_mu, aggregated_nu]

    # Validate the resulting TIFN
    try:
        validate_tifn(result)
    except ValueError as e:
        raise ValueError(f'Error in resulting TIFN: {str(e)}')

    return result

# --------------------------------------------------------------------------------------------------

def weighted_aggregate_tifns(tifns, weights):
    '''
    Perform the weighted aggregation of trapezoidal intuitionistic fuzzy numbers (TIFNs).

    Parameters:
    tifns (list): A list of lists [(a_i, b_i, c_i, d_i), mu_i, nu_i] representing the TIFNs.
    weights (list): A list of weights ω_i corresponding to each TIFN, where ω_i ∈ [0, 1] and ∑ω_i = 1.

    Returns:
    list: A list [(a, b, c, d), mu, nu] representing the weighted aggregated TIFN.

    Raises:
    ValueError: If the input list is empty or any of the input values are invalid.
    '''
    if not tifns or len(tifns) != len(weights):
        raise ValueError('The list of TIFNs and weights must be of the same length and non-empty.')

    if not all(0 <= weight <= 1 for weight in weights) or sum(weights) != 1:
        raise ValueError('Weights must be in the range [0, 1] and sum up to 1.')

    # Initialize products for trapezoidal parameters and membership/non-membership degrees
    prod_a = prod_b = prod_c = prod_d = 1
    prod_mu = 1
    prod_nu_complement = 1

    for (tifn, weight) in zip(tifns, weights):
        (a, b, c, d), mu, nu = tifn

        # Validate TIFNs
        for i, tifn in enumerate(tifns, start=1):
            try:
                validate_tifn(tifn)
            except ValueError as e:
                raise ValueError(f'Error in TIFN {i}: {str(e)}')

        # Compute the weighted product for trapezoidal parameters
        prod_a *= a ** weight
        prod_b *= b ** weight
        prod_c *= c ** weight
        prod_d *= d ** weight

        # Compute the weighted product for membership and non-membership degrees
        prod_mu *= mu ** weight
        prod_nu_complement *= (1 - nu) ** weight

    # Calculate the aggregated membership and non-membership degrees
    aggregated_mu = prod_mu
    aggregated_nu = 1 - prod_nu_complement

    # Create the resulting TIFN
    result = [(prod_a, prod_b, prod_c, prod_d), aggregated_mu, aggregated_nu]

    # Validate the resulting TIFN
    try:
        validate_tifn(result)
    except ValueError as e:
        raise ValueError(f'Error in resulting TIFN: {str(e)}')

    return result

# --------------------------------------------------------------------------------------------------

def expected_value(A):
    '''
    Calculate the expected value for a trapezoidal intuitionistic fuzzy number (TIFN).

    Parameters:
    A (list): A list [(a, b, c, d), mu, nu] representing the TIFN.

    Returns:
    float: The expected value of the TIFN, rounded to the specified precision.

    Raises:
    ValueError: If any of the input values are invalid.
    '''
    # Unpack the TIFN
    (a, b, c, d), mu, nu = A

    # Validate the TIFN
    validate_tifn(A)

    # Calculate the expected value
    expected_value = (1/8) * ((a + b + c + d) * (1 + mu - nu))

    return expected_value

# --------------------------------------------------------------------------------------------------

def score_function(A):
    '''
    Calculate the score function for a trapezoidal intuitionistic fuzzy number (TIFN).

    Parameters:
    A (list): A list [(a, b, c, d), mu, nu] representing the TIFN.

    Returns:
    float: The score function value of the TIFN, rounded to the specified precision.

    Raises:
    ValueError: If any of the input values are invalid.
    '''
    # Unpack the TIFN
    (a, b, c, d), mu, nu = A

    # Validate the TIFN
    validate_tifn(A)

    # Calculate the score function
    score_function = expected_value(A) * (mu - nu)

    return score_function

# --------------------------------------------------------------------------------------------------

def accuracy_function(A):
    '''
    Calculate the accuracy function for a trapezoidal intuitionistic fuzzy number (TIFN).

    Parameters:
    A (list): A list [(a, b, c, d), mu, nu] representing the TIFN.

    Returns:
    float: The accuracy function value of the TIFN, rounded to the specified precision.

    Raises:
    ValueError: If any of the input values are invalid.
    '''
    # Unpack the TIFN
    (a, b, c, d), mu, nu = A

    # Validate the TIFN
    validate_tifn(A)

    # Calculate the accuracy function
    accuracy_function = expected_value(A) * (mu + nu)

    return accuracy_function

# --------------------------------------------------------------------------------------------------

def sort_tifns(tifns):
    '''
    Sort a list of TIFNs according to the comparison rules.

    Parameters:
    tifns (list): A list of lists [(a_i, b_i, c_i, d_i), mu_i, nu_i] representing the TIFNs.

    Returns:
    list: The ascending sorted list of TIFNs.

    Raises:
    ValueError: If any of the input values are invalid.
    '''
    # Validate TIFNs
    for i, tifn in enumerate(tifns, start=1):
        try:
            validate_tifn(tifn)
        except ValueError as e:
            raise ValueError(f'Error in TIFN {i}: {str(e)}')

    # Sort the list using the custom comparison function
    sorted_tifns = sorted(tifns, key=lambda x: (score_function(x), accuracy_function(x)), reverse=False)

    return sorted_tifns

# --------------------------------------------------------------------------------------------------

def min_tifns(tifns):
    '''
    Get the minimum TIFN from the list of tifns.

    Parameters:
    tifns (list): A list of lists [(a_i, b_i, c_i, d_i), mu_i, nu_i] representing the TIFNs.

    Returns:
    tuple: A list containing the minimum TIFN.
    '''
    sorted_tifns = sort_tifns(tifns)

    return sorted_tifns[0]

# --------------------------------------------------------------------------------------------------

def max_tifns(tifns):
    '''
    Get the maximum TIFN from the list of tifns.

    Parameters:
    tifns (list): A list of lists [(a_i, b_i, c_i, d_i), mu_i, nu_i] representing the TIFNs.

    Returns:
    tuple: A list containing the maximum TIFN.
    '''
    sorted_tifns = sort_tifns(tifns)

    return sorted_tifns[-1]

# --------------------------------------------------------------------------------------------------

def hamming_distance(A1, A2):
    '''
    Calculate the Hamming distance between two trapezoidal intuitionistic fuzzy numbers (TIFNs).

    Parameters:
    A1 (list): A list [(a1, b1, c1, d1), mu1, nu1] representing the first TIFN.
    A2 (list): A list [(a2, b2, c2, d2), mu2, nu2] representing the second TIFN.

    Returns:
    float: The Hamming distance between the two TIFNs, rounded to the specified precision.

    Raises:
    ValueError: If any of the TIFN parameters are invalid.
    '''
    # Unpack the TIFNs
    (a1, b1, c1, d1), mu1, nu1 = A1
    (a2, b2, c2, d2), mu2, nu2 = A2

    # Validate both TIFNs
    for i, A in enumerate([A1, A2], start=1):
        try:
            validate_tifn(A)
        except ValueError as e:
            raise ValueError(f'Error in TIFN {i}: {str(e)}')

    # Compute the Hamming distance
    trapezoidal_distance = (abs(a1 - a2) + abs(b1 - b2) + abs(c1 - c2) + abs(d1 - d2)) / 4
    membership_distance = abs(mu1 - mu2)
    non_membership_distance = abs(nu1 - nu2)
    hamming_distance = trapezoidal_distance + max(membership_distance, non_membership_distance)

    return hamming_distance

# --------------------------------------------------------------------------------------------------

def euclidean_distance(A1, A2):
    '''
    Calculate the Euclidean distance between two trapezoidal intuitionistic fuzzy numbers (TIFNs).

    Parameters:
    A1 (list): A list [(a1, b1, c1, d1), mu1, nu1] representing the first TIFN.
    A2 (list): A list [(a2, b2, c2, d2), mu2, nu2] representing the second TIFN.

    Returns:
    float: The Euclidean distance between the two TIFNs, rounded to the specified precision.

    Raises:
    ValueError: If any of the TIFN parameters are invalid.
    '''
    # Unpack the TIFNs
    (a1, b1, c1, d1), mu1, nu1 = A1
    (a2, b2, c2, d2), mu2, nu2 = A2

    # Validate both TIFNs
    for i, A in enumerate([A1, A2], start=1):
        try:
            validate_tifn(A)
        except ValueError as e:
            raise ValueError(f'Error in TIFN {i}: {str(e)}')

    # Compute the Euclidean distance
    trapezoidal_distance_sq = (a1 - a2) ** 2 + (b1 - b2) ** 2 + (c1 - c2) ** 2 + (d1 - d2) ** 2
    membership_distance_sq = (mu1 - mu2) ** 2
    non_membership_distance_sq = (nu1 - nu2) ** 2
    euclidean_distance_sq = trapezoidal_distance_sq + max(membership_distance_sq, non_membership_distance_sq)
    euclidean_distance = math.sqrt(euclidean_distance_sq) / 2

    return euclidean_distance

# --------------------------------------------------------------------------------------------------

def alpha_cut(A, alpha=None):
    '''
    Calculate the α-cut set for a trapezoidal intuitionistic fuzzy number (TIFN).

    Parameters:
    A (list): A list [(a, b, c, d), mu, nu] representing the TIFN.
    alpha (float or None): The α value for the α-cut, must be between 0 and membership degree if provided. If None, return the bounds parametrically as functions of α.

    Returns:
    list: If alpha is provided, returns [alpha_cut_lower_bound, alpha_cut_upper_bound] representing the lower and upper bounds of the α-cut set.
          If alpha is None, returns the bounds parametrically as [lower_bound_expr, upper_bound_expr].

    Raises:
    ValueError: If any of the input values are invalid.
    '''

    # Unpack the TIFN
    (a, b, c, d), mu, nu = A

    # Validate the TIFN
    validate_tifn(A)

    if alpha is not None:
        # Validate alpha
        if not (0 <= alpha <= mu):
            raise ValueError(f'Invalid value for alpha: {alpha}. It must be between 0 and the membership degree mu={mu} (inclusive).')

        # Calculate the lower and upper bounds of the α-cut set
        alpha_cut_lower_bound = a + (alpha * (b - a) / mu)
        alpha_cut_upper_bound = d - (alpha * (d - c) / mu)

        return [alpha_cut_lower_bound, alpha_cut_upper_bound]

    else:
        # Return the bounds parametrically
        lower_bound_expr = f'{a} + {(b - a) / mu}α'
        upper_bound_expr = f'{d} - {(d - c) / mu}α'

        return [lower_bound_expr, upper_bound_expr]
    
# --------------------------------------------------------------------------------------------------

def beta_cut(A, beta=None):
    '''
    Calculate the β-cut set for a trapezoidal intuitionistic fuzzy number (TIFN).

    Parameters:
    A (list): A list [(a, b, c, d), mu, nu] representing the TIFN.
    beta (float or None): The β value for the β-cut, must be between non-membership degree and 1 if provided. If None, return the bounds parametrically as functions of β.

    Returns:
    list: If beta is provided, returns [beta_cut_lower_bound, beta_cut_upper_bound] representing the lower and upper bounds of the β-cut set.
          If beta is None, returns the bounds parametrically as [lower_bound_expr, upper_bound_expr].

    Raises:
    ValueError: If any of the input values are invalid.
    '''

    # Unpack the TIFN
    (a, b, c, d), mu, nu = A

    # Validate the TIFN
    validate_tifn(A)

    if beta is not None:
        # Validate beta
        if not (nu <= beta <= 1):
            raise ValueError(f'Invalid value for beta: {beta}. It must be between non-membership degree nu={nu} and 1 (inclusive).')

        # Calculate the lower and upper bounds of the β-cut set
        beta_cut_lower_bound = (b * (1 - beta) + a * (beta - nu)) / (1 - nu)
        beta_cut_upper_bound = (c * (1 - beta) + d * (beta - nu)) / (1 - nu)

        return [beta_cut_lower_bound, beta_cut_upper_bound]

    else:
        # Return the bounds parametrically
        lower_bound_expr = f'({b}(1 - β) + {a}(β - {nu})) / {1 - nu})'
        upper_bound_expr = f'({c}(1 - β) + {d}(β- {nu})) / {1 - nu})'

        return [lower_bound_expr, upper_bound_expr]
    
# --------------------------------------------------------------------------------------------------

def membership_mean(A):
    '''
    Calculate the possibilistic mean of the membership function for a trapezoidal intuitionistic fuzzy number (TIFN).

    Parameters:
    A (list): A list [(a, b, c, d), mu, nu] representing the TIFN.

    Returns:
    float: The possibilistic mean of the membership function, rounded to the specified precision.

    Raises:
    ValueError: If any of the input values are invalid.
    '''
    # Unpack the TIFN
    (a, b, c, d), mu, nu = A

    # Validate the TIFN
    validate_tifn(A)

    # Define alpha cut lower and upper bounds
    def alpha_cut_lower_bound(a, b, mu, alpha):
        return a + (alpha * (b - a) / mu)

    def alpha_cut_upper_bound(c, d, mu, alpha):
        return d - (alpha * (d - c) / mu)

    # Define the integrand for the possibilistic mean calculation
    def integrand(alpha):
        lower_bound = alpha_cut_lower_bound(a, b, mu, alpha)
        upper_bound = alpha_cut_upper_bound(c, d, mu, alpha)
        return (lower_bound + upper_bound) * alpha

    # Perform the integration
    result, _ = integrate.quad(integrand, 0, mu)

    return result

# --------------------------------------------------------------------------------------------------

def nonmembership_mean(A):
    '''
    Calculate the possibilistic mean of the non-membership function for a trapezoidal intuitionistic fuzzy number (TIFN).

    Parameters:
    A (list): A list [(a, b, c, d), mu, nu] representing the TIFN.

    Returns:
    float: The possibilistic mean of the non-membership function, rounded to the specified precision.

    Raises:
    ValueError: If any of the input values are invalid.
    '''
    # Unpack the TIFN
    (a, b, c, d), mu, nu = A

    # Validate the TIFN
    validate_tifn(A)

    # Define beta cut lower and upper bounds
    def beta_cut_lower_bound(a, b, nu, beta):
        return (b * (1 - beta) + a * (beta - nu)) / (1 - nu)

    def beta_cut_upper_bound(c, d, nu, beta):
        return (c * (1 - beta) + d * (beta - nu)) / (1 - nu)

    # Define the integrand for the possibilistic mean calculation
    def integrand(beta):
        lower_bound = beta_cut_lower_bound(a, b, nu, beta)
        upper_bound = beta_cut_upper_bound(c, d, nu, beta)
        return (lower_bound + upper_bound) * beta

    # Perform the integration
    result, _ = integrate.quad(integrand, nu, 1)

    return result

# --------------------------------------------------------------------------------------------------

def membership_variance(A):
    '''
    Calculate the possibilistic variance of the membership function for a trapezoidal intuitionistic fuzzy number (TIFN).

    Parameters:
    A (list): A list [(a, b, c, d), mu, nu] representing the TIFN.

    Returns:
    float: The possibilistic variance of the membership function, rounded to the specified precision.

    Raises:
    ValueError: If any of the input values are invalid.
    '''
    # Unpack the TIFN
    (a, b, c, d), mu, nu = A

    # Validate the TIFN
    validate_tifn(A)

    # Define alpha cut lower and upper bounds
    def alpha_cut_lower_bound(a, b, mu, alpha):
        return a + (alpha * (b - a) / mu)

    def alpha_cut_upper_bound(c, d, mu, alpha):
        return d - (alpha * (d - c) / mu)

    # Define the integrand for the possibilistic variance calculation
    def integrand(alpha):
        mean = membership_mean(A)
        lower_bound = alpha_cut_lower_bound(a, b, mu, alpha)
        upper_bound = alpha_cut_upper_bound(c, d, mu, alpha)
        return (0.5) * ((mean - lower_bound) ** 2 + (upper_bound - mean) ** 2) * alpha

    # Perform the integration
    result, _ = integrate.quad(integrand, 0, mu)

    return result

# --------------------------------------------------------------------------------------------------

def nonmembership_variance(A):
    '''
    Calculate the possibilistic variance of the non-membership function for a trapezoidal intuitionistic fuzzy number (TIFN).

    Parameters:
    A (list): A list [(a, b, c, d), mu, nu] representing the TIFN.

    Returns:
    float: The possibilistic variance of the non-membership function, rounded to the specified precision.

    Raises:
    ValueError: If any of the input values are invalid.
    '''
    # Unpack the TIFN
    (a, b, c, d), mu, nu = A

    # Validate the TIFN
    validate_tifn(A)

    # Define beta cut lower and upper bounds
    def beta_cut_lower_bound(a, b, nu, beta):
        return (b * (1 - beta) + a * (beta - nu)) / (1 - nu)

    def beta_cut_upper_bound(c, d, nu, beta):
        return (c * (1 - beta) + d * (beta - nu)) / (1 - nu)

    # Define the integrand for the possibilistic variance calculation
    def integrand(beta):
        mean = nonmembership_mean(A)
        lower_bound = beta_cut_lower_bound(a, b, nu, beta)
        upper_bound = beta_cut_upper_bound(c, d, nu, beta)
        return (0.5) * ((mean - lower_bound) ** 2 + (upper_bound - mean) ** 2) * beta

    # Perform the integration
    result, _ = integrate.quad(integrand, nu, 1)

    return result

# --------------------------------------------------------------------------------------------------

def membership_covariance(A1, A2):
    '''
    Calculate the possibilistic covariance of the membership function between two trapezoidal intuitionistic fuzzy numbers (TIFNs).

    Parameters:
    A1 (list): A list [(a1, b1, c1, d1), mu1, nu1] representing the first TIFN.
    A2 (list): A list [(a2, b2, c2, d2), mu2, nu2] representing the second TIFN.

    Returns:
    float: The possibilistic covariance of the membership function, rounded to the specified precision.

    Raises:
    ValueError: If any of the input values are invalid.
    '''
    # Unpack TIFNs
    (a1, b1, c1, d1), mu1, nu1 = A1
    (a2, b2, c2, d2), mu2, nu2 = A2

    # Validate both TIFNs
    for i, A in enumerate([A1, A2], start=1):
        try:
            validate_tifn(A)
        except ValueError as e:
            raise ValueError(f'Error in TIFN {i}: {str(e)}')

    # Define alpha cut lower and upper bounds
    def alpha_cut_lower_bound(a, b, mu, alpha):
        return a + (alpha * (b - a) / mu)

    def alpha_cut_upper_bound(c, d, mu, alpha):
        return d - (alpha * (d - c) / mu)

    # Define the integrand for the possibilistic covariance calculation
    def integrand(alpha):
        mean1 = membership_mean(A1)
        mean2 = membership_mean(A2)
        lower_bound1 = alpha_cut_lower_bound(a1, b1, mu1, alpha)
        lower_bound2 = alpha_cut_lower_bound(a2, b2, mu2, alpha)
        upper_bound1 = alpha_cut_upper_bound(c1, d1, mu1, alpha)
        upper_bound2 = alpha_cut_upper_bound(c2, d2, mu2, alpha)
        return (0.5) * ((mean1 - lower_bound1) * (mean2 - lower_bound2) +
                        (upper_bound1 - mean1) * (upper_bound2 - mean2)) * alpha

    # Perform the integration
    result, _ = integrate.quad(integrand, 0, min(mu1, mu2))

    return result

# --------------------------------------------------------------------------------------------------

def nonmembership_covariance(A1, A2):
    '''
    Calculate the possibilistic covariance of the non-membership function between two trapezoidal intuitionistic fuzzy numbers (TIFNs).

    Parameters:
    A1 (list): A list [(a1, b1, c1, d1), mu1, nu1] representing the first TIFN.
    A2 (list): A list [(a2, b2, c2, d2), mu2, nu2] representing the second TIFN.

    Returns:
    float: The possibilistic covariance of the non-membership function, rounded to the specified precision.

    Raises:
    ValueError: If any of the input values are invalid.
    '''
    # Unpack TIFNs
    (a1, b1, c1, d1), mu1, nu1 = A1
    (a2, b2, c2, d2), mu2, nu2 = A2

    # Validate both TIFNs
    for i, A in enumerate([A1, A2], start=1):
        try:
            validate_tifn(A)
        except ValueError as e:
            raise ValueError(f'Error in TIFN {i}: {str(e)}')

    # Define beta cut lower and upper bounds
    def beta_cut_lower_bound(a, b, nu, beta):
        return (b * (1 - beta) + a * (beta - nu)) / (1 - nu)

    def beta_cut_upper_bound(c, d, nu, beta):
        return (c * (1 - beta) + d * (beta - nu)) / (1 - nu)

    # Define the integrand for the possibilistic covariance calculation
    def integrand(beta):
        mean1 = nonmembership_mean(A1)
        mean2 = nonmembership_mean(A2)
        lower_bound1 = beta_cut_lower_bound(a1, b1, nu1, beta)
        lower_bound2 = beta_cut_lower_bound(a2, b2, nu2, beta)
        upper_bound1 = beta_cut_upper_bound(c1, d1, nu1, beta)
        upper_bound2 = beta_cut_upper_bound(c2, d2, nu2, beta)
        return (0.5) * ((mean1 - lower_bound1) * (mean2 - lower_bound2) +
                        (upper_bound1 - mean1) * (upper_bound2 - mean2)) * beta

    # Perform the integration
    result, _ = integrate.quad(integrand, max(nu1, nu2), 1)

    return result

# --------------------------------------------------------------------------------------------------

def credibility_measure(x, A):
    '''
    Calculate both the membership and non-membership degrees of credibility measure for a trapezoidal intuitionistic fuzzy number (TIFN) based on its multi-rule functions.

    Parameters:
    x (float): The value at which to evaluate the functions.
    A (list): A list [(a, b, c, d), mu, nu] representing the TIFN.

    Returns:
    tuple: A tuple (mu_x, nu_x, pi_x) representing the membership, non-membership, and hesitation degrees of credibility measure for x.

    Raises:
    ValueError: If any of the input values are invalid.
    '''
    # Unpack the TIFN
    (a, b, c, d), mu, nu = A

    # Validate the TIFN
    validate_tifn(A)

    # Calculate mu_x and nu_x
    if x < a:
        mu_x = 0
        nu_x = nu
    elif a <= x < b:
        mu_x = (mu * (x - a)) / (2 * (b - a))
        nu_x = (nu * (2 * b - a - x)) / (2 * (b - a))
    elif b <= x <= c:
        mu_x = 0.5 * mu
        nu_x = 0.5 * nu
    elif c < x <= d:
        mu_x = (mu * (x + d - 2 * c)) / (2 * (d - c))
        nu_x = (nu * (d - x)) / (2 * (d - c))
    elif x > d:
        mu_x = mu
        nu_x = 0

    # Calculate pi_x
    pi_x = 1 - (mu_x + nu_x)

    return mu_x, nu_x, pi_x

# --------------------------------------------------------------------------------------------------

def membership_entropy(A):
    '''
    Calculate the credibilistic entropy of the membership function for a trapezoidal intuitionistic fuzzy number (TIFN).

    Parameters:
    A (list): A list [(a, b, c, d), mu, nu] representing the TIFN.

    Returns:
    float: The credibilistic entropy of the membership function, rounded to the specified precision.

    Raises:
    ValueError: If any of the input values are invalid.
    '''
    # Unpack the TIFN
    (a, b, c, d), mu, nu = A

    # Validate the TIFN
    validate_tifn(A)

    # Calculate entropy function over the specified intervals
    def integrand_left_tail(x):
        # This corresponds to the interval where x < a
        return 0

    def integrand_rising_slope(x):
        # This corresponds to the interval a ≤ x < b
        term = (mu * (x - a)) / (2 * (b - a))
        if term == 0 or term == 1:
            return 0
        return -term * math.log(term) - (1 - term) * math.log(1 - term)

    def integrand_plateau(x):
        # This corresponds to the interval b ≤ x ≤ c
        term = mu / 2
        if term == 0 or term == 1:
            return 0
        return -term * math.log(term) - (1 - term) * math.log(1 - term)

    def integrand_falling_slope(x):
        # This corresponds to the interval c < x ≤ d
        term = (mu * (x + d - 2 * c)) / (2 * (d - c))
        if term == 0 or term == 1:
            return 0
        return -term * math.log(term) - (1 - term) * math.log(1 - term)

    def integrand_right_tail(x):
        # This corresponds to the interval where x > d
        term = mu
        if term == 0 or term == 1:
            return 0
        return -term * math.log(term) - (1 - term) * math.log(1 - term)

    # Integrate each term over the specified intervals
    integral_left_tail, _ = integrate.quad(integrand_left_tail, -np.inf, a)
    integral_rising_slope, _ = integrate.quad(integrand_rising_slope, a, b)
    integral_plateau, _ = integrate.quad(integrand_plateau, b, c)
    integral_falling_slope, _ = integrate.quad(integrand_falling_slope, c, d)
    integral_right_tail, _ = integrate.quad(integrand_right_tail, d, +np.inf)

    # Sum the integrals
    result = integral_left_tail + integral_rising_slope + integral_plateau + integral_falling_slope + integral_right_tail

    return result

# Suppress the specific warning
warnings.filterwarnings("ignore")

# --------------------------------------------------------------------------------------------------

def nonmembership_entropy(A):
    '''
    Calculate the credibilistic entropy of the non-membership function for a trapezoidal intuitionistic fuzzy number (TIFN).

    Parameters:
    A (list): A list [(a, b, c, d), mu, nu] representing the TIFN.

    Returns:
    float: The credibilistic entropy of the non-membership function, rounded to the specified precision.

    Raises:
    ValueError: If any of the input values are invalid.
    '''
    # Unpack the TIFN
    (a, b, c, d), mu, nu = A

    # Validate the TIFN
    validate_tifn(A)

    # Calculate entropy function over the specified intervals
    def integrand_left_tail(x):
        # This corresponds to the interval where x < a
        term = nu
        if term == 0 or term == 1:
            return 0
        return -term * math.log(term) - (1 - term) * math.log(1 - term)

    def integrand_rising_slope(x):
        # This corresponds to the interval a ≤ x < b
        term = (nu * (2 * b - a - x)) / (2 * (b - a))
        if term == 0 or term == 1:
            return 0
        return -term * math.log(term) - (1 - term) * math.log(1 - term)

    def integrand_plateau(x):
        # This corresponds to the interval b ≤ x ≤ c
        term = nu / 2
        if term == 0 or term == 1:
            return 0
        return -term * math.log(term) - (1 - term) * math.log(1 - term)

    def integrand_falling_slope(x):
        # This corresponds to the interval c < x ≤ d
        term = (nu * (d - x)) / (2 * (d - c))
        if term == 0 or term == 1:
            return 0
        return -term * math.log(term) - (1 - term) * math.log(1 - term)

    def integrand_right_tail(x):
        # This corresponds to the interval where x > d
        return 0

    # Integrate each term over the specified intervals
    integral_left_tail, _ = integrate.quad(integrand_left_tail, -np.inf, a)
    integral_rising_slope, _ = integrate.quad(integrand_rising_slope, a, b)
    integral_plateau, _ = integrate.quad(integrand_plateau, b, c)
    integral_falling_slope, _ = integrate.quad(integrand_falling_slope, c, d)
    integral_right_tail, _ = integrate.quad(integrand_right_tail, d, +np.inf)

    # Sum the integrals
    result = integral_left_tail + integral_rising_slope + integral_plateau + integral_falling_slope + integral_right_tail

    return result

# Suppress the specific warning
warnings.filterwarnings("ignore")

# --------------------------------------------------------------------------------------------------