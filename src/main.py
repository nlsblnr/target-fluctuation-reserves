'''
The target fluctuation reserves are typically calculated as 2/3*(assets/liabilities - 1) such that this value is only negative in the worst 2.2 % of possible outcomes after five years of observation (less than two standard deviations below zero).
This is a common rule of thumb to ensure that there are sufficient reserves to cover potential fluctuations in asset values relative to liabilities
'''

import numpy as np
import matplotlib.pyplot as plt
import liabilities as lia
import assets as ast

SIM_RUNS = 1_000
DELTA_T = 1/200
OBSERVED_TIME = 5
TIME_STEPS = round(OBSERVED_TIME/DELTA_T)

# define initial assets and portfolio
stocks = ast.Asset(0.07, 0.2, 7E07, DELTA_T)
bonds = ast.Asset(0.03, 0.03, 3E07, DELTA_T)
real_estate = ast.Asset(0.04, 0.014, 5E07, DELTA_T)
miscellaneous = ast.Asset(0.03, 0.05, 5E07, DELTA_T)
pf = [stocks, bonds, real_estate, miscellaneous]
corr_matrix = [
    [1.0, 0.4, -0.2, 0.1],
    [0.4, 1.0, 0.3, 0.7],
    [-0.2, 0.3, 1.0, -0.1],
    [0.1, 0.7, -0.1, 1.0]
]

# define target allocation and corridor needed for rebalancing
target_allocation = [7/20, 3/20, 5/20, 5/20] # tells rebalancing function how to rebalance the portfolio
min_weights = [0.95 * w_t for w_t in target_allocation] # min weights are 5 % below target weights
max_weights = [1.05 * w_t for w_t in target_allocation] # max weights are 5 % above target weights

# two list that again include lists representing asset and liability paths
portfolio_vals_total = []
liability_vals_total = []

# simulate specified number of asset and liability paths
for n in range(SIM_RUNS):
    asset_path_n = ast.simulate_assets(delta_t=DELTA_T, observed_time=OBSERVED_TIME, portfolio=pf, correlation_matrix=corr_matrix, rebalancing_activated=True, rebalancing_style="calendar", rebalancing_period=1/4, target_allocation=target_allocation, min_weights=min_weights, max_weights=max_weights)
    portfolio_vals_total.append(asset_path_n)
    
    liability_path_n = lia.simulate_liabilities(delta_t=DELTA_T, observed_time=OBSERVED_TIME, initial_liabilities=1.78E08)
    liability_vals_total.append(liability_path_n)
    
final_prices = [path_i[-1] for path_i in portfolio_vals_total]
final_liabilites = [path_j[-1] for path_j in liability_vals_total]

# set up the both diagrams 
fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(12, 4))

time = [t for t in range(TIME_STEPS)]

final_asset_liability_ratios = []

# left diagram (all simulated paths of asset/liabilities)
for asset_path, liability_path in zip(portfolio_vals_total, liability_vals_total):
    
    asset_liability_path = []
    for a_val, l_val in zip(asset_path, liability_path):
        asset_liability_path.append(a_val/l_val)
        
    final_asset_liability_ratios.append(asset_liability_path[-1])
    
    ax_left.plot(time, asset_liability_path, color="black", alpha=0.1)
ax_left.set_title("Assets/Liabilities ratio for all simulated paths")
ax_left.set_xlabel("time")
ax_left.set_ylabel("asset/liabilities")

# right diagram (histogram of final asset/liability ratios)
ax_right.hist(final_asset_liability_ratios, bins=50, edgecolor="black")
ax_right.set_title("Distribution of final asset/liability ratios")
ax_right.set_xlabel("asset/liability ratio")
ax_right.set_ylabel("frequency")

# general stats about assets
print(f"Average portfolio value after {OBSERVED_TIME} year(s): {np.mean(final_prices)}")
print(f"Standard deviation of portfolio values after {OBSERVED_TIME} year(s): {np.std(final_prices)}")

# general stats about asset/liability ratios
print(f"\nAverage asset/liability ratio after {OBSERVED_TIME} year(s): {np.mean(final_asset_liability_ratios)*100} %")
print(f"Standard deviation of asset/liability ratios after {OBSERVED_TIME} year(s): {np.std(final_asset_liability_ratios)*100} %")

# calculate percentage of paths for which liabilities > assets
amt_underfunding = 0
for final_price, final_liability in zip(final_prices, final_liabilites):
    if final_price < final_liability:
        amt_underfunding += 1
pct_underfunding = amt_underfunding / len(final_prices)
print(f"\nShare of cases in which assets do not cover liabilites after {OBSERVED_TIME} year(s): {pct_underfunding}")


plt.tight_layout()
plt.show()