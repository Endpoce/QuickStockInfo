# %%
import json
import pandas as pd
import openai
import requests
import yfinance as yf
import wikipedia
from GetArticles import *
import datetime

# %%
# Set up your OpenAI API credentials
openai.api_key = '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'


def get_wiki_info(search_query):
    try:
        for stock in search_query:
            # wikipedia search request
            page_url = wikipedia.page(stock).url

            return page_url

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return ''
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return ''
    except KeyError as e:
        print(f"Key error: {e}")
        return ''


def get_company_info(stock):
    try:
        # Create a Ticker object for the specified symbol
        ticker = yf.Ticker(stock)

        # Get company info from the Ticker object
        info = ticker.info

        # Extract the desired information
        company_name = info['longName']
        sector = info['sector']
        industry = info['industry']
        summary = info['longBusinessSummary']

        # Return the company information as a dictionary
        company_dict = {
            'name': company_name,
            'sector': sector,
            'industry': industry,
            'summary': summary
        }

        return company_dict

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return ''
