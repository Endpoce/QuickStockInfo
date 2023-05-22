import streamlit as st
import yfinance as yf
import pandas as pd
import openai
from Company_Info_Web_Scraper import get_company_info, get_wiki_info, summarize_article
from GetArticles import get_MW_Articles
from Stock_Analyzer import *
import config


yf.pdr_override()

# set openai api key
openai.api_key = config.API_KEY


def get_stock_data(symbol, start_date, end_date):
    ticker = yf.download(symbol, start_date, end_date)

    # save stock data to csv
    file = ticker.to_csv("Price_data\\"+symbol + '_Price_Data.csv')

    return file


def main():
    st.title("Stock Information App")

    # Sidebar
    st.sidebar.header("User Input")
    ticker_symbol = st.sidebar.text_input("Enter Ticker Symbol:").upper()
    start_date = st.sidebar.date_input(
        "Start date", value=pd.to_datetime("2020-01-01"))
    end_date = st.sidebar.date_input(
        "End date", value=pd.to_datetime("2021-12-31"))
    fetch_button = st.sidebar.button("Get Stock Data")

    # Main Page
    if fetch_button:

        # download and save stock data
        stock_data = get_stock_data(ticker_symbol, start_date, end_date)

        # display stock data
        st.write(f"Displaying data for {ticker_symbol}:")

        # Get company info and stock data
        info = get_company_info(ticker_symbol)

        st.write(info['name'])
        st.write(info['sector'])
        st.write(info['industry'])
        st.write(info['summary'])

        # get wiki info
        wiki_url = get_wiki_info(ticker_symbol)
        st.write(wiki_url)

        # read stock price data from csv
        filename = "Price_Data\\" + ticker_symbol + '_Price_Data.csv'
        df = pd.read_csv(filename)

        # plot price stock data
        st.pyplot(plot_stock_with_moving_averages_from_csv(filename))

        # analyze stock data
        st.write(analyze_stock(filename))

        # get articles
        articles = get_MW_Articles(ticker_symbol)

        # display articles
        for article in articles:
            st.write(article['title'])
            st.write(article['url'])
            st.write(summarize_article(article))


if __name__ == "__main__":
    main()
