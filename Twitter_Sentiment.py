import streamlit as st
import yfinance as yf
import tweepy
import matplotlib.pyplot as plt
from Twitter_Sentiment import twitterclient
import dotenv
import os
import praw
import textblob

# Load Bearer token
dotenv.load_dotenv()

# Page config (Title at top and icon at top )
st.set_page_config(page_title="Tweet Analysis", page_icon="chart_with_upwards_trend",
                   layout='wide', initial_sidebar_state="expanded")

# Page Config
# Dashboard Title
st.title("Dashboard")

# Set default search term
search1 = st.text_input("Search:", value="$SPY")

col1, col2, col3, col4 = st.columns((2, 1, 1, 1))

# Sidebar
# Sidebar Title
st.sidebar.title("Options:")

# Sidebar Dropdown
option = st.sidebar.selectbox("Select Dashboard:", ("Twitter", "Reddit"))

# Functions
# uses css to create styles for each tweet


def create_tweet_styles():
    # CSS selectors created by manually grabbing class from inpsect element in browser / all containers will have the same auto-generated class in the html
    tweet_styles = '''
    <style>
        /* container encompasing tweet */
        div.css-1ex6qxy.e1tzin5v0 div.css-1ex6qxy.e1tzin5v0 {
            background-color: rgb(34, 42, 64);
            padding: 0px;
            overflow-wrap: break-word;
            border: 2px solid;
            border-radius: 10px;
        }

    </style>
    '''
    st.markdown(tweet_styles, unsafe_allow_html=True)

# Use the class from TwitterSentiment file to get sentiment of tweets


def main_twitter():

    # Oauth
    api = twitterclient()

    # for each tweet in tweets, if tweet is positive, add to ptweets, if negative, add to ntweets
    tweets = api.get_tweets(search, count=3000)
    ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive']
    ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']

    # Finds the tweet with the most likes of the list NOTE: CLEANUP THIS AND MOST RETWEETS SECTION ASAP...PROBABLY CREATE FUNCTION TO GET MAX
    # try:
    # max_likes = max(tweets['num_likes'])

    # for tweet in tweets:
    #     if tweet.num_likes >= max_likes:
    #         max_likes = tweet['num_likes']
    #         tweet_most_likes = tweet['text']
    #         screen_name_most_likes = tweet['screen_name']
    #         profile_pic_most_likes = tweet['profile_pic']

    # Finds the tweet with the most retweets of the list
    # max_retweets = tweets[0]['retweet_count']
    #     max_retweets = max(tweets['retweet_count'])

    #     for tweet in tweets:
    #         if tweet['retweet_count'] >= max_retweets:
    #             max_retweets = tweet['retweet_count']
    #             tweet_most_retweets = tweet['text']
    #             screen_name_most_retweets = tweet['screen_name']
    #             profile_pic_most_retweets = tweet['profile_pic']
    #             num_likes_most_retweets = tweet['num_likes']

    # except IndexError as e:
    #     st.write(e)

    # Displays the user's profile pic, username, number of likes, and tweet at the top of the page.  If all tweets found have 0 likes (max_likes = 0), then it will display that all tweets found have 0 likes
    # try:
    #     if max_likes >= 1:

    #         with st.container():

    #             create_tweet_styles()

    #             st.write("The tweet with the most likes was:")
    #             ## Markdown
    #             st.image(profile_pic_most_likes)
    #             st.markdown('Username: ' + screen_name_most_likes, unsafe_allow_html=False)
    #             st.write(f"Number of likes: {max_likes}")
    #             # st.markdown(tweet, unsafe_allow_html=False)

    #             ## Text
    #             st.write(tweet["text"])
    #     else:
    #         st.write("---")
    #         st.write("All tweets found have 0 likes.")
    # except UnboundLocalError as e:
    #     st.write(e)

    # Does same as above, but for user with the most retweets.
    # try:
    #     if max_retweets >= 1:

    #         with st.container():

    #             create_tweet_styles()

    #             st.write("The tweet with the most retweets was:")
    #             ## Markdown
    #             st.image(profile_pic_most_retweets)
    #             st.markdown('Username: ' + screen_name_most_retweets, unsafe_allow_html=False)
    #             st.write(f"Number of likes: {num_likes_most_retweets}")
    #             st.write(f"Number of retweets: {max_retweets}")
    #             # st.markdown(tweet, unsafe_allow_html=False)

    #             ## Text
    #             st.write(tweet["text"])
    #     else:
    #         st.write("---")
    #         st.write("All tweets found have 0 retweets.")
    # except UnboundLocalError:
    #     pass

    try:
        positive_tweet_percent = (100*len(ptweets)/len(tweets))
        negative_tweet_percent = (100*len(ntweets)/len(tweets))
        neutral_tweet_percent = (
            100*(len(tweets)-(len(ntweets)+len(ptweets)))/len(tweets))

        with col1:
            # Add chart #1

            # NOTE: CLEAN UP ASAP
            labels = ['Positive', 'Negative', 'Neutral']
            sizes = [positive_tweet_percent,
                     negative_tweet_percent, neutral_tweet_percent]
            max_percent = max(
                [positive_tweet_percent, negative_tweet_percent, neutral_tweet_percent])
            pos_explode = 0
            neg_explode = 0
            neutral_explode = 0
            if max_percent == positive_tweet_percent:
                pos_explode = 0.05
            elif max_percent == negative_tweet_percent:
                neg_explode = 0.05
            elif max_percent == neutral_tweet_percent:
                neutral_explode = 0.05
            explode = [pos_explode, neg_explode, neutral_explode]
            fig1, ax1 = plt.subplots()
            ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
                    shadow=True, startangle=90, textprops=dict(color="w"))
            ax1.axis('equal')
            fig1.set_facecolor('#0e1117')

            st.pyplot(fig1)

        st.write("---")

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
                st.write(tweet["text"])
                st.write("---")

        st.subheader("There were no tweets found.")
    except TypeError as e:
        st.write(e)

