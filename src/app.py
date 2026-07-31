import numpy as np
import pandas as pd
import streamlit as st

import liabilities as lia
import assets as ast

st.set_page_config(layout="wide")
st.title("Pension fund ALM simulation")

# --- sidebar / form for user inputs ---

with st.form("simulation_parameters"):
    st.subheader("Simulation settings")

    sim_runs = st.number_input("Number of simulation runs", min_value=100, max_value=10_000, value=1_000, step=100)
    observed_time = st.number_input("Observation period (years)", min_value=1.0, max_value=30.0, value=5.0, step=1.0)
    delta_t = st.number_input("Time step Δt (in years)", min_value=1/250.0, max_value=1.0, value=1/200.0, format="%.6f")
    transaction_costs = st.number_input("Transaction costs (as fraction, e.g. 0.001)", min_value=0.0, max_value=0.1, value=0.001, step=0.0001)

    st.subheader("Initial portfolio")
    stocks_val = st.number_input("Stocks (initial value)", min_value=0.0, value=7e7, step=1e6)
    bonds_val = st.number_input("Bonds (initial value)", min_value=0.0, value=3e7, step=1e6)
    re_val = st.number_input("Real estate (initial value)", min_value=0.0, value=5e7, step=1e6)
    misc_val = st.number_input("Miscellaneous (initial value)", min_value=0.0, value=5e7, step=1e6)

    st.subheader("Asset parameters")
    stocks_mu = st.number_input("Stocks μ (expected return)", min_value=-0.5, max_value=1.0, value=0.07, step=0.01)
    stocks_sigma = st.number_input("Stocks σ (volatility)", min_value=0.0, max_value=2.0, value=0.20, step=0.01)

    bonds_mu = st.number_input("Bonds μ", min_value=-0.5, max_value=1.0, value=0.03, step=0.01)
    bonds_sigma = st.number_input("Bonds σ", min_value=0.0, max_value=2.0, value=0.03, step=0.01)

    re_mu = st.number_input("Real estate μ", min_value=-0.5, max_value=1.0, value=0.04, step=0.01)
    re_sigma = st.number_input("Real estate σ", min_value=0.0, max_value=2.0, value=0.014, step=0.001)

    misc_mu = st.number_input("Miscellaneous μ", min_value=-0.5, max_value=1.0, value=0.03, step=0.01)
    misc_sigma = st.number_input("Miscellaneous σ", min_value=0.0, max_value=2.0, value=0.05, step=0.01)

    st.subheader("Correlation matrix (4×4, rows: stocks, bonds, real estate, misc)")
    c11 = st.number_input("ρ(stocks,stocks)", value=1.0, key="c11")
    c12 = st.number_input("ρ(stocks,bonds)", value=0.4, key="c12")
    c13 = st.number_input("ρ(stocks,real_estate)", value=-0.2, key="c13")
    c14 = st.number_input("ρ(stocks,misc)", value=0.1, key="c14")

    c21 = st.number_input("ρ(bonds,stocks)", value=0.4, key="c21")
    c22 = st.number_input("ρ(bonds,bonds)", value=1.0, key="c22")
    c23 = st.number_input("ρ(bonds,real_estate)", value=0.3, key="c23")
    c24 = st.number_input("ρ(bonds,misc)", value=0.7, key="c24")

    c31 = st.number_input("ρ(real_estate,stocks)", value=-0.2, key="c31")
    c32 = st.number_input("ρ(real_estate,bonds)", value=0.3, key="c32")
    c33 = st.number_input("ρ(real_estate,real_estate)", value=1.0, key="c33")
    c34 = st.number_input("ρ(real_estate,misc)", value=-0.1, key="c34")

    c41 = st.number_input("ρ(misc,stocks)", value=0.1, key="c41")
    c42 = st.number_input("ρ(misc,bonds)", value=0.7, key="c42")
    c43 = st.number_input("ρ(misc,real_estate)", value=-0.1, key="c43")
    c44 = st.number_input("ρ(misc,misc)", value=1.0, key="c44")

    st.subheader("Target allocation and rebalancing")
    w_stocks = st.number_input("Target weight stocks", min_value=0.0, max_value=1.0, value=7/20, step=0.01)
    w_bonds = st.number_input("Target weight bonds", min_value=0.0, max_value=1.0, value=3/20, step=0.01)
    w_re = st.number_input("Target weight real estate", min_value=0.0, max_value=1.0, value=5/20, step=0.01)
    w_misc = st.number_input("Target weight misc", min_value=0.0, max_value=1.0, value=5/20, step=0.01)

    corridor_halfwidth = st.number_input("Corridor half‑width (e.g. 0.05 for ±5%)", min_value=0.0, max_value=0.5, value=0.05, step=0.01)
    rebalancing_style = st.selectbox("Rebalancing style", ["calendar", "corridor"])
    rebalancing_period = st.number_input("Rebalancing period (years, for calendar)", min_value=delta_t, max_value=observed_time, value=0.25, step=0.05)

    st.subheader("Contributions and liabilities")
    yearly_contributions = st.number_input("Yearly contributions (total)", min_value=0.0, value=2e6, step=1e5)
    contributions_period = st.number_input("Contributions period (years)", min_value=delta_t, max_value=observed_time, value=1.0, step=0.1)

    initial_liabilities = st.number_input("Initial liabilities", min_value=0.0, value=1.78e8, step=1e6)

    submitted = st.form_submit_button("Run simulation")

