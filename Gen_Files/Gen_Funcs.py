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
        # calculate portfolio returns and volatility
        port_returns = []
        port_volatility = []
        stock_weights = []

        # generate random weights for the stocks
        for portfolio in range(num_portfolios):
            weights = np.random.random(len(stock_data.columns[1:]))
            weights /= np.sum(weights)
            stock_weights.append(weights)

            # calculate portfolio returns and volatility
            returns = np.dot(weights, expected_returns.T)
            volatility = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights.T)))

            port_returns.append(returns)
            port_volatility.append(volatility)

        # create a dictionary to store the portfolio returns and volatility
        portfolio = {'Returns': port_returns, 'Volatility': port_volatility}

        # add the stock weights to the dictionary
        for counter, symbol in enumerate(stock_data.columns[1:]):
            portfolio[symbol + ' Weight'] = [weight[counter] for weight in stock_weights]

        # create a DataFrame from the dictionary
        df = pd.DataFrame(portfolio)

        # calculate the Sharpe ratio
        risk_free_rate = 0.0178

        df['Sharpe Ratio'] = (df['Returns'] - risk_free_rate) / df['Volatility']

        # find the minimum volatility and maximum Sharpe ratio
        min_volatility_index = df['Volatility'].idxmin()
        max_sharpe_ratio_index = df['Sharpe Ratio'].idxmax().all()
        max_return_index = df['Returns'].idxmax()

        # get the minimum volatility and maximum Sharpe ratio
        min_volatility = df['Volatility'][min_volatility_index]

        max_sharpe_ratio = df['Sharpe Ratio'][max_sharpe_ratio_index]
        max_return = df['Returns'][max_return_index]

        return df, min_volatility_index, max_sharpe_ratio_index, max_return_index, min_volatility, max_sharpe_ratio, max_return        



    except Exception as e:
        error_message(e)

    try:

        # plot the efficient frontier
        fig = go.Figure()

        # add scatter plot for each portfolio
        fig.add_trace(go.Scatter(
            x=df['Volatility'],
            y=df['Returns'],
            mode='markers',
            marker=dict(
                size=8,
                color=df['Sharpe Ratio'],
                colorscale='Viridis',
                showscale=True
            ),
            text=df.columns[1:],
            hovertemplate=
            '<b>Stock</b>: %{text}<br>' +
            '<b>Volatility</b>: %{x}<br>' +
            '<b>Returns</b>: %{y}<br>' +
            '<b>Sharpe Ratio</b>: %{marker.color}<br>',
        ))

        # add minimum volatility portfolio
        fig.add_trace(go.Scatter(
            x=[df['Volatility'][min_volatility_index]],
            y=[df['Returns'][min_volatility_index]],
            mode='markers',
            marker=dict(
                size=12,
                color='red',
                symbol='star'
            ),
            name='Minimum Volatility',
            text=df.columns[1:][min_volatility_index],
            hovertemplate=
            '<b>Stock</b>: %{text}<br>' +
            '<b>Volatility</b>: %{x}<br>' +
            '<b>Returns</b>: %{y}<br>' +
            '<b>Sharpe Ratio</b>: Minimum Volatility<br>',
        ))

        # add maximum Sharpe ratio portfolio
        fig.add_trace(go.Scatter(
            x=[df['Volatility'][max_sharpe_ratio_index]],
            y=[df['Returns'][max_sharpe_ratio_index]],
            mode='markers',
            marker=dict(
                size=12,
                color='green',
                symbol='star'
            ),
            name='Maximum Sharpe Ratio',
            text=df.columns[1:][max_sharpe_ratio_index],
            hovertemplate=
            '<b>Stock</b>: %{text}<br>' +
            '<b>Volatility</b>: %{x}<br>' +
            '<b>Returns</b>: %{y}<br>' +
            '<b>Sharpe Ratio</b>: Maximum Sharpe Ratio<br>',
        ))

        # add maximum return portfolio
        fig.add_trace(go.Scatter(
            x=[df['Volatility'][max_return_index]],
            y=[df['Returns'][max_return_index]],
            mode='markers',
            marker=dict(
                size=12,
                color='blue',
                symbol='star'
            ),
            name='Maximum Return',
            text=df.columns[1:][max_return_index],
            hovertemplate=
            '<b>Stock</b>: %{text}<br>' +
            '<b>Volatility</b>: %{x}<br>' +
            '<b>Returns</b>: %{y}<br>' +
            '<b>Sharpe Ratio</b>: Maximum Return<br>',
        ))

        # set plot layout
        fig.update_layout(
            title='Efficient Frontier',
            xaxis=dict(title='Volatility'),
            yaxis=dict(title='Returns'),
            legend=dict(
                x=0.7,
                y=1,
                traceorder='normal',
                font=dict(family='sans-serif', size=12, color='black'),
                bgcolor='rgba(0,0,0,0)'
            ),
            hovermode='closest'
        )

        fig.show()
    except Exception as e:
        error_message(e)

    return fig
