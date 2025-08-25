# poropto/portfolio_optimization.py

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
import matplotlib.pyplot as plt
from pyomo.opt import SolverFactory
import poropto.preliminaries as prelim
import poropto.sustainability_evaluation as sust_eval 
import poropto.return_evaluation as ret_eval

# --------------------------------------------------------------------------------------------------

def min_operator(sustainability_scores_data, returns_data, selected_assets, gamma):
    '''
    Optimize a series of investment dimensions objective functions and extract results.

    This function sets up and solves multiple investment optimization models using Pyomo.
    Each model targets a different objective related to investment optimization, including sustainability, returns mean, variance, and entropy.
    It solves the models using appropriate solvers and returns a DataFrame summarizing the results.

    Parameters:
    - models (list of pyomo.ConcreteModel): List of Pyomo optimization models to be solved. Each model should be defined with specific parameters and constraints.
    - model_names (list of str): Names of the models. This list should correspond to the order of the models in the `models` list.
    - sustainability_scores_expected_values (dict): Dictionary of expected values for sustainability scores, with keys as asset indices.
    - gamma (float): Parameter used in investment constraints related to sustainability scores.
    - selected_assets (tuple): Tuple containing the lower and upper bounds for the number of selected assets.
    - lower_investment_bounds (dict): Dictionary of lower bounds for investment proportions, with keys as asset indices.
    - upper_investment_bounds (dict): Dictionary of upper bounds for investment proportions, with keys as asset indices.
    - sustainability_scores_membership_mean (dict): Dictionary of mean membership scores for sustainability, with keys as asset indices.
    - sustainability_scores_nonmembership_mean (dict): Dictionary of mean non-membership scores for sustainability, with keys as asset indices.
    - returns_membership_mean (dict): Dictionary of mean membership scores for returns, with keys as asset indices.
    - returns_nonmembership_mean (dict): Dictionary of mean non-membership scores for returns, with keys as asset indices.
    - returns_membership_variance (dict of dict): Dictionary of variance membership scores for returns, with keys as tuples of asset indices (i, j).
    - returns_nonmembership_variance (dict of dict): Dictionary of variance non-membership scores for returns, with keys as tuples of asset indices (i, j).
    - returns_membership_entropy (dict): Dictionary of entropy membership scores for returns, with keys as asset indices.
    - returns_nonmembership_entropy (dict): Dictionary of entropy non-membership scores for returns, with keys as asset indices.

    Returns:
    - pd.DataFrame: DataFrame summarizing the results of the optimization models. The DataFrame includes:
        - 'Objective Functions': Names of the models.
        - 'Minimum Value': Minimum values of the objective functions for each model.
        - 'x1', 'x2', ..., 'xn': Investment proportions for each asset across models, where n is the total number of assets.
    '''
    # Define asset numbers as indexes of sets ---------------------------------------------------------------------------------------------------
    assets_number = sustainability_scores_data.shape[0]

    # Define parameters of objective functions --------------------------------------------------------------------------------------------------
    # Sustainability functions
    sustainability_scores_membership_mean = {
        i + 1: sust_eval.sustainability_scores_mean(sustainability_scores_data).iloc[i, 1]
        for i in range(assets_number)
    }

    sustainability_scores_nonmembership_mean = {
        i + 1: sust_eval.sustainability_scores_mean(sustainability_scores_data).iloc[i, 2]
        for i in range(assets_number)
    }

    # Returns' mean functions
    returns_membership_mean = {
        i + 1: ret_eval.returns_mean(returns_data).iloc[i, 1]
        for i in range(assets_number)
    }

    returns_nonmembership_mean = {
        i + 1: ret_eval.returns_mean(returns_data).iloc[i, 2]
        for i in range(assets_number)
    }

    # Returns' variance functions
    returns_membership_variance = {
        (i + 1, j + 1): ret_eval.returns_covariance(returns_data)[0].iloc[i, j]
        for i in range(assets_number)
        for j in range(assets_number)
    }

    returns_nonmembership_variance = {
        (i + 1, j + 1): ret_eval.returns_covariance(returns_data)[1].iloc[i, j]
        for i in range(assets_number)
        for j in range(assets_number)
    }

    # Returns' entropy functions
    returns_membership_entropy = {
        i + 1: ret_eval.returns_entropy(returns_data).iloc[i, 1]
        for i in range(assets_number)
    }

    returns_nonmembership_entropy = {
        i + 1: ret_eval.returns_entropy(returns_data).iloc[i, 2]
        for i in range(assets_number)
    }

    # Define parameters of constraints ----------------------------------------------------------------------------------------------------------
    sustainability_scores_expected_values = {}
    for i in range(assets_number):
        sustainability_scores_expected_values[i+1] = prelim.expected_value(sustainability_scores_data.iloc[i, 0])

    lower_investment_bounds = {}
    for i in range(assets_number):
        lower_investment_bounds[i+1] = returns_data.iloc[i, 1]

    upper_investment_bounds = {}
    for i in range(assets_number):
        upper_investment_bounds[i+1] = returns_data.iloc[i, 2]

    # Model1 ------------------------------------------------------------------------------------------------------------------------------------
    model1 = pyo.ConcreteModel(name='Sustainability Membership Function')

    model1.i = pyo.RangeSet(1, assets_number)

    model1.sustainability_scores_membership_mean = pyo.Param(model1.i, initialize=sustainability_scores_membership_mean)
    model1.sustainability_scores_expected_values = pyo.Param(model1.i, initialize=sustainability_scores_expected_values)
    model1.gamma = pyo.Param(initialize=gamma)
    model1.selected_assets_lower_bound = pyo.Param(initialize=selected_assets[0])
    model1.selected_assets_upper_bound = pyo.Param(initialize=selected_assets[1])
    model1.lower_investment_bounds = pyo.Param(model1.i, initialize=lower_investment_bounds)
    model1.upper_investment_bounds = pyo.Param(model1.i, initialize=upper_investment_bounds)

    model1.x = pyo.Var(model1.i, domain=pyo.NonNegativeReals, bounds=(0, 1))
    model1.y = pyo.Var(model1.i, domain=pyo.Binary)

    def sustainability_membership_function(model1):
        return sum(model1.x[i] * model1.sustainability_scores_membership_mean[i] for i in model1.i)
    model1.Obj = pyo.Objective(rule=sustainability_membership_function, sense=pyo.minimize)

    model1.CapitalBudgetConstraint = pyo.Constraint(rule=lambda model1: sum(model1.x[i] for i in model1.i) == 1)
    model1.CardinalityConstraintLowerBound = pyo.Constraint(rule=lambda model1: model1.selected_assets_lower_bound <= sum(model1.y[i] for i in model1.i))
    model1.CardinalityConstraintUpperBound = pyo.Constraint(rule=lambda model1: sum(model1.y[i] for i in model1.i) <= model1.selected_assets_upper_bound)
    model1.InvestmentBoundsConstraintLowerBound = pyo.Constraint(model1.i, rule=lambda model1, i: (model1.lower_investment_bounds[i] - model1.sustainability_scores_expected_values[i] * (1 - model1.gamma)) * model1.y[i] <= model1.x[i])
    model1.InvestmentBoundsConstraintUpperBound = pyo.Constraint(model1.i, rule=lambda model1, i: (model1.upper_investment_bounds[i] + model1.sustainability_scores_expected_values[i] * (1 - model1.gamma)) * model1.y[i] >= model1.x[i])
    model1.NoShortSelling = pyo.Constraint(model1.i, rule=lambda model1, i: model1.x[i] >= 0)

    solver = pyo.SolverFactory('bonmin')
    result = solver.solve(model1)

    # Model2 ------------------------------------------------------------------------------------------------------------------------------------
    model2 = pyo.ConcreteModel(name='Returns Mean Membership Function')

    model2.i = pyo.RangeSet(1, assets_number)

    model2.returns_membership_mean = pyo.Param(model2.i, initialize=returns_membership_mean)
    model2.sustainability_scores_expected_values = pyo.Param(model2.i, initialize=sustainability_scores_expected_values)
    model2.gamma = pyo.Param(initialize=gamma)
    model2.selected_assets_lower_bound = pyo.Param(initialize=selected_assets[0])
    model2.selected_assets_upper_bound = pyo.Param(initialize=selected_assets[1])
    model2.lower_investment_bounds = pyo.Param(model2.i, initialize=lower_investment_bounds)
    model2.upper_investment_bounds = pyo.Param(model2.i, initialize=upper_investment_bounds)

    model2.x = pyo.Var(model2.i, domain=pyo.NonNegativeReals, bounds=(0, 1))
    model2.y = pyo.Var(model2.i, domain=pyo.Binary)

    def returns_mean_membership_function(model2):
        return sum(model2.x[i] * model2.returns_membership_mean[i] for i in model2.i)
    model2.Obj = pyo.Objective(rule=returns_mean_membership_function, sense=pyo.minimize)

    model2.CapitalBudgetConstraint = pyo.Constraint(rule=lambda model2: sum(model2.x[i] for i in model2.i) == 1)
    model2.CardinalityConstraintLowerBound = pyo.Constraint(rule=lambda model2: model2.selected_assets_lower_bound <= sum(model2.y[i] for i in model2.i))
    model2.CardinalityConstraintUpperBound = pyo.Constraint(rule=lambda model2: sum(model2.y[i] for i in model2.i) <= model2.selected_assets_upper_bound)
    model2.InvestmentBoundsConstraintLowerBound = pyo.Constraint(model2.i, rule=lambda model2, i: (model2.lower_investment_bounds[i] - model2.sustainability_scores_expected_values[i] * (1 - model2.gamma)) * model2.y[i] <= model2.x[i])
    model2.InvestmentBoundsConstraintUpperBound = pyo.Constraint(model2.i, rule=lambda model2, i: (model2.upper_investment_bounds[i] + model2.sustainability_scores_expected_values[i] * (1 - model2.gamma)) * model2.y[i] >= model2.x[i])
    model2.NoShortSelling = pyo.Constraint(model2.i, rule=lambda model2, i: model2.x[i] >= 0)

    solver = pyo.SolverFactory('bonmin')
    result = solver.solve(model2)

    # Model3 ------------------------------------------------------------------------------------------------------------------------------------
    model3 = pyo.ConcreteModel(name='Returns Variance Membership Function')

    model3.i = pyo.RangeSet(1, assets_number)
    model3.j = pyo.RangeSet(1, assets_number)

    model3.returns_membership_variance = pyo.Param(model3.i, model3.j, initialize=returns_membership_variance)
    model3.sustainability_scores_expected_values = pyo.Param(model3.i, initialize=sustainability_scores_expected_values)
    model3.gamma = pyo.Param(initialize=gamma)
    model3.selected_assets_lower_bound = pyo.Param(initialize=selected_assets[0])
    model3.selected_assets_upper_bound = pyo.Param(initialize=selected_assets[1])
    model3.lower_investment_bounds = pyo.Param(model3.i, initialize=lower_investment_bounds)
    model3.upper_investment_bounds = pyo.Param(model3.i, initialize=upper_investment_bounds)

    model3.x = pyo.Var(model3.i, domain=pyo.NonNegativeReals, bounds=(0, 1))
    model3.y = pyo.Var(model3.i, domain=pyo.Binary)

    def returns_variance_membership_function(model3):
        return sum(model3.x[i] * model3.x[j] * model3.returns_membership_variance[(i, j)] for i in model3.i for j in model3.j)
    model3.Obj = pyo.Objective(rule=returns_variance_membership_function, sense=pyo.minimize)

    model3.CapitalBudgetConstraint = pyo.Constraint(rule=lambda model3: sum(model3.x[i] for i in model3.i) == 1)
    model3.CardinalityConstraintLowerBound = pyo.Constraint(rule=lambda model3: model3.selected_assets_lower_bound <= sum(model3.y[i] for i in model3.i))
    model3.CardinalityConstraintUpperBound = pyo.Constraint(rule=lambda model3: sum(model3.y[i] for i in model3.i) <= model3.selected_assets_upper_bound)
    model3.InvestmentBoundsConstraintLowerBound = pyo.Constraint(model3.i, rule=lambda model3, i: (model3.lower_investment_bounds[i] - model3.sustainability_scores_expected_values[i] * (1 - model3.gamma)) * model3.y[i] <= model3.x[i])
    model3.InvestmentBoundsConstraintUpperBound = pyo.Constraint(model3.i, rule=lambda model3, i: (model3.upper_investment_bounds[i] + model3.sustainability_scores_expected_values[i] * (1 - model3.gamma)) * model3.y[i] >= model3.x[i])
    model3.NoShortSelling = pyo.Constraint(model3.i, rule=lambda model3, i: model3.x[i] >= 0)

    solver = pyo.SolverFactory('bonmin')
    result = solver.solve(model3)

    # Model4 ------------------------------------------------------------------------------------------------------------------------------------
    model4 = pyo.ConcreteModel(name='Returns Entropy Membership Function')

    model4.i = pyo.RangeSet(1, assets_number)

    model4.returns_membership_entropy = pyo.Param(model4.i, initialize=returns_membership_entropy)
    model4.sustainability_scores_expected_values = pyo.Param(model4.i, initialize=sustainability_scores_expected_values)
    model4.gamma = pyo.Param(initialize=gamma)
    model4.selected_assets_lower_bound = pyo.Param(initialize=selected_assets[0])
    model4.selected_assets_upper_bound = pyo.Param(initialize=selected_assets[1])
    model4.lower_investment_bounds = pyo.Param(model4.i, initialize=lower_investment_bounds)
    model4.upper_investment_bounds = pyo.Param(model4.i, initialize=upper_investment_bounds)

    model4.x = pyo.Var(model4.i, domain=pyo.NonNegativeReals, bounds=(0, 1))
    model4.y = pyo.Var(model4.i, domain=pyo.Binary)

    def returns_entropy_membership_function(model4):
        return sum(model4.x[i] * model4.returns_membership_entropy[i] for i in model4.i)
    model4.Obj = pyo.Objective(rule=returns_entropy_membership_function, sense=pyo.minimize)

    model4.CapitalBudgetConstraint = pyo.Constraint(rule=lambda model4: sum(model4.x[i] for i in model4.i) == 1)
    model4.CardinalityConstraintLowerBound = pyo.Constraint(rule=lambda model4: model4.selected_assets_lower_bound <= sum(model4.y[i] for i in model4.i))
    model4.CardinalityConstraintUpperBound = pyo.Constraint(rule=lambda model4: sum(model4.y[i] for i in model4.i) <= model4.selected_assets_upper_bound)
    model4.InvestmentBoundsConstraintLowerBound = pyo.Constraint(model4.i, rule=lambda model4, i: (model4.lower_investment_bounds[i] - model4.sustainability_scores_expected_values[i] * (1 - model4.gamma)) * model4.y[i] <= model4.x[i])
    model4.NoShortSelling = pyo.Constraint(model4.i, rule=lambda model4, i: model4.x[i] >= 0)

    solver = pyo.SolverFactory('bonmin')
    result = solver.solve(model4)

    # Model5 ------------------------------------------------------------------------------------------------------------------------------------
    model5 = pyo.ConcreteModel(name='Sustainability Non-Membership Function')

    model5.i = pyo.RangeSet(1, assets_number)

    model5.sustainability_scores_nonmembership_mean = pyo.Param(model5.i, initialize=sustainability_scores_nonmembership_mean)
    model5.sustainability_scores_expected_values = pyo.Param(model5.i, initialize=sustainability_scores_expected_values)
    model5.gamma = pyo.Param(initialize=gamma)
    model5.selected_assets_lower_bound = pyo.Param(initialize=selected_assets[0])
    model5.selected_assets_upper_bound = pyo.Param(initialize=selected_assets[1])
    model5.lower_investment_bounds = pyo.Param(model5.i, initialize=lower_investment_bounds)
    model5.upper_investment_bounds = pyo.Param(model5.i, initialize=upper_investment_bounds)

    model5.x = pyo.Var(model5.i, domain=pyo.NonNegativeReals, bounds=(0, 1))
    model5.y = pyo.Var(model5.i, domain=pyo.Binary)

    def sustainability_nonmembership_function(model5):
        return sum(model5.x[i] * model5.sustainability_scores_nonmembership_mean[i] for i in model5.i)
    model5.Obj = pyo.Objective(rule=sustainability_nonmembership_function, sense=pyo.minimize)

    model5.CapitalBudgetConstraint = pyo.Constraint(rule=lambda model5: sum(model5.x[i] for i in model5.i) == 1)
    model5.CardinalityConstraintLowerBound = pyo.Constraint(rule=lambda model5: model5.selected_assets_lower_bound <= sum(model5.y[i] for i in model5.i))
    model5.CardinalityConstraintUpperBound = pyo.Constraint(rule=lambda model5: sum(model5.y[i] for i in model5.i) <= model5.selected_assets_upper_bound)
    model5.InvestmentBoundsConstraintLowerBound = pyo.Constraint(model5.i, rule=lambda model5, i: (model5.lower_investment_bounds[i] - model5.sustainability_scores_expected_values[i] * (1 - model5.gamma)) * model5.y[i] <= model5.x[i])
    model5.InvestmentBoundsConstraintUpperBound = pyo.Constraint(model5.i, rule=lambda model5, i: (model5.upper_investment_bounds[i] + model5.sustainability_scores_expected_values[i] * (1 - model5.gamma)) * model5.y[i] >= model5.x[i])
    model5.NoShortSelling = pyo.Constraint(model5.i, rule=lambda model5, i: model5.x[i] >= 0)

    solver = pyo.SolverFactory('bonmin')
    result = solver.solve(model5)

    # Model6 ------------------------------------------------------------------------------------------------------------------------------------
    model6 = pyo.ConcreteModel(name='Returns Mean Non-Membership Function')

    model6.i = pyo.RangeSet(1, assets_number)

    model6.returns_nonmembership_mean = pyo.Param(model6.i, initialize=returns_nonmembership_mean)
    model6.sustainability_scores_expected_values = pyo.Param(model6.i, initialize=sustainability_scores_expected_values)
    model6.gamma = pyo.Param(initialize=gamma)
    model6.selected_assets_lower_bound = pyo.Param(initialize=selected_assets[0])
    model6.selected_assets_upper_bound = pyo.Param(initialize=selected_assets[1])
    model6.lower_investment_bounds = pyo.Param(model6.i, initialize=lower_investment_bounds)
    model6.upper_investment_bounds = pyo.Param(model6.i, initialize=upper_investment_bounds)

    model6.x = pyo.Var(model6.i, domain=pyo.NonNegativeReals, bounds=(0, 1))
    model6.y = pyo.Var(model6.i, domain=pyo.Binary)

    def returns_mean_nonmembership_function(model6):
        return sum(model6.x[i] * model6.returns_nonmembership_mean[i] for i in model6.i)
    model6.Obj = pyo.Objective(rule=returns_mean_nonmembership_function, sense=pyo.minimize)

    model6.CapitalBudgetConstraint = pyo.Constraint(rule=lambda model6: sum(model6.x[i] for i in model6.i) == 1)
    model6.CardinalityConstraintLowerBound = pyo.Constraint(rule=lambda model6: model6.selected_assets_lower_bound <= sum(model6.y[i] for i in model6.i))
    model6.CardinalityConstraintUpperBound = pyo.Constraint(rule=lambda model6: sum(model6.y[i] for i in model6.i) <= model6.selected_assets_upper_bound)
    model6.InvestmentBoundsConstraintLowerBound = pyo.Constraint(model6.i, rule=lambda model6, i: (model6.lower_investment_bounds[i] - model6.sustainability_scores_expected_values[i] * (1 - model6.gamma)) * model6.y[i] <= model6.x[i])
    model6.InvestmentBoundsConstraintUpperBound = pyo.Constraint(model6.i, rule=lambda model6, i: (model6.upper_investment_bounds[i] + model6.sustainability_scores_expected_values[i] * (1 - model6.gamma)) * model6.y[i] >= model6.x[i])
    model6.NoShortSelling = pyo.Constraint(model6.i, rule=lambda model6, i: model6.x[i] >= 0)

    solver = pyo.SolverFactory('bonmin')
    result = solver.solve(model6)

    # Model7 ------------------------------------------------------------------------------------------------------------------------------------
    model7 = pyo.ConcreteModel(name='Returns Variance Non-Membership Function')

    model7.i = pyo.RangeSet(1, assets_number)
    model7.j = pyo.RangeSet(1, assets_number)

    model7.returns_nonmembership_variance = pyo.Param(model7.i, model7.j, initialize=returns_nonmembership_variance)
    model7.sustainability_scores_expected_values = pyo.Param(model7.i, initialize=sustainability_scores_expected_values)
    model7.gamma = pyo.Param(initialize=gamma)
    model7.selected_assets_lower_bound = pyo.Param(initialize=selected_assets[0])
    model7.selected_assets_upper_bound = pyo.Param(initialize=selected_assets[1])
    model7.lower_investment_bounds = pyo.Param(model7.i, initialize=lower_investment_bounds)
    model7.upper_investment_bounds = pyo.Param(model7.i, initialize=upper_investment_bounds)

    model7.x = pyo.Var(model7.i, domain=pyo.NonNegativeReals, bounds=(0, 1))
    model7.y = pyo.Var(model7.i, domain=pyo.Binary)

    def returns_variance_nonmembership_function(model7):
        return sum(model7.x[i] * model7.x[j] * model7.returns_nonmembership_variance[(i, j)] for i in model7.i for j in model7.j)
    model7.Obj = pyo.Objective(rule=returns_variance_nonmembership_function, sense=pyo.minimize)

    model7.CapitalBudgetConstraint = pyo.Constraint(rule=lambda model7: sum(model7.x[i] for i in model7.i) == 1)
    model7.CardinalityConstraintLowerBound = pyo.Constraint(rule=lambda model7: model7.selected_assets_lower_bound <= sum(model7.y[i] for i in model7.i))
    model7.CardinalityConstraintUpperBound = pyo.Constraint(rule=lambda model7: sum(model7.y[i] for i in model7.i) <= model7.selected_assets_upper_bound)
    model7.InvestmentBoundsConstraintLowerBound = pyo.Constraint(model7.i, rule=lambda model7, i: (model7.lower_investment_bounds[i] - model7.sustainability_scores_expected_values[i] * (1 - model7.gamma)) * model7.y[i] <= model7.x[i])
    model7.InvestmentBoundsConstraintUpperBound = pyo.Constraint(model7.i, rule=lambda model7, i: (model7.upper_investment_bounds[i] + model7.sustainability_scores_expected_values[i] * (1 - model7.gamma)) * model7.y[i] >= model7.x[i])
    model7.NoShortSelling = pyo.Constraint(model7.i, rule=lambda model7, i: model7.x[i] >= 0)

    solver = pyo.SolverFactory('bonmin')
    result = solver.solve(model7)

    # Model8 ------------------------------------------------------------------------------------------------------------------------------------
    model8 = pyo.ConcreteModel(name='Returns Entropy Non-Membership Function')

    model8.i = pyo.RangeSet(1, assets_number)

    model8.returns_nonmembership_entropy = pyo.Param(model8.i, initialize=returns_nonmembership_entropy)
    model8.sustainability_scores_expected_values = pyo.Param(model8.i, initialize=sustainability_scores_expected_values)
    model8.gamma = pyo.Param(initialize=gamma)
    model8.selected_assets_lower_bound = pyo.Param(initialize=selected_assets[0])
    model8.selected_assets_upper_bound = pyo.Param(initialize=selected_assets[1])
    model8.lower_investment_bounds = pyo.Param(model8.i, initialize=lower_investment_bounds)
    model8.upper_investment_bounds = pyo.Param(model8.i, initialize=upper_investment_bounds)

    model8.x = pyo.Var(model8.i, domain=pyo.NonNegativeReals, bounds=(0, 1))
    model8.y = pyo.Var(model8.i, domain=pyo.Binary)

    def returns_entropy_nonmembership_function(model8):
        return sum(model8.x[i] * model8.returns_nonmembership_entropy[i] for i in model8.i)
    model8.Obj = pyo.Objective(rule=returns_entropy_nonmembership_function, sense=pyo.minimize)

    model8.CapitalBudgetConstraint = pyo.Constraint(rule=lambda model8: sum(model8.x[i] for i in model8.i) == 1)
    model8.CardinalityConstraintLowerBound = pyo.Constraint(rule=lambda model8: model8.selected_assets_lower_bound <= sum(model8.y[i] for i in model8.i))
    model8.CardinalityConstraintUpperBound = pyo.Constraint(rule=lambda model8: sum(model8.y[i] for i in model8.i) <= model8.selected_assets_upper_bound)
    model8.InvestmentBoundsConstraintLowerBound = pyo.Constraint(model8.i, rule=lambda model8, i: (model8.lower_investment_bounds[i] - model8.sustainability_scores_expected_values[i] * (1 - model8.gamma)) * model8.y[i] <= model8.x[i])
    model8.InvestmentBoundsConstraintUpperBound = pyo.Constraint(model8.i, rule=lambda model8, i: (model8.upper_investment_bounds[i] + model8.sustainability_scores_expected_values[i] * (1 - model8.gamma)) * model8.y[i] >= model8.x[i])
    model8.NoShortSelling = pyo.Constraint(model8.i, rule=lambda model8, i: model8.x[i] >= 0)

    solver = pyo.SolverFactory('bonmin')
    result = solver.solve(model8)

    # Results -----------------------------------------------------------------------------------------------------------------------------------
    # Extract results of models
    # Define your models
    models = [model1, model2, model3, model4, model5, model6, model7, model8]
    model_names = [model1.name, model2.name, model3.name, model4.name, model5.name, model6.name, model7.name, model8.name]

    # Initialize dictionaries
    objective_values = {}
    investment_proportions = {}

    # Loop through each model and extract objective values and investment proportions
    for idx, model in enumerate(models, start=1):
        objective_values[idx] = pyo.value(model.Obj)
        investment_proportions[idx] = {i: round(pyo.value(model.x[i]), 6) for i in model.i}

    # Create a DataFrame with the objective values and model names
    df_data = {
        'Objective Functions': model_names,
        'Minimum Value': [objective_values[i] for i in range(1, len(models) + 1)]
    }

    df = pd.DataFrame(df_data)

    # Add investment proportions to the DataFrame
    for i in range(1, assets_number + 1):
        df[f'X{i}'] = [investment_proportions[idx].get(i, 0) for idx in range(1, len(models) + 1)]

    # Set the logging level to ERROR to suppress WARNING messages --------------------------------------------------------------------------------
    logging.getLogger('pyomo.core').setLevel(logging.ERROR)

    return df

