# Authors: Aidan Murphy, Matt Anderson
# Date Created: 5/15/23

from datetime import timedelta, datetime, time
import yfinance as yf
import pandas as pd
from dotenv import load_dotenv
import os

from Gen_Files.GetArticles import *
from Gen_Files.Stock_Analyzer import *
import streamlit as st
from Gen_Files.Gen_Funcs import *

# set env vars
load_dotenv()

# Page config (Title at top and icon at top )
st.set_page_config(layout='wide', initial_sidebar_state="expanded", )


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
        col1, col2 = st.columns((1, 1))
    except Exception as e:
        pass

    if portfolio_tickers != "":
        # get stock data for the input tickers
        try:
            stock_data = get_stock_data(portfolio_tickers, start_date, end_date)
            tickers = portfolio_tickers.split(",")
        except Exception as e:
            error_message(e)
    
    try:
        if portfolio_tickers != "":
            fig, max_sharpe_portfolio, min_volatility_portfolio, results_dict = get_efficient_frontier(1000, stock_data)

            container = st.container()

            # display the efficient frontier
            with container:
                st.plotly_chart(fig, use_container_width=True)


            with col1:
                # display the max sharpe portfolio
                st.write("Max Sharpe Portfolio:")

                st.write("Return:")
                st.markdown(max_sharpe_portfolio['Return'])

                st.write("Volatility:")
                st.markdown(max_sharpe_portfolio['Volatility'])

                st.write("Sharpe Ratio:")
                st.markdown(max_sharpe_portfolio['Sharpe Ratio'])

                # display the weights from the max sharpe portfolio
                st.write("Weights:")
                for key, value in results_dict['Weights']:
                    if key in tickers:
                        st.write(key + ": " + str(value))
                

            with col2:
                # display the min volatility portfolio
                st.write("Min Volatility Portfolio:")

                st.write("Return:")
                st.markdown(min_volatility_portfolio['Return'])

                st.write("Volatility:")
                st.markdown(min_volatility_portfolio['Volatility'])

                st.write("Sharpe Ratio:")
                st.markdown(min_volatility_portfolio['Sharpe Ratio'])

                # display the weights of each stock from the min volatility portfolio
                st.write("Weights:")
                for key, value in results_dict['Weights']:
                    if key in tickers:
                        st.write(key + ": " + str(value))

    
    except Exception as e:
        error_message(e)

### tab 4: AI Analysis
with tab4:
    try:
        if primary_ticker != "":            
            # plot price stock data                
            plot_stock_with_interactive_chart(primary_ticker, hist)
        
    except Exception as e:
        error_message(e)

    try:
        if primary_ticker != "":
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

            st.markdown("***Placeholder text for article analysis***")
    except Exception as e:
        error_message(e)
