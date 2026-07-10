from bs_functions import put, call
import streamlit as st #for the user interface
import numpy as np #for calc
import pandas as pd #for the dataframe view
import matplotlib.pyplot as plt #for the plots

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


#--------------------------------------------------------------------------
# Visualisations
#--------------------------------------------------------------------------
display = st.multiselect(
    'Display:',
    ['Heatmap', 'Dataframe', 'Payoff', 'Price vs spot'],
    default=['Heatmap'],
)

# Grids used by both the heatmap and the dataframe:
# how the CALL price changes as spot and volatility move away from the current inputs.
spot_changes = np.linspace(-40, 40, 20)     # absolute change in spot price
vol_changes = np.linspace(-10, 20, 20)      # change in volatility, in percentage points

base_price = call(S, K, r, tau, sigma)
price_grid = np.zeros((len(vol_changes), len(spot_changes)))
for i, dvol in enumerate(vol_changes):
    for j, dspot in enumerate(spot_changes):
        new_price = call(S + dspot, K, r, tau, sigma + dvol / 100)
        price_grid[i, j] = new_price - base_price


#Heatmap
if 'Heatmap' in display:
    fig, ax = plt.subplots(figsize=(8, 6))
    # origin='lower' puts the smallest vol change at the bottom, largest at the top
    im = ax.imshow(price_grid, origin='lower', cmap='rainbow', aspect='auto')

    ax.set_xticks(range(len(spot_changes)))
    ax.set_xticklabels([f'{x:.2f}' for x in spot_changes], rotation=90)
    ax.set_yticks(range(len(vol_changes)))
    ax.set_yticklabels([f'{v:.2f}' for v in vol_changes])

    ax.set_xlabel('Change in spot price')
    ax.set_ylabel('Change in volatility (%)')
    ax.set_title(
        'Change in call option price\n'
        f'(S, K, r, \u03c4, \u03c3) = ({S:.2f}, {K:.2f}, {r*100:.1f}%, {tau:.3f}yrs, {sigma*100:.1f}%)'
    )
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label('Change in call option price')
    fig.tight_layout()
    st.pyplot(fig)

#Dataframe
if 'Dataframe' in display:
    df = pd.DataFrame(
        price_grid,
        index=[f'{v:.2f}' for v in vol_changes],
        columns=[f'{x:.2f}' for x in spot_changes],
    )
    df.index.name = 'Δvol (%)'
    df.columns.name = 'Δspot'
    # show largest vol change on top, like the heatmap
    st.dataframe(df.iloc[::-1])

#Payoff diagram: value at expiry (hockey stick) vs value now
if 'Payoff' in display:
    spots = np.linspace(0.5 * K, 1.5 * K, 200)
    value_now = np.array([call(s, K, r, tau, sigma) for s in spots])
    value_expiry = np.maximum(spots - K, 0.0)

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(spots, value_expiry, '--', color='gray', label='At expiry (intrinsic)')
    ax.plot(spots, value_now, color='tab:blue', lw=2, label=f'Now (\u03c4 = {tau} yr)')
    ax.axvline(K, color='crimson', ls=':', lw=1, label=f'Strike K = {K:g}')
    ax.axvline(S, color='black', ls='-', lw=0.8, label=f'Spot S = {S:g}')
    ax.set_xlabel('Spot price')
    ax.set_ylabel('Call value')
    ax.set_title('Call payoff diagram')
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    st.pyplot(fig)

#Price vs spot: call and put price as the spot moves
if 'Price vs spot' in display:
    spots = np.linspace(0.5 * K, 1.5 * K, 200)
    calls = np.array([call(s, K, r, tau, sigma) for s in spots])
    puts = np.array([put(s, K, r, tau, sigma) for s in spots])

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(spots, calls, color='tab:green', lw=2, label='Call')
    ax.plot(spots, puts, color='tab:red', lw=2, label='Put')
    ax.axvline(S, color='black', ls='-', lw=0.8, label=f'Spot S = {S:g}')
    ax.set_xlabel('Spot price')
    ax.set_ylabel('Option price')
    ax.set_title('Option price vs spot')
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    st.pyplot(fig)

