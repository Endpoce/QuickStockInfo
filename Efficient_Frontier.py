# %%
import pandas as pd
import numpy as np
from tqdm import tqdm
import plotly.graph_objects as go
import yfinance as yf


def get_daily_returns(tickers, start_date, end_date):

    # -- calculate the daily returns
    daily_returns = pd.DataFrame()

    # -- Loop through and download the data for each ticker
    for ticker in tqdm(tickers):
        df = yf.download(ticker, start=start_date, end=end_date)
        df['daily_return'] = df['Adj Close'].pct_change()
        daily_returns[ticker] = df['daily_return']

    return daily_returns


def get_mean_returns_and_covariance(daily_returns):

    # -- Get annualised mean returns
    mus = (1+daily_returns.mean())**252 - 1

    # -- Get covariances
    cov = daily_returns.cov()*252

    return mus, cov


def set_randomness(n_assets, n_portfolios):
    # - How many assests to include in each portfolio
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