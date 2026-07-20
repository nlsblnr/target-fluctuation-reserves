# target-fluctuation-reserves: Asset and Liability Management Applied to Pension Funds
In this project, I use Monte Carlo simulations in order to find out whether a pension fund's assets can sufficiently cover the funds liabilities.

## Structure
The project consists of the following files:
### requirements.txt
Lists the required Python libraries
### src/assets.py
Includes the definition of the Asset class and the function used to simulate one single portfolio value path; is called in main.py
### src/liabilities.py
Includes the function used to simulate one single liability time series; is called in main.py
### src/rebalancing.py
Includes all functions used to rebalance the asset portfolio; is called in assets.py
### src/main.py
This is where the simulation is put together: for a given number of sim runs, portfolio value paths and liability time series are simulated and combined to calculate the asset/liability ratio (in German: Deckungsgrad). Here you can also create figures/diagrams using matplotlib if wanted.

## How to run your own simulation
The entire project can be executed locally with Python 3.14. Some standard libraries are used, such as NumPy and Matplotlib.

1. Install missing libraries if needed
2. Run main.py

## Further work

The following things would be valuable extensions to the simulation:

- Add correlated asset returns so the portfolio reflects how markets move together. This will make the simulation more realistic than treating each asset independently.

- Include transaction costs and more detailed rebalancing rules. That will show how often rebalancing is truly beneficial after costs.

- Make liabilities more realistic by linking them to interest rates, benefit payments, or contributions. This will improve the asset-liability view of the pension fund.

- Add cash flows such as contributions and benefit payments. Pension funds are not static, so these flows make the simulation much closer to reality.

- Test different market scenarios like crashes, rising rates, or inflation shocks. This helps evaluate how robust the portfolio is under stress.

- Use the model to compare different investment strategies, not just a single setup. That makes it more useful for decision-making and risk analysis.