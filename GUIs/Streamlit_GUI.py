# Authors: Aidan Murphy
# Date Created: 5/15/23

import sys

sys.path.append('QuickStockInfo/Gen_Files')

from datetime import timedelta, datetime
import streamlit as st
import yfinance as yf
import pandas as pd
import openai
from dotenv import load_dotenv
from Company_Info_Web_Scraper import *
from Efficient_Frontier import *
from Stock_Analyzer import *
from Sentiment import *
from GetArticles import *
import os


load_dotenv()

yf.pdr_override()

# Page config (Title at top and icon at top )
st.set_page_config(page_title="Quick Stock Info", page_icon="chart_with_upwards_trend",
                   layout='wide', initial_sidebar_state="expanded")
st.theme('dark')

# set openai api key
openai.api_key = os.environ.get('API_KEY')


# set dates
start_date = pd.to_datetime("2020-01-01")
end_date = datetime.today().strftime('%Y-%m-%d')

tab1, tab2, tab3, tab4 = st.tabs(
    ["Quick Stock Info", "Investor Info", "Efficient Frontier", "GPT-4 Analysis"])


def get_estimated_1y_return(info, ticker):

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


def get_investors(ticker):

    institutional_investor_dict = {}

    # Get institutional investor information
    institutional_holders = ticker.institutional_holders
    for _, row in institutional_holders.iterrows():
        investor_name = row['Holder']
        investor_position = row['Shares']
        institutional_investor_dict[investor_name] = investor_position

    major_holder_dict = {}

    # Get major holder information
    major_holders = ticker.major_holders
    for _, row in major_holders.iterrows():
        investor_name = row['Holder']
        investor_position = row['Shares']
        major_holder_dict[investor_name] = investor_position

    return institutional_investor_dict, major_holder_dict


