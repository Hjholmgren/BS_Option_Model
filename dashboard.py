from bs_functions import put, call
import streamlit as st #for the user interface
import numpy as np #for calc

#Create default values for the keys the app actually uses: _box and _slider
defaults = {'S': 100.0, 'K': 100.0, 'r': 5.0, 'tau': 1.0, 'sigma': 20.0}
for name, value in defaults.items():
    if f'{name}_box' not in st.session_state:
        st.session_state[f'{name}_box'] = value
        st.session_state[f'{name}_slider'] = value

#keep box and slider in sync: copy the edited one into its sibling
def update_param(param_name, source):
    """
    param_name: 'S', 'K', 'r', etc.
    source: 'box' or 'slider'
    """
    if source == 'box':
        st.session_state[f'{param_name}_slider'] = st.session_state[f'{param_name}_box']
    elif source == 'slider':
        st.session_state[f'{param_name}_box'] = st.session_state[f'{param_name}_slider']

#Interface Header
st.header('Black-Scholes Option Pricer')

#Spot Price (S)
st.number_input('Spot Price', min_value=1.0, max_value=1000.0, step=0.01, key='S_box', on_change=update_param, args=('S', 'box'))
st.slider('Spot Price (Slider)', min_value=1.0, max_value=1000.0, step=0.01, key='S_slider', on_change=update_param, args=('S', 'slider'))

#Strike Price (K)
st.number_input('Strike Price', min_value=1.0, max_value=1000.0, step=0.01, key='K_box', on_change=update_param, args=('K', 'box'))
st.slider('Strike Price (Slider)', min_value=1.0, max_value=1000.0, step=0.01, key='K_slider', on_change=update_param, args=('K', 'slider'))

#Interest rate (r) (%)
st.number_input('Interest Rate (%)', min_value=0.0, max_value=50.0, step=0.25, key='r_box', on_change=update_param, args=('r', 'box'))
st.slider('Interest Rate (%) (Slider)', min_value=0.0, max_value=50.0, step=0.25, key='r_slider', on_change=update_param, args=('r', 'slider'))

#Time to maturity tau (years)
st.number_input('Time to Maturity (years)', min_value=0.0, max_value=10.0, step=0.1, key='tau_box', on_change=update_param, args=('tau', 'box'))
st.slider('Time to Maturity (years) (Slider)', min_value=0.0, max_value=10.0, step=0.1, key='tau_slider', on_change=update_param, args=('tau', 'slider'))

#Volatility (sigma) (%)
st.number_input('Volatility (%)', min_value=0.01, max_value=200.0, step=0.01, key='sigma_box', on_change=update_param, args=('sigma', 'box'))
st.slider('Volatility (%) (Slider)', min_value=0.01, max_value=200.0, step=0.01, key='sigma_slider', on_change=update_param, args=('sigma', 'slider'))

#Read the values and convert percentages to decimals for the formula
S = st.session_state['S_box']
K = st.session_state['K_box']
r = st.session_state['r_box'] / 100
tau = st.session_state['tau_box']
sigma = st.session_state['sigma_box'] / 100

#call and put prices
call_price = call(S, K, r, tau, sigma)
put_price = put(S, K, r, tau, sigma)

st.write(f'**Call Price:** ${call_price:.2f}')
st.write(f'**Put Price:** ${put_price:.2f}')

#Put-call parity sanity check: C - P should equal S - K*e^(-r*tau)
parity_lhs = call_price - put_price
parity_rhs = S - K * np.exp(-r * tau)
if np.isclose(parity_lhs, parity_rhs):
    st.caption(f'Parity check  C - P = S - K*e^(-r*tau):  {parity_lhs:.4f} = {parity_rhs:.4f}')
else:
    st.caption(f'Parity broken: {parity_lhs:.4f} != {parity_rhs:.4f}')