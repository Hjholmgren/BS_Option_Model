import streamlit as st #for the user interface
import numpy as np #for calc
from scipy.stats import norm #compute option price, CDF (cumulative distribution formula) of normal distribution in "call" and "put" functions

"""
    Parameters:
    S - Spot price (current price)
    K - Strike price
    r - annualized risk-free interest rate (in percentage)
    tau - time to maturity in years
    sigma - volatility of underlying asset
"""

#Black-Scholes function
#Define call and put options
def call(S, K, r, tau, sigma):
    if tau == 0:
        return max(S-K,0) #if maturatiy has reached
    else :
        d_1 = (np.log(S/K) + (r + (sigma**2)/2)*tau) /(sigma*(np.sqrt(tau)))
        d_2 = d_1 - sigma*np.sqrt(tau)
        #norm.cdf is standard normal CDF -> N(0,1)
        return norm.cdf(d_1)*S - norm.cdf(d_2)*K*np.exp(-r*tau)
    
def put(S, K, r, tau, sigma):
    if tau == 0:
        return max(K-S, 0)
    else :
        d_1 = (np.log(S/K) + (r + (sigma**2)/2)) / (sigma * (np.sqrt(tau)))
        d_2 = d_1 - sigma*np.sqrt(tau)

        return K * norm.cdf(-d_2) * np.exp(-r*(tau)) - norm.cdf(-d_1) * S


#simple interface
st.header('Black-Scholes Option Pricer')

#numbers input
S = st.number_input('Spot Price', value=100.0, min_value=1.0)
K = st.number_input('Strike Price', value=100.0, min_value=1.0)
r = st.number_input('Interest Rate (%)', value=5.0)/100
tau = st.number_input('Time to maturity (years)', value=1.0, min_value=0.0)
sigma = st.number_input('Volatility (%)', value=20.0)/100

call_price = call(S, K, r, tau, sigma)
put_price = put(S, K, r, tau, sigma)

st.write(f'**Call Price:** ${call_price:.2f}')
st.write(f'**Put Price:** ${put_price:.2f}')




