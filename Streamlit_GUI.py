from datetime import timedelta
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
import tweepy
import plotly.graph_objects as go

load_dotenv()

yf.pdr_override()

# set openai api key
openai.api_key = os.environ.get('API_KEY')


auth = tweepy.OAuth2BearerHandler(os.environ.get("Bearer_token"))
api = tweepy.API(auth)

# set dates
start_date = pd.to_datetime("2020-01-01")
end_date = datetime.today().strftime('%Y-%m-%d')


# Page config (Title at top and icon at top )
st.set_page_config(page_title="Tweet Analysis", page_icon="chart_with_upwards_trend",
                   layout='wide', initial_sidebar_state="expanded")


def get_estimated_return(info, ticker):

    if 'trailingAnnualDividendYield' in info:
        dividend = ticker.info['trailingAnnualDividendYield']
    elif 'dividendYield' in info:
        dividend = ticker.info['dividendYield']
    else:
        dividend = 0

    one_year_ago_date = (
        datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    history = ticker.history(start=one_year_ago_date)

    # Get the first available price, which should be the price from approximately one year ago
    # Assumes that the stock market was open on the 'one_year_ago_date',
    # you may want to handle cases where it was not, such as weekends and holidays.
    price_one_year_ago = history.iloc[0]['Close']
    current_price = history.iloc[-1]['Close']

    estimated_return = round(
        ((current_price - price_one_year_ago + dividend)/price_one_year_ago) * 100, 2)

    return estimated_return


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
        ticker, info, hist, file = get_stock_data(
            ticker_symbol, start_date, end_date)

        # get company info
        info = ticker.info

        # info to display
        to_display = ['longName', 'sector', 'industry',
                      'longBusinessSummary', 'symbol', 'legalType', 'category'
                      ]

        # get sector and industry
        for key in to_display:
            if key not in info:
                info[key] = "N/A"

        sector = info['sector'] != "N/A"
        industry = info['industry'] != "N/A"
        legalType = info['legalType'] != "N/A"
        category = info['category'] != "N/A"

        with col1.container():

            col1.write("Company Info:")

            col1.write(info['longName'])

            if sector:
                col1.write("Sector: "+info['sector'])

            if industry:
                col1.write("Industry: " + info['industry'])

            if legalType:
                col1.write("Legal Type: " + info['legalType'])

            if category:
                col1.write("Category: " + info['category'])

            col1.write(info['longBusinessSummary'])

            # get wiki info
            wiki_url = get_wiki_info(info['longName'])
            col1.write("Wikipedia URL:")
            col1.write(wiki_url)

        # read stock price data from csv
        filename = ticker_symbol + '_Price_Data.csv'
        df = pd.read_csv(filename)

        with col2.container():
            # plot price stock data
            col2.plotly_chart(plot_stock_with_interactive_chart(
                filename), use_container_width=True)

        with col3.container():

            # display finance info
            col3.subheader("Info:")

            # display current price
            col3.write("Current Price: " + str(hist['Close'].iloc[-1]))

            # display estimated 52 return
            col3.write("Estimated 52 Week Return: " +
                       str(get_estimated_return(info, ticker)) + "%")

            # display ytd return
            col3.write("Estimated YTD Return: " +
                       str(info['ytdReturn']*100) + "%")

            # list of indicators I don't want to display
            not_displayed = ['longName', 'sector', 'category', 'currentPrice', 'regularMarketPrice',
                             'industry', 'longBusinessSummary', 'symbol', 'legalType',
                             'underlyingSymbol', 'underlyingExchangeSymbol', 'headquartersCity',
                             'headquartersCountry', 'quoteType', 'city', 'state',
                             'country', 'website', 'address1', 'address2', 'zip', 'phone',
                             'numberOfEmployees', 'fullTimeEmployees', 'averageDailyVolume10Day',
                             'averageVolume10days', 'boardRiskGovernanceExperience', 'boardRisk',
                             'currency', 'firstTradeDateEpochUtc', 'gmtOffSetMilliseconds',
                             'governanceEpochDate', 'impliedSharesOutstanding', 'zip', 'uuid',
                             'maxAge', 'logo_url', 'compensationAsOfEpochDate', 'compensationRisk',
                             'compensationRank', 'compensationScore', 'compensationDescription',
                             'compensationCalendarDate', 'compensationPeerGroup', 'compensationPeerGroupDescription',
                             'messageBoardId', 'maxAge', 'logo_url', 'compensationAsOfEpochDate',
                             'navPrice', 'priceHint', 'shortName', 'exchangeTimezoneName', 'trailingPegRatio',
                             'twoHundredDayAverage', 'twoHundredDayAverageChange', 'twoHundredDayAverageChangePercent',
                             'yield', 'ytdReturn', 'trailingAnnualDividendRate', 'trailingAnnualDividendYield',
                             'SandP52WeekChange'
                             ]

            indicators = [
                indicator for indicator in info if indicator not in not_displayed]
            sorted_indicators = sorted(indicators)

            for indicator in sorted_indicators:
                col3.write(indicator + ": " + str(info[indicator]))

        with col2.container():

            # analyze stock data
            # col2.write(analyze_stock(filename, ticker))
            col2.write("Placeholder text for stock analysis")
            time.sleep(5)

            # get articles
            articles = get_MW_Articles(ticker_symbol, 5)

            # display articles
            col2.write("Articles:")

            time.sleep(5)

            # display articles
            for article in articles:
                col2.write(article['title'])
                col2.write(article['url'])
                col2.markdown(summarize_article(article))
                time.sleep(5)
            col2.write("Placeholder text for article analysis")


if __name__ == "__main__":
    main()
