# Streamlit Trading Application

import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import time
from streamlit_autorefresh import st_autorefresh

# Page configuration
st.set_page_config(
    page_title="Live Trading System",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration constants
DEFAULT_TICKER = "TCS.NS"
DEFAULT_REFRESH_INTERVAL = 60
DEFAULT_ORDER_QUANTITY = 10
DEFAULT_INITIAL_CAPITAL = 10000
DEFAULT_TRANSACTION_COST = 0.05

# Sidebar configuration
st.sidebar.title("Trading Configuration")
ticker = st.sidebar.text_input("Stock Ticker", value=DEFAULT_TICKER, help="Enter stock symbol (e.g., TCS.NS for NSE)")
refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", min_value=10, max_value=300, value=DEFAULT_REFRESH_INTERVAL)
order_quantity = st.sidebar.number_input("Order Quantity", min_value=1, max_value=1000, value=DEFAULT_ORDER_QUANTITY)
initial_capital = st.sidebar.number_input("Initial Capital (₹)", min_value=1000, max_value=10000000, value=DEFAULT_INITIAL_CAPITAL)
transaction_cost = st.sidebar.slider("Transaction Cost (%)", min_value=0.01, max_value=1.0, value=DEFAULT_TRANSACTION_COST, step=0.01)

# Auto-refresh component
count = st_autorefresh(interval=refresh_interval * 1000, key="trading_refresh")

# Initialize session state for trading system
if 'trading_system' not in st.session_state:
    st.session_state.trading_system = {
        'cash': initial_capital,
        'holdings': 0,
        'transactions': [],
        'position': 0,  # 0=neutral, 1=long, -1=short
        'last_action': None,
        'portfolio_value': []
    }

# Reset trading system if configuration changes
if st.sidebar.button("Reset Trading System"):
    st.session_state.trading_system = {
        'cash': initial_capital,
        'holdings': 0,
        'transactions': [],
        'position': 0,
        'last_action': None,
        'portfolio_value': []
    }
    st.success("Trading system reset successfully!")

def execute_order(price, action_type, trader):
    """Execute buy/sell orders and update portfolio"""
    if action_type == "BUY" and trader['cash'] >= price * order_quantity:
        cost = price * order_quantity
        trader['cash'] -= cost * (1 + transaction_cost/100)
        trader['holdings'] += order_quantity
        trader['position'] = 1
        trader['transactions'].append({
            'timestamp': pd.Timestamp.now(),
            'price': price,
            'quantity': order_quantity,
            'type': action_type
        })
        
    elif action_type == "SELL" and trader['holdings'] >= order_quantity:
        proceeds = price * order_quantity
        trader['cash'] += proceeds * (1 - transaction_cost/100)
        trader['holdings'] -= order_quantity
        trader['position'] = -1
        trader['transactions'].append({
            'timestamp': pd.Timestamp.now(),
            'price': price,
            'quantity': order_quantity,
            'type': action_type
        })
    
    trader['portfolio_value'].append({
        'timestamp': pd.Timestamp.now(),
        'cash': trader['cash'],
        'holdings_value': trader['holdings'] * price,
        'total': trader['cash'] + (trader['holdings'] * price)
    })

@st.cache_data(ttl=30)  # Cache for 30 seconds
def fetch_data(ticker_symbol):
    """Fetch 1-minute interval data for the last day"""
    try:
        return yf.Ticker(ticker_symbol).history(period="1d", interval="1m")
    except Exception as e:
        st.error(f"Error fetching data for {ticker_symbol}: {e}")
        return pd.DataFrame()

def check_signals(df, trader):
    """Check for Bollinger Bands trading signals"""
    if len(df) < 2:
        return None
        
    latest = df.iloc[-1]
    
    # Buy signal (price touches lower band)
    if latest['Low'] <= latest['Lower'] and trader['position'] != 1:
        execute_order(latest['Close'], "BUY", trader)
        return 'buy'
    
    # Sell signal (price touches upper band)
    if latest['High'] >= latest['Upper'] and trader['position'] != -1:
        execute_order(latest['Close'], "SELL", trader)
        return 'sell'
    
    return None

def calculate_bollinger_bands(df):
    """Calculate Bollinger Bands"""
    if len(df) < 20:
        return df
    
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    df['Upper'] = df['SMA20'] + 2 * df['Close'].rolling(window=20).std()
    df['Lower'] = df['SMA20'] - 2 * df['Close'].rolling(window=20).std()
    return df

# Main app
st.title(f"📈 Live Trading System - {ticker}")
st.markdown("Real-time Bollinger Bands trading strategy")

# Fetch and process data
df = fetch_data(ticker)

if not df.empty:
    # Calculate Bollinger Bands
    df = calculate_bollinger_bands(df)
    
    # Check for trading signals
    signal = check_signals(df, st.session_state.trading_system)
    
    # Current portfolio metrics
    current_price = df['Close'].iloc[-1] if len(df) > 0 else 0
    portfolio_value = st.session_state.trading_system['cash'] + (st.session_state.trading_system['holdings'] * current_price)
    
    # Display portfolio metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Cash", f"₹{st.session_state.trading_system['cash']:,.2f}")
    
    with col2:
        st.metric("Holdings", f"{st.session_state.trading_system['holdings']} shares")
    
    with col3:
        holdings_value = st.session_state.trading_system['holdings'] * current_price
        st.metric("Holdings Value", f"₹{holdings_value:,.2f}")
    
    with col4:
        profit_loss = portfolio_value - initial_capital
        st.metric("Total Portfolio", f"₹{portfolio_value:,.2f}", 
                 delta=f"₹{profit_loss:,.2f}")
    
    # Create the chart
    fig = go.Figure()
    
    # Add candlestick chart
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Price'
    ))
    
    # Add Bollinger Bands
    if 'SMA20' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, 
            y=df['SMA20'], 
            name='20 SMA',
            line=dict(color='blue', width=1.5)
        ))
        
        fig.add_trace(go.Scatter(
            x=df.index, 
            y=df['Upper'], 
            name='Upper Band',
            line=dict(color='red', width=1, dash='dot')
        ))
        
        fig.add_trace(go.Scatter(
            x=df.index, 
            y=df['Lower'], 
            name='Lower Band',
            line=dict(color='green', width=1, dash='dot')
        ))
    
    # Add trade markers
    if signal:
        marker_color = 'green' if signal == 'buy' else 'red'
        marker_symbol = 'triangle-up' if signal == 'buy' else 'triangle-down'
        fig.add_trace(go.Scatter(
            x=[df.index[-1]],
            y=[df['Close'].iloc[-1]],
            mode='markers',
            marker=dict(color=marker_color, size=15, symbol=marker_symbol),
            name=f'{signal.upper()} Signal',
            showlegend=True
        ))
    
    # Update layout
    fig.update_layout(
        title=f"{ticker} Live Chart - Last Updated: {pd.Timestamp.now().strftime('%H:%M:%S')}",
        xaxis_title="Time",
        yaxis_title="Price (₹)",
        xaxis_rangeslider_visible=False,
        showlegend=True,
        height=600
    )
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True)
    
    # Trading status and signals
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Current Status")
        position_text = {0: "Neutral", 1: "Long", -1: "Short"}
        st.write(f"**Position:** {position_text[st.session_state.trading_system['position']]}")
        st.write(f"**Current Price:** ₹{current_price:.2f}")
        
        if signal:
            st.success(f"🔔 {signal.upper()} signal detected!")
        
        # Recent transactions
        if st.session_state.trading_system['transactions']:
            latest_transaction = st.session_state.trading_system['transactions'][-1]
            st.write(f"**Last Trade:** {latest_transaction['type']} {latest_transaction['quantity']} @ ₹{latest_transaction['price']:.2f}")
    
    with col2:
        st.subheader("Performance")
        if len(st.session_state.trading_system['portfolio_value']) > 0:
            pnl_pct = ((portfolio_value - initial_capital) / initial_capital) * 100
            st.write(f"**P&L:** {pnl_pct:.2f}%")
            st.write(f"**Total Trades:** {len(st.session_state.trading_system['transactions'])}")
    
    # Transaction history
    if st.session_state.trading_system['transactions']:
        st.subheader("Recent Transactions")
        transactions_df = pd.DataFrame(st.session_state.trading_system['transactions'])
        st.dataframe(transactions_df.tail(10), use_container_width=True)
    
    # Market data info
    st.subheader("Market Data")
    if len(df) > 0:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Day High", f"₹{df['High'].max():.2f}")
        with col2:
            st.metric("Day Low", f"₹{df['Low'].min():.2f}")
        with col3:
            st.metric("Volume", f"{df['Volume'].iloc[-1]:,.0f}" if 'Volume' in df.columns else "N/A")

else:
    st.error("Unable to fetch data. Please check the ticker symbol and try again.")
    st.info("Make sure to use the correct format (e.g., TCS.NS for NSE, AAPL for NASDAQ)")

# Footer
st.markdown("---")
st.markdown("**Disclaimer:** This is a demo trading system. Do not use for actual trading without proper risk management.")