# Authors: Aidan Murphy
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

# set env vars
load_dotenv()

# set pandas override
yf.pdr_override()

# Page config (Title at top and icon at top )
st.set_page_config(page_title="Quick Stock Info", page_icon="chart_with_upwards_trend",
                   layout='wide', initial_sidebar_state="expanded")

# set openai api key
openai.api_key = os.environ.get('API_KEY')

# set dates
start_date = pd.to_datetime("2020-01-01")
end_date = datetime.today().strftime('%Y-%m-%d')

# set page parameters
# Title
st.title("Quick Stock Info")

tab1, tab2, tab3, tab4 = st.tabs(
    ["Quick Stock Info", "Investor Info", "Efficient Frontier", "GPT-4 Analysis"])

# Sidebar
st.sidebar.header("User Input")

# get user input for multiple tickers
primary_ticker = st.sidebar.text_input("Ticker Symbol:").upper()

comparative_tickers = st.sidebar.text_input(
    "Comparative Ticker Symbols (separated by commas)").upper()

# get start and end date
start_date = st.sidebar.date_input(
    "Start date", value=pd.to_datetime("2014-01-01"))
end_date = st.sidebar.date_input(
    "End date", value=pd.to_datetime(datetime.today().strftime('%Y-%m-%d')))

# fetch button
fetch_button = st.sidebar.button("Get Stock Data")

# set vars and calculate returns
# get start of year date
start_of_year = datetime.today().strftime('%Y-01-01')


# tab 1
with tab1:

    # Columns
    col1, col2 = st.columns((1, 1))

    # if button is pressed
    if fetch_button:

        # try to get basic company info

        # display company info
        ticker, info, hist, symbol = get_stock_data(primary_ticker, start_date, end_date)
        
        # get ytd data
        ytd_data = ticker.history(period="ytd")

        # get daily returns
        daily_returns = get_daily_returns(
            symbol, start_date, end_date)

        try:
                   
            # get ytd returns
            ytd_returns = ytd_data.pct_change()

            # get mean returns and covariance
            mus, cov = get_mean_returns_and_covariance(daily_returns)

            # set randomness
            n_assets, n_portfolios = set_randomness(1, 1000)

            # get random portfolios
            mean_variance_pairs = get_random_portfolios(
                n_assets, n_portfolios, daily_returns, mus, cov)

            # get efficient frontier
            efficient_frontier = get_efficient_frontier(
                n_assets, n_portfolios, mean_variance_pairs, mus, cov)
            
        except Exception as e:
            st.write("Error getting efficient frontier:: " + str(e))

        try:

            # get wiki info
            wiki_info = get_wiki_info(info['longName'] + " company")

        except Exception as e:
            st.write("Error getting wiki info:: " + str(e))

        # try to display company info
        with st.container():

            # display company info
            st.title(info['longName'])
            
            try:
                with col1.container():

                    # print company info
                    print(info)

                    # display sector
                    if info["sector"]:
                        st.write("Sector: "+info["sector"])

                    # display industry
                    if info["industry"]:
                        st.write("Industry: " + info["industry"])

                    # display legal type
                    if info["legalType"]:
                        st.write("Legal Type: " + info["legalType"])

                    # display category
                    if info['Category']:
                        st.write("Category: " + info["category"])

                    # display year founded
                    if info["yearBorn"]:
                        st.write("Year Founded: " + str(info["yearBorn"]))


                with col2.container():
                    if info['longBusinessSummary']:
                        st.write("Summary:")
                        st.markdown(info['longBusinessSummary'])

                    # display wiki info
                    if wiki_info:
                        st.write("Wikipedia URL:")
                        st.write(wiki_info['url'])

                        st.write("Wikipedia Summary:")
                        st.markdown(wiki_info['summary'])
            except Exception as e:
                st.write("Error displaying company info :: " + str(e))

        with st.container():

            try:
                # plot price stock data
                st.plotly_chart(plot_stock_with_interactive_chart(
                    primary_ticker), use_container_width=True)
            except Exception as e:
                st.write("Error plotting stock data:: " + str(e))



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

