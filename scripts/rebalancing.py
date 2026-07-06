'''
Assume zero transaction costs when rebalancing portfolio
Assume that the portfolio is always rebalanced when the function is called => no additional checks whether any threshold/limit is reached

takes list of current assets and list of target allocation weights (e.g. [0.2, 0.45, 0.35])
returns list of new values for each of the given assets (e.g. [2E07, 3E07, 9E06])
'''
def rebalance_portfolio(portfolio_now, target_allocation):
    portfolio_value_now = sum([asset.value for asset in portfolio_now])    
    target_portfolio = [portfolio_value_now * target_weight for target_weight in target_allocation]
    
    return target_portfolio