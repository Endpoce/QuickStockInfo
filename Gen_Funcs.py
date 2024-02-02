# Gen_Funcs.py

import yfinance as yf
import streamlit as st
import plotly.graph_objects as go

def get_stock_info(symbol):
    """
    Get stock information for a given symbol using the yfinance library.
    """
    stock = yf.Ticker(symbol)
    info = stock.info
    return info

def get_stock_data(symbol, start_date, end_date):
    ticker = yf.Ticker(symbol)

    symbol = ticker.ticker

    info = ticker.info

    hist = ticker.history(period="1d", start=start_date, end=end_date)

    return ticker, info, hist, symbol

def display_stock_info(info):
    """
    Display stock information using the Streamlit API.
    """
    st.write("Company Name:", info['longName'])
    st.write("Symbol:", info['symbol'])
    st.write("Sector:", info['sector'])
    st.write("Industry:", info['industry'])
    st.write("Market Cap:", info['marketCap'])
    st.write("Price:", info['regularMarketPrice'])
    st.write("Volume:", info['regularMarketVolume'])

# plot stock data on an interactive chart
def plot_Stock(info):

    hist = info.history(period="5d")

    fig = go.Figure(data=[go.Candlestick(x=hist.index,
                                         open=hist['Open'],
                                         high=hist['High'],
                                         low=hist['Low'],
                                         close=hist['Close'])])

    fig.update_layout(
        title='Stock Price Chart',
        xaxis_title='Date',
        yaxis_title='Price',
        xaxis_rangeslider_visible=False
    )

    st.plotly_chart(fig)


