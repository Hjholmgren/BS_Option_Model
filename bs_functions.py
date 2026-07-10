import numpy as np
from scipy.stats import norm

"""
    Parameters:
    S - Spot price (current price)
    K - Strike price
    r - annualized risk-free interest rate (as a decimal, e.g. 0.05)
    tau - time to maturity in years
    sigma - volatility of underlying asset (as a decimal, e.g. 0.20)

    r and sigma are decimals here; the % -> decimal conversion is done in the UI.
"""

#d_1 and d_2 are the core of every Black-Scholes quantity,
#so compute them once here instead of repeating the formula in each function.
def d1_d2(S, K, r, tau, sigma):
    d_1 = (np.log(S/K) + (r + (sigma**2)/2)*tau) / (sigma*np.sqrt(tau))
    d_2 = d_1 - sigma*np.sqrt(tau)
    return d_1, d_2

#Prices
def call(S, K, r, tau, sigma):
    if tau == 0:
        return max(S-K, 0)
    d_1, d_2 = d1_d2(S, K, r, tau, sigma)
    return norm.cdf(d_1)*S - norm.cdf(d_2)*K*np.exp(-r*tau)

def put(S, K, r, tau, sigma):
    if tau == 0:
        return max(K-S, 0)
    d_1, d_2 = d1_d2(S, K, r, tau, sigma)
    return K * norm.cdf(-d_2) * np.exp(-r*tau) - norm.cdf(-d_1) * S

#Greeks - raw partial derivatives. The UI scales them to the units traders quote.
def delta(S, K, r, tau, sigma, option='call'):
    if tau == 0:
        return float('nan')
    d_1, d_2 = d1_d2(S, K, r, tau, sigma)
    if option == 'call':
        return norm.cdf(d_1)
    else:
        return norm.cdf(d_1) - 1     #put delta

def gamma(S, K, r, tau, sigma):      #same for call and put
    if tau == 0:
        return float('nan')
    d_1, d_2 = d1_d2(S, K, r, tau, sigma)
    return norm.pdf(d_1) / (S*sigma*np.sqrt(tau))

def vega(S, K, r, tau, sigma):       #same for call and put. Raw: per +1.0 in sigma
    if tau == 0:
        return float('nan')
    d_1, d_2 = d1_d2(S, K, r, tau, sigma)
    return S * norm.pdf(d_1) * np.sqrt(tau)

def theta(S, K, r, tau, sigma, option='call'):   #raw: per year
    if tau == 0:
        return float('nan')
    d_1, d_2 = d1_d2(S, K, r, tau, sigma)
    decay = -(S * norm.pdf(d_1) * sigma) / (2*np.sqrt(tau))
    if option == 'call':
        return decay - r*K*np.exp(-r*tau)*norm.cdf(d_2)
    else:
        return decay + r*K*np.exp(-r*tau)*norm.cdf(-d_2)

def rho(S, K, r, tau, sigma, option='call'):      #raw: per +1.0 in r
    if tau == 0:
        return float('nan')
    d_1, d_2 = d1_d2(S, K, r, tau, sigma)
    if option == 'call':
        return K*tau*np.exp(-r*tau)*norm.cdf(d_2)
    else:
        return -K*tau*np.exp(-r*tau)*norm.cdf(-d_2)

#Implied volatility via Newton-Raphson.
#We look for the sigma that makes the model price equal the market price.
#vega is d(price)/d(sigma), so it is the natural Newton step.
def implied_vol(price, S, K, r, tau, option='call', tol=1e-6, max_iter=100):
    price_fn = call if option == 'call' else put
    sigma = 0.2                      #starting guess: 20% vol
    for _ in range(max_iter):
        diff = price_fn(S, K, r, tau, sigma) - price
        if abs(diff) < tol:
            return sigma
        v = vega(S, K, r, tau, sigma)
        if v < 1e-8:                 #vega ~ 0 would blow the step up
            break
        sigma = sigma - diff / v
        if sigma <= 0:               #keep volatility positive
            sigma = tol
    return sigma                     #best estimate (may not converge for extreme inputs)