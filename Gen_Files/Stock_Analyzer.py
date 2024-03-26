import os
from dotenv import load_dotenv
import yfinance as yf
import pandas as pd
from datetime import datetime
import sys

import plotly.graph_objects as go
import openai
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import google.generativeai as gai
import streamlit as st
import vertexai
from vertexai.generative_models import GenerativeModel, Part

load_dotenv()

# get stock info and feed to it to google ai, get response
def google_summary(ticker, hist):

    # Get the latest closing price
    latest_close = hist['Close'].iloc[-1]

    # Get the highest and lowest closing prices
    high_close = hist['Close'].max()
    low_close = hist['Close'].min()

    # Calculate the average closing price
    avg_close = hist['Close'].mean()

    stock_data = {}

    # Get basic info
    info = ticker.info


    # Technical Indicators
    stock_data['P/E Ratio'] = info.get('trailingPE')
    stock_data['P/B Ratio'] = info.get('priceToBook')
    stock_data['Dividend Yield'] = info.get('dividendYield')
    stock_data['EPS'] = info.get('trailingEps')
    stock_data['D/E Ratio'] = info.get('debtToEquity')
    stock_data['Beta'] = info.get('beta')
    stock_data['Market Cap'] = info.get('marketCap')
    stock_data['Shares Outstanding'] = info.get('sharesOutstanding')
    stock_data['Return on Equity'] = info.get('returnOnEquity')
    stock_data['Return on Assets'] = info.get('returnOnAssets')
    stock_data['Return on Capital'] = info.get('returnOnCapital')
    stock_data['Profit Margin'] = info.get('profitMargins')
    stock_data['Operating Margin'] = info.get('operatingMargins')
    stock_data['Gross Profit'] = info.get('grossProfits')
    stock_data['Operating Cash Flow'] = info.get('operatingCashflow')
    stock_data['Leveraged Free Cash Flow'] = info.get('freeCashflow')
    stock_data['Revenue'] = info.get('revenue')
    stock_data['Revenue Per Share'] = info.get('revenuePerShare')
    stock_data['Revenue Growth'] = info.get('revenueGrowth')
    stock_data['Gross Profit Growth'] = info.get('grossMargins')
    stock_data['EBITDA'] = info.get('ebitda')
    stock_data['EBITDA Margin'] = info.get('ebitdaMargins')
    stock_data['EBITDA Growth'] = info.get('ebitdaGrowth')
    stock_data['EPS Growth'] = info.get('earningsGrowth')
    stock_data['EPS Diluted Growth'] = info.get('earningsQuarterlyGrowth')
    stock_data['EPS Diluted'] = info.get('trailingEps')

    # Fundamental Indicators
    stock_data['52 Week High'] = info.get('fiftyTwoWeekHigh')
    stock_data['52 Week Low'] = info.get('fiftyTwoWeekLow')

    # Historical Market Data
    stock_data['Average Open'] = hist['Open'].mean()
    stock_data['Average High'] = hist['High'].mean()
    stock_data['Average Low'] = hist['Low'].mean()
    stock_data['Average Close'] = hist['Close'].mean()
    stock_data['Average Volume'] = hist['Volume'].mean()

    # Moving Averages
    stock_data['10 Day Moving Average'] = hist['Close'].rolling(
        window=10).mean().iloc[-1]
    stock_data['100 Day Moving Average'] = hist['Close'].rolling(
        window=100).mean().iloc[-1]

    # Create a summary of the stock data
    summary = f"The stock had its highest closing price of ${high_close} and its lowest of ${low_close}. "
    summary += f"The average closing price was ${avg_close:.2f}. "
    summary += f"As of {datetime.now}, the closing price was ${latest_close}."
    summary += f"Here are some other key data points about the stock: {stock_data}"

    # Construct the ChatGPT prompt
    prompt = f"{summary} What could these figures suggest about the stock's performance and potential future trends?"

    gai.configure(api_key=os.environ['google_api_key'])

    # Generate a response using the google gemini model
    model = gai.GenerativeModel('gemini-pro')

    response = model.generate_content(prompt)

    return response.text

