'''
Assume zero transaction costs when rebalancing portfolio
'''
# takes list of current assets and list of target allocation weights (e.g. [0.2, 0.45, 0.35])
# returns list of new values for each of the given assets (e.g. [2E07, 3E07, 9E06])
# THIS FUNCTION IS ONLY CALLED WHEN THE PORTFOLIO ACTUALLY HAS TO BE REBALANCED
def calendar_rebalancing(portfolio_now, target_allocation):
    portfolio_value_now = sum([asset.value for asset in portfolio_now])    
    target_portfolio = [portfolio_value_now * target_weight for target_weight in target_allocation]
    return target_portfolio

# takes list of current assets and list of corridors (min, target and max weights) (e.g. [[0.15, 0.2, 0.25], [0.4, 0.45, 0.5], [0.32, 0.35, 0.38]])
# returns list of new values for each of the given assets (e.g. [2E07, 3E07, 9E06])
# THIS FUNCTION IS CALLED EVERY TIME STEP, IT CHECKS ITSELF IF REBALANCING IS NEEDED
def corridor_rebalancing(portfolio_now, target_allocation, min_weights, max_weights):
    portfolio_value_now = sum([asset.value for asset in portfolio_now])    
    
    for i, asset in enumerate(portfolio_now):
        min_weight = min_weights[i]
        max_weight = max_weights[i]
        
        # if corridor boundary is crossed => rebalance the entire portfolio to the target weights
        if asset.value < min_weight or asset.value > max_weight:
            target_portfolio = [portfolio_value_now * target_weight for target_weight in target_allocation]
            return target_portfolio
            
    # if no corridor boundaries are crossed => return the current portfolio
    return portfolio_now