# --------------------------------------------------------------------------------------------------

def max_operator(sustainability_scores_data, returns_data, selected_assets, gamma):
    '''
    Optimize a series of investment dimensions objective functions and extract results.

    This function sets up and solves multiple investment optimization models using Pyomo.
    Each model targets a different objective related to investment optimization, including sustainability, returns mean, variance, and entropy.
    It solves the models using appropriate solvers and returns a DataFrame summarizing the results.

    Parameters:
    - models (list of pyomo.ConcreteModel): List of Pyomo optimization models to be solved. Each model should be defined with specific parameters and constraints.
    - model_names (list of str): Names of the models. This list should correspond to the order of the models in the `models` list.
    - sustainability_scores_expected_values (dict): Dictionary of expected values for sustainability scores, with keys as asset indices.
    - gamma (float): Parameter used in investment constraints related to sustainability scores.
    - selected_assets (tuple): Tuple containing the lower and upper bounds for the number of selected assets.
    - lower_investment_bounds (dict): Dictionary of lower bounds for investment proportions, with keys as asset indices.
    - upper_investment_bounds (dict): Dictionary of upper bounds for investment proportions, with keys as asset indices.
    - sustainability_scores_membership_mean (dict): Dictionary of mean membership scores for sustainability, with keys as asset indices.
    - sustainability_scores_nonmembership_mean (dict): Dictionary of mean non-membership scores for sustainability, with keys as asset indices.
    - returns_membership_mean (dict): Dictionary of mean membership scores for returns, with keys as asset indices.
    - returns_nonmembership_mean (dict): Dictionary of mean non-membership scores for returns, with keys as asset indices.
    - returns_membership_variance (dict of dict): Dictionary of variance membership scores for returns, with keys as tuples of asset indices (i, j).
    - returns_nonmembership_variance (dict of dict): Dictionary of variance non-membership scores for returns, with keys as tuples of asset indices (i, j).
    - returns_membership_entropy (dict): Dictionary of entropy membership scores for returns, with keys as asset indices.
    - returns_nonmembership_entropy (dict): Dictionary of entropy non-membership scores for returns, with keys as asset indices.

    Returns:
    - pd.DataFrame: DataFrame summarizing the results of the optimization models. The DataFrame includes:
        - 'Objective Functions': Names of the models.
        - 'Maximum Value': Maximum values of the objective functions for each model.
        - 'x1', 'x2', ..., 'xn': Investment proportions for each asset across models, where n is the total number of assets.
    '''
    # Define asset numbers as indexes of sets ---------------------------------------------------------------------------------------------------
    assets_number = sustainability_scores_data.shape[0]

    # Define parameters of objective functions --------------------------------------------------------------------------------------------------
    # Sustainability functions
    sustainability_scores_membership_mean = {
        i + 1: sust_eval.sustainability_scores_mean(sustainability_scores_data).iloc[i, 1]
        for i in range(assets_number)
    }

    sustainability_scores_nonmembership_mean = {
        i + 1: sust_eval.sustainability_scores_mean(sustainability_scores_data).iloc[i, 2]
        for i in range(assets_number)
    }

    # Returns' mean functions
    returns_membership_mean = {
        i + 1: ret_eval.returns_mean(returns_data).iloc[i, 1]
        for i in range(assets_number)
    }

    returns_nonmembership_mean = {
        i + 1: ret_eval.returns_mean(returns_data).iloc[i, 2]
        for i in range(assets_number)
    }

    # Returns' variance functions
    returns_membership_variance = {
        (i + 1, j + 1): ret_eval.returns_covariance(returns_data)[0].iloc[i, j]
        for i in range(assets_number)
        for j in range(assets_number)
    }

    returns_nonmembership_variance = {
        (i + 1, j + 1): ret_eval.returns_covariance(returns_data)[1].iloc[i, j]
        for i in range(assets_number)
        for j in range(assets_number)
    }

    # Returns' entropy functions
    returns_membership_entropy = {
        i + 1: ret_eval.returns_entropy(returns_data).iloc[i, 1]
        for i in range(assets_number)
    }

    returns_nonmembership_entropy = {
        i + 1: ret_eval.returns_entropy(returns_data).iloc[i, 2]
        for i in range(assets_number)
    }

    # Define parameters of constraints ----------------------------------------------------------------------------------------------------------
    sustainability_scores_expected_values = {}
    for i in range(assets_number):
        sustainability_scores_expected_values[i+1] = prelim.expected_value(sustainability_scores_data.iloc[i, 0])

    lower_investment_bounds = {}
    for i in range(assets_number):
        lower_investment_bounds[i+1] = returns_data.iloc[i, 1]

    upper_investment_bounds = {}
    for i in range(assets_number):
        upper_investment_bounds[i+1] = returns_data.iloc[i, 2]

    # Model1 ------------------------------------------------------------------------------------------------------------------------------------
    model1 = pyo.ConcreteModel(name='Sustainability Membership Function')

    model1.i = pyo.RangeSet(1, assets_number)

    model1.sustainability_scores_membership_mean = pyo.Param(model1.i, initialize=sustainability_scores_membership_mean)
    model1.sustainability_scores_expected_values = pyo.Param(model1.i, initialize=sustainability_scores_expected_values)
    model1.gamma = pyo.Param(initialize=gamma)
    model1.selected_assets_lower_bound = pyo.Param(initialize=selected_assets[0])
    model1.selected_assets_upper_bound = pyo.Param(initialize=selected_assets[1])
    model1.lower_investment_bounds = pyo.Param(model1.i, initialize=lower_investment_bounds)
    model1.upper_investment_bounds = pyo.Param(model1.i, initialize=upper_investment_bounds)

    model1.x = pyo.Var(model1.i, domain=pyo.NonNegativeReals, bounds=(0, 1))
    model1.y = pyo.Var(model1.i, domain=pyo.Binary)

    def sustainability_membership_function(model1):
        return sum(model1.x[i] * model1.sustainability_scores_membership_mean[i] for i in model1.i)
    model1.Obj = pyo.Objective(rule=sustainability_membership_function, sense=pyo.maximize)

    model1.CapitalBudgetConstraint = pyo.Constraint(rule=lambda model1: sum(model1.x[i] for i in model1.i) == 1)
    model1.CardinalityConstraintLowerBound = pyo.Constraint(rule=lambda model1: model1.selected_assets_lower_bound <= sum(model1.y[i] for i in model1.i))
    model1.CardinalityConstraintUpperBound = pyo.Constraint(rule=lambda model1: sum(model1.y[i] for i in model1.i) <= model1.selected_assets_upper_bound)
    model1.InvestmentBoundsConstraintLowerBound = pyo.Constraint(model1.i, rule=lambda model1, i: (model1.lower_investment_bounds[i] - model1.sustainability_scores_expected_values[i] * (1 - model1.gamma)) * model1.y[i] <= model1.x[i])
    model1.InvestmentBoundsConstraintUpperBound = pyo.Constraint(model1.i, rule=lambda model1, i: (model1.upper_investment_bounds[i] + model1.sustainability_scores_expected_values[i] * (1 - model1.gamma)) * model1.y[i] >= model1.x[i])
    model1.NoShortSelling = pyo.Constraint(model1.i, rule=lambda model1, i: model1.x[i] >= 0)

    solver = pyo.SolverFactory('bonmin')
    result = solver.solve(model1)

    # Model2 ------------------------------------------------------------------------------------------------------------------------------------
    model2 = pyo.ConcreteModel(name='Returns Mean Membership Function')

    model2.i = pyo.RangeSet(1, assets_number)

    model2.returns_membership_mean = pyo.Param(model2.i, initialize=returns_membership_mean)
    model2.sustainability_scores_expected_values = pyo.Param(model2.i, initialize=sustainability_scores_expected_values)
    model2.gamma = pyo.Param(initialize=gamma)
    model2.selected_assets_lower_bound = pyo.Param(initialize=selected_assets[0])
    model2.selected_assets_upper_bound = pyo.Param(initialize=selected_assets[1])
    model2.lower_investment_bounds = pyo.Param(model2.i, initialize=lower_investment_bounds)
    model2.upper_investment_bounds = pyo.Param(model2.i, initialize=upper_investment_bounds)

    model2.x = pyo.Var(model2.i, domain=pyo.NonNegativeReals, bounds=(0, 1))
    model2.y = pyo.Var(model2.i, domain=pyo.Binary)

    def returns_mean_membership_function(model2):
        return sum(model2.x[i] * model2.returns_membership_mean[i] for i in model2.i)
    model2.Obj = pyo.Objective(rule=returns_mean_membership_function, sense=pyo.maximize)

    model2.CapitalBudgetConstraint = pyo.Constraint(rule=lambda model2: sum(model2.x[i] for i in model2.i) == 1)
    model2.CardinalityConstraintLowerBound = pyo.Constraint(rule=lambda model2: model2.selected_assets_lower_bound <= sum(model2.y[i] for i in model2.i))
    model2.CardinalityConstraintUpperBound = pyo.Constraint(rule=lambda model2: sum(model2.y[i] for i in model2.i) <= model2.selected_assets_upper_bound)
    model2.InvestmentBoundsConstraintLowerBound = pyo.Constraint(model2.i, rule=lambda model2, i: (model2.lower_investment_bounds[i] - model2.sustainability_scores_expected_values[i] * (1 - model2.gamma)) * model2.y[i] <= model2.x[i])
    model2.InvestmentBoundsConstraintUpperBound = pyo.Constraint(model2.i, rule=lambda model2, i: (model2.upper_investment_bounds[i] + model2.sustainability_scores_expected_values[i] * (1 - model2.gamma)) * model2.y[i] >= model2.x[i])
    model2.NoShortSelling = pyo.Constraint(model2.i, rule=lambda model2, i: model2.x[i] >= 0)

    solver = pyo.SolverFactory('bonmin')
    result = solver.solve(model2)

    # Model3 ------------------------------------------------------------------------------------------------------------------------------------
    model3 = pyo.ConcreteModel(name='Returns Variance Membership Function')

    model3.i = pyo.RangeSet(1, assets_number)
    model3.j = pyo.RangeSet(1, assets_number)

    model3.returns_membership_variance = pyo.Param(model3.i, model3.j, initialize=returns_membership_variance)
    model3.sustainability_scores_expected_values = pyo.Param(model3.i, initialize=sustainability_scores_expected_values)
    model3.gamma = pyo.Param(initialize=gamma)
    model3.selected_assets_lower_bound = pyo.Param(initialize=selected_assets[0])
    model3.selected_assets_upper_bound = pyo.Param(initialize=selected_assets[1])
    model3.lower_investment_bounds = pyo.Param(model3.i, initialize=lower_investment_bounds)
    model3.upper_investment_bounds = pyo.Param(model3.i, initialize=upper_investment_bounds)

    model3.x = pyo.Var(model3.i, domain=pyo.NonNegativeReals, bounds=(0, 1))
    model3.y = pyo.Var(model3.i, domain=pyo.Binary)

    def returns_variance_membership_function(model3):
        return sum(model3.x[i] * model3.x[j] * model3.returns_membership_variance[(i, j)] for i in model3.i for j in model3.j)
    model3.Obj = pyo.Objective(rule=returns_variance_membership_function, sense=pyo.maximize)

    model3.CapitalBudgetConstraint = pyo.Constraint(rule=lambda model3: sum(model3.x[i] for i in model3.i) == 1)
    model3.CardinalityConstraintLowerBound = pyo.Constraint(rule=lambda model3: model3.selected_assets_lower_bound <= sum(model3.y[i] for i in model3.i))
    model3.CardinalityConstraintUpperBound = pyo.Constraint(rule=lambda model3: sum(model3.y[i] for i in model3.i) <= model3.selected_assets_upper_bound)
    model3.InvestmentBoundsConstraintLowerBound = pyo.Constraint(model3.i, rule=lambda model3, i: (model3.lower_investment_bounds[i] - model3.sustainability_scores_expected_values[i] * (1 - model3.gamma)) * model3.y[i] <= model3.x[i])
    model3.InvestmentBoundsConstraintUpperBound = pyo.Constraint(model3.i, rule=lambda model3, i: (model3.upper_investment_bounds[i] + model3.sustainability_scores_expected_values[i] * (1 - model3.gamma)) * model3.y[i] >= model3.x[i])
    model3.NoShortSelling = pyo.Constraint(model3.i, rule=lambda model3, i: model3.x[i] >= 0)

    solver = pyo.SolverFactory('bonmin')
    result = solver.solve(model3)

    # Model4 ------------------------------------------------------------------------------------------------------------------------------------
    model4 = pyo.ConcreteModel(name='Returns Entropy Membership Function')

    model4.i = pyo.RangeSet(1, assets_number)

    model4.returns_membership_entropy = pyo.Param(model4.i, initialize=returns_membership_entropy)
    model4.sustainability_scores_expected_values = pyo.Param(model4.i, initialize=sustainability_scores_expected_values)
    model4.gamma = pyo.Param(initialize=gamma)
    model4.selected_assets_lower_bound = pyo.Param(initialize=selected_assets[0])
    model4.selected_assets_upper_bound = pyo.Param(initialize=selected_assets[1])
    model4.lower_investment_bounds = pyo.Param(model4.i, initialize=lower_investment_bounds)
    model4.upper_investment_bounds = pyo.Param(model4.i, initialize=upper_investment_bounds)

    model4.x = pyo.Var(model4.i, domain=pyo.NonNegativeReals, bounds=(0, 1))
    model4.y = pyo.Var(model4.i, domain=pyo.Binary)

    def returns_entropy_membership_function(model4):
        return sum(model4.x[i] * model4.returns_membership_entropy[i] for i in model4.i)
    model4.Obj = pyo.Objective(rule=returns_entropy_membership_function, sense=pyo.maximize)

    model4.CapitalBudgetConstraint = pyo.Constraint(rule=lambda model4: sum(model4.x[i] for i in model4.i) == 1)
    model4.CardinalityConstraintLowerBound = pyo.Constraint(rule=lambda model4: model4.selected_assets_lower_bound <= sum(model4.y[i] for i in model4.i))
    model4.CardinalityConstraintUpperBound = pyo.Constraint(rule=lambda model4: sum(model4.y[i] for i in model4.i) <= model4.selected_assets_upper_bound)
    model4.InvestmentBoundsConstraintLowerBound = pyo.Constraint(model4.i, rule=lambda model4, i: (model4.lower_investment_bounds[i] - model4.sustainability_scores_expected_values[i] * (1 - model4.gamma)) * model4.y[i] <= model4.x[i])
    model4.NoShortSelling = pyo.Constraint(model4.i, rule=lambda model4, i: model4.x[i] >= 0)

    solver = pyo.SolverFactory('bonmin')
    result = solver.solve(model4)

    # Model5 ------------------------------------------------------------------------------------------------------------------------------------
    model5 = pyo.ConcreteModel(name='Sustainability Non-Membership Function')

    model5.i = pyo.RangeSet(1, assets_number)

    model5.sustainability_scores_nonmembership_mean = pyo.Param(model5.i, initialize=sustainability_scores_nonmembership_mean)
    model5.sustainability_scores_expected_values = pyo.Param(model5.i, initialize=sustainability_scores_expected_values)
    model5.gamma = pyo.Param(initialize=gamma)
    model5.selected_assets_lower_bound = pyo.Param(initialize=selected_assets[0])
    model5.selected_assets_upper_bound = pyo.Param(initialize=selected_assets[1])
    model5.lower_investment_bounds = pyo.Param(model5.i, initialize=lower_investment_bounds)
    model5.upper_investment_bounds = pyo.Param(model5.i, initialize=upper_investment_bounds)

    model5.x = pyo.Var(model5.i, domain=pyo.NonNegativeReals, bounds=(0, 1))
    model5.y = pyo.Var(model5.i, domain=pyo.Binary)

    def sustainability_nonmembership_function(model5):
        return sum(model5.x[i] * model5.sustainability_scores_nonmembership_mean[i] for i in model5.i)
    model5.Obj = pyo.Objective(rule=sustainability_nonmembership_function, sense=pyo.maximize)

    model5.CapitalBudgetConstraint = pyo.Constraint(rule=lambda model5: sum(model5.x[i] for i in model5.i) == 1)
    model5.CardinalityConstraintLowerBound = pyo.Constraint(rule=lambda model5: model5.selected_assets_lower_bound <= sum(model5.y[i] for i in model5.i))
    model5.CardinalityConstraintUpperBound = pyo.Constraint(rule=lambda model5: sum(model5.y[i] for i in model5.i) <= model5.selected_assets_upper_bound)
    model5.InvestmentBoundsConstraintLowerBound = pyo.Constraint(model5.i, rule=lambda model5, i: (model5.lower_investment_bounds[i] - model5.sustainability_scores_expected_values[i] * (1 - model5.gamma)) * model5.y[i] <= model5.x[i])
    model5.InvestmentBoundsConstraintUpperBound = pyo.Constraint(model5.i, rule=lambda model5, i: (model5.upper_investment_bounds[i] + model5.sustainability_scores_expected_values[i] * (1 - model5.gamma)) * model5.y[i] >= model5.x[i])
    model5.NoShortSelling = pyo.Constraint(model5.i, rule=lambda model5, i: model5.x[i] >= 0)

    solver = pyo.SolverFactory('bonmin')
    result = solver.solve(model5)

    # Model6 ------------------------------------------------------------------------------------------------------------------------------------
    model6 = pyo.ConcreteModel(name='Returns Mean Non-Membership Function')

    model6.i = pyo.RangeSet(1, assets_number)

    model6.returns_nonmembership_mean = pyo.Param(model6.i, initialize=returns_nonmembership_mean)
    model6.sustainability_scores_expected_values = pyo.Param(model6.i, initialize=sustainability_scores_expected_values)
    model6.gamma = pyo.Param(initialize=gamma)
    model6.selected_assets_lower_bound = pyo.Param(initialize=selected_assets[0])
    model6.selected_assets_upper_bound = pyo.Param(initialize=selected_assets[1])
    model6.lower_investment_bounds = pyo.Param(model6.i, initialize=lower_investment_bounds)
    model6.upper_investment_bounds = pyo.Param(model6.i, initialize=upper_investment_bounds)

    model6.x = pyo.Var(model6.i, domain=pyo.NonNegativeReals, bounds=(0, 1))
    model6.y = pyo.Var(model6.i, domain=pyo.Binary)

    def returns_mean_nonmembership_function(model6):
        return sum(model6.x[i] * model6.returns_nonmembership_mean[i] for i in model6.i)
    model6.Obj = pyo.Objective(rule=returns_mean_nonmembership_function, sense=pyo.maximize)

    model6.CapitalBudgetConstraint = pyo.Constraint(rule=lambda model6: sum(model6.x[i] for i in model6.i) == 1)
    model6.CardinalityConstraintLowerBound = pyo.Constraint(rule=lambda model6: model6.selected_assets_lower_bound <= sum(model6.y[i] for i in model6.i))
    model6.CardinalityConstraintUpperBound = pyo.Constraint(rule=lambda model6: sum(model6.y[i] for i in model6.i) <= model6.selected_assets_upper_bound)
    model6.InvestmentBoundsConstraintLowerBound = pyo.Constraint(model6.i, rule=lambda model6, i: (model6.lower_investment_bounds[i] - model6.sustainability_scores_expected_values[i] * (1 - model6.gamma)) * model6.y[i] <= model6.x[i])
    model6.InvestmentBoundsConstraintUpperBound = pyo.Constraint(model6.i, rule=lambda model6, i: (model6.upper_investment_bounds[i] + model6.sustainability_scores_expected_values[i] * (1 - model6.gamma)) * model6.y[i] >= model6.x[i])
    model6.NoShortSelling = pyo.Constraint(model6.i, rule=lambda model6, i: model6.x[i] >= 0)

    solver = pyo.SolverFactory('bonmin')
    result = solver.solve(model6)

    # Model7 ------------------------------------------------------------------------------------------------------------------------------------
    model7 = pyo.ConcreteModel(name='Returns Variance Non-Membership Function')

    model7.i = pyo.RangeSet(1, assets_number)
    model7.j = pyo.RangeSet(1, assets_number)

    model7.returns_nonmembership_variance = pyo.Param(model7.i, model7.j, initialize=returns_nonmembership_variance)
    model7.sustainability_scores_expected_values = pyo.Param(model7.i, initialize=sustainability_scores_expected_values)
    model7.gamma = pyo.Param(initialize=gamma)
    model7.selected_assets_lower_bound = pyo.Param(initialize=selected_assets[0])
    model7.selected_assets_upper_bound = pyo.Param(initialize=selected_assets[1])
    model7.lower_investment_bounds = pyo.Param(model7.i, initialize=lower_investment_bounds)
    model7.upper_investment_bounds = pyo.Param(model7.i, initialize=upper_investment_bounds)

    model7.x = pyo.Var(model7.i, domain=pyo.NonNegativeReals, bounds=(0, 1))
    model7.y = pyo.Var(model7.i, domain=pyo.Binary)

    def returns_variance_nonmembership_function(model7):
        return sum(model7.x[i] * model7.x[j] * model7.returns_nonmembership_variance[(i, j)] for i in model7.i for j in model7.j)
    model7.Obj = pyo.Objective(rule=returns_variance_nonmembership_function, sense=pyo.maximize)

    model7.CapitalBudgetConstraint = pyo.Constraint(rule=lambda model7: sum(model7.x[i] for i in model7.i) == 1)
    model7.CardinalityConstraintLowerBound = pyo.Constraint(rule=lambda model7: model7.selected_assets_lower_bound <= sum(model7.y[i] for i in model7.i))
    model7.CardinalityConstraintUpperBound = pyo.Constraint(rule=lambda model7: sum(model7.y[i] for i in model7.i) <= model7.selected_assets_upper_bound)
    model7.InvestmentBoundsConstraintLowerBound = pyo.Constraint(model7.i, rule=lambda model7, i: (model7.lower_investment_bounds[i] - model7.sustainability_scores_expected_values[i] * (1 - model7.gamma)) * model7.y[i] <= model7.x[i])
    model7.InvestmentBoundsConstraintUpperBound = pyo.Constraint(model7.i, rule=lambda model7, i: (model7.upper_investment_bounds[i] + model7.sustainability_scores_expected_values[i] * (1 - model7.gamma)) * model7.y[i] >= model7.x[i])
    model7.NoShortSelling = pyo.Constraint(model7.i, rule=lambda model7, i: model7.x[i] >= 0)

    solver = pyo.SolverFactory('bonmin')
    result = solver.solve(model7)

    # Model8 ------------------------------------------------------------------------------------------------------------------------------------
    model8 = pyo.ConcreteModel(name='Returns Entropy Non-Membership Function')

    model8.i = pyo.RangeSet(1, assets_number)

    model8.returns_nonmembership_entropy = pyo.Param(model8.i, initialize=returns_nonmembership_entropy)
    model8.sustainability_scores_expected_values = pyo.Param(model8.i, initialize=sustainability_scores_expected_values)
    model8.gamma = pyo.Param(initialize=gamma)
    model8.selected_assets_lower_bound = pyo.Param(initialize=selected_assets[0])
    model8.selected_assets_upper_bound = pyo.Param(initialize=selected_assets[1])
    model8.lower_investment_bounds = pyo.Param(model8.i, initialize=lower_investment_bounds)
    model8.upper_investment_bounds = pyo.Param(model8.i, initialize=upper_investment_bounds)

    model8.x = pyo.Var(model8.i, domain=pyo.NonNegativeReals, bounds=(0, 1))
    model8.y = pyo.Var(model8.i, domain=pyo.Binary)

    def returns_entropy_nonmembership_function(model8):
        return sum(model8.x[i] * model8.returns_nonmembership_entropy[i] for i in model8.i)
    model8.Obj = pyo.Objective(rule=returns_entropy_nonmembership_function, sense=pyo.maximize)

    model8.CapitalBudgetConstraint = pyo.Constraint(rule=lambda model8: sum(model8.x[i] for i in model8.i) == 1)
    model8.CardinalityConstraintLowerBound = pyo.Constraint(rule=lambda model8: model8.selected_assets_lower_bound <= sum(model8.y[i] for i in model8.i))
    model8.CardinalityConstraintUpperBound = pyo.Constraint(rule=lambda model8: sum(model8.y[i] for i in model8.i) <= model8.selected_assets_upper_bound)
    model8.InvestmentBoundsConstraintLowerBound = pyo.Constraint(model8.i, rule=lambda model8, i: (model8.lower_investment_bounds[i] - model8.sustainability_scores_expected_values[i] * (1 - model8.gamma)) * model8.y[i] <= model8.x[i])
    model8.InvestmentBoundsConstraintUpperBound = pyo.Constraint(model8.i, rule=lambda model8, i: (model8.upper_investment_bounds[i] + model8.sustainability_scores_expected_values[i] * (1 - model8.gamma)) * model8.y[i] >= model8.x[i])
    model8.NoShortSelling = pyo.Constraint(model8.i, rule=lambda model8, i: model8.x[i] >= 0)

    solver = pyo.SolverFactory('bonmin')
    result = solver.solve(model8)

    # Results -----------------------------------------------------------------------------------------------------------------------------------
    # Extract results of models
    # Define your models
    models = [model1, model2, model3, model4, model5, model6, model7, model8]
    model_names = [model1.name, model2.name, model3.name, model4.name, model5.name, model6.name, model7.name, model8.name]

    # Initialize dictionaries
    objective_values = {}
    investment_proportions = {}

    # Loop through each model and extract objective values and investment proportions
    for idx, model in enumerate(models, start=1):
        objective_values[idx] = pyo.value(model.Obj)
        investment_proportions[idx] = {i: round(pyo.value(model.x[i]), 6) for i in model.i}

    # Create a DataFrame with the objective values and model names
    df_data = {
        'Objective Functions': model_names,
        'Maximum Value': [objective_values[i] for i in range(1, len(models) + 1)]
    }

    df = pd.DataFrame(df_data)

    # Add investment proportions to the DataFrame
    for i in range(1, assets_number + 1):
        df[f'X{i}'] = [investment_proportions[idx].get(i, 0) for idx in range(1, len(models) + 1)]

    # Set the logging level to ERROR to suppress WARNING messages --------------------------------------------------------------------------------
    logging.getLogger('pyomo.core').setLevel(logging.ERROR)

    return df

