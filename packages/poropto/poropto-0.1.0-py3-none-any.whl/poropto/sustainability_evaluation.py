# popy/sustainability_evaluation.py

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

def linguistic_scale(term):
    '''
    Converts a linguistic term into its predefined trapezoidal intuitionistic fuzzy scale.

    Parameters:
    term (str): A string representing the linguistic term to be converted. Acceptable values are as follows:
        'VL' - Very Low
        'L'  - Low
        'ML' - Medium Low
        'M'  - Medium
        'MH' - Medium High
        'H'  - High
        'VH' - Very High

    Returns:
    list: A list [(a, b, c, d), mu, nu] representing the trapezoidal intuitionistic fuzzy scale.

    Raises:
    ValueError: If any of the input terms are invalid.
    '''
    # Define a mapping from linguistic terms to their corresponding fuzzy scales
    mapping = {
            'VL': [(0.00, 0.10, 0.20, 0.30), 0.6, 0.3],  # Very Low
            'L' : [(0.05, 0.15, 0.25, 0.35), 0.2, 0.5],  # Low
            'ML': [(0.20, 0.30, 0.40, 0.70), 0.7, 0.1],  # Medium Low
            'M' : [(0.35, 0.45, 0.50, 0.65), 0.5, 0.5],  # Medium
            'MH': [(0.50, 0.60, 0.75, 0.80), 0.3, 0.6],  # Medium High
            'H' : [(0.65, 0.70, 0.85, 0.90), 0.4, 0.5],  # High
            'VH': [(0.80, 0.90, 1.00, 1.00), 0.7, 0.2],  # Very High
        }

    # Check if the input term is in the mapping
    if term not in mapping:
        raise ValueError(f"Invalid linguistic term '{term}'. Acceptable terms are: {', '.join(mapping.keys())}.")

    return mapping.get(term)

# --------------------------------------------------------------------------------------------------

def experts_weights(linguistic_importance):
    '''
    Calculate the weights (λ) of decision-makers based on their linguistic importance using Trapezoidal Intuitionistic Fuzzy Numbers (TIFNs).

    Parameters:
    linguistic_importance (tuple): A tuple of strings, where each string represents the linguistic term of a decision-maker's importance.
                                   Accepted terms are: 'VL', 'L', 'ML', 'M', 'MH', 'H', 'VH'.

    Returns:
    tuple: A tuple of floats representing the normalized weights of the decision-makers.

    Raises:
    ValueError: If any of the input terms are invalid or if the total importance value is zero.
    '''
    # Define a set of valid linguistic terms
    valid_terms = ['VL', 'L', 'ML', 'M', 'MH', 'H', 'VH']

    # Validate input terms
    if not all(term in valid_terms for term in linguistic_importance):
        raise ValueError(f"Invalid linguistic terms provided. Accepted terms are: {', '.join(valid_terms)}.")

    # Compute the importance values for each term
    importance_values = []
    for term in linguistic_importance:
        # Convert the linguistic term to its TIFN representation
        tifn = linguistic_scale(term)

        # Calculate the expected value for the TIFN
        importance_value = prelim.expected_value(tifn)

        # Append the calculated value to the list
        importance_values.append(importance_value)

    # Calculate the total sum of importance values
    total_importance = sum(importance_values)

    # Check for zero total importance to avoid division errors
    if total_importance == 0:
        raise ValueError('The total sum of importance values is zero, which leads to invalid weight calculations.')

    # Normalize the importance values to compute weights
    weights = tuple(value / total_importance for value in importance_values)

    return weights

# --------------------------------------------------------------------------------------------------

