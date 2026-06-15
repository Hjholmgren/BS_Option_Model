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


#Create Default value in sliders in streamlit
if 'S' not in st.session_state:
    st.session_state.S = 100.0
if 'K' not in st.session_state:
    st.session_state.K = 100.0
if 'r' not in st.session_state:
    st.session_state.r = 5.0
if 'tau' not in st.session_state:
    st.session_state.tau = 1.0
if 'sigma' not in st.session_state:
    st.session_state.sigma = 20.0
    
#keep widget in sync for sliders
def update_param(param_name, source):
    """
    param_name: 'S', 'K', 'r', etc.
    source: 'box' or 'slider'
    """
    if source == 'box':
        st.session_state[param_name] = st.session_state[f'{param_name}_box']
    elif source == 'slider':
        st.session_state[param_name] = st.session_state[f'{param_name}_slider']


#Interface Header
st.header('Black-Scholes Option Pricer')

#numbers input and its sliders

#Spot Price (S)
st.number_input('Spot Price', min_value=1.0, max_value=1000.0, value= st.session_state.S, step=0.01, key='S_box', on_change=update_param, args=('S', 'box'))
st.slider('Spot Price (Slider)', min_value = 1.0, max_value= 1000.0, value=st.session_state.S, step=0.01,key='S_slider', on_change=update_param, args=('S', 'slider'))

#Strike Price (K)
st.number_input('Strike Price', min_value=1.0, max_value=1000.0, value= st.session_state.K, step=0.01, key='K_box', on_change=update_param, args=('K', 'box'))
st.slider('Strike Price (Slider)', min_value = 1.0, max_value= 1000.0, value=st.session_state.K, step=0.01,key='K_slider', on_change=update_param, args=('K', 'slider'))

#Interest rate (r) (%)
st.number_input('Interest Rate (%)', min_value=0.0, max_value=50.0, value= st.session_state.r, step=0.25, key='r_box', on_change=update_param, args=('r', 'box'))
st.slider('Interest Rate (%) (Slider)', min_value = 0.0, max_value= 50.0, value=st.session_state.r, step=0.25,key='r_slider', on_change=update_param, args=('r', 'slider'))

#Time to maturity tau (years)
st.number_input('Time to Maturity(years)', min_value=0.0, max_value=10.0, value= st.session_state.tau, step=0.1, key='tau_box', on_change=update_param, args=('tau', 'box'))
st.slider('Time to Maturity (years)(Slider)', min_value = 0.0, max_value= 10.0, value=st.session_state.tau, step=0.1,key='tau_slider', on_change=update_param, args=('tau', 'slider'))

#Volatility (Sigma)
st.number_input('Volatility (%)', min_value=0.01, max_value=200.0, value= st.session_state.sigma, step=0.01, key='sigma_box', on_change=update_param, args=('sigma', 'box'))
st.slider('Volatility (%) (Slider)', min_value = 0.01, max_value= 200.0, value=st.session_state.sigma, step=0.01,key='sigma_slider', on_change=update_param, args=('sigma', 'slider'))

#call and put price depends on st.session_state
call_price = call(st.session_state.S, st.session_state.K, st.session_state.r, st.session_state.tau, st.session_state.sigma)
put_price = put(st.session_state.S, st.session_state.K, st.session_state.r, st.session_state.tau, st.session_state.sigma)

st.write(f'**Call Price:** ${call_price:.2f}')
st.write(f'**Put Price:** ${put_price:.2f}')



#Now create phase 3 or try creating another branch to merge