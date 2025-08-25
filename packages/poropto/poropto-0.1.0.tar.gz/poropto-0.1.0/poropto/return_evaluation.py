# poropto/return_evaluation.py

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
import poropto.preliminaries as prelim

# --------------------------------------------------------------------------------------------------

def read_returns_data(file_path):
    '''
    Reads the trapezoidal intuitionistic fuzzy (TIF) return's matrix from an Excel file and formats the data.
    Reads the lower and upper bounds of the investment associated with the respective asset.

    Parameters:
    file_path (str): Path to the Excel file containing the TIF return's data.

    Returns:
    pd.DataFrame: A cleaned DataFrame where the row indices are labeled from 'A1' to 'Am', where 'm' is the number of risky assets.
    '''
    # Load the Excel file into a Pandas ExcelFile object
    xls = pd.ExcelFile(file_path)

    # Read the first sheet of the Excel file into a DataFrame and clean it up
    returns_dataframe = pd.read_excel(xls)
    returns_dataframe = returns_dataframe.iloc[:, 1:]
    returns_dataframe.index = [f'A{index+1}' for index in range(returns_dataframe.shape[0])]

    return returns_dataframe

# --------------------------------------------------------------------------------------------------

def validate_return_matrix(returns_data, aggregated_decision_matrix):
    '''
    Validates the trapezoidal intuitionistic fuzzy (TIF) return's data format.
    Validate the lower and upper bounds of the investment associated with the respective asset.
    Checks if the return matrix has the same dimensions as the aggregated qualitative decision matrix and reports any discrepancies.

    - The first row and first column are headers and should be excluded from the data.
    - The remaining cells contain TIF return's data in a string format.

        Example format of a matrix in the Excel sheet:

        |     |               Return               | Lower bound of investment | Upper bound of investment |
        |-----|------------------------------------|---------------------------|---------------------------|
        | A1  | [(a_1, b_1, c_1, d_1), mu_1, nu_1] |            l1             |            u1             |
        | A2  | [(a_2, b_2, c_2, d_2), mu_2, nu_2] |            l2             |            u2             |
        | ... |                 ...                |           ....            |           ....            |
        | Am  | [(a_m, b_m, c_m, d_m), mu_m, nu_m] |            lm             |            um             |

    Parameters:
    returns_data (pd.DataFrame): A DataFrame containing the TIF return's data.
    aggregated_decision_matrix (pd.DataFrame): A DataFrame containing the aggregated quantitative decision matrix for all experts' opinions.

    Returns:
    str: Confirmation message if the returns' data format is validated successfully.

    Raises:
    ValueError: If any of the input terms are invalid or if dimension discrepancies are found.
    FileNotFoundError: If the specified file does not exist.
    '''
    # Extract the dimensions
    aggregated_rows = aggregated_decision_matrix.shape[0]
    return_rows = returns_data.shape[0]

    # Check if the number of rows match
    if return_rows != aggregated_rows:
        raise ValueError(f'Risky assets numbers (alternatives) mismatch:\n'
                         f'Aggregated Matrix Rows: {aggregated_rows}\n'
                         f'Return Matrix Rows: {return_rows}\n'
                         'Please check the input Excel files for discrepancies.')

    # Validate TIFN entries and bounds in the return matrix
    for row in range(returns_data.shape[0]):
        tifn_str = returns_data.iloc[row, 0]     # TIF return in string format
        lower_bound = returns_data.iloc[row, 1]  # Lower bound of investment
        upper_bound = returns_data.iloc[row, 2]  # Upper bound of investment

        # Validate the TIFN format
        try:
            tifn = ast.literal_eval(tifn_str)  # Convert the string representation of TIFN to a list
            prelim.validate_tifn(tifn)
        except (ValueError, SyntaxError) as e:
            raise ValueError(f'Invalid TIFN at row {returns_data.index[row]}: {str(e)}')

        # Validate that the bounds are between 0 and 1
        if not (0 <= lower_bound <= 1):
            raise ValueError(f'Lower bound of investment at row {returns_data.index[row]} is out of range (0 to 1): {lower_bound}')
        if not (0 <= upper_bound <= 1):
            raise ValueError(f'Upper bound of investment at row {returns_data.index[row]} is out of range (0 to 1): {upper_bound}')

    return r'Trapezoidal intuitionistic fuzzy returns data format and its corresponding investment bounds validated successfully.'

# --------------------------------------------------------------------------------------------------

def returns_mean(returns_data):
    '''
    Calculates the mean of each row's TIFNs and appends the means as new columns to the DataFrame.

    Parameters:
    returns_data (pd.DataFrame): A DataFrame containing the TIF return's data.

    Returns:
    pd.DataFrame: The input DataFrame with two additional columns for the mean of each row's TIFNs.
    '''
    # Remove the bounds columns
    returns_data = returns_data.drop(columns=['Lower bound of investment', 'Upper bound of investment'])

    # Initialize lists to store the mean values
    membership_means = []
    nonmembership_means = []

    # Iterate over each row in the DataFrame
    for index, row in returns_data.iterrows():
        # Assuming there is only one column of TIFN data
        tifn_str = row[0]
        try:
            # Convert the string representation of TIFN to a list
            tifn = ast.literal_eval(tifn_str)
            # Calculate the mean membership and non-membership degrees
            membership_means.append(prelim.membership_mean(tifn))
            nonmembership_means.append(prelim.nonmembership_mean(tifn))
        except (ValueError, SyntaxError) as e:
            raise ValueError(f'Error processing TIFN at row {index}: {str(e)}')

    # Append the means as new columns to the DataFrame
    returns_data['Membership Mean'] = membership_means
    returns_data['Non-membership Mean'] = nonmembership_means

    return returns_data