# --------------------------------------------------------------------------------------------------

def mean_variance_entropy_model(sustainability_scores_data, returns_data, selected_assets, gamma, min_operator_values, max_operator_values):
    '''
    Solves a sustainability-aware mean–variance–entropy portfolio optimization problem 
    using an iterative α–β maximization approach under Intuitionistic Fuzzy Set (IFS) theory.

    This model integrates three key performance dimensions—mean return, variance, and entropy—
    alongside sustainability scores, representing both membership and non-membership degrees 
    for each asset. The optimization seeks to maximize the difference between aggregated 
    membership (α) and non-membership (β) degrees, subject to capital allocation, cardinality, 
    and investment bounds constraints. 

    The model uses Pyomo to construct a mixed-integer nonlinear programming (MINLP) formulation 
    and solves it iteratively with the Bonmin solver until convergence is reached based on 
    specified tolerance thresholds.

    Returns
    -------
    pandas.DataFrame
        A single-row DataFrame containing the optimal α, β, γ values and portfolio weights (X1, X2, ...).
        The index is labeled 'Optimal Solution'.

    Notes
    -----
    - The model enforces no short-selling (non-negative weights).
    - Sustainability scores and return measures are normalized between corresponding min and max 
      operator values to ensure comparability across criteria.
    - Cardinality constraints enforce the selection of a specific range of assets.
    - Investment bounds are adjusted based on sustainability expectations and the gamma parameter.
    - The iterative α–β refinement loop stops when the change between iterations falls below the 
      specified tolerance or when the maximum number of iterations is reached.
    '''

    #ِ Define iteration parameters 
    max_iterations=100
    tolerance=1e-6
    
    # Define asset numbers as indexes of sets ---------------------------------------------------------------------------------------------------
    assets_number = len(sustainability_scores_data)

    # Define parameters of objective functions --------------------------------------------------------------------------------------------------
    # Sustainability functions
    sustainability_scores_membership_mean = {i + 1: sust_eval.sustainability_scores_mean(sustainability_scores_data).iloc[i, 1] for i in range(assets_number)}
    sustainability_scores_nonmembership_mean = {i + 1: sust_eval.sustainability_scores_mean(sustainability_scores_data).iloc[i, 2] for i in range(assets_number)}

    # Returns' mean functions
    returns_membership_mean = {i + 1: ret_eval.returns_mean(returns_data).iloc[i, 1] for i in range(assets_number)}
    returns_nonmembership_mean = {i + 1: ret_eval.returns_mean(returns_data).iloc[i, 2] for i in range(assets_number)}

    # Returns' variance functions
    returns_membership_variance = {(i + 1, j + 1): ret_eval.returns_covariance(returns_data)[0].iloc[i, j] for i in range(assets_number) for j in range(assets_number)}
    returns_nonmembership_variance = {(i + 1, j + 1): ret_eval.returns_covariance(returns_data)[1].iloc[i, j] for i in range(assets_number) for j in range(assets_number)}

    # Returns' entropy functions
    returns_membership_entropy = {i + 1: ret_eval.returns_entropy(returns_data).iloc[i, 1] for i in range(assets_number)}
    returns_nonmembership_entropy = {i + 1: ret_eval.returns_entropy(returns_data).iloc[i, 2] for i in range(assets_number)}

    # Define parameters of constraints ----------------------------------------------------------------------------------------------------------
    sustainability_scores_expected_values = {}
    for i in range(assets_number):
        sustainability_scores_expected_values[i+1] = prelim.expected_value(sustainability_scores_data.iloc[i, 0])

    lower_investment_bounds = {}
    for i in range(assets_number):
        lower_investment_bounds[i+1] = returns_data.iloc[i, 1]

    upper_investment_bounds = {}
    for i in range(assets_number):
        upper_investment_bounds[i+1] = returns_data.iloc[i, 2]

    mu_sustainability_operator_min = min_operator_values.iloc[0, 1]
    mu_sustainability_operator_max = max_operator_values.iloc[0, 1]
    mu_means_operator_min = min_operator_values.iloc[1, 1]
    mu_means_operator_max = max_operator_values.iloc[1, 1]
    mu_variance_operator_min = min_operator_values.iloc[2, 1]
    mu_variance_operator_max = max_operator_values.iloc[2, 1]
    mu_entropy_operator_min = min_operator_values.iloc[3, 1]
    mu_entropy_operator_max = max_operator_values.iloc[3, 1]
    
    nu_sustainability_operator_min = min_operator_values.iloc[4, 1]
    nu_sustainability_operator_max = max_operator_values.iloc[4, 1]
    nu_means_operator_min = min_operator_values.iloc[5, 1]
    nu_means_operator_max = max_operator_values.iloc[5, 1]
    nu_variance_operator_min = min_operator_values.iloc[6, 1]
    nu_variance_operator_max = max_operator_values.iloc[6, 1]
    nu_entropy_operator_min = min_operator_values.iloc[7, 1]
    nu_entropy_operator_max = max_operator_values.iloc[7, 1]

    # Initialize α and β
    alpha_prev = 1
    beta_prev = 0

    # Iterative loop
    for iteration in range(max_iterations):
        # Model -------------------------------------------------------------------------------------------------------------------------------------
        # Define Model
        model = pyo.ConcreteModel()

        # Define Sets
        model.i = pyo.RangeSet(1, assets_number)
        model.j = pyo.RangeSet(1, assets_number)

        # Define Parameters
        model.sustainability_scores_membership_mean = pyo.Param(model.i, initialize=sustainability_scores_membership_mean)
        model.returns_membership_mean = pyo.Param(model.i, initialize=returns_membership_mean)
        model.returns_membership_variance = pyo.Param(model.i, model.j, initialize=returns_membership_variance)
        model.returns_membership_entropy = pyo.Param(model.i, initialize=returns_membership_entropy)

        model.sustainability_scores_nonmembership_mean = pyo.Param(model.i, initialize=sustainability_scores_nonmembership_mean)
        model.returns_nonmembership_mean = pyo.Param(model.i, initialize=returns_nonmembership_mean)
        model.returns_nonmembership_variance = pyo.Param(model.i, model.j, initialize=returns_nonmembership_variance)
        model.returns_nonmembership_entropy = pyo.Param(model.i, initialize=returns_nonmembership_entropy)

        model.mu_sustainability_operator_min = pyo.Param(initialize=mu_sustainability_operator_min)
        model.mu_sustainability_operator_max = pyo.Param(initialize=mu_sustainability_operator_max)
        model.mu_means_operator_min = pyo.Param(initialize=mu_means_operator_min)
        model.mu_means_operator_max = pyo.Param(initialize=mu_means_operator_max)
        model.mu_variance_operator_min = pyo.Param(initialize=mu_variance_operator_min)
        model.mu_variance_operator_max = pyo.Param(initialize=mu_variance_operator_max)
        model.mu_entropy_operator_min = pyo.Param(initialize=mu_entropy_operator_min)
        model.mu_entropy_operator_max = pyo.Param(initialize=mu_entropy_operator_max)

        model.nu_sustainability_operator_min = pyo.Param(initialize=nu_sustainability_operator_min)
        model.nu_sustainability_operator_max = pyo.Param(initialize=nu_sustainability_operator_max)
        model.nu_means_operator_min = pyo.Param(initialize=nu_means_operator_min)
        model.nu_means_operator_max = pyo.Param(initialize=nu_means_operator_max)
        model.nu_variance_operator_min = pyo.Param(initialize=nu_variance_operator_min)
        model.nu_variance_operator_max = pyo.Param(initialize=nu_variance_operator_max)
        model.nu_entropy_operator_min = pyo.Param(initialize=nu_entropy_operator_min)
        model.nu_entropy_operator_max = pyo.Param(initialize=nu_entropy_operator_max)

        model.sustainability_scores_expected_values = pyo.Param(model.i, initialize=sustainability_scores_expected_values)
        model.gamma = pyo.Param(initialize=gamma)
        model.selected_assets_lower_bound = pyo.Param(initialize=selected_assets[0])
        model.selected_assets_upper_bound = pyo.Param(initialize=selected_assets[1])
        model.lower_investment_bounds = pyo.Param(model.i, initialize=lower_investment_bounds)
        model.upper_investment_bounds = pyo.Param(model.i, initialize=upper_investment_bounds)

        # Define Decision Variables
        model.a = pyo.Var(domain=pyo.NonNegativeReals)
        model.b = pyo.Var(domain=pyo.NonNegativeReals)
        model.x = pyo.Var(model.i, domain=pyo.NonNegativeReals, bounds=(0, 1))
        model.y = pyo.Var(model.i, domain=pyo.Binary)

        # Define Objective Function
        def intuitionistic_degrees_maximization(model):
            return (model.a - model.b)
        model.Obj = pyo.Objective(rule=intuitionistic_degrees_maximization, sense=pyo.maximize)

        # Define Membership Constraints
        model.mu_sustainability = pyo.Constraint(
            rule=lambda model: (
                ((sum(model.x[i] * model.sustainability_scores_membership_mean[i] for i in model.i)) - mu_sustainability_operator_min) / 
                                (mu_sustainability_operator_max - mu_sustainability_operator_min)) >= model.a
            )
        
        model.mu_returns_mean = pyo.Constraint(
            rule=lambda model: (
                ((sum(model.x[i] * model.returns_membership_mean[i] for i in model.i)) - mu_means_operator_min) / 
                                (mu_means_operator_max - mu_means_operator_min)) >= model.a
            )
        
        model.mu_returns_variance = pyo.Constraint(
            rule=lambda model: (
                (mu_variance_operator_max - (sum(model.x[i] * model.x[j] * model.returns_membership_variance[(i, j)] for i in model.i for j in model.j))) / 
                                (mu_variance_operator_max - mu_variance_operator_min)) >= model.a
            )

        model.mu_returns_entropy = pyo.Constraint(
            rule=lambda model: (
                (mu_entropy_operator_max - (sum(model.x[i] * model.returns_membership_entropy[i] for i in model.i))) / 
                                (mu_entropy_operator_max - mu_entropy_operator_min)) >= model.a
            )

        # Define Non-Membership Constraints
        model.nu_sustainability = pyo.Constraint(
            rule=lambda model: (
                (nu_sustainability_operator_max - (sum(model.x[i] * model.sustainability_scores_nonmembership_mean[i] for i in model.i))) / 
                                (nu_sustainability_operator_max - nu_sustainability_operator_min)) <= model.b
            )
        
        model.nu_returns_mean = pyo.Constraint(
            rule=lambda model: (
                (nu_means_operator_max - (sum(model.x[i] * model.returns_nonmembership_mean[i] for i in model.i))) / 
                                (nu_means_operator_max - nu_means_operator_min)) <= model.b
            )
        
        model.nu_returns_variance = pyo.Constraint(
            rule=lambda model: (
                ((sum(model.x[i] * model.x[j] * model.returns_nonmembership_variance[(i, j)] for i in model.i for j in model.j)) - nu_variance_operator_min) / 
                                (nu_variance_operator_max - nu_variance_operator_min)) <= model.b
            )
        
        model.nu_returns_entropy = pyo.Constraint(
            rule=lambda model: (
                ((sum(model.x[i] * model.returns_nonmembership_entropy[i] for i in model.i)) - nu_entropy_operator_min) / 
                                (nu_entropy_operator_max - nu_entropy_operator_min)) <= model.b
            )

        # Define Bounds on Membership and Non-Membership Degrees
        model.sustainability_degrees_upper_bound = pyo.Constraint(
            rule=lambda model: (
                ((sum(model.x[i] * model.sustainability_scores_membership_mean[i] for i in model.i)) - mu_sustainability_operator_min) / (mu_sustainability_operator_max - mu_sustainability_operator_min)) +
                                                                  ((nu_sustainability_operator_max - (sum(model.x[i] * model.sustainability_scores_nonmembership_mean[i] for i in model.i))) / (nu_sustainability_operator_max - nu_sustainability_operator_min)) <= 1
                                                                  )

        model.mean_degrees_upper_bound = pyo.Constraint(
            rule=lambda model: (
                ((sum(model.x[i] * model.returns_membership_mean[i] for i in model.i)) - mu_means_operator_min) / (mu_means_operator_max - mu_means_operator_min)) +
                                                        ((nu_means_operator_max - (sum(model.x[i] * model.returns_nonmembership_mean[i] for i in model.i))) / (nu_means_operator_max - nu_means_operator_min)) <= 1
                                                        )


        model.variance_degrees_upper_bound = pyo.Constraint(
            rule=lambda model: (
                (mu_variance_operator_max - (sum(model.x[i] * model.x[j] * model.returns_membership_variance[(i, j)] for i in model.i for j in model.j))) / (mu_variance_operator_max - mu_variance_operator_min)) +
                                                            (((sum(model.x[i] * model.x[j] * model.returns_nonmembership_variance[(i, j)] for i in model.i for j in model.j)) - nu_variance_operator_min) / (nu_variance_operator_max - nu_variance_operator_min)) <= 1
                                                            )

        model.entropy_degrees_upper_bound = pyo.Constraint(
            rule=lambda model: (
                (mu_entropy_operator_max - (sum(model.x[i] * model.returns_membership_entropy[i] for i in model.i))) / (mu_entropy_operator_max - mu_entropy_operator_min)) +
                                                           (((sum(model.x[i] * model.returns_nonmembership_entropy[i] for i in model.i)) - nu_entropy_operator_min) / (nu_entropy_operator_max - nu_entropy_operator_min)) <= 1
                                                           )
        
        # Define Investment Constraints
        model.CapitalBudgetConstraint = pyo.Constraint(rule=lambda model: sum(model.x[i] for i in model.i) == 1)
        model.CardinalityConstraintLowerBound = pyo.Constraint(rule=lambda model: model.selected_assets_lower_bound <= sum(model.y[i] for i in model.i))
        model.CardinalityConstraintUpperBound = pyo.Constraint(rule=lambda model: sum(model.y[i] for i in model.i) <= model.selected_assets_upper_bound)
        model.InvestmentBoundsConstraintLowerBound = pyo.Constraint(model.i, rule=lambda model, i: (model.lower_investment_bounds[i] - model.sustainability_scores_expected_values[i] * (1 - model.gamma)) * model.y[i] <= model.x[i])
        model.InvestmentBoundsConstraintUpperBound = pyo.Constraint(model.i, rule=lambda model, i: (model.upper_investment_bounds[i] + model.sustainability_scores_expected_values[i] * (1 - model.gamma)) * model.y[i] >= model.x[i])
        model.NoShortSelling = pyo.Constraint(model.i, rule=lambda model, i: model.x[i] >= 0)

        # Define Bounds on Alpha and Beta
        model.degrees_lower_bound = pyo.Constraint(rule=lambda model: (model.a + model.b) >= 0)
        model.degrees_upper_bound = pyo.Constraint(rule=lambda model: (model.a + model.b) <= 1)
        model.degrees_relation = pyo.Constraint(rule=lambda model: model.a >= model.b)

        # Add iterative constraints
        if iteration > 0:
            model.alpha_constraint = pyo.Constraint(rule=lambda model: model.a <= alpha_prev)
            model.beta_constraint = pyo.Constraint(rule=lambda model: model.b >= beta_prev)

        # Define Solver
        solver = pyo.SolverFactory('bonmin')
        result = solver.solve(model)

        # Extract the values
        a_value = pyo.value(model.a)
        b_value = pyo.value(model.b)

        # Check for convergence
        if abs(a_value - alpha_prev) < tolerance and abs(b_value - beta_prev) < tolerance:
            break

        # Update previous values
        alpha_prev = a_value
        beta_prev = b_value

    # Extract decision variable values
    x_values = {i: pyo.value(model.x[i]) for i in model.i}
    y_values = {i: pyo.value(model.y[i]) for i in model.i}

    # Create a DataFrame
    result_df = pd.DataFrame({
        'α': [a_value],
        'β': [b_value],
        'γ': [gamma],
        **{f'X{i}': [x_values[i]] for i in model.i}
    }, index=['Optimal Solution'])
   
    # Extract X variables (asset allocations)
    x_vars = x_values
    
    # Calculation functions
    def calc_sustainability():
        mu = (sum(x_vars[i] * sustainability_scores_membership_mean[i] for i in x_vars) - mu_sustainability_operator_min) / (mu_sustainability_operator_max - mu_sustainability_operator_min)
        nu = (nu_sustainability_operator_max - sum(x_vars[i] * sustainability_scores_nonmembership_mean[i] for i in x_vars)) / (nu_sustainability_operator_max - nu_sustainability_operator_min)
        return mu - nu

    def calc_returns_mean():
        mu = (sum(x_vars[i] * returns_membership_mean[i] for i in x_vars) - mu_means_operator_min) / (mu_means_operator_max - mu_means_operator_min)
        nu = (nu_means_operator_max - sum(x_vars[i] * returns_nonmembership_mean[i] for i in x_vars)) / (nu_means_operator_max - nu_means_operator_min)
        return mu - nu

    def calc_returns_variance():
        mu = (mu_variance_operator_max - sum(x_vars[i] * x_vars[j] * returns_membership_variance[(i, j)] for i in x_vars for j in x_vars)) / (mu_variance_operator_max - mu_variance_operator_min)
        nu = (sum(x_vars[i] * x_vars[j] * returns_nonmembership_variance[(i, j)] for i in x_vars for j in x_vars) - nu_variance_operator_min) / (nu_variance_operator_max - nu_variance_operator_min)
        return mu - nu

    def calc_returns_entropy():
        mu = (mu_entropy_operator_max - sum(x_vars[i] * returns_membership_entropy[i] for i in x_vars)) / (mu_entropy_operator_max - mu_entropy_operator_min)
        nu = (sum(x_vars[i] * returns_nonmembership_entropy[i] for i in x_vars) - nu_entropy_operator_min) / (nu_entropy_operator_max - nu_entropy_operator_min)
        return mu - nu

    # Select model type and calculate results
    optimal_solution_df = pd.DataFrame({
        'Sustainability': [calc_sustainability()],
        'Mean': [calc_returns_mean()],
        'Variance': [calc_returns_variance()],
        'Entropy': [calc_returns_entropy()]
        }, index=['Optimal Solution'])

    # Append results to the original DataFrame
    updated_df = pd.concat([optimal_solution_df, result_df], axis=1)

    return updated_df

# ------------------------------

def main():
    print("POROPTO CLI is alive!")