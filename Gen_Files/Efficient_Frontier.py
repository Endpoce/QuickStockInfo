import pandas as pd
import numpy as np
from tqdm import tqdm
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime, timedelta
import math

# calculate ytd return
def get_ytd_return(ticker_symbols, start_of_year):

    for ticker in ticker_symbols:
        ytd_data = []
        ytd_returns = []

        # get ytd data
        ytd_data = ticker.history(start=start_of_year)

        # calculate ytd return
        ytdReturn = round(
            (ytd_data['Close'].iloc[-1] - ytd_data['Close'].iloc[0]) / ytd_data['Close'].iloc[0] * 100, 2)

        ytd_returns.append(ytdReturn)

    return ytd_returns


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


def get_daily_returns(ticker, start_date, end_date):

    # -- Get each daily return for the historical data
    data = yf.download(str(ticker), start=start_date, end=end_date)
    daily_returns = data['Adj Close'].dropna()
    daily_returns = data['Adj Close'].pct_change()

    return daily_returns


def get_mean_returns_and_covariance(daily_returns):
    # -- Get annualized mean returns
    mus = daily_returns.mean() * 252

    # -- Get covariances
    cov = daily_returns.cov(cov) * 252

    return mus, cov


def set_randomness(n_assets, n_portfolios):
    # - How many assets to include in each portfolio
    n_assets = n_assets
    # -- How many portfolios to generate
    n_portfolios = n_portfolios

    return n_assets, n_portfolios


def get_random_portfolios(n_assets, n_portfolios, daily_returns, mus, cov):
    # -- Initialize empty list to store mean-variance pairs for plotting
    mean_variance_pairs = []

    # -- Set random seed for reproducibility
    np.random.seed(75)

    # -- Loop through and generate lots of random portfolios
    for i in range(n_portfolios):

        # - Choose assets randomly without replacement
        assets = np.random.choice(
            list(daily_returns.columns), n_assets, replace=False)

        # - Choose weights randomly
        weights = np.random.rand(n_assets)

        # - Ensure weights sum to 1
        weights = weights/sum(weights)

        # -- Loop over asset pairs and compute portfolio return and variance
        # - https://quant.stackexchange.com/questions/43442/portfolio-variance-explanation-for-equation-investments-by-zvi-bodie
        portfolio_E_Variance = 0
        portfolio_E_Return = 0
        for i in range(len(assets)):
            portfolio_E_Return += weights[i] * mus.loc[assets[i]]
            for j in range(len(assets)):
                # -- Add variance/covariance for each asset pair
                # - Note that when i==j this adds the variance
                portfolio_E_Variance += weights[i] * \
                    weights[j] * cov.loc[assets[i], assets[j]]

        # -- Add the mean/variance pairs to a list for plotting
        mean_variance_pairs.append([portfolio_E_Return, portfolio_E_Variance])

    # -- Plot the risk vs. return of randomly generated portfolios
    # -- Convert the list from before into an array for easy plotting
    mean_variance_pairs = np.array(mean_variance_pairs)

    return mean_variance_pairs


def plot_random_portfolios(mean_variance_pairs):
    risk_free_rate = 0  # -- Include risk free rate here
    # -- Plot the risk vs. return of randomly generated portfolios
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=mean_variance_pairs[:, 1]**0.5, y=mean_variance_pairs[:, 0],
                             marker=dict(color=(mean_variance_pairs[:, 0]-risk_free_rate)/(mean_variance_pairs[:, 1]**0.5),
                                         showscale=True,
                                         size=7,
                                         line=dict(width=1),
                                         colorscale="RdBu",
                                         colorbar=dict(title="Sharpe<br>Ratio")
                                         ),
                             mode='markers'))
    fig.update_layout(template='plotly_white',
                      xaxis=dict(title='Annualised Risk (Volatility)'),
                      yaxis=dict(title='Annualised Return'),
                      title='Sample of Random Portfolios',
                      width=850,
                      height=500)
    fig.update_xaxes(range=[0.18, 0.32])
    fig.update_yaxes(range=[0.02, 0.27])
    fig.update_layout(coloraxis_colorbar=dict(title="Sharpe Ratio"))

    return fig


def get_efficient_frontier(n_assets, n_portfolios, daily_returns, mus, cov, ):
    # -- Create random portfolio weights and indexes
    # - How many assests in the portfolio
    n_assets = n_assets
    n_portfolios = n_portfolios

    mean_variance_pairs = []
    weights_list = []
    tickers_list = []

    for i in tqdm(range(n_portfolios)):
        next_i = False
        while True:
            # - Choose assets randomly without replacement
            assets = np.random.choice(
                list(daily_returns.columns), n_assets, replace=False)
            # - Choose weights randomly ensuring they sum to one
            weights = np.random.rand(n_assets)
            weights = weights/sum(weights)

            # -- Loop over asset pairs and compute portfolio return and variance
            portfolio_E_Variance = 0
            portfolio_E_Return = 0
            for i in range(len(assets)):
                portfolio_E_Return += weights[i] * mus.loc[assets[i]]
                for j in range(len(assets)):
                    portfolio_E_Variance += weights[i] * \
                        weights[j] * cov.loc[assets[i], assets[j]]

            # -- Skip over dominated portfolios
            for R, V in mean_variance_pairs:
                if (R > portfolio_E_Return) & (V < portfolio_E_Variance):
                    next_i = True
                    break
            if next_i:
                break

            # -- Add the mean/variance pairs to a list for plotting
            mean_variance_pairs.append(
                [portfolio_E_Return, portfolio_E_Variance])
            weights_list.append(weights)
            tickers_list.append(assets)

    # -- Plot the risk vs. return of randomly generated portfolios
    # -- Convert the list from before into an array for easy plotting
    mean_variance_pairs = np.array(mean_variance_pairs)

    return mean_variance_pairs, weights_list, tickers_list


def plot_efficient_frontier(mean_variance_pairs, weights_list, tickers_list):
    risk_free_rate = 0  # -- Include risk free rate here

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=mean_variance_pairs[:, 1]**0.5, y=mean_variance_pairs[:, 0],
                             marker=dict(color=(mean_variance_pairs[:, 0]-risk_free_rate)/(mean_variance_pairs[:, 1]**0.5),
                                         showscale=True,
                                         size=7,
                                         line=dict(width=1),
                                         colorscale="RdBu",
                                         colorbar=dict(title="Sharpe<br>Ratio")
                                         ),
                             mode='markers',
                             text=[str(np.array(tickers_list[i])) + "<br>" + str(np.array(weights_list[i]).round(2)) for i in range(len(tickers_list))]))
    fig.update_layout(template='plotly_white',
                      xaxis=dict(title='Annualised Risk (Volatility)'),
                      yaxis=dict(title='Annualised Return'),
                      title='Sample of Random Portfolios',
                      width=850,
                      height=500)
    fig.update_xaxes(range=[0.18, 0.35])
    fig.update_yaxes(range=[0.05, 0.29])
    fig.update_layout(coloraxis_colorbar=dict(title="Sharpe Ratio"))

    return fig
