import numpy as np #for calc
from scipy.stats import norm #compute option price, CDF (cumulative distribution formula) of normal distribution in "call" and "put" functions

"""
    Parameters:
    S - Spot price (current price)
    K - Strike price
    r - annualized risk-free interest rate (as decimal)
    tau - time to maturity in years
    sigma - volatility of underlying asset (as decimal)

    Percentage conversion happens in dashboard.py
"""

#Black-Scholes function
#Define call and put options
def call(S, K, r, tau, sigma):
    if tau == 0:
        return max(S-K,0) #if maturity has been reached
    else :
        d_1 = (np.log(S/K) + (r + (sigma**2)/2)*tau) /(sigma*(np.sqrt(tau)))
        d_2 = d_1 - sigma*np.sqrt(tau)
        #norm.cdf is standard normal CDF -> N(0,1)
        return norm.cdf(d_1)*S - norm.cdf(d_2)*K*np.exp(-r*tau)
    
def put(S, K, r, tau, sigma):
    if tau == 0:
        return max(K-S, 0)
    else :
        d_1 = (np.log(S/K) + (r + (sigma**2)/2)*tau) / (sigma * (np.sqrt(tau)))
        d_2 = d_1 - sigma*np.sqrt(tau)

        return K * norm.cdf(-d_2) * np.exp(-r*(tau)) - norm.cdf(-d_1) * S