if not submitted:
    st.stop()

# --- basic checks ---

target_allocation = [w_stocks, w_bonds, w_re, w_misc]
if not np.isclose(sum(target_allocation), 1.0, atol=1e-6):
    st.error("Target weights must sum to 1.")
    st.stop()

corr_matrix = np.array([
    [c11, c12, c13, c14],
    [c21, c22, c23, c24],
    [c31, c32, c33, c34],
    [c41, c42, c43, c44],
])

# quick symmetry check
if not np.allclose(corr_matrix, corr_matrix.T, atol=1e-8):
    st.error("Correlation matrix must be symmetric.")
    st.stop()

# --- build portfolio ---

stocks = ast.Asset(stocks_mu, stocks_sigma, stocks_val, delta_t)
bonds = ast.Asset(bonds_mu, bonds_sigma, bonds_val, delta_t)
real_estate = ast.Asset(re_mu, re_sigma, re_val, delta_t)
miscellaneous = ast.Asset(misc_mu, misc_sigma, misc_val, delta_t)
pf = [stocks, bonds, real_estate, miscellaneous]

min_weights = [w - corridor_halfwidth for w in target_allocation]
max_weights = [w + corridor_halfwidth for w in target_allocation]

# --- run simulation ---

time_steps = round(observed_time / delta_t)

portfolio_vals_total = []
liability_vals_total = []

progress_bar = st.progress(0)
status_text = st.empty()

for n in range(int(sim_runs)):
    if (n + 1) % 100 == 0:
        status_text.text(f"Completed {n+1}/{sim_runs} sim runs ----- {round((n+1)/sim_runs*100)} % done")
        progress_bar.progress((n + 1) / sim_runs)

    asset_path_n = ast.simulate_assets(
        delta_t=delta_t,
        observed_time=observed_time,
        portfolio=pf,
        yearly_contributions=yearly_contributions,
        contributions_period=contributions_period,
        correlation_matrix=corr_matrix,
        transaction_costs=transaction_costs,
        rebalancing_activated=True,
        rebalancing_style=rebalancing_style,
        rebalancing_period=rebalancing_period,
        target_allocation=target_allocation,
        min_weights=min_weights,
        max_weights=max_weights,
    )
    portfolio_vals_total.append(asset_path_n)

    liability_path_n = lia.simulate_liabilities(
        delta_t=delta_t,
        observed_time=observed_time,
        initial_liabilities=initial_liabilities,
    )
    liability_vals_total.append(liability_path_n)

progress_bar.progress(1.0)
status_text.text("Simulation completed.")

# --- compute funding ratios ---

final_prices = [path_i[-1] for path_i in portfolio_vals_total]
final_liabilites = [path_j[-1] for path_j in liability_vals_total]

time = list(range(time_steps))

funding_ratio_paths = []
for asset_path, liability_path in zip(portfolio_vals_total, liability_vals_total):
    fr_path = [a_val / l_val for a_val, l_val in zip(asset_path, liability_path)]
    funding_ratio_paths.append(fr_path)

final_funding_ratios = [fr_path[-1] for fr_path in funding_ratio_paths]

# --- prepare data for Streamlit charts ---

# For line_chart, Streamlit expects a DataFrame with columns as series.
# To avoid plotting 1000+ lines, sample a subset of paths.

sample_size = min(200, len(funding_ratio_paths))
sample_indices = np.random.choice(len(funding_ratio_paths), size=sample_size, replace=False)

df_lines = pd.DataFrame({
    "time": time
})
for i, idx in enumerate(sample_indices):
    df_lines[f"path_{i}"] = [funding_ratio_paths[idx][t] for t in range(time_steps)]

# Histogram data
df_hist = pd.DataFrame({"final_funding_ratio": final_funding_ratios})

# --- plots with Streamlit built‑in charts ---

st.subheader("Funding ratio (assets / liabilities) over time")
st.line_chart(df_lines.set_index("time"))

st.subheader("Distribution of final funding ratios")
st.bar_chart(df_hist["final_funding_ratio"].value_counts(bins=50, sort=False).sort_index())

# Some summary stats
st.subheader("Summary statistics")

avg_final_portfolio = np.mean(final_prices)
std_final_portfolio = np.std(final_prices)
pct_underfunded = np.mean(np.array(final_prices) < np.array(final_liabilites))

st.metric("Average final portfolio value", f"{avg_final_portfolio:,.0f}")
st.metric("Std dev of final portfolio value", f"{std_final_portfolio:,.0f}")
st.metric("Share of scenarios with assets < liabilities", f"{pct_underfunded:.2%}")