def main():

    # Title
    st.title("Quick Stock Info")

    # Sidebar
    st.sidebar.header("User Input")

    # get user input for multiple tickers
    ticker_symbols = st.sidebar.text_input(
        "Ticker Symbols (separated by commas)").upper()

    # ticker_symbols -> list of tickers
    ticker_symbols = ticker_symbols.split(",")

    # get start and end date
    start_date = st.sidebar.date_input(
        "Start date", value=pd.to_datetime("2020-01-01"))
    end_date = st.sidebar.date_input(
        "End date", value=pd.to_datetime(datetime.today().strftime('%Y-%m-%d')))

    # fetch button
    fetch_button = st.sidebar.button("Get Stock Data")

    # set vars and calculate returns
    # get start of year date
    start_of_year = datetime.today().strftime('%Y-01-01')

    # calculate ytd return
    ytdReturn = round(
        (((ytd_data['Close'].iloc[-1] - ytd_data['Close'].iloc[0])/ytd_data['Close'].iloc[0])*100), 2)

    # get daily returns
    daily_returns = get_daily_returns(
        ticker_symbols, start_date, end_date)

    # get mean returns and covariance
    mus, cov = get_mean_returns_and_covariance(daily_returns)

    # set randomness
    n_assets, n_portfolios = set_randomness(5, 1000)

    # get random portfolios
    mean_variance_pairs = get_random_portfolios(
        n_assets, n_portfolios, daily_returns, mus, cov)

    # get efficient frontier
    efficient_frontier = get_efficient_frontier(
        mean_variance_pairs, mus, cov)

    # tab 1
    with tab1:

        # Columns
        col1, col2 = st.columns((1, 1))

        # if button is pressed
        if fetch_button:

            # try to get basic company info
            try:

                # download and save stock data
                for ticker in ticker_symbols:
                    data = yf.download(ticker, start=start_date, end=end_date)
                    filename = "QuickStockInfo\\Price_Data\\" + ticker + '_Price_Data.csv'
                    data.to_csv(filename)

                    # get company info and save to csv
                    info = get_company_info(ticker)
                    filename = "QuickStockInfo\\Company_Info\\" + ticker + '_Company_Info.csv'
                    pd.DataFrame.from_dict(info, orient='index').to_csv(
                        filename, header=False)

                # get ytd data
                ytd_data = ticker.history(start=start_of_year)

                try:
                    # get wiki info
                    wiki_info = get_wiki_info(info['longName'] + " company")
                except Exception as e:
                    st.write("Error getting wiki info:: " + str(e))
                    return

            except Exception as e:
                st.write("Error getting company info:: " + str(e))
                return

            # try to display company info
            try:
                with col1.container():
                    col1.subheader("Company Info:")

                    col1.subheader(info['longName'], color="blue")

                    if info["sector"]:
                        col1.write("Sector: "+info["sector"])

                    if info["industry"]:
                        col1.write("Industry: " + info["industry"])

                    if info["legalType"]:
                        col1.write("Legal Type: " + info["legalType"])

                    if info.category:
                        col1.write("Category: " + info["category"])

                    if info['longBusinessSummary']:
                        col1.write("Summary:")
                        col1.markdown(info['longBusinessSummary'])

                    # display wiki info
                    if wiki_info:
                        col1.write("Wikipedia URL:")
                        col1.write(wiki_info['url'])

                        col1.write("Wikipedia Summary:")
                        col1.markdown(wiki_info['summary'])

            except Exception as e:
                st.write("Error in col 1:: " + str(e))
                return

            try:
                with col2.container():

                    try:
                        # read stock price data from csv
                        filename = ticker_symbols + '_Price_Data.csv'
                        df = pd.read_csv(filename)

                    except Exception as e:
                        st.write("Error in col 1: " + str(e))
                        return

                    try:
                        # plot price stock data
                        col2.plotly_chart(plot_stock_with_interactive_chart(
                            filename), use_container_width=True)

                    except Exception as e:
                        st.write("Error in plotting price data: " + str(e))
                        return

                    try:
                        # plot efficient frontier
                        col2.plotly_chart(plot_efficient_frontier(
                            efficient_frontier), use_container_width=True)

                    except Exception as e:
                        st.write(
                            "Error in plotting efficient frontier: " + str(e))
                        return

            except Exception as e:
                st.write("Error in col 2: " + str(e))
                return

    with tab2:
        try:
            st.title("Investor Info")

            col1, col2 = st.columns((1, 2))

            with col1.container():
                st.subheader("Institutional Investors:")

                # # get institutional investors
                # institutional_investor = ticker.constituent.get_institutional_holders()

                # # display institutional investors
                # for investor in institutional_investor:
                #     st.write(investor + ":" + investor["shares"])

            with col2.container():
                st.subheader("Major Holders:")

                # # get investor info from yfinance
                # investor_info = ticker.major_holders

                # # display investor info
                # for holder in investor_info["Holder"]:
                #     st.write(holder + ": " + investor_info["Shares"][holder])
        except Exception as e:
            st.write("Error: Cant find investor info")
            return

    with tab3:
        st.subheader("Efficient Frontier")

        st.sidebar.subheader("Efficient Frontier")

        col1, col2 = st.columns((2, 1))

        with col1.container():
            # set randomness
            n_assets, n_portfolios = set_randomness(5, 1000)

            # get random portfolios
            mean_variance_pairs = get_random_portfolios(
                n_assets, n_portfolios, daily_returns, mus, cov)

            # plot efficient frontier
            col1.plotly_chart(plot_efficient_frontier(
                efficient_frontier), use_container_width=True)

    with tab4:
        try:
            st.title("GPT-4 Analysis")

            col1, col2 = st.columns((1, 2))

            with col1:
                # display finance info
                st.subheader("Summary:")

                # display current price
                st.metric(label="Current Price: ",
                          value=round(hist['Close'].iloc[-1], 2))

                # display estimated 52 return
                st.write("Estimated 52 Week Return: " +
                         str(get_estimated_1y_return(info, ticker)) + "%")

                # display ytd return
                st.metric(label="Estimated YTD Return", value=ytdReturn,
                          delta=ytdReturn)

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

            with col2:

                st.subheader("Analysis:")

                # plot price stock data
                col2.plotly_chart(plot_stock_with_interactive_chart(
                    filename), use_container_width=True)

                # analyze stock data
                # col2.write(analyze_stock(filename, ticker))
                col2.write("Placeholder text for stock analysis")
                time.sleep(5)

                # get articles
                articles = get_MW_Articles(ticker_symbols, 5)

                # display articles
                col2.write("Articles:")

                time.sleep(5)

                # display articles
                # for article in articles[:5]:
                #     col2.write(article['title'])
                #     col2.write(article['url'])
                #     col2.markdown(summarize_article(article))
                #     time.sleep(5)
                col2.write("Placeholder text for article analysis")
        except Exception as e:
            st.write("Error: Cant find GPT-4 analysis")
            return


if __name__ == "__main__":
    main()
