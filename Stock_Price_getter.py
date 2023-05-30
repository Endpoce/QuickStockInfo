# %%
import numpy as np
import pandas as pd
import datetime
import yfinance as yf
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

yf.pdr_override()

# %%


def save_stock_data(symbol, filename):
    # Get the date 3 years ago from today
    end_date = datetime.today()
    start_date = end_date - timedelta(days=3*365)

    # Format the dates
    end_date = end_date.strftime('%Y-%m-%d')
    start_date = start_date.strftime('%Y-%m-%d')

    # Download the data
    data = yf.download(symbol, start=start_date, end=end_date)

    # Save the data to a CSV file
    data.to_csv("Stock_Price_Info\\" + filename)


# Use the function
# save_stock_data('AAPL', 'AAPL_3_years.csv')
