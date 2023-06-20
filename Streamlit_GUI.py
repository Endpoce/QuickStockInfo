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
    if 'currentPrice' in ticker.info:
        current_price = ticker.info['currentPrice']
    elif 'regularMarketPrice' in ticker.info:
        current_price = ticker.info['regularMarketPrice']
    else:
        current_price = None

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

        # get sector and industry
        if 'sector' in info:
            sector = True
        else:
            sector = False

        if 'industry' in info:
            industry = True
        else:
            industry = False

        with col1.container():
            col1.write("Company Info:")
            col1.write(info['longName'])
            if sector:
                col1.write("Sector: "+info['sector'])
            if industry:
                col1.write("Industry: " + info['industry'])
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
            if 'regularMarketPrice' or 'currentPrice' in info:
                col3.subheader("Info:")
                if 'regularMarketPrice' in info:
                    col3.write("Current Price: " +
                               str(info['regularMarketPrice']))
                elif 'currentPrice' in info:
                    col3.write("Current Price: " + str(info['currentPrice']))
                col3.write("Estimated 52 week return: " +
                           str(get_estimated_return(info, ticker)))
                col3.write("Market Cap: " + str(info['marketCap']))
                col3.write("Enterprise Value: " + str(info['enterpriseValue']))
                col3.write("Trailing P/E: " + str(info['trailingPE']))
                col3.write("Forward P/E: " + str(info['forwardPE']))
                col3.write("PEG Ratio: " + str(info['pegRatio']))
                col3.write("Price to Sales Ratio: " +
                           str(info['priceToSalesTrailing12Months']))
                col3.write("Price to Book Ratio: " + str(info['priceToBook']))
                col3.write("Enterprise Value to Revenue: " +
                           str(info['enterpriseToRevenue']))
                col3.write("Enterprise Value to EBITDA: " +
                           str(info['enterpriseToEbitda']))
                col3.write("Profit Margins: " + str(info['profitMargins']))
                col3.write("Forward EPS: " + str(info['forwardEps']))
                col3.write("Beta: " + str(info['beta']))
                col3.write("52 Week High: " + str(info['fiftyTwoWeekHigh']))
                col3.write("52 Week Low: " + str(info['fiftyTwoWeekLow']))
                col3.write("50 Day Moving Average: " +
                           str(info['fiftyDayAverage']))
                col3.write("200 Day Moving Average: " +
                           str(info['twoHundredDayAverage']))
                col3.write("Shares Outstanding: " +
                           str(info['sharesOutstanding']))
                col3.write("Shares Short: " + str(info['sharesShort']))
                col3.write("Shares Short Prior Month: " +
                           str(info['sharesShortPriorMonth']))
                col3.write("Short Ratio: " + str(info['shortRatio']))
                col3.write("Short Percent Outstanding: " +
                           str(info['shortPercentOfFloat']))
                # col3.write("Short Percent of Shares Outstanding: " +
                #            str(info['shortPercentOfSharesOutstanding']))
                col3.write("Shares Short (Prior Month Date): " +
                           str(info['sharesShortPriorMonth']))
                col3.write("Shares Short (Prior Month): " +
                           str(info['sharesShortPriorMonth']))
                # col3.write("Forward Annual Dividend Rate: " +
                #            str(info['forwardAnnualDividendRate']))
                # col3.write("Forward Annual Dividend Yield: " +
                #            str(info['forwardAnnualDividendYield']))
                col3.write("Trailing Annual Dividend Rate: " +
                           str(info['trailingAnnualDividendRate']))
                if 'trailingAnnualDividendYield' in info:
                    col3.write("Trailing Annual Dividend Yield: " +
                               str(info['trailingAnnualDividendYield']))
                col3.write("5 Year Average Dividend Yield: " +
                           str(info['fiveYearAvgDividendYield']))
                col3.write("Payout Ratio: " + str(info['payoutRatio']))
                # col3.write("Dividend Date: " + str(info['dividendDate']))
                # col3.write("Ex Dividend Date: " +
                #            str(datetime.date(info['exDividendDate'])))
                col3.write("Last Split Factor: " +
                           str(info['lastSplitFactor']))
                # col3.write("Last Split Date: " +
                #    str(datetime.date(info['lastSplitDate'])))

            # display tweets
            # st.write("Tweets:")
            # tweets = get_tweets(ticker_symbol, 5)

            # display tweets
            # display tweet text
            # for tweet in tweets:

            #     with st.container():

            #         create_tweet_styles()

            #         # Markdown
            #         st.image(tweet["profile_pic"])
            #         st.markdown('Username: ' +
            #                     tweet["screen_name"], unsafe_allow_html=False)
            #         st.write(f"Number of likes: {tweet['num_likes']}")
            #         # st.markdown(tweet, unsafe_allow_html=False)

            #         # Text
            #         st.write("Sentiment: " +
            #                  get_tweet_sentiment(tweet["text"]))
            #         st.markdown(tweet["text"])
            #         st.write("---")
            #         time.sleep(5)
            # else:
            #     st.write("No tweets found")
        with col2.container():

            # analyze stock data
            time.sleep(5)
            # col2.write(analyze_stock(filename, ticker))
            col2.write("Placeholder text for stock analysis")

            # get articles

            articles = get_MW_Articles(ticker_symbol, 5)

            # display articles
            st.write("Articles:")

            time.sleep(5)

            # display articles
            for article in articles:
                st.write(article['title'])
                st.write(article['url'])
                st.markdown(summarize_article(article))
                time.sleep(5)
            st.write("Placeholder text for article analysis")


if __name__ == "__main__":
    main()
