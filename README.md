# target-fluctuation-reserves: Asset and Liability Management Applied to Pension Funds
In this project, I use Monte Carlo simulations in order to find out whether a pension fund's assets can sufficiently cover the funds liabilities.

## Structure
The project consists of the following files:
### assets.py
Includes the definition of the Asset class and the function used to simulate one single portfolio value path; is called in main.py
### liabilities.py
Includes the function used to simulate one single liability time series; is called in main.py
### rebalancing.py
Includes all functions used to rebalance the asset portfolio; is called in assets.py
### main.py
This is where the simulation is put together: for a given number of sim runs, portfolio value paths and liability time series are simulated and combined to calculate the asset/liability ratio (in German: Deckungsgrad). Here you can also create figures/diagrams using matplotlib if wanted.

## How to run your own simulation
The entire project can be executed locally with Python 3.14. Some standard libraries are used, such as NumPy and Matplotlib.

1. Install missing libraries if needed
2. Run main.py