# plot from csv
def plot_stock_with_moving_averages_from_csv(filename, short_window=15, long_window=100):
    # Read data from CSV file
    df = pd.read_csv(filename, parse_dates=['Date'], index_col='Date')

    # Calculate short and long moving averages
    df['ShortMA'] = df['Close'].rolling(window=short_window).mean()
    df['LongMA'] = df['Close'].rolling(window=long_window).mean()

    # Create a column for the difference between the short and long MAs
    df['Diff'] = df['ShortMA'] - df['LongMA']

    # Identify crossover points
    df['ShortCrossesAboveLong'] = (
        (df['Diff'] > 0) & (df['Diff'].shift(1) < 0))
    df['LongCrossesAboveShort'] = (
        (df['Diff'] < 0) & (df['Diff'].shift(1) > 0))

    # Create plot
    fig, ax = plt.subplots(figsize=(12, 8))
    plt.grid(True)
    plt.plot(df['Close'], label='Close Price', color='blue')
    plt.plot(df['ShortMA'], label=f'{short_window} Day MA', color='red')
    plt.plot(df['LongMA'], label=f'{long_window} Day MA', color='green')

    # Add arrows for crossover points
    for i in df[df['ShortCrossesAboveLong']].index:
        plt.annotate('', xy=(i, df['ShortMA'][i]), xytext=(i, df['ShortMA'][i] - 5),
                     arrowprops={'arrowstyle': '->', 'color': 'purple'})  # green for ShortMA crosses above LongMA

    for i in df[df['LongCrossesAboveShort']].index:
        plt.annotate('', xy=(i, df['LongMA'][i]), xytext=(i, df['LongMA'][i] + 5),
                     arrowprops={'arrowstyle': '->', 'color': 'purple'})  # red for LongMA crosses above ShortMA

    plt.title(
        f'Close Price with {short_window}-Day & {long_window}-Day Moving Averages')
    plt.xlabel('Date')
    plt.ylabel('Close Price ($)')
    plt.legend(loc=2)

    # Show plot
    # plt.show()

    return fig

# plot stock data on an interactive chart
def plot_stock_with_interactive_chart(ticker, hist, short_window=15, long_window=100):
    # Read data from CSV file
    df = hist
    

    # Calculate short and long moving averages
    df['ShortMA'] = df['Close'].rolling(window=short_window).mean()
    df['LongMA'] = df['Close'].rolling(window=long_window).mean()

    # Create a column for the difference between the short and long MAs
    df['Diff'] = df['ShortMA'] - df['LongMA']

    # Identify crossover points
    df['ShortCrossesAboveLong'] = (
        (df['Diff'] > 0) & (df['Diff'].shift(1) < 0))
    df['LongCrossesAboveShort'] = (
        (df['Diff'] < 0) & (df['Diff'].shift(1) > 0))

    # Create plot
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df.index, y=df['Close'], mode='lines', name='Close Price'))
    fig.add_trace(go.Scatter(
        x=df.index, y=df['ShortMA'], mode='lines', name=f'{short_window} Day MA'))
    fig.add_trace(go.Scatter(
        x=df.index, y=df['LongMA'], mode='lines', name=f'{long_window} Day MA'))

    # Add arrows for crossover points
    for i in df[df['ShortCrossesAboveLong']].index:
        fig.add_annotation(x=i, y=df['ShortMA'][i], text='', arrowhead=1, arrowsize=1, arrowwidth=2, arrowcolor='green')

    for i in df[df['LongCrossesAboveShort']].index:
        fig.add_annotation(x=i, y=df['LongMA'][i], text='', arrowhead=1, arrowsize=1, arrowwidth=2, arrowcolor='red')

    fig.update_layout(title=f'Close Price with {short_window}-Day & {long_window}-Day Moving Averages',
                      xaxis_title='Date', yaxis_title='Close Price ($)', autosize=False, width=1200, height=800, plot_bgcolor='white')

    st.plotly_chart(fig, use_container_width=True)

    return fig
