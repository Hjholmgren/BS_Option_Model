from bs_funtions import call, put, delta, gamma, vega, theta, rho, implied_vol
import streamlit as st #for the user interface
import numpy as np #for calc
import pandas as pd #for the tables
import matplotlib.pyplot as plt #for the plots
from matplotlib.colors import TwoSlopeNorm #to center the heatmap colours on zero

st.set_page_config(page_title='Black-Scholes Option Pricer', layout='wide')

#--------------------------------------------------------------------------
# Inputs (sidebar)
#--------------------------------------------------------------------------
defaults = {'S': 100.0, 'K': 100.0, 'r': 5.0, 'tau': 1.0, 'sigma': 20.0}
for name, value in defaults.items():
    if f'{name}_box' not in st.session_state:
        st.session_state[f'{name}_box'] = value
        st.session_state[f'{name}_slider'] = value

def update_param(param_name, source):
    if source == 'box':
        st.session_state[f'{param_name}_slider'] = st.session_state[f'{param_name}_box']
    elif source == 'slider':
        st.session_state[f'{param_name}_box'] = st.session_state[f'{param_name}_slider']

st.sidebar.header('Parameters')

def param_input(label, name, lo, hi, step):
    st.sidebar.number_input(label, min_value=lo, max_value=hi, step=step,
                            key=f'{name}_box', on_change=update_param, args=(name, 'box'))
    st.sidebar.slider(' ', min_value=lo, max_value=hi, step=step,
                      key=f'{name}_slider', on_change=update_param, args=(name, 'slider'),
                      label_visibility='collapsed')

param_input('Spot Price', 'S', 1.0, 1000.0, 0.01)
param_input('Strike Price', 'K', 1.0, 1000.0, 0.01)
param_input('Interest Rate (%)', 'r', 0.0, 50.0, 0.25)
param_input('Time to Maturity (years)', 'tau', 0.0, 10.0, 0.1)
param_input('Volatility (%)', 'sigma', 0.01, 200.0, 0.01)

#Read values and convert percentages to decimals for the formulas
S = st.session_state['S_box']
K = st.session_state['K_box']
r = st.session_state['r_box'] / 100
tau = st.session_state['tau_box']
sigma = st.session_state['sigma_box'] / 100

#--------------------------------------------------------------------------
# Prices + parity
#--------------------------------------------------------------------------
st.header('Black-Scholes Option Pricer')

call_price = call(S, K, r, tau, sigma)
put_price = put(S, K, r, tau, sigma)

c1, c2 = st.columns(2)
c1.metric('Call Price', f'${call_price:.2f}')
c2.metric('Put Price', f'${put_price:.2f}')

parity_lhs = call_price - put_price
parity_rhs = S - K * np.exp(-r * tau)
if np.isclose(parity_lhs, parity_rhs):
    st.caption(f'Parity check  C - P = S - K*e^(-r*tau):  {parity_lhs:.4f} = {parity_rhs:.4f}')
else:
    st.caption(f'Parity broken: {parity_lhs:.4f} != {parity_rhs:.4f}')

#--------------------------------------------------------------------------
# Greeks table
#--------------------------------------------------------------------------
st.subheader('Greeks')
if tau == 0:
    st.caption('Greeks are undefined at expiry (tau = 0).')
else:
    #Scale to the units traders quote:
    #Vega per +1% vol, Theta per calendar day, Rho per +1% rate.
    greeks = pd.DataFrame(
        {
            'Delta': [delta(S, K, r, tau, sigma, 'call'), delta(S, K, r, tau, sigma, 'put')],
            'Gamma': [gamma(S, K, r, tau, sigma)] * 2,
            'Vega':  [vega(S, K, r, tau, sigma) / 100] * 2,
            'Theta': [theta(S, K, r, tau, sigma, 'call') / 365, theta(S, K, r, tau, sigma, 'put') / 365],
            'Rho':   [rho(S, K, r, tau, sigma, 'call') / 100, rho(S, K, r, tau, sigma, 'put') / 100],
        },
        index=['Call', 'Put'],
    )
    st.table(greeks.style.format('{:.4f}'))
    st.caption('Vega per +1% vol . Theta per day . Rho per +1% rate')

#--------------------------------------------------------------------------
# Implied volatility solver
#--------------------------------------------------------------------------
st.subheader('Implied volatility')
st.caption('Enter a market price and solve for the volatility that reproduces it (Newton-Raphson).')
iv_col1, iv_col2 = st.columns(2)
iv_option = iv_col1.radio('Option type', ['call', 'put'], horizontal=True, key='iv_opt')
default_price = call_price if iv_option == 'call' else put_price
market_price = iv_col2.number_input('Market price', min_value=0.0, value=float(round(default_price, 2)), step=0.01, key='mkt_price')
if tau == 0:
    st.caption('Implied vol is undefined at expiry (tau = 0).')
else:
    iv = implied_vol(market_price, S, K, r, tau, iv_option)
    st.write(f'Implied volatility: **{iv*100:.2f}%**')

#--------------------------------------------------------------------------
# Visualisations
#--------------------------------------------------------------------------
st.subheader('Visualisations')
display = st.multiselect(
    'Display:',
    ['Call heatmap', 'Put heatmap', 'Dataframe', 'Payoff', 'Price vs spot', 'Greeks vs spot'],
    default=['Call heatmap'],
)

