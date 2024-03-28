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
    
def get_efficient_frontier(num_portfolios, stock_data):
    # calculate efficient fronteir for multiple stocks with historical data for each
    
    # for each stock, calculate and create a column for the expected returns and covariance matrix
    try:
        # calculate expected returns, ignore the first column
        for col in stock_data.columns[1:]:
            stock_data[col + ' Expected Returns'] = stock_data[col].pct_change().mean()
            expected_returns = stock_data.iloc[:, 1:]

        # calculate covariance matrix
        cov_matrix = stock_data.iloc[:, 1:].pct_change().cov()

    except Exception as e:
        error_message(e)
    
    try:

        # set random seed
        np.random.seed(42)

        # set number of portfolios
        num_portfolios = num_portfolios

        # create empty arrays to store returns, volatility, and sharpe ratio
        results = np.zeros((3, num_portfolios))

        # create empty arrays to store weights
        weights_arr = []

        # create empty arrays to store returns and volatility
        ret_arr = []
        vol_arr = []

        # create empty arrays to store sharpe ratio
        sharpe_arr = []

        # create loop to generate portfolios
        for i in range(num_portfolios):
            # generate random weights
            weights = np.random.random(len(stock_data.columns[1:]))
            weights /= np.sum(weights)
            weights_arr.append(weights)

            # calculate expected returns
            ret = np.dot(weights, expected_returns)
            ret_arr.append(ret)

            # calculate volatility
            vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            vol_arr.append(vol)

            # calculate sharpe ratio
            sharpe = ret / vol
            sharpe_arr.append(sharpe)
        
        # convert arrays to numpy arrays
        ret_arr = np.array(ret_arr)
        vol_arr = np.array(vol_arr)
        sharpe_arr = np.array(sharpe_arr)

        # get max sharpe ratio
        max_sharpe_ratio = sharpe_arr.max()

        # get max return
        max_return = ret_arr.max()

        # get min volatility
        min_volatility = vol_arr.min()

        # get max sharpe ratio index
        max_sharpe_ratio_index = sharpe_arr.argmax()

        # get max return index
        max_return_index = ret_arr.argmax()

        # get min volatility index
        min_volatility_index = vol_arr.argmin()

        # store results in results array
        results[0] = ret_arr
        results[1] = vol_arr
        results[2] = sharpe_arr
        
        # plot efficient frontier
        fig.add_trace(go.Scatter(x=results[1], y=results[0], mode='markers', marker=dict(size=10, color=results[2], colorscale='Viridis', showscale=True)))

        # add max sharpe ratio
        fig.add_trace(go.Scatter(x=[vol_arr[max_sharpe_ratio_index]], y=[ret_arr[max_sharpe_ratio_index]], mode='markers', marker=dict(size=15, color='red')))
        fig.add_annotation(text="Max Sharpe Ratio", x=vol_arr[max_sharpe_ratio_index], y=ret_arr[max_sharpe_ratio_index], showarrow=True, arrowhead=1)

        # add max return
        fig.add_trace(go.Scatter(x=[vol_arr[max_return_index]], y=[ret_arr[max_return_index]], mode='markers', marker=dict(size=15, color='green')))
        fig.add_annotation(text="Max Return", x=vol_arr[max_return_index], y=ret_arr[max_return_index], showarrow=True, arrowhead=1)

        # add min volatility
        fig.add_trace(go.Scatter(x=[vol_arr[min_volatility_index]], y=[ret_arr[min_volatility_index]], mode='markers', marker=dict(size=15, color='blue')))
        fig.add_annotation(text="Min Volatility", x=vol_arr[min_volatility_index], y=ret_arr[min_volatility_index], showarrow=True, arrowhead=1)

        # set layout
        fig.update_layout(title='Efficient Frontier', xaxis_title='Volatility', yaxis_title='Return')
    except Exception as e:
        error_message(e)

    try:

        # plot efficient frontier
        fig = go.Figure()

        # add efficient frontier
        fig.add_trace(go.Scatter(x=results[1], y=results[0], mode='markers', marker=dict(size=10, color=results[2], colorscale='Viridis', showscale=True)))

        # add max sharpe ratio
        fig.add_trace(go.Scatter(x=[vol_arr[max_sharpe_ratio_index]], y=[ret_arr[max_sharpe_ratio_index]], mode='markers', marker=dict(size=15, color='red')))
        fig.add_annotation(text="Max Sharpe Ratio", x=vol_arr[max_sharpe_ratio_index], y=ret_arr[max_sharpe_ratio_index], showarrow=True, arrowhead=1)

        # add max return
        fig.add_trace(go.Scatter(x=[vol_arr[max_return_index]], y=[ret_arr[max_return_index]], mode='markers', marker=dict(size=15, color='green')))
        fig.add_annotation(text="Max Return", x=vol_arr[max_return_index], y=ret_arr[max_return_index], showarrow=True, arrowhead=1)

        # add min volatility
        fig.add_trace(go.Scatter(x=[vol_arr[min_volatility_index]], y=[ret_arr[min_volatility_index]], mode='markers', marker=dict(size=15, color='blue')))
        fig.add_annotation(text="Min Volatility", x=vol_arr[min_volatility_index], y=ret_arr[min_volatility_index], showarrow=True, arrowhead=1)

        # set layout
        fig.update_layout(title='Efficient Frontier', xaxis_title='Volatility', yaxis_title='Return')

    except Exception as e:
        error_message(e)

    return fig
