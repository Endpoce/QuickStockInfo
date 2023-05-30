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


def get_tweets(query, count):

    # create tweet list
    tweets = []

    # get tweets containing phrase
    fetched_tweets = api.search_tweets(
        q=query, count=count, tweet_mode='extended', result_type='popular')
    for tweet in fetched_tweets:
        parsed_tweet = {}
        # parsed_tweet = clean_tweet(tweet.full_text)
        parsed_tweet['text'] = tweet.full_text
        parsed_tweet['retweet_count'] = tweet.retweet_count
        parsed_tweet['user'] = tweet.user
        parsed_tweet['screen_name'] = tweet.user.screen_name
        parsed_tweet['profile_pic'] = tweet.user.profile_image_url
        parsed_tweet['num_likes'] = tweet.favorite_count

        # print(parsed_tweet['text'])

        if parsed_tweet not in tweets:
            tweets.append(parsed_tweet)

    return tweets


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

        with col1.container():
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

        with col2.container():
            # plot price stock data
            col2.pyplot(plot_stock_with_moving_averages_from_csv(filename))

            # analyze stock data
            # time.sleep(5)
            # col2.markdown(analyze_stock(filename))
            col2.write("Placeholder text for stock analysis")
            # time.sleep(5)

        with col3.container():
            # display tweets
            st.write("Tweets:")
            tweets = get_tweets(str(ticker_symbol), 5)

            # display tweets
            # display tweet text
            for tweet in tweets:

                with st.container():

                    create_tweet_styles()

                    # Markdown
                    st.image(tweet["profile_pic"])
                    st.markdown('Username: ' +
                                tweet["screen_name"], unsafe_allow_html=False)
                    st.write(f"Number of likes: {tweet['num_likes']}")
                    # st.markdown(tweet, unsafe_allow_html=False)

                    # Text
                    st.write("Sentiment: " +
                             get_tweet_sentiment(tweet["text"]))
                    st.markdown(tweet["text"])
                    st.write("---")
                    time.sleep(5)
            else:
                st.write("No tweets found")
        with col2.container():
            # get articles
            articles = get_MW_Articles(ticker_symbol, 5)

            # display articles
            st.write("Articles:")

            # display articles
            for article in articles:
                st.write(article['title'])
                st.write(article['url'])
                st.container(summarize_article(article))
                time.sleep(5)
            st.write("Placeholder text for article analysis")


if __name__ == "__main__":
    main()
