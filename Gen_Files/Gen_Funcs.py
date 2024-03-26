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

    # Calculate expected returns and covariance matrix
    expected_returns = get_expected_returns(hist)
    cov_matrix = get_cov_matrix(hist)

    # Generate random portfolios
    results = np.zeros((3, num_portfolios))
    weights = np.zeros((len(get_expected_returns(hist)), num_portfolios))
    for i in range(num_portfolios):
        # Generate random weights
        w = np.random.random(len(get_expected_returns(hist)))
        w /= np.sum(w)
        
        # Calculate portfolio statistics
        portfolio_return = np.dot(w, expected_returns)
        portfolio_std_dev = np.sqrt(np.dot(w.T, np.dot(cov_matrix, w)))
        portfolio_sharpe_ratio = portfolio_return / portfolio_std_dev
        
        # Save results
        results[0,i] = portfolio_return
        results[1,i] = portfolio_std_dev
        results[2,i] = portfolio_sharpe_ratio
        weights[:,i] = w
    
    # Calculate portfolios on the efficient frontier
    max_sharpe_idx = np.argmax(results[2])
    min_vol_idx = np.argmin(results[1])

    # Plot the efficient frontier
    fig, ax = plt.subplots()
    ax.scatter(results[1,:], results[0,:], c=results[2,:], cmap='viridis', marker='o')
    ax.scatter(results[1,max_sharpe_idx], results[0,max_sharpe_idx], c='red', marker='*', s=100)
    ax.scatter(results[1,min_vol_idx], results[0,min_vol_idx], c='blue', marker='*', s=100)
    ax.set_title('Efficient Frontier')
    ax.set_xlabel('Standard Deviation')
    ax.set_ylabel('Return')
    
    return fig