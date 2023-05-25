# %%
import pandas as pd
import openai
from datetime import datetime
import matplotlib.pyplot as plt
import yfinance as yf
from Company_Info_Web_Scraper import *

# %%
# Set up your OpenAI API credentials
openai.api_key = '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'


def get_stock_indicators(stock, start_date, end_date):
    # Fetch the ticker data
    ticker_data = yf.Ticker(stock)

    # Fetch the info dictionary
    info = ticker_data.info

    # Fetch the history data
    history = ticker_data.history(start=start_date, end=end_date)

    # read and Load the CSV data into a DataFrame
    filename = f'Price_Data\\{stock}_Price_Data.csv'
    df = pd.read_csv(filename)

    # Ensure the data is sorted by date
    df = df.sort_values('Date')

    # Get the highest and lowest closing prices
    high_close = df['Close'].max()
    low_close = df['Close'].min()

    # Calculate the average closing price
    avg_close = df['Close'].mean()

    # Calculate some indicators
    indicators = {
        "Current Price": info.get('currentPrice'),
        "Average Price": avg_close,
        "Highest Price": high_close,
        "Lowest Price": low_close,
        "Market Cap": info.get('marketCap'),
        "Enterprise Value": info.get('enterpriseValue'),
        "Price-to-Sales (P/S) Ratio": info.get('priceToSalesTrailing12Months'),
        "Price-to-Earnings (P/E) Ratio": info.get('trailingPE'),
        "Price-to-Book (P/B) Ratio": info.get('priceToBook'),
        "Debt-to-Equity (D/E) Ratio": info.get('debtToEquity'),
        "Return on Equity (ROE)": info.get('returnOnEquity'),
        "Earnings Per Share (EPS)": info.get('trailingEps'),
        "Dividend Yield": info.get('dividendYield'),
        "52 Week High": info.get('fiftyTwoWeekHigh'),
        "52 Week Low": info.get('fiftyTwoWeekLow'),
        "50 Day Moving Average": info.get('fiftyDayAverage'),
        "200 Day Moving Average": info.get('twoHundredDayAverage'),
        "Beta": info.get('beta'),
        "Volume": history['Volume'].tolist()[-1],  # Get the latest volume
    }

    return indicators


def summarize_indicators(indicators):
    # Convert the indicators dictionary to a string
    indicators_str = "\n".join(
        f"{key}: {value}" for key, value in indicators.items())

    # Prepare the prompt for the GPT-3 model
    prompt = f"I have some stock indicators:\n\n{indicators_str}\n\nWhat does this information tell you about the company's past performance and future prospects?"

    # Use the GPT-3 model to generate a summary
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        temperature=0.3,
        max_tokens=100
    )

    return response.choices[0].text.strip()


def analyze_stock(symbol, start_date, end_date):

    # get indicators
    indicators = get_stock_indicators(symbol, start_date, end_date)

    # Convert the indicators dictionary to a string
    indicators_str = "\n".join(
        f"{key}: {value}" for key, value in indicators.items())

    # Prepare the messages for the GPT-3.5 Turbo model
    messages = [
        {"role": "system", "content": "You are a helpful stock analysis assistant."},
        {"role": "user", "content": f"I have some stock indicators:\n\n{indicators_str}\n\nWhat does this information tell you about past performance and future prospects?"}
    ]

    # Use the GPT-3.5 Turbo model to generate a response
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=300
    )

    return response['choices'][0]['message']['content'].strip()


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
    fig, ax = plt.subplots(figsize=(8, 6))  # Adjust the figure size as desired
    plt.grid(True)
    plt.plot(df['Close'], label='Close Price', color='blue')
    plt.plot(df['ShortMA'], label=f'{short_window} Day MA', color='red')
    plt.plot(df['LongMA'], label=f'{long_window} Day MA', color='green')

    # Add arrows for crossover points
    for i in df[df['ShortCrossesAboveLong']].index:
        plt.annotate('', xy=(i, df['ShortMA'][i]), xytext=(i, df['ShortMA'][i] - 5),
                     arrowprops={'arrowstyle': '->', 'color': 'green'})  # green for ShortMA crosses above LongMA

    for i in df[df['LongCrossesAboveShort']].index:
        plt.annotate('', xy=(i, df['LongMA'][i]), xytext=(i, df['LongMA'][i] + 5),
                     arrowprops={'arrowstyle': '->', 'color': 'red'})  # red for LongMA crosses above ShortMA

    plt.title(
        f'Close Price with {short_window}-Day & {long_window}-Day Moving Averages')
    plt.xlabel('Date')
    plt.ylabel('Close Price ($)')
    plt.legend(loc=2)

    # Save plot as image
    fig.savefig('plot.png', dpi=300, bbox_inches='tight')

    return fig
