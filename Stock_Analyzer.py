# %%
import pandas as pd
import openai
from datetime import datetime
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv
import yfinance as yf

load_dotenv()

# %%
# Set up your OpenAI API credentials
openai.api_key = os.environ.get('API_KEY')


def get_stock_data(symbol, start_date, end_date):
    ticker = yf.Ticker(symbol)

    info = ticker.info

    hist = ticker.history(period="1d", start=start_date, end=end_date)

    # save stock data to csv
    file = hist.to_csv(symbol + '_Price_Data.csv')

    return ticker, info, hist, file


def analyze_stock(filename, ticker):

    # read and Load the CSV data into a DataFrame
    df = pd.read_csv(filename)

    # Ensure the data is sorted by date
    df = df.sort_values('Date')

    # # Get the latest date in the dataset
    # latest_date = df['Date'].iloc[-1]
    # # assuming the date is in this format
    # latest_date = datetime.strptime(latest_date, '%Y-%m-%d')

    # Get the latest closing price
    latest_close = df['Close'].iloc[-1]

    # Get the highest and lowest closing prices
    high_close = df['Close'].max()
    low_close = df['Close'].min()

    # Calculate the average closing price
    avg_close = df['Close'].mean()

    stock_data = {}

    # Get basic info
    info = ticker.info

    # Get historical market data
    hist = ticker.history(period="5d")

    # Fundamental Indicators
    stock_data['P/E Ratio'] = info.get('trailingPE')
    stock_data['P/B Ratio'] = info.get('priceToBook')
    stock_data['Dividend Yield'] = info.get('dividendYield')
    stock_data['EPS'] = info.get('trailingEps')
    stock_data['D/E Ratio'] = info.get('debtToEquity')

    # Technical Indicators
    stock_data['52 Week High'] = info.get('fiftyTwoWeekHigh')
    stock_data['52 Week Low'] = info.get('fiftyTwoWeekLow')

    # Volume and Moving Averages might need to be calculated from the historical data
    # Here's an example for volume:
    stock_data['Volume'] = hist['Volume'].mean()

    # For moving averages, you'll need to implement it yourself. Here's a simple example for a 5 day moving average:
    stock_data['5 Day Moving Average'] = hist['Close'].rolling(
        window=5).mean().iloc[-1]

    # Create a summary of the stock data
    summary = f"The stock had its highest closing price of ${high_close} and its lowest of ${low_close}. "
    summary += f"The average closing price was ${avg_close:.2f}. "
    summary += f"As of {datetime.now}, the closing price was ${latest_close}."
    summary += f"Here are some other key data points about the stock: {stock_data}"

    # Construct the ChatGPT prompt
    prompt = f"{summary} What could these figures suggest about the stock's performance and potential future trends?"

    # Use the OpenAI API to generate a response
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are analyzing a stock."},
                  {"role": "user", "content": prompt}],
        max_tokens=500
    )

    return response.choices[0].text.strip()


# Use the function
# print(analyze_stock('C:\\Users\\Aidan\\Desktop\\USB\\Projects\\Python\\MoneyBots\\2PREPARE_Basic_info_Getter\\Stock_Price_Info\\AAPL_3_years.csv'))

# %%
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
                     arrowprops={'arrowstyle': '->', 'color': 'green'})  # green for ShortMA crosses above LongMA

    for i in df[df['LongCrossesAboveShort']].index:
        plt.annotate('', xy=(i, df['LongMA'][i]), xytext=(i, df['LongMA'][i] + 5),
                     arrowprops={'arrowstyle': '->', 'color': 'red'})  # red for LongMA crosses above ShortMA

    plt.title(
        f'Close Price with {short_window}-Day & {long_window}-Day Moving Averages')
    plt.xlabel('Date')
    plt.ylabel('Close Price ($)')
    plt.legend(loc=2)

    # Show plot
    # plt.show()

    return fig


# Use the function
# plot_stock_with_moving_averages_from_csv(
#     'C:\\Users\\Aidan\\Desktop\\USB\\Projects\\Python\\MoneyBots\\2PREPARE_Basic_info_Getter\\Stock_Price_Info\\AAPL_3_years.csv')
