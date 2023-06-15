# %%
import openai
import requests
import wikipedia
from GetArticles import *
import os
from dotenv import load_dotenv

load_dotenv()

# %%
# Set up your OpenAI API credentials
openai.api_key = os.environ.get('API_KEY')

# %%
# set search query (must be ticker symbol or list of symbols)
search_query = ['WKHS']

# %%


def get_wiki_info(query):
    results = wikipedia.search(query)
    if results:
        first_result = results[0]  # get the first result
        try:
            # get the page of the first result
            page = wikipedia.page(first_result)
            url = page.url  # get the url of the page
            return url  # return the content of the page
        except wikipedia.DisambiguationError as e:
            print(
                f"Disambiguation page found, consider choosing a specific title from: {e.options}")
        except wikipedia.PageError:
            print("Page not found on Wikipedia")
    else:
        return None  # return None if no results found


def get_company_info(ticker):
    try:

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

# %%


def summarize_article(url):
    # Initialize a new chat model
    chat_model = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"Write: '--Summary--'. Write 'Sentiment: ' and give the sentiment of te article. Two lines down, Write a summary of the provided article. Then write on a new line: '--Additional Info--'. Then return a list of the main points in the provided article, one on each line. Limit each list item to 100 words, and return no more than 10 points per list. URL: {url}\n\nSummary:",
        temperature=0.3,
        max_tokens=300
    )

    return chat_model['choices'][0]['text']


# Test the function
# print(summarize_article('https://www.marketwatch.comhttps://www.marketwatch.com/story/tech-stock-picks-that-are-small-and-focused-this-fund-invests-in-unsung-innovators-here-are-2-top-choices-2028d2aa?mod=search_headline'))

# %%
# if __name__ == "__main__":

#     for stock in search_query:
#         with open("Company_info\\" + stock + '.txt', 'w') as f:
#             f.write("Company Name: " + get_company_info(stock)['name'] + "\n")
#             f.write("Sector: " + get_company_info(stock)['sector'] + "\n")
#             f.write("Industry: " + get_company_info(stock)['industry'] + "\n")
#             f.write("Description: " +
#                     textwrap.fill(get_company_info(stock)['summary']) + "\n")
#             f.write("Wiki: " + get_wiki_info(stock) + "\n")
#             f.write("\n")
#             f.write("MarketWatch Links:\n\n")
#             for article in get_MW_Articles(stock)[:10]:
#                 # print(article['title'])
#                 f.write(textwrap.fill(article['title']) + "\n")
#                 f.write("\t" + article['url'] + "\n\n")
#                 f.write(textwrap.fill(
#                     summarize_article(article)) + "\n\n")

    # print("Company Name: " + get_company_info(stock)['name'])
    # print("Sector: " + get_company_info(stock)['sector'])
    # print("Industry: " + get_company_info(stock)['industry'])
    # print("Description: " + get_company_info(stock)['summary'])
    # print("Wiki: " + get_wiki_info(stock))
    # print("\n")
    # for article in get_MW_Articles(stock)[:10]:
    #     print(textwrap.fill(article['title']) + "\n")
    #     print("\t" + article['url'] + "\n\n")
