# Gen_Funcs.py

import yfinance as yf
import streamlit as st
import plotly.graph_objects as go
import google.generativeai as gai
import sys
import linecache
import pandas as pd
from datetime import datetime, timedelta
import wikipedia
import dotenv
import numpy as np
import matplotlib.pyplot as plt

# set env vars
dotenv.load_dotenv()

# set pandas override
yf.pdr_override()

# error message
def error_message(message):
    """
    Display an error message using the Streamlit API.
    """
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    response = ('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
        
    st.error(response)

# get stock information
def get_stock_info(symbol):
    """
    Get stock information for a given symbol using the yfinance library.
    """
    stock = yf.Ticker(symbol)
    info = stock.info
    return info

# get stock data
def get_stock_data(symbol, start_date, end_date):
    ticker = yf.Ticker(symbol)

    symbol = ticker.ticker

    info = ticker.info

    hist = ticker.history(period="1d", start=start_date, end=end_date)

    return ticker, info, hist, symbol

# display stock information
def display_stock_info(info, hist):
    """
    Display stock information using the Streamlit API.
    """

    st.write(info["longBusinessSummary"])
    st.write("Sector:", info['sector'])
    st.write("Industry:", info['industry'])
    st.write("Market Cap:", info['marketCap'])
    st.write("Recent Close Price:", hist['Close'][-1])
    st.write("Recent Daily Volume:", hist['Volume'][-1])

def get_long_info(info, hist, primary_ticker, start_of_year):
        # display finance info
        st.subheader("Summary:")
        
        # read stock price data from csv
        filename = str(primary_ticker) + '_Price_Data.csv'
        df = pd.read_csv(filename)


        # display current price
        st.metric(label="Current Price: ",
                    value=round(hist['Close'].iloc[-1], 2))
        
        # display latest volume
        st.metric(label="Latest Volume: ",
                    value=hist['Volume'].iloc[-1])

        # display high price
        st.metric(label="High Price: ",
                    value=round(df['High'].max(), 2))
        
        # display low price
        st.metric(label="Low Price: ",
                    value=round(df['Low'].min(), 2))
        
        # display average price
        st.metric(label="Average Price: ",
                    value=round(df['Close'].mean(), 2))
        
        # average volume
        st.metric(label="Average Volume: ",
                    value=round(df['Volume'].mean(), 2))
        
        # 

def get_wiki_info(query):

    results = wikipedia.search(query)
    if results != None:
        first_result = results[0]  # get the first result
        try:
            # get the page of the first result
            page = wikipedia.page(first_result)
            url = page.url  # get the url of the page
            return url, page  # return the content of the page
        except wikipedia.DisambiguationError as e:
            print(
                f"Disambiguation page found, consider choosing a specific title from: {e.options}")
        except wikipedia.PageError:
            print("Page not found on Wikipedia")
    else:
        return None  # return None if no results found
    
def get_expected_returns(hist):

    # Calculate daily returns of each 'close' column in the DataFrame
    daily_returns = hist.pct_change().dropna()
    
    # Calculate expected returns
    expected_returns = daily_returns.mean()
    
    return expected_returns

def get_cov_matrix(hist):
    """
    Calculate the covariance matrix from historical data of stocks.
    
    Parameters:
        historical_data (DataFrame): Historical prices of stocks where each column represents a stock.
        
    Returns:
        cov_matrix (array): Covariance matrix of the stocks.
    """
    # Calculate daily returns
    daily_returns = hist.pct_change().dropna()
    
    # Calculate covariance matrix
    cov_matrix = daily_returns.cov()
    
    return cov_matrix


def get_efficient_frontier(num_portfolios, hist):

    ### Efficient Frontier
    # Calculate expected returns and covariance matrix
    expected_returns = get_expected_returns(hist)
    cov_matrix = get_cov_matrix(hist)

    # Number of assets
    num_assets = len(expected_returns)

    # Empty lists to store returns, volatility and weights of the portfolios
    portfolio_returns = []
    portfolio_volatilities = []
    portfolio_weights = []

    # Loop to generate portfolios
    for _ in range(num_portfolios):
        # Generate random weights
        weights = np.random.random(num_assets)
        weights /= np.sum(weights)

        # Calculate expected return
        portfolio_return = np.dot(weights, expected_returns)

        # Calculate expected volatility
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

        # Append to the lists
        portfolio_returns.append(portfolio_return)
        portfolio_volatilities.append(portfolio_volatility)
        portfolio_weights.append(weights)
    
    # Convert the lists to NumPy arrays
    portfolio_returns = np.array(portfolio_returns)
    portfolio_volatilities = np.array(portfolio_volatilities)
    portfolio_weights = np.array(portfolio_weights)

    # Create a dictionary to store the data
    data = {
        "Returns": portfolio_returns,
        "Volatility": portfolio_volatilities
    }

    # Add the weights to the dictionary
    for i, symbol in enumerate(hist.columns):
        data[symbol] = portfolio_weights[:, i]
    
    # Create a DataFrame from the dictionary
    df = pd.DataFrame(data)

    # plot efficient frontier
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Volatility"], y=df["Returns"], mode="markers", marker=dict(size=5)))
    fig.update_layout(title="Efficient Frontier", xaxis_title="Volatility", yaxis_title="Returns")

    return fig