# --------------------------------------------------------------------------------------------------

def returns_variance(returns_data):
    '''
    Calculates the variance of each row's TIFNs and appends the variance as new columns to the DataFrame.

    Parameters:
    returns_data (pd.DataFrame): A DataFrame containing the TIF return's data.

    Returns:
    pd.DataFrame: The input DataFrame with two additional columns for the variance of each row's TIFNs.
    '''
    # Remove the bounds columns
    returns_data = returns_data.drop(columns=['Lower bound of investment', 'Upper bound of investment'])

    # Initialize lists to store the variance values
    membership_variances = []
    nonmembership_variances = []

    # Iterate over each row in the DataFrame
    for index, row in returns_data.iterrows():
        # Assuming there is only one column of TIFN data
        tifn_str = row[0]
        try:
            # Convert the string representation of TIFN to a list
            tifn = ast.literal_eval(tifn_str)
            # Calculate the variance for membership and non-membership degrees
            membership_variances.append(prelim.membership_variance(tifn))
            nonmembership_variances.append(prelim.nonmembership_variance(tifn))
        except (ValueError, SyntaxError) as e:
            raise ValueError(f'Error processing TIFN at row {index}: {str(e)}')

    # Append the variances as new columns to the DataFrame
    returns_data['Membership Variance'] = membership_variances
    returns_data['Non-membership Variance'] = nonmembership_variances

    return returns_data

# --------------------------------------------------------------------------------------------------

def returns_covariance(returns_data):
    '''
    Calculates the covariance matrix of TIFNs.

    Parameters:
    returns_data (pd.DataFrame): A DataFrame containing the TIF return's data.

    Returns:
    tuple: A tuple containing two DataFrames:
            - membership_covariance_df: A DataFrame representing the covariance matrix of membership values of TIFNs.
            - nonmembership_covariance_df: A DataFrame representing the covariance matrix of non-membership values of TIFNs.
    '''
    # Initialize matrices to store covariance results
    num_rows = returns_data.shape[0]
    membership_covariance_matrix = np.zeros((num_rows, num_rows))
    nonmembership_covariance_matrix = np.zeros((num_rows, num_rows))

    # Convert TIFN strings to lists
    tifns = []
    for index, row in returns_data.iterrows():
        tifn_str = row[0]
        try:
            tifn = ast.literal_eval(tifn_str)
            tifns.append(tifn)
        except (ValueError, SyntaxError) as e:
            raise ValueError(f'Error processing TIFN at row {index}: {str(e)}')

    # Compute pairwise covariance
    for i in range(num_rows):
        for j in range(num_rows):
            if i == j:
                membership_covariance_matrix[i, j] = prelim.membership_variance(tifns[i])
                nonmembership_covariance_matrix[i, j] = prelim.nonmembership_variance(tifns[i])
            else:
                membership_covariance_matrix[i, j] = prelim.membership_covariance(tifns[i], tifns[j])
                nonmembership_covariance_matrix[i, j] = prelim.nonmembership_covariance(tifns[i], tifns[j])

    # Create DataFrames with covariance matrices and proper labels
    membership_covariance_df = pd.DataFrame(membership_covariance_matrix, index=returns_data.index, columns=returns_data.index)
    nonmembership_covariance_df = pd.DataFrame(nonmembership_covariance_matrix, index=returns_data.index, columns=returns_data.index)

    return membership_covariance_df, nonmembership_covariance_df

# --------------------------------------------------------------------------------------------------

def returns_entropy(returns_data):
    '''
    Calculates the entropy of each row's TIFNs and appends the entropy as new columns to the DataFrame.

    Parameters:
    returns_data (pd.DataFrame): A DataFrame containing the TIF return's data.

    Returns:
    pd.DataFrame: The input DataFrame with two additional columns for the entropy of each row's TIFNs.
    '''
    # Remove the bounds columns
    returns_data = returns_data.drop(columns=['Lower bound of investment', 'Upper bound of investment'])

    # Initialize lists to store the entropy values
    membership_entropy_values = []
    nonmembership_entropy_values = []

    # Iterate over each row in the DataFrame
    for index, row in returns_data.iterrows():
        # Assuming there is only one column of TIFN data
        tifn_str = row[0]
        try:
            # Convert the string representation of TIFN to a list
            tifn = ast.literal_eval(tifn_str)
            # Calculate the mean membership and non-membership degrees
            membership_entropy_values.append(prelim.membership_entropy(tifn))
            nonmembership_entropy_values.append(prelim.nonmembership_entropy(tifn))
        except (ValueError, SyntaxError) as e:
            raise ValueError(f'Error processing TIFN at row {index}: {str(e)}')

    # Append the means as new columns to the DataFrame
    returns_data['Membership Entropy'] = membership_entropy_values
    returns_data['Non-membership Entropy'] = nonmembership_entropy_values

    return returns_data

# --------------------------------------------------------------------------------------------------