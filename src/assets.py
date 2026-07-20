import numpy as np
import rebalancing as rb

# create asset class with attributes standard distribution of returns, mean return and the total amount invested
class Asset:
    def __init__(self, mu, sigma, value, delta_t=1/200):
        self.sigma = sigma
        self.mu = mu
        self.value = value
        self.initial_value = value
        self.delta_t = delta_t
        
    def reset_value(self):
        self.value = self.initial_value

    def calculate_next_price(self, run_index, shock):
        if run_index == 0:
            return self.value

        drift = (self.mu - self.sigma**2/2) * self.delta_t
        diffusion = self.sigma * np.sqrt(self.delta_t) * shock

        self.value *= np.exp(drift + diffusion)
        return self.value

# simulates exactly one asset value path
def simulate_assets(observed_time=5, delta_t=1/200, portfolio=[], correlation_matrix=[], rebalancing_activated=True, rebalancing_period=1/4, rebalancing_style="calendar", target_allocation=[], min_weights=[], max_weights=[]):
    
    time_steps = round(observed_time/delta_t)
    
    # verification if correlation matrix is valid (written by Perplexity AI)
    correlation_matrix = np.asarray(correlation_matrix, dtype=float)
    if correlation_matrix.ndim != 2 or correlation_matrix.shape[0] != correlation_matrix.shape[1]:
        raise ValueError("correlation_matrix must be a square 2D array.")
    if correlation_matrix.shape[0] != len(portfolio):
        raise ValueError("correlation_matrix size must match the number of assets in portfolio.")
    if not np.allclose(correlation_matrix, correlation_matrix.T, atol=1e-8):
        raise ValueError("correlation_matrix must be symmetric.")
    if not np.allclose(np.diag(correlation_matrix), 1.0, atol=1e-8):
        raise ValueError("correlation_matrix must have ones on the diagonal.")
    eigvals = np.linalg.eigvalsh(correlation_matrix)
    if np.min(eigvals) < -1e-8:
        raise ValueError("correlation_matrix must be positive semidefinite.")
    
    # Cholesky decomposition needed to impose correlation on random asset price shocks
    L = np.linalg.cholesky(correlation_matrix)
        
    # reset asset values to initial values at the start of each sim run
    for asset in portfolio:
        asset.reset_value()
        
    value_path = []
    
    # simulate portfolio over time
    for i in range(time_steps):
        # generate standard normal shocks and impose correlation
        st_norm_shocks = np.random.normal(size=len(portfolio))
        correlated_shocks = L @ st_norm_shocks
        
        portfolio_value = 0
        for shock, asset in zip(correlated_shocks, portfolio):
            new_asset_value = asset.calculate_next_price(run_index=i, shock=shock)
            portfolio_value += new_asset_value
        
        value_path.append(float(portfolio_value))
        
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
    
    # return price path
    return value_path