# If twitter phrase starts with '@' then search users


def for_users():

    # Oauth
    auth = tweepy.OAuth2BearerHandler('Bearer_token')
    api = tweepy.API(auth)
    twitterapi = twitterclient()

    try:
        # Gets user's last tweet
        tweets = api.user_timeline(
            screen_name=search[1:], count=1, tweet_mode='extended')

        # Must be formatted into for loop or a new variable must be set equal to index of it because "user_timeline" returns a list.
        for tweet in tweets:

            # Getting the tweet sentiment using the function from the TwitterSentiment file.
            tweet_sentiment = twitterapi.get_tweet_sentiment(tweet.full_text)

            st.markdown(tweet.user.screen_name +
                        "'s most recent tweet/reply was:")
            st.markdown('"' + tweet.full_text + '"')
            st.markdown("This tweet was determined to have a " +
                        tweet_sentiment + " sentiment by our natural language processor.")
    except:
        st.subheader("That profile could not be found.")

# get text sentiment given any text string


def get_text_sentiment(text):

    # Use textblob to analyze sentiment

    analysis = textblob.TextBlob(text)

    if analysis.sentiment.polarity > 0:
        return 'positive'
    elif analysis.sentiment.polarity == 0:
        return 'neutral'
    else:
        return 'negative'

# Make a graph given, pos, neg, and neu sentiments


def pie_Graph(texts):
    ptexts = []
    ntexts = []
    neutraltexts = []

    texts = [Sub.hot(limit=100)]

    for submission in Sub.hot(limit=100):
        parsed_text = {}
        parsed_text['text'] = submission.selftext
        parsed_text['sentiment'] = get_text_sentiment(submission.selftext)
        parsed_text['score'] = submission.score

        analysis = textblob.TextBlob(parsed_text['text'])

        if parsed_text['score'] > 0:
            if parsed_text not in texts:
                texts.append(parsed_text["sentiment"])
        else:
            texts.append(parsed_text["sentiment"])

        if analysis.sentiment.polarity > 0:
            ptexts.append(parsed_text['sentiment'])
        elif analysis.sentiment.polarity == 0:
            neutraltexts.append(parsed_text['sentiment'])
        elif analysis.sentiment.polarity < 0:
            ntexts.append(parsed_text['sentiment'])

    positive_text_percent = (100*len(ptexts)/len(texts))
    negative_text_percent = (100*len(ntexts)/len(texts))
    neutral_text_percent = (
        100*(len(texts)-(len(ntexts)+len(ptexts)))/len(texts))

    with col1:

        # Add chart #1

        # NOTE: CLEAN UP ASAP
        labels = ['Positive', 'Negative', 'Neutral']
        sizes = [positive_text_percent,
                 negative_text_percent, neutral_text_percent]
        max_percent = max(
            [positive_text_percent, negative_text_percent, neutral_text_percent])
        pos_explode = 0
        neg_explode = 0
        neutral_explode = 0
        if max_percent == positive_text_percent:
            pos_explode = 0.05
        elif max_percent == negative_text_percent:
            neg_explode = 0.05
        elif max_percent == neutral_text_percent:
            neutral_explode = 0.05
        explode = [pos_explode, neg_explode, neutral_explode]
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
                shadow=True, startangle=90, textprops=dict(color="w"))
        ax1.axis('equal')
        fig1.set_facecolor('#0e1117')

        st.pyplot(fig1)

