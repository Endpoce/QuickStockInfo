# Gen_Funcs.py

import yfinance as yf
import streamlit as st

def get_stock_info(symbol):
    """
    Get stock information for a given symbol using the yfinance library.
    """
    stock = yf.Ticker(symbol)
    info = stock.info
    return info

def display_stock_info(info):
    """
    Display stock information using the Streamlit API.
    """
    st.write("Company Name:", info['longName'])
    st.write("Symbol:", info['symbol'])
    st.write("Sector:", info['sector'])
    st.write("Industry:", info['industry'])
    st.write("Market Cap:", info['marketCap'])
    st.write("Price:", info['regularMarketPrice'])
    st.write("Volume:", info['regularMarketVolume'])

def main():
    """
    Main function to run the Streamlit app.
    """
    st.title("Stock Information App")
    symbol = st.text_input("Enter a stock symbol:")
    
    if st.button("Get Info"):
        info = get_stock_info(symbol)
        display_stock_info(info)

if __name__ == "__main__":
    main()
