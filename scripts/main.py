'''
The target fluctuation reserves are typically calculated as 2/3*(assets/liabilities - 1) such that this value is only negative in the worst 2.2 % of possible outcomes after five years of observation (less than two standard deviations below zero).
This is a common rule of thumb to ensure that there are sufficient reserves to cover potential fluctuations in asset values relative to liabilities
'''

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import rebalancing as rb

sim_runs = 1
observed_time = 5
delta_t = 1/200
time_steps = round(observed_time/delta_t)

rebalancing_activated = True
rebalancing_period = 0.25 # rebalance portfolio after every x years, needed for calendar rebalancing
rebalancing_style = "corridor"

# asset multiplier (proportional factor) multiplied with portfolio values to experiment with its effect on the share of cases in which liablitites > assets
asset_multiplier = 1.0

# create asset class with attributes standard distribution of returns, mean return and the total invested capital in said asset
class Asset:
    def __init__(self, mu, sigma, value):
        self.sigma = sigma
        self.mu = mu
        self.value = float(value)
        self.brownian_motion_process = [0.0]

    def calculate_next_price(self, run_index):
        if run_index == 0:
            return float(self.value)

        dW = np.random.normal(loc=0.0, scale=np.sqrt(delta_t))
        self.brownian_motion_process.append(self.brownian_motion_process[-1] + dW)

        drift = (self.mu - 0.5 * self.sigma**2) * delta_t
        diffusion = self.sigma * dW

        self.value *= np.exp(drift + diffusion)
        return self.value

# define liabilities as an amount constant over time
liabilities = 1.75E08

end_prices = []
portfolio_vals_total = []

for a in range(sim_runs):
    
    # define assets - they NEED to be defined for every single path
    # because their data is permanently updated after every calculation
    stocks = Asset(0.07, 0.2, 7E07*asset_multiplier)
    bonds = Asset(0.03, 0.03, 3E07*asset_multiplier)
    real_estate = Asset(0.04, 0.014, 5E07*asset_multiplier)
    miscellaneous = Asset(0.03, 0.05, 5E07*asset_multiplier)
    portfolio = [stocks, bonds, real_estate, miscellaneous]

    target_allocation = [7/20, 3/20, 5/20, 5/20] # tells rebalancing function how to rebalance the portfolio
    min_weights = [0.95 * w_t for w_t in target_allocation] # min weights are 5 % below target weights
    max_weights = [1.05 * w_t for w_t in target_allocation] # max weights are 5 % above target weights
    
    portfolio_vals_a = []
    
    for i in range(time_steps):
        portfolio_value = 0
        for asset in portfolio:
            new_asset_value = asset.calculate_next_price(i)
            portfolio_value += new_asset_value
        
        portfolio_vals_a.append(portfolio_value)
        
        # start rebalancing procedure if rebalancing is activated
        if rebalancing_activated:

            if rebalancing_style == "calendar":
                # for calendar rebalancing: only call function if end of rebalancing period is reached
                if i % round(rebalancing_period/delta_t):
                    target_portfolio_values = rb.calendar_rebalancing(portfolio, target_allocation)
                    for k, asset in enumerate(portfolio):
                        asset.value = target_portfolio_values[k]
            
            elif rebalancing_style == "corridor":
                # for corridor rebalancing: always call function
                target_portfolio_values = rb.corridor_rebalancing(portfolio, target_allocation, min_weights, max_weights)
                for k, asset in enumerate(portfolio):
                    asset.value = target_portfolio_values[k]
            
    time = [t for t in range(time_steps)]
    portfolio_vals_total.append(portfolio_vals_a)                 
    
    end_prices.append(portfolio_vals_a[-1])
    
time = [t for t in range(time_steps)]

# set up the both diagrams 
fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(12, 4))

# left diagram (all simulated paths)
for y in portfolio_vals_total:
    ax_left.plot(time, y, color="black", alpha=0.1)
ax_left.set_title("All simulated paths")
ax_left.set_xlabel("time")
ax_left.set_ylabel("price")

# right diagram (histogram of end prices)
ax_right.hist(end_prices, bins=50, edgecolor="black")
ax_right.set_title("Distribution of end prices")
ax_right.set_xlabel("end prices")
ax_right.set_ylabel("frequency")

# percentage of paths for which liabilities > assets
amt_low_coverage = 0
for e in end_prices:
    if e < liabilities:
        amt_low_coverage += 1
pct_low_coverage = amt_low_coverage / len(end_prices)
print(f"Share of cases in which assets do not cover liabilites after {observed_time} year(s): {pct_low_coverage}")

print(f"Average portfolio value after {observed_time} year(s): {np.mean(end_prices)}")
print(f"Standard deviation of portfolio values after {observed_time} year(s): {np.std(end_prices)}")

plt.tight_layout()
plt.show()