def validate_decision_matrices(file_path):
    '''
    Reads an Excel file containing multiple sheets and validates the qualitative data format.
    Checks if all matrices across sheets have the same dimensions and reports any discrepancies.

    - The first row and first column are headers and should be excluded from the data.
    - The remaining cells contain qualitative data organized in a matrix format.

        Example format of a matrix in the Excel sheet:

        |     | C1 | C2 | ... | Cn |
        |-----|----|----|-----|----|
        | A1  |    |    |     |    |
        | A2  |    |    |     |    |
        | ... |    |    |     |    |
        | Am  |    |    |     |    |

    - The acceptable qualitative terms for filling the matrix are:

        'VL' - Very Low
        'L'  - Low
        'ML' - Medium Low
        'M'  - Medium
        'MH' - Medium High
        'H'  - High
        'VH' - Very High

    Parameters:
    file_path (str): Path to the Excel file.

    Returns:
    str: Confirmation message if the qualitative data format is validated successfully.

    Raises:
    ValueError: If any of the input terms are invalid or if dimension discrepancies are found.
    FileNotFoundError: If the specified file does not exist.
    '''
    # Define valid qualitative terms
    valid_terms = {'VL', 'L', 'ML', 'M', 'MH', 'H', 'VH'}

    # Check if file exists
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")

    # Load the Excel file
    xls = pd.ExcelFile(file_path)

    # Initialize containers
    dimensions = {}

    for sheet_name in xls.sheet_names:
        # Read the sheet
        df = pd.read_excel(xls, sheet_name=sheet_name)

        # Ensure there are at least two rows and two columns
        if df.shape[0] <= 1 or df.shape[1] <= 1:
            raise ValueError(f"Sheet '{sheet_name}' does not have enough data.")

        # Remove the first row and column (headers)
        df = df.iloc[:, 1:]

        # Rename rows and columns
        df.index = [f'A{i+1}' for i in range(df.shape[0])]
        df.columns = [f'C{j+1}' for j in range(df.shape[1])]

        # Validate qualitative terms
        if not df.applymap(lambda x: x in valid_terms).all().all():
            invalid_terms = df[~df.applymap(lambda x: x in valid_terms)]
            raise ValueError(f"Invalid qualitative terms found in sheet '{sheet_name}':\n{invalid_terms}")

        # Store the DataFrame dimensions
        dimensions[sheet_name] = df.shape

    # Check and report dimension discrepancies
    unique_dimensions = set(dimensions.values())

    if len(unique_dimensions) > 1:
        discrepancy_message = '\nDimension discrepancies error found:\n'
        for sheet_name, dim in dimensions.items():
            discrepancy_message += f'{sheet_name}: {dim}\n'
        raise ValueError(discrepancy_message)

    # Return confirmation message if no errors are found
    return 'Qualitative data format validated successfully across all sheets.'

# --------------------------------------------------------------------------------------------------

def aggregate_decision_matrices(file_path, experts_importance):
    '''
    This function validates the Excel sheets, extracts the matrices, converts linguistic terms to TIFNs, and performs weighted aggregation.

    Parameters:
    - file_path (str): Path to the Excel file.
    - experts_importance (tuple): A tuple of strings, where each string represents the linguistic term of a decision-maker's importance.
                                   Accepted terms are: 'VL', 'L', 'ML', 'M', 'MH', 'H', 'VH'.

    Returns:
    pd.DataFrame: A DataFrame containing the aggregated decision matrix for all sheets.
    '''
    # Validate the Excel sheets
    validation_message = validate_decision_matrices(file_path)

    if validation_message != 'Qualitative data format validated successfully across all sheets.':
        raise ValueError('Validation failed. Please check the input Excel file.')

    # Load the Excel file and process each sheet
    xls = pd.ExcelFile(file_path)

    matrices = []
    for i, sheet_name in enumerate(xls.sheet_names):
        # Read and clean up the sheet
        df = pd.read_excel(xls, sheet_name=sheet_name)
        df = df.iloc[:, 1:]
        df.index = [f'A{index+1}' for index in range(df.shape[0])]
        df.columns = [f'C{col+1}' for col in range(df.shape[1])]

        # Convert qualitative terms to TIFNs using linguistic_scale
        tifns = df.applymap(linguistic_scale)

        # Append the processed DataFrame (with TIFNs) to the list of matrices
        matrices.append(tifns)

    # Convert experts' importance to weights
    weights = experts_weights(experts_importance)

    # Initialize an empty DataFrame to store the aggregated matrix
    num_rows, num_cols = matrices[0].shape
    aggregated_matrix = pd.DataFrame(index=matrices[0].index, columns=matrices[0].columns)

    # Iterate over each cell in the matrices
    for i in range(num_rows):
        for j in range(num_cols):
            # Extract corresponding TIFNs from each matrix
            tifns = [matrices[k].iloc[i, j] for k in range(len(matrices))]

            # Perform the weighted aggregation
            aggregated_tifn = prelim.weighted_aggregate_tifns(tifns, weights)

            # Store the result in the aggregated matrix
            aggregated_matrix.iloc[i, j] = aggregated_tifn

    # Set Pandas option to display full content of cells
    pd.set_option('display.max_colwidth', None)

    return aggregated_matrix

