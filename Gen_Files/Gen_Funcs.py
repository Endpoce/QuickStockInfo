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

    print(hist)

    # Create empty dicts to store returns for each, volatility and weights of the imaginary portfolios
    port_returns = {}
    port_volatility = {}
    stock_weights = {}

    # Calculate daily returns of each 'close' column in the DataFrame
    for column in hist.columns:
        hist[column] = hist[column].pct_change()

    # Calculate expected returns
    expected_returns = hist.mean()

    # Calculate the covariance matrix
    cov_matrix = hist.cov()

    # set number of assets
    num_assets = len(hist.columns)

    # Set the number of combinations for imaginary portfolios
    num_portfolios = num_portfolios



    # Populate the empty lists with each portfolios returns, risk and weights
    for single_portfolio in range(num_portfolios):
        weights = np.random.random(num_assets)
        weights /= np.sum(weights)
        returns = np.dot(weights, expected_returns)
        volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        port_returns[single_portfolio] = returns
        port_volatility[single_portfolio] = volatility
        stock_weights[single_portfolio] = weights
    
    # Create a dictionary for returns, volatility and weights
    portfolio = {'Returns': port_returns, 'Volatility': port_volatility}
    
    # Extend original dictionary to accomodate each ticker and weight in the portfolio
    for counter, symbol in enumerate(hist.columns):
        portfolio[symbol + ' Weight'] = [weight[counter] for weight in stock_weights.values()]

    # Create a DataFrame from the extended dictionary
    df = pd.DataFrame(portfolio)

    # Create scatter plot coloured by Sharpe Ratio
    fig = go.Figure(data=[go.Scatter(
        x=df['Volatility'],
        y=df['Returns'],
        mode='markers',
        marker=dict(
            size=10,
            color=df['Returns'],  # Set color equal to a variable
            colorscale='Viridis',  # One of plotly colorscales
            showscale=True
        )
    )])

    return fig

