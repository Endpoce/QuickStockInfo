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

    # create new column for daily returns for each stock
    for stock in hist.columns:
        hist[stock + " Daily Return"] = hist[stock].pct_change()

    # calculate expected returns
    for stock in hist.columns:
        hist[stock + " Expected Return"] = hist[stock + " Daily Return"].mean()

    # get expected returns
    expected_returns = hist[[stock + " Expected Return" for stock in hist.columns]].iloc[-1]

    return expected_returns

def get_cov_matrix(hist):
    
    # create new column for daily returns for each stock
    for stock in hist.columns:
        hist[stock + " Daily Return"] = hist[stock].pct_change()

    # calculate covariance matrix
    cov_matrix = hist[[(stock + " Daily Return") for stock in hist.columns]].cov()

    return cov_matrix


def get_efficient_frontier(num_portfolios, stock_data):

    # set number of portfolios
    num_portfolios = num_portfolios

    # set number of stocks
    num_stocks = len(stock_data.keys())

    # set random seed
    np.random.seed(42)

    # set number of simulations
    num_simulations = 10000

    # set risk free rate
    risk_free_rate = 0.02

    # set number of trading days
    trading_days = 252
    
    # create dicts to store returns, weights, and volatilities
    portfolio_returns = {}
    portfolio_volatilities = {}
    portfolio_weights = {}
    
    # calculate expected returns
    for stock in stock_data.keys():
        stock_data[stock + " Daily Return"] = stock_data[stock]["Adj Close"].pct_change()
        stock_data[stock + " Expected Return"] = stock_data[stock + " Daily Return"].mean()
    
    # calculate covariance matrix
    cov_matrix = pd.DataFrame()
    for stock in stock_data.keys():
        cov_matrix[stock] = stock_data[stock + " Daily Return"]
    cov_matrix = cov_matrix.cov()

    # populate dicts with random weights
    for i in range(num_portfolios):
        weights = np.random.random(num_stocks)
        weights /= np.sum(weights)
        portfolio_weights[i] = weights

    # calculate returns and volatilities
    for i in range(num_portfolios):
        portfolio_returns[i] = np.sum(stock_data[stock + " Expected Return"] * portfolio_weights[i])
        portfolio_volatilities[i] = np.sqrt(np.dot(portfolio_weights[i].T, np.dot(cov_matrix, portfolio_weights[i])))

    # create a dict to store portfolio data
    for i in range(num_portfolios):
        portfolio_data = {
            "Returns": portfolio_returns[i],
            "Volatility": portfolio_volatilities[i],
            "Sharpe Ratio": (portfolio_returns[i] - risk_free_rate) / portfolio_volatilities[i]
        }
    
    # create a DataFrame from the portfolio data
    portfolio_df = pd.DataFrame(portfolio_data)

    # create a scatter plot of the efficient frontier
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=portfolio_df["Volatility"], y=portfolio_df["Returns"], mode="markers", name="Efficient Frontier"))
    fig.update_layout(title="Efficient Frontier", xaxis_title="Volatility", yaxis_title="Returns")

    return fig
    

