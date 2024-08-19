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
    Get the expected returns and covariance matrix of a portfolio using the Efficient Frontier method.

    Args:
        num_portfolios: Number of portfolios to simulate.
        stock_data: Pandas DataFrame containing asset returns.

    Returns:
        results_dict: Dictionary containing portfolio data.
        max_sharpe_portfolio: Dictionary containing the maximum Sharpe ratio portfolio.
        min_volatility_portfolio: Dictionary containing the minimum volatility portfolio.
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
        min_volatility = float('inf')
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

            # Store results in a list (optional)
            results[i] = [returns, volatility, sharpe_ratio, weights]

            # Find the portfolio with the minimum volatility
            if volatility < min_volatility:
                min_volatility = volatility
                min_volatility_portfolio = results_dict.copy()

            # Find the portfolio with the maximum Sharpe ratio
            if sharpe_ratio > max_sharpe:
                max_sharpe = sharpe_ratio
                max_sharpe_portfolio = results_dict.copy()


            # Extract data for plotting
            returns = [result['Returns'] for result in results_dict["Returns"]]
            volatilities = [result['Volatility'] for result in results_dict["Volatility"]]

            # Create the scatter plot
            fig = go.Figure(data=go.Scatter(
                x=volatilities,
                y=returns,
                mode='markers',
                marker=dict(
                    size=8,
                    color=returns,  # Color points based on returns
                    colorscale='Viridis',
                    opacity=0.7
                )
            ))

            # Add layout elements
            fig.update_layout(
                title='Efficient Frontier',
                xaxis_title='Volatility',
                yaxis_title='Expected Return',
                hovermode='closest'  # Enable hover information
            )

            return fig, max_sharpe_portfolio, min_volatility_portfolio, results_dict
    except Exception as e:
      error_message(e)

