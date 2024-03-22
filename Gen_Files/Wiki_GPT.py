import openai
import requests
import wikipedia
from Gen_Files.GetArticles import *
import os
from dotenv import load_dotenv
import yfinance as yf
import google.generativeai as gai





def summarize_article(url):
    # Initialize a new chat model
    chat_model = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"Write: '--Summary--'. Write 'Sentiment: ' and give the sentiment of te article. Two lines down, Write a summary of the provided article. Then write on a new line: '--Additional Info--'. Then return a list of the main points in the provided article, one on each line. Limit each list item to 100 words, and return no more than 10 points per list. URL: {url}\n\nSummary:",
        temperature=0.3,
        max_tokens=300
    )

    return chat_model['choices'][0]['text']
