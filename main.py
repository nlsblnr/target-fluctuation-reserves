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

sim_runs = 100
observed_time = 1
delta_t = 1/365

# create asset class with attributes standard distribution of returns, mean return and the total invested capital in said asset
class Asset:
    def __init__(self, sigma, mu, invested_capital):
        self.sigma = sigma
        self.mu = mu
        self.invested_capital = invested_capital

    def calculate_next_price(self, invested_capital):
        pass

# define liabilities as an amount constant over time
liabilities = 7E08