# --------------------------------------------------------------------------------------------------

def extract_decision_matrix(aggregated_decision_matrix, sustainability_dimensions, investment_mode):
    '''
    Adjusts the aggregated decision matrix based on the specified investment mode by setting non-relevant columns to 0.

    Parameters:
    - aggregated_decision_matrix (pd.DataFrame): The DataFrame containing the aggregated quantitative decision matrix.
    - sustainability_dimensions (dict): A dictionary specifying the number of columns for each sustainability dimension.
                                        The keys should be 'social', 'environmental', and 'economic', with the corresponding integer values representing the number of columns.
    - investment_mode (str): The mode of investment to filter the matrix. Acceptable modes are: 'sustainable', 'bearable', 'viable', 'equitable', 'social', 'environmental', 'economic'.

    Returns:
    pd.DataFrame: The adjusted decision matrix with non-relevant columns set to 0 based on the selected investment mode.

    Raises:
    ValueError: If the investment mode is not recognized or if the number of columns in the matrix does not match the sum of the sustainability dimensions.
    '''
    aggregated_rows, aggregated_cols = aggregated_decision_matrix.shape

    # Validate dimensions
    if aggregated_cols != sum(sustainability_dimensions.values()):
        raise ValueError('The number of columns in the aggregated decision matrix does not match the number of sustainability dimensions.')

    # Determine the indices for each dimension
    social_end = sustainability_dimensions['social']
    environmental_end = social_end + sustainability_dimensions['environmental']
    economic_end = environmental_end + sustainability_dimensions['economic']

    # Create a boolean mask array initialized to True (keep all columns)
    column_mask = np.ones(aggregated_cols, dtype=bool)

    # Modify the mask based on the investment mode
    if investment_mode == 'bearable':                     # Keep only Social + Environmental
        column_mask[environmental_end:] = False
    elif investment_mode == 'viable':                     # Keep only Environmental + Economic
        column_mask[:social_end] = False
    elif investment_mode == 'equitable':                  # Keep only Social + Economic
        column_mask[social_end:environmental_end] = False
    elif investment_mode == 'social':                     # Keep only Social
        column_mask[social_end:] = False
    elif investment_mode == 'environmental':              # Keep only Environmental
        column_mask[:social_end] = False
        column_mask[environmental_end:] = False
    elif investment_mode == 'economic':                   # Keep only Economic
        column_mask[:environmental_end] = False
    elif investment_mode != 'sustainable':                # Keep all columns
        raise ValueError(f'Invalid investment mode: {investment_mode}.\nAcceptable modes are: sustainable, bearable, viable, equitable, social, environmental, economic.')

    # Apply the mask to set irrelevant columns to 0
    adjusted_matrix = aggregated_decision_matrix.copy()
    adjusted_matrix.loc[:, ~column_mask] = 0

    return adjusted_matrix

# --------------------------------------------------------------------------------------------------

def shannon_entropy(extracted_decision_matrix):
    '''
    Implements the Shannon entropy weighting method with the provided decision matrix to calculate the criteria weights.

    Parameters:
    extracted_decision_matrix (pd.DataFrame): The decision matrix to be analyzed, where each cell contains a TIFN.

    Returns:
    weights_df (pd.DataFrame): A DataFrame containing the weights of sustainability criteria.
    '''
    # Extract the number of rows and columns from the decision matrix
    extracted_rows, extracted_cols = extracted_decision_matrix.shape

    # Calculate the normalization constant for entropy
    k = 1 / math.log(extracted_rows)

    # Initialize matrices for normalized values and entropy
    normalized_matrix = np.zeros((extracted_rows, extracted_cols))
    entropy = np.zeros(extracted_cols)

    # Normalize the decision matrix
    for col in range(extracted_cols):
        # Get the column data, which is a list of TIFNs (Trapezoidal Interval Fuzzy Numbers)
        column_data = extracted_decision_matrix.iloc[:, col].tolist()

        # Check if all values in the column are zero
        if np.all(np.array([value[1] for value in column_data if isinstance(value, tuple) or isinstance(value, list)]) == 0):
            # If the column is zero, set normalized values to zero and skip entropy calculation for this column
            normalized_matrix[:, col] = 0
            continue

        # Aggregate the column data using a user-defined function (not provided here)
        aggregate_value = prelim.aggregate_tifns(column_data)

        # Normalize the values in the column by dividing each TIFN by the aggregated value
        for row in range(extracted_rows):
            normalized_value = prelim.divide_tifns(column_data[row], aggregate_value)
            normalized_matrix[row, col] = prelim.expected_value(normalized_value)

    # Calculate entropy for each criterion
    for col in range(extracted_cols):
        column_sum = np.sum(normalized_matrix[:, col])

        if column_sum == 0:
            # Handle the case where the sum of the column is zero (entropy should be 1 in this case)
            entropy[col] = 1
        else:
            # Calculate the probability distribution
            p_ij = normalized_matrix[:, col] / column_sum
            # Avoid taking log of zero by clipping probabilities
            p_ij = np.clip(p_ij, 1e-10, None)
            # Calculate entropy for the column
            entropy[col] = -k * np.sum(p_ij * np.log(p_ij))

    # Calculate the degree of divergence from maximum entropy
    divergence = 1 - entropy

    # Normalize the divergence to get the weights
    if np.sum(divergence) == 0:
        weights = np.zeros(extracted_cols)
    else:
        weights = divergence / np.sum(divergence)

    # Create a DataFrame for the weights
    weights_df = pd.DataFrame(weights, index=[f'W{i+1}' for i in range(extracted_cols)], columns=['Weight'])

    return weights_df

