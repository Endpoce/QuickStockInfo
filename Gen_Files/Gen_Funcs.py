# Gen_Funcs.py

import yfinance as yf
import streamlit as st
import plotly.graph_objects as go
import sys
import linecache
import pandas as pd
from datetime import datetime, timedelta
import wikipedia
import dotenv
import numpy as np
import random

# set env vars
dotenv.load_dotenv()


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

# get price info
def get_price_info(info, hist, primary_ticker, start_of_year):
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

# get wiki paragraphs
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

# Display efficient frontier
def get_efficient_frontier(num_portfolios, stock_data):
    """
    Get the expected returns and covariance matrix of a portfolio using the Efficient Frontier method. The 
    Efficient Frontier method is a mathematical optimization technique used to find the set of optimal portfolios
    that offer the highest expected return for a given level of risk or the lowest risk for a given level of expected return.
    """
    try:
        # Calculate daily returns
        returns = stock_data.pct_change()
        
        # Calculate expected returns and covariance matrix
        expected_returns = returns.mean()
        cov_matrix = returns.cov()

        # Initialize variables
        results = {}
        results_dict = {}
        weights = {}
        max_sharpe = 0
        min_volatility = 0
        max_sharpe_portfolio = {}
        min_volatility_portfolio = {}

        # Simulate num_portfolios
        for i in range(num_portfolios):
            # Generate random weights
            weights = np.random.random(len(stock_data.columns))
            weights /= np.sum(weights)

            # Calculate portfolio returns, volatility, and Sharpe ratio
            returns = np.sum(expected_returns * weights) * 252
            volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)
            sharpe_ratio = returns / volatility

            # Store results in a dictionary
            results_dict['Returns'] = returns
            results_dict['Volatility'] = volatility
            results_dict['Sharpe Ratio'] = sharpe_ratio
            results_dict['Weights'] = weights

            # Store results in a list
            results[i] = [returns, volatility, sharpe_ratio, weights]

            # Find the portfolio with the minimum volatility
            min_volatility_portfolio
            
            if sharpe_ratio > max_sharpe:
                max_sharpe = sharpe_ratio
                max_sharpe_portfolio = {"Return": returns, "Volatility": volatility, "Sharpe Ratio": sharpe_ratio, "Weights": weights}
    except Exception as e:
        error_message(e)

    return fig, max_sharpe_portfolio, min_volatility_portfolio, results_dict