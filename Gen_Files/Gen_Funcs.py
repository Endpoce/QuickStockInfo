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

    # Calculate daily returns
    returns = stock_data.pct_change()
    
    # Calculate expected returns and covariance matrix
    expected_returns = returns.mean()
    cov_matrix = returns.cov()

    results = np.zeros((3,num_portfolios))
    weights_record = []

    # Simulate random portfolio allocations
    for i in range(num_portfolios):
        weights = np.random.random(len(stock_data.columns))
        weights /= np.sum(weights)
        weights_record.append(weights)
        portfolio_return = np.sum(weights * expected_returns) * 252
        portfolio_std_dev = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)
        results[0,i] = portfolio_return
        results[1,i] = portfolio_std_dev
        results[2,i] = results[0,i] / results[1,i]

    # Convert results array to pandas DataFrame
    results_df = pd.DataFrame(results.T, columns=['Return', 'Volatility', 'Sharpe Ratio'])

    # Find portfolios with maximum Sharpe ratio and min risk and store weights and tickers
    max_sharpe_portfolio = {}
    min_volatility_portfolio = {}

    max_sharpe_portfolio['Return'] = results_df['Return'].max()
    max_sharpe_portfolio['Volatility'] = results_df.loc[results_df['Sharpe Ratio'].idxmax()]['Volatility']
    max_sharpe_portfolio['Sharpe Ratio'] = results_df['Sharpe Ratio'].max()
    max_sharpe_portfolio['weights'] = weights_record[results_df['Sharpe Ratio'].idxmax()] * 100  # weights as percentages
    max_sharpe_portfolio['tickers'] = list(stock_data.columns)  # get tickers from column names

    min_volatility_portfolio['Return'] = results_df.loc[results_df['Volatility'].idxmin()]['Return']
    min_volatility_portfolio['Volatility'] = results_df['Volatility'].min()
    min_volatility_portfolio['Sharpe Ratio'] = results_df.loc[results_df['Volatility'].idxmin()]['Sharpe Ratio']
    min_volatility_portfolio['weights'] = weights_record[results_df['Volatility'].idxmin()] * 100  # weights as percentages
    min_volatility_portfolio['tickers'] = list(stock_data.columns)  # get tickers from column names

    # Plot the Efficient Frontier
    fig = go.Figure()

    # Add trace for portfolios
    fig.add_trace(go.Scatter(x=results_df['Volatility'], y=results_df['Return'], mode='markers', name='Portfolios'))
    fig.add_trace(go.Scatter(x=[max_sharpe_portfolio['Volatility']], y=[max_sharpe_portfolio['Return']], mode='markers', marker=dict(color='red', size=10), name='Max Sharpe Ratio Portfolio'))
    fig.add_trace(go.Scatter(x=[min_volatility_portfolio['Volatility']], y=[min_volatility_portfolio['Return']], mode='markers', marker=dict(color='green', size=10), name='Min Volatility Portfolio'))
    fig.update_layout(title='Efficient Frontier', xaxis_title='Risk', yaxis_title='Return')
    
    return fig, max_sharpe_portfolio, min_volatility_portfolio