# --------------------------------------------------------------------------------------------------

def sustainability_scores(extracted_decision_matrix, criteria_weights):
    '''
    Calculates sustainability scores for each alternative based on the decision matrix and criteria weights.

    Parameters:
    - extracted_decision_matrix (pd.DataFrame): The decision matrix containing TIFNs for each criterion.
    - criteria_weights (pd.DataFrame): The criteria weights calculated using Shannon entropy weighting method.

    Returns:
    sustainability_scores_df (pd.DataFrame): A DataFrame containing the sustainability scores for each alternative.
    '''
    # Extract the number of rows and columns from the decision matrix
    extracted_rows, extracted_cols = extracted_decision_matrix.shape

    # Initialize list for sustainability scores
    sustainability_scores = []

    # Initialize the weighted sum as a neutral TIFN (assumed to be zero)
    neutral_tifn = [(0, 0, 0, 0), 0, 1]

    for row in range (extracted_rows):

        weighted_sum = neutral_tifn

        for col in range (extracted_cols):

            # Get the TIFN value from the DataFrame
            tifn_value = extracted_decision_matrix.iloc[row, col]

            # Check if the TIFN value is zero
            if tifn_value == 0:
                continue  # Skip zero values

            # Get the weight for the current criterion
            weight = criteria_weights.iloc[col, 0]

            # Scale the TIFN by the weight
            scaled_tifn = prelim.scale_tifn(tifn_value, weight)

            # Add the scaled TIFN to the weighted sum
            weighted_sum = prelim.add_tifns(weighted_sum, scaled_tifn)

        # Store the sustainability score for the current row
        sustainability_scores.append(weighted_sum)

    # Create DataFrame for the sustainability scores
    sustainability_scores_df = pd.DataFrame({'Sustainability Score': sustainability_scores}, index=[f'A{i+1}' for i in range(extracted_rows)])

    return sustainability_scores_df

# --------------------------------------------------------------------------------------------------

def sustainability_scores_mean(sustainability_scores_data):
    '''
    Calculates the mean of each row's TIFNs and appends the means as new columns to the DataFrame.

    Parameters:
    returns_data (pd.DataFrame): A DataFrame containing the TIF sustainability scores' data.

    Returns:
    pd.DataFrame: The input DataFrame with two additional columns for the mean of each row's TIFNs.
    '''
    # Initialize lists to store the mean values
    membership_means = []
    nonmembership_means = []

    # Iterate over each row in the DataFrame
    for index, row in sustainability_scores_data.iterrows():
        # Assuming there is only one column of TIFN data
        tifn = row[0]
        try:
            # Calculate the mean membership and non-membership degrees
            membership_means.append(prelim.membership_mean(tifn))
            nonmembership_means.append(prelim.nonmembership_mean(tifn))
        except (ValueError, SyntaxError) as e:
            raise ValueError(f'Error processing TIFN at row {index}: {str(e)}')

    # Append the means as new columns to the DataFrame
    sustainability_scores_data['Membership Mean'] = membership_means
    sustainability_scores_data['Non-membership Mean'] = nonmembership_means

    return sustainability_scores_data

# --------------------------------------------------------------------------------------------------