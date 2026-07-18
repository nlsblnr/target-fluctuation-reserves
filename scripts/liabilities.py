import numpy as np

def simulate_liabilities(observed_time=5, delta_t=1/200, initial_liabilities=1.0):
    LIABILITY_GROWTH_RATE = 0.005
    time_steps = round(observed_time/delta_t)
    
    liability_path = [float(initial_liabilities*np.exp(LIABILITY_GROWTH_RATE * t * delta_t)) for t in range(time_steps)]
    
    return liability_path