with tab3:
    st.subheader("Efficient Frontier")

    st, st = st.columns((2, 1))

    with st.container():
        try:

            # Define comparative_tickers or remove the if statement if not needed

            # Check if comparative_tickers is not empty
            if comparative_tickers >= 1:
                # set randomness
                n_assets = len(comparative_tickers.split(",")) + 1
                n_portfolios = 1000
                        
                # get daily returns
                daily_returns = get_daily_returns(primary_ticker, start_date, end_date)

                # get random portfolios
                mean_variance_pairs = get_random_portfolios(
                    n_assets, n_portfolios, daily_returns, mus, cov)

                # plot efficient frontier
                st.plotly_chart(plot_efficient_frontier(
                    efficient_frontier), use_container_width=True)
            
        except Exception as e:
            st.write("Error plotting efficient frontier ::" + str(e))

with tab4:
    try:
        st.title("GPT-4 Analysis")

        st, st = st.columns((1, 2))

        with st:
            # display finance info
            st.subheader("Summary:")

            
            # read stock price data from csv
            filename = str(primary_ticker) + '_Price_Data.csv'
            df = pd.read_csv(filename)

            # get stock price data
            hist = df[['Date', 'Close']]
            hist = hist.set_index('Date')

            # display current price
            st.metric(label="Current Price: ",
                      value=round(hist['Close'].iloc[-1], 2))

            # display estimated 52 return
            st.write("Estimated 52 Week Return: " +
                     str(get_estimated_1y_return(info, primary_ticker)) + "%")

            # display ytd return
            ytdReturn = get_ytd_return(primary_ticker, start_of_year)
            st.metric(label="Estimated YTD Return", value=ytdReturn,
                      delta=ytdReturn)

            # list of indicators I don't want to display
            not_displayed = ['longName', 'sector', 'category', 'currentPrice', 'regularMarketPrice',
                             'industry', 'longBusinessSummary', 'symbol', 'shortName',
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
                             'SandP52WeekChange', 'regularMarketDayHigh', 'regularMarketDayLow', 'regularMarketOpen',
                             'regularMarketPreviousClose', 'regularMarketVolume', 'regularMarketChange',
                             'timeZoneShortName', 'exchangeTimezoneShortName', 'gmtOffSetMilliseconds', 'maxAge',
                             'fundFamily', 'fundInceptionDate', 'open', 'previousClose', 'regularMarketChangePercent',
                             'auditRisk', 'boardRisk', 'compensationRisk', 'shareHolderRightsRisk', 'overallRisk',
                             'companyOfficers', 'maxAge', 'logo_url', 'compensationAsOfEpochDate', 'compensationRisk',
                             'dateShortInterest', 'daysToCover', 'daylow', 'dayhigh', 'exDividendDate',
                             'earningsquarterlyGrowth', 'enterpriseToEbitda', 'enterpriseToRevenue', 'enterpriseValue',
                             'financialCurrency', 'floatShares', 'freeCashflow', 'fundFamily', 'fundInceptionDate',
                             'industrydisplayName', 'lastfiscalYearEnd', 'numberOfAnalystOpinions', 'netIncomeToCommon',
                             'nextFiscalYearEnd', 'payoutratio', 'pricetosalestrailing12months', 'sectordisplayname',
                             'sectorkey', 'shareholderRightsRisk', 'sharesshort', 'sharesshortpriormonth',
                             'shortPercentFloat', ' shortPercentOutstanding', 'sharesoutstanding', 'sharespercentsharesout',
                             'targetHighPrice', 'targetLowPrice', 'targetMeanPrice', 'targetMedianPrice', 'totalAssets',
                             'timeZoneShortName', 'exchangeTimezoneShortName', 'gmtOffSetMilliseconds', 'maxAge'
                             ]

            indicators = [
                indicator for indicator in info if indicator not in not_displayed]
            sorted_indicators = sorted(indicators)

            for indicator in sorted_indicators:
                st.write(indicator + ": " + str(info[indicator]))

        with st:

            st.subheader("Analysis:")

            # plot price stock data
            st.plotly_chart(plot_stock_with_interactive_chart(
                filename), use_container_width=True)

            # analyze stock data
            # col2.write(analyze_stock(filename, ticker))
            st.write("Placeholder text for stock analysis")
            time.sleep(5)

            # get articles
            articles = get_MW_Articles(primary_ticker, 5)

            # display articles
            st.write("Articles:")

            time.sleep(5)

            # display articles
            # for article in articles[:5]:
            #     col2.write(article['title'])
            #     col2.write(article['url'])
            #     col2.markdown(summarize_article(article))
            #     time.sleep(5)
            st.write("Placeholder text for article analysis")
    except Exception as e:
        st.write("Error: Cant find GPT-4 analysis")


# if __name__ == "__main__":
#     main()
