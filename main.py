'''

The target fluctuation reserves are typically calculated as 2/3*(assets/liabilities - 1) such that this value is only negative in the worst 2.2 % of possible outcomes after five years of observation (less than two standard deviations below zero).

This is a common rule of thumb to ensure that there are sufficient reserves to cover potential fluctuations in asset values relative to liabilities

To go about this calculation, we need to:
1. simulate possible outcomes for the given assets given their expected values and standard deviations
2. simulate possible outcomes for the given liabilites statistical info
3. calculate the fluctuation reserves (= assets/liabilities - 1) for each simulated outcome
4. determine the 2.2 percentile of the fluctuation reserves to find the target fluctuation reserve

We will have to agree on an initial asset portfolio and initial liabilities. For this we will simply use the actual information of a given pension fund using their annual report

'''


import random
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

sim_runs = 100
observed_time = 1
delta_t = 1/365
time_steps = round(observed_time/delta_t)

# create asset class with attributes standard distribution of returns, mean return and the total invested capital in said asset
class Asset:
    def __init__(self, mu, sigma, invested_capital):
        self.sigma = sigma
        self.mu = mu
        self.invested_capital = invested_capital
        self.initial_capital = invested_capital
        self.brownian_motion_process = []

    def calculate_next_price(self, run_index, invested_capital):
        
        time_now = run_index * delta_t
        
        if run_index == 0:
            self.brownian_motion_process.append(0)
            new_invested_capital = self.initial_capital
        else:
            dW = np.random.normal(loc=0, scale=np.sqrt(delta_t))
            self.brownian_motion_process.append(self.brownian_motion_process[-1] + dW)
            
            drift = self.mu - self.sigma**2/2
            
            new_invested_capital = self.initial_capital*np.exp(drift*time_now + self.sigma*self.brownian_motion_process[run_index])
            
        self.invested_capital = float(new_invested_capital)
        return self.invested_capital


# define liabilities as an amount constant over time
liabilities = 7E08

mean_portfolio = [0.0 for _ in range(time_steps)]

for a in range(sim_runs):
    
    # define assets
    stocks = Asset(0.07, 0.2, 1E07)
    bonds = Asset(0.03, 0.03, 3E06)
    real_estate = Asset(0.04, 0.014, 8E06)
    portfolio = [stocks, bonds, real_estate]
    
    portfolio_values = []
    
    for i in range(time_steps):
        portfolio_value = 0
        for asset in portfolio:
            new_asset_value = asset.calculate_next_price(i, asset.invested_capital)
            portfolio_value += new_asset_value
        
        mean_portfolio[i] += portfolio_value
        portfolio_values.append(portfolio_value)
        
    time = [t for t in range(time_steps)]
    plt.plot(time, portfolio_values, alpha=0.2)
    
time = [t for t in range(time_steps)]
for mp_i, s in enumerate(mean_portfolio):
    mean_portfolio[mp_i] = s / sim_runs
    
log_returns_mean_portfolio = [float(np.log(c + 1)) for c in pd.Series(mean_portfolio).pct_change()]
# overwrite nan
log_returns_mean_portfolio[0] = 0

plt.plot(time, mean_portfolio, color="black")

plt.show()