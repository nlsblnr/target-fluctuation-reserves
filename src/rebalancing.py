'''
Assume no short positions in  the portfolio

Remark: when an asset leaves its allocation corridor and corridor rebalancing is enabled,
all assets are rebalanced to the target allocation and NOT the nearest corridor boundary
'''

import numpy as np
from scipy.optimize import minimize

def objective(gross_trade_vector, target_difference, transaction_costs):
    '''
    Objective function: (gross_trades - difference between actual and target values)^2 + transaction_costs*abs(gross_trades)
    => this function will be minimized
    
    gross_trade_vector: vector of changes in asset values before transaction costs
    target_difference: target_value - actual_value
    transaction_costs: percentage of trading volume representing transaction costs
    '''
    
    deviation = np.sum((gross_trade_vector - target_difference)**2)
    costs = transaction_costs * np.sum(np.abs(gross_trade_vector))
    return deviation + costs

def optimized_target_portfolio(portfolio, target_allocation, transaction_costs):
    '''
    portfolio: list of Asset instances
    target_allocation: list of target weights
    transaction_costs: proportional transaction costs factor
    
    returns list of optimal portfolio values
    '''
    
    actual_values = np.array([asset.value for asset in portfolio], dtype=float)
    target_allocation = np.array(target_allocation, dtype=float)
    n = len(actual_values)
    
    portfolio_value_now = actual_values.sum()
    target_values = target_allocation * portfolio_value_now
    target_difference = target_values - actual_values
    
    # if transaction_costs == 0.0: return the trivial solution
    
    
    # no short positions: only sell what we actually own
    lower_bounds = -actual_values
    upper_bounds = np.full(n, np.inf)
    bounds = [(lower, upper) for lower, upper in zip(lower_bounds, upper_bounds)]
    
    # initial solution to start minimization
    initial_solution = target_difference
    
    # define constraints
    cons = ({
		"type": "eq",
		"fun": lambda x: np.sum(x)
	})
    
    result = minimize(
		fun=objective,
		x0=initial_solution,
		args=(target_difference, transaction_costs),
		method="SLSQP",
		constraints=cons,
		bounds=bounds,
		options={
			"maxiter": 1000,
			"ftol": 1e-06
		}
	)
    
    if not result.success:
        raise RuntimeError(f"Optimization failed: {result.message}")
    
    optimal_gross_trades = result.x
    
    # calculate new asset values after transaction costs
    updated_values = actual_values + optimal_gross_trades - transaction_costs * np.abs(optimal_gross_trades)
    
    return updated_values

'''
 takes list of current assets and list of target allocation weights (e.g. [0.2, 0.45, 0.35])
 returns list of new values for each of the given assets (e.g. [2E07, 3E07, 9E06])
 THIS FUNCTION IS ONLY CALLED WHEN THE PORTFOLIO ACTUALLY HAS TO BE REBALANCED
 '''
def calendar_rebalancing(portfolio_now, target_allocation, transaction_costs=0.0):
    return optimized_target_portfolio(portfolio=portfolio_now, target_allocation=target_allocation, transaction_costs=transaction_costs)

'''
 takes list of current assets and list of corridors (min, target and max weights) (e.g. [[0.15, 0.2, 0.25], [0.4, 0.45, 0.5], [0.32, 0.35, 0.38]])
 returns list of new values for each of the given assets (e.g. [2E07, 3E07, 9E06])
 THIS FUNCTION IS CALLED EVERY TIME STEP, IT CHECKS ITSELF IF REBALANCING IS NEEDED
'''
def corridor_rebalancing(portfolio_now, target_allocation, min_weights, max_weights, transaction_costs=0.0):
    portfolio_value_now = sum([asset.value for asset in portfolio_now])
            
    for i, asset in enumerate(portfolio_now):
        min_weight = min_weights[i]
        max_weight = max_weights[i]
        
        # if corridor boundary is crossed => rebalance the entire portfolio to the target weights
        if asset.value/portfolio_value_now < min_weight or asset.value/portfolio_value_now > max_weight:
            return optimized_target_portfolio(portfolio=portfolio_now, target_allocation=target_allocation, transaction_costs=transaction_costs)
            
    # if no corridor boundaries are crossed => return the current portfolio
    return [asset.value for asset in portfolio_now]