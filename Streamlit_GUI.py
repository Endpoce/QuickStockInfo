import streamlit as st
import yfinance as yf
import pandas as pd
import openai
from Company_Info_Web_Scraper import get_company_info, get_wiki_info, summarize_article
from GetArticles import get_MW_Articles
from Stock_Analyzer import *
import os
from dotenv import load_dotenv
import time
from Sentiment import *

load_dotenv()

yf.pdr_override()

# set openai api key
openai.api_key = os.environ.get('API_KEY')

# set dates
start_date = pd.to_datetime("2020-01-01")
end_date = datetime.today().strftime('%Y-%m-%d')


# Page config (Title at top and icon at top )
st.set_page_config(page_title="Tweet Analysis", page_icon="chart_with_upwards_trend",
                   layout='wide', initial_sidebar_state="expanded")


def get_stock_data(symbol, start_date, end_date):
    ticker = yf.download(symbol, start_date, end_date)

    # save stock data to csv
    file = ticker.to_csv(symbol + '_Price_Data.csv')

    return file


def main():

    # Title
    st.title("Quick Stock Info")

    col1, col2, col3 = st.columns((1, 2, 1))

    # Sidebar
    st.sidebar.header("User Input")
    ticker_symbol = st.sidebar.text_input("Enter Ticker Symbol:").upper()
    start_date = st.sidebar.date_input(
        "Start date", value=pd.to_datetime("2020-01-01"))
    end_date = st.sidebar.date_input(
        "End date", value=pd.to_datetime(datetime.today().strftime('%Y-%m-%d')))
    fetch_button = st.sidebar.button("Get Stock Data")

    # Main Page
    if fetch_button:

        # download and save stock data
        stock_data = get_stock_data(ticker_symbol, start_date, end_date)

        # Get company info and stock data
        info = get_company_info(ticker_symbol)

        col1.write(info['name'])
        col1.write(info['sector'])
        col1.write(info['industry'])
        col1.write(info['summary'])

        # get wiki info
        wiki_url = get_wiki_info(ticker_symbol)
        col1.write("Wikipedia URL:")
        col1.write(wiki_url)

        # read stock price data from csv
        filename = ticker_symbol + '_Price_Data.csv'
        df = pd.read_csv(filename)

        # plot price stock data
        col2.pyplot(plot_stock_with_moving_averages_from_csv(filename))

        # analyze stock data
        # time.sleep(5)
        # col2.markdown(analyze_stock(filename))
        col2.write("Placeholder text for stock analysis")
        # time.sleep(5)

        # display tweets
        col3.write("Tweets:")
        tweets = get_tweets(ticker_symbol, 5)

        # display tweets
        for tweet in tweets:
            col3.write(tweet)
            # col3.write(tweet)

        # get articles
        articles = get_MW_Articles(ticker_symbol, 5)

        # display articles
        st.write("Articles:")

        # display articles
        for article in articles:
            st.write(article['title'])
            st.write(article['url'])
            st.markdown(summarize_article(article))
            time.sleep(5)


if __name__ == "__main__":
    main()