# sidebar stock analysis


def sidebar_Stocks():

    st.sidebar.write("---")

    st.sidebar.subheader("Stock Analysis: ")

    stock_search = st.sidebar.text_input(
        "Ticker: ", value="$"+"SPY", max_chars=5)

    # NOTE: RESOLVED...Incorporate a function to change it to company name instead of their ticker.  Makes more user-friendly for people not "stock saavy"
    st.sidebar.markdown("Ticker: " + stock_search)

    def sidebar_tweets(tweets):

        st.sidebar.image(f"https://finviz.com/chart.ashx?t={stock_search}")

        # Oauth

        api = twitterclient()

        tweets = api.get_tweets(query=stock_search, count=300)

        try:
            for tweet in tweets:

                with st.container():

                    create_tweet_styles()

                    # Markdown
                    if tweet['num_likes'] > 1:
                        st.sidebar.image(tweet["profile_pic"])
                        st.sidebar.markdown(
                            'Username: ' + tweet["screen_name"], unsafe_allow_html=False)
                        st.sidebar.write(
                            f"Number of likes: {tweet['num_likes']}")

                        # Text

                        st.sidebar.write(tweet["text"])
                        st.sidebar.write("---")

        except:

            st.subheader("There were no tweets found.")

            st.write("---")

    sidebar_tweets(stock_search)


# Sidebar dropdown option for twitter, display twitter stats
if option == "Twitter":

    # subheader
    st.subheader("Twitter Stats:")

    # Sidebar dropdown for types of searching
    search = st.sidebar.text_input("Search a phrase:", value=search1)

    # subheader for stock title
    st.subheader('Phrase: {}'.format(search.upper()))

    # use twitter function to get tweets, or display an error message
    if search.startswith('@'):
        for_users()
    else:
        try:
            main_twitter()
        except TypeError as e:
            st.text(e)

# Reddit
if option == "Reddit":

    # subheader
    st.subheader("Reddit Mentions:")

    sub = st.sidebar.text_input("Input a subreddit:", value=search1)

    phrase = st.sidebar.text_input("Input a phrase:")

    try:
        reddit = praw.Reddit(
            client_id=os.environ.get("Reddit_token"),
            client_secret=os.environ.get("Reddit_secret"),
            user_agent="SentimentAnalysis",
        )

        Sub = reddit.subreddit(sub)
        subreddittexts = []

        for submission in Sub.hot(limit=100):
            if phrase in submission.title or phrase in submission.selftext:
                subreddittexts.append(submission.selftext)

        pie_Graph(Sub)

        for submission in Sub.hot(limit=100):
            if phrase in submission.title or phrase in submission.selftext:

                st.write("Title: ")
                st.write(submission.title)
                st.write("Score: ", submission.score)
                st.write("Sentiment: " +
                         get_text_sentiment(str(submission.selftext)))
                st.image(submission.url)
                st.write("Link:")
                st.write("https://www.reddit.com" + submission.permalink)

                if submission.selftext:
                    st.write("Text: ")
                    st.write(submission.selftext)
                st.write("---")

            else:
                st.write("No submissions found!")
                break

    except ValueError as e:
        st.write("Search for something!")


# Sidebar stock analysis

    st.sidebar.write("---")
    st.sidebar.subheader("Stock Analysis: ")

    stock_search = st.sidebar.text_input("Ticker: ", value="TSLA", max_chars=5)

    # NOTE: RESOLVED...Incorporate a function to change it to company name instead of their ticker.  Makes more user-friendly for people not "stock saavy"
    st.sidebar.markdown("Ticker: " + stock_search)

    def sidebar_tweets(tweets):

        st.sidebar.image(f"https://finviz.com/chart.ashx?t={stock_search}")
        # Oauth
        api = twitterclient()
        tweets = api.get_tweets(query=stock_search, count=300)
        try:
            for tweet in tweets:

                with st.container():

                    create_tweet_styles()

                    # Markdown
                    st.sidebar.image(tweet["profile_pic"])
                    st.sidebar.markdown(
                        'Username: ' + tweet["screen_name"], unsafe_allow_html=False)
                    st.sidebar.write(f"Number of likes: {tweet['num_likes']}")
                    # st.markdown(tweet, unsafe_allow_html=False)

                    # Text
                    st.sidebar.write(tweet["text"])
                    st.sidebar.write("---")

        except:

            st.subheader("There were no tweets found.")
            st.write("---")

    sidebar_tweets(stock_search)


sidebar_Stocks()
