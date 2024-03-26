# Authors: Aidan Murphy, Matt Anderson
# Date Created: 5/15/23

from datetime import timedelta, datetime, time
import yfinance as yf
import pandas as pd
import openai
from dotenv import load_dotenv
import os

from Gen_Files.Wiki_GPT import *
from Gen_Files.GetArticles import *
from Gen_Files.Stock_Analyzer import *
from Gen_Files.Efficient_Frontier import *
import streamlit as st
from Gen_Files.Gen_Funcs import *
import google.generativeai as gai
import vertexai
from vertexai.generative_models import GenerativeModel, Part

# set env vars
load_dotenv()

# set pandas override
yf.pdr_override()

# Page config (Title at top and icon at top )
st.set_page_config(layout='wide', initial_sidebar_state="expanded")


# set page parameters
# Title
st.title("Quick Stock Info")

# set tabs
tab1, tab2, tab3, tab4 = st.tabs(["Quick Stock Info", "Investor Info", "Efficient Frontier", "Analysis"])

# Sidebar
with st.sidebar:
    st.header("User Input")

    # get user input for primary ticker
    primary_ticker = st.sidebar.text_input("Ticker Symbol:").upper()

    # start and end date, start of year
    start_date = st.sidebar.date_input("Start date", value=pd.to_datetime("2020-01-01"))
    end_date = st.sidebar.date_input("End date", value=pd.to_datetime(datetime.today().strftime('%Y-%m-%d')))
    start_of_year = datetime.today().strftime('%Y-01-01')

    ## fetch button
    fetch_button = st.sidebar.button("Get Stock Data")

    # if button is pressed
    if fetch_button or primary_ticker != "":
        try:
            # display company info
            global ticker, info, hist, symbol
            ticker, info, hist, symbol = get_stock_data(primary_ticker, start_date, end_date)

            # get ytd data
            ytd_data = ticker.history(period="ytd")

            # get daily returns
            # daily_returns = get_daily_returns(symbol, start_date, end_date)
        
        except Exception as e:
            error_message(e)

### tab 1: Info
with tab1:

        if fetch_button or primary_ticker != "":    

            # set container title
            st.subheader(info['longName'] + " (" + primary_ticker + ")")
            
            try:
                # plot price stock data                
                plot_stock_with_interactive_chart(primary_ticker, hist)

            except Exception as e:
                error_message(e)
            
            # Columns
            col1, col2 = st.columns((1, 1))
            
            with col1:
                try:
                    # display company info
                    st.write("Company Info:")
                    display_stock_info(info, hist)
                    

                except Exception as e:
                    error_message(e)



            with col2:
                try:
                    # display wiki info
                    st.write("Wiki Info:")
                    wiki_info = get_wiki_info(primary_ticker)
                    st.markdown(wiki_info)

                except Exception as e:
                    st.write("Error displaying wiki info :: " + error_message(e))

### tab 2: Investors
with tab2:
    try:
        st.title("Investor Info")

        col1, col2 = st.columns((1, 2))

        with st.container():
            st.subheader("Institutional Investors:")

            # # get institutional investors
            # institutional_investor = ticker.constituent.get_institutional_holders()

            # # display institutional investors
            # for investor in institutional_investor:
            #     st.write(investor + ":" + investor["shares"])

        with st.container():
            st.subheader("Major Holders:")

            # # get investor info from yfinance
            # investor_info = ticker.major_holders

            # # display investor info
            # for holder in investor_info["Holder"]:
            #     st.write(holder + ": " + investor_info["Shares"][holder])
    except Exception as e:
        st.write("Error: Cant find investor info")

### tab 3: Portfolio Analysis
with tab3:
    """
    This tab will display the efficient frontier for the selected stock plus the portfolio of the input stocks. First, it will download the stock data for the input stocks,
    then it will calculate the efficient frontier and display it.
    """

    st.subheader("Efficient Frontier")

    secondary_tickers = st.text_input("Comparative Tickers (comma separated):").upper()

    # get stock data for the input tickers
    try:
        # get stock data for the input tickers
        tickers = [primary_ticker] + secondary_tickers.split(",")

        # get stock data for the input tickers
        for ticker in tickers:
            # get stock data
            stock_data = yf.download(ticker, start=start_date, end=end_date)
            stock_data.to_csv(str(ticker) + '_Price_Data.csv')
        
        # display the efficient frontier
        st.plotly_chart(get_efficient_frontier(10000, hist))

        # delete the stock data files
        for ticker in tickers:
            os.remove(str(ticker) + '_Price_Data.csv')

    
    except Exception as e:
        error_message(e)






### tab 4: AI Analysis
with tab4:
    try:        
        # plot price stock data                
        plot_stock_with_interactive_chart(primary_ticker, hist)
        
    except Exception as e:
        error_message(e)

    try:
        # analyze stock data
        st.write(google_summary(ticker, hist))
    
    except Exception as e:
        error_message(e)
    
    try:
            # get articles
            # articles = get_MW_Articles(primary_ticker, 5)

            # # display articles
            # st.write("Articles:")

            # # display articles
            # for article in articles[:5]:
            #     col2.write(article['title'])
            #     col2.write(article['url'])

            st.write("Placeholder text for article analysis")
    except Exception as e:
        error_message(e)
