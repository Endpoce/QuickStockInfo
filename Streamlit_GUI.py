# Authors: Aidan Murphy, Matt Anderson
# Date Created: 5/15/23

from datetime import timedelta, datetime, time
import yfinance as yf
import pandas as pd
from dotenv import load_dotenv
import os

from Gen_Files.Wiki_GPT import *
from Gen_Files.GetArticles import *
from Gen_Files.Stock_Analyzer import *
import streamlit as st
from Gen_Files.Gen_Funcs import *


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
                    error_message(e)

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

    st.subheader("Efficient Frontier")
    try:
        portfolio_tickers = st.text_input("Portfolio Tickers (comma separated):").upper()
    except Exception as e:
        pass
    # get stock data for the input tickers
    try:
        # add the primary ticker to the list of tickers
        tickers = portfolio_tickers.split(",") + [primary_ticker]

        # create a dict to store stock data
        stock_data = {}

        # get stock data
        for ticker in tickers:
            stock_data = yf.download(ticker, start_date, end_date)
            stock_data[ticker] = stock_data["Close"]

        stock_data = pd.DataFrame(stock_data)


    except Exception as e:
        error_message(e)
    
    try:
        fig, max_sharpe_portfolio, min_volatility_portfolio = get_efficient_frontier(1000, stock_data)

        # display the efficient frontier
        st.plotly_chart(fig)

        # display the max sharpe portfolio
        st.write("Max Sharpe Portfolio:")

        st.write("Return:")
        st.write(max_sharpe_portfolio['Return'])

        st.write("Volatility:")
        st.write(max_sharpe_portfolio['Volatility'])

        st.write("Sharpe Ratio:")
        st.write(max_sharpe_portfolio['Sharpe Ratio'])

        # display the weights from the max sharpe portfolio
        st.write("Weights:")
        for key, value in max_sharpe_portfolio['tickers']:
            if key in tickers:
                st.write(key + ": " + str(value))


        # display the min volatility portfolio
        st.write("Min Volatility Portfolio:")

        st.write("Return:")
        st.write(min_volatility_portfolio['Return'])

        st.write("Volatility:")
        st.write(min_volatility_portfolio['Volatility'])

        st.write("Sharpe Ratio:")
        st.write(min_volatility_portfolio['Sharpe Ratio'])

        st.write("Weights:")
        for key, value in min_volatility_portfolio['tickers']:
            if key in tickers:
                st.write(key + ": " + str(value))
    
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
        st.write(google_summary(hist, info))
    
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