#Axes shared by the heatmaps and the dataframe
spot_changes = np.linspace(-40, 40, 20)   #absolute change in spot price
vol_changes = np.linspace(-10, 20, 20)    #change in volatility, percentage points

#Grid of how an option price changes as spot and vol move off the current inputs.
#price_fn is either call or put, so the same code builds both heatmaps.
def price_change_grid(price_fn):
    base = price_fn(S, K, r, tau, sigma)
    grid = np.zeros((len(vol_changes), len(spot_changes)))
    for i, dvol in enumerate(vol_changes):
        for j, dspot in enumerate(spot_changes):
            grid[i, j] = price_fn(S + dspot, K, r, tau, sigma + dvol / 100) - base
    return grid

#Draw one heatmap. Diverging colours centred on zero: blue = loss, red = gain, white = no change.
def show_heatmap(grid, option_name):
    span = max(abs(grid.min()), abs(grid.max()), 1e-9)
    divnorm = TwoSlopeNorm(vmin=-span, vcenter=0.0, vmax=span)
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(grid, origin='lower', cmap='RdBu_r', norm=divnorm, aspect='auto')
    ax.set_xticks(range(len(spot_changes)))
    ax.set_xticklabels([f'{x:.2f}' for x in spot_changes], rotation=90)
    ax.set_yticks(range(len(vol_changes)))
    ax.set_yticklabels([f'{v:.2f}' for v in vol_changes])
    ax.set_xlabel('Change in spot price')
    ax.set_ylabel('Change in volatility (%)')
    ax.set_title(f'Change in {option_name} option price\n'
                 f'(S, K, r, \u03c4, \u03c3) = ({S:.2f}, {K:.2f}, {r*100:.1f}%, {tau:.3f}yrs, {sigma*100:.1f}%)')
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label(f'Change in {option_name} option price')
    fig.tight_layout()
    st.pyplot(fig)

#Call heatmap
if 'Call heatmap' in display:
    show_heatmap(price_change_grid(call), 'call')

#Put heatmap
if 'Put heatmap' in display:
    show_heatmap(price_change_grid(put), 'put')

#Dataframe (change in call price on the same grid)
if 'Dataframe' in display:
    df = pd.DataFrame(price_change_grid(call),
                      index=[f'{v:.2f}' for v in vol_changes],
                      columns=[f'{x:.2f}' for x in spot_changes])
    df.index.name = 'dvol (%)'
    df.columns.name = 'dspot'
    st.dataframe(df.iloc[::-1])

#Payoff diagram
if 'Payoff' in display:
    spots = np.linspace(0.5 * K, 1.5 * K, 200)
    value_now = np.array([call(s, K, r, tau, sigma) for s in spots])
    value_expiry = np.maximum(spots - K, 0.0)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(spots, value_expiry, '--', color='gray', label='At expiry (intrinsic)')
    ax.plot(spots, value_now, color='tab:blue', lw=2, label=f'Now (\u03c4 = {tau} yr)')
    ax.axvline(K, color='crimson', ls=':', lw=1, label=f'Strike K = {K:g}')
    ax.axvline(S, color='black', ls='-', lw=0.8, label=f'Spot S = {S:g}')
    ax.set_xlabel('Spot price'); ax.set_ylabel('Call value')
    ax.set_title('Call payoff diagram'); ax.legend(); ax.grid(alpha=0.3)
    fig.tight_layout()
    st.pyplot(fig)

#Price vs spot
if 'Price vs spot' in display:
    spots = np.linspace(0.5 * K, 1.5 * K, 200)
    calls = np.array([call(s, K, r, tau, sigma) for s in spots])
    puts = np.array([put(s, K, r, tau, sigma) for s in spots])
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(spots, calls, color='tab:green', lw=2, label='Call')
    ax.plot(spots, puts, color='tab:red', lw=2, label='Put')
    ax.axvline(S, color='black', ls='-', lw=0.8, label=f'Spot S = {S:g}')
    ax.set_xlabel('Spot price'); ax.set_ylabel('Option price')
    ax.set_title('Option price vs spot'); ax.legend(); ax.grid(alpha=0.3)
    fig.tight_layout()
    st.pyplot(fig)

#Greeks vs spot (call), one panel each
if 'Greeks vs spot' in display:
    if tau == 0:
        st.caption('Greeks are undefined at expiry (tau = 0).')
    else:
        spots = np.linspace(0.5 * K, 1.5 * K, 200)
        deltas = [delta(s, K, r, tau, sigma, 'call') for s in spots]
        gammas = [gamma(s, K, r, tau, sigma) for s in spots]
        vegas = [vega(s, K, r, tau, sigma) / 100 for s in spots]
        thetas = [theta(s, K, r, tau, sigma, 'call') / 365 for s in spots]
        fig, axs = plt.subplots(2, 2, figsize=(9, 6))
        for ax, y, name in zip(axs.ravel(), [deltas, gammas, vegas, thetas],
                               ['Delta', 'Gamma', 'Vega (per 1%)', 'Theta (per day)']):
            ax.plot(spots, y, color='tab:blue', lw=2)
            ax.axvline(S, color='black', ls='-', lw=0.7)
            ax.set_title(name); ax.set_xlabel('Spot price'); ax.grid(alpha=0.3)
        fig.suptitle('Call Greeks vs spot')
        fig.tight_layout()
        st.pyplot(fig)