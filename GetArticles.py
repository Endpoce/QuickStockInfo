import requests
from bs4 import BeautifulSoup


symbols = []


def get_symbols():

    # Grab up to 10 tickers
    j = 0
    while j < 10:

        # Get input
        uinput = input('Ticker Symbol: ').upper()

        # If ticker symbol = QUIT, quit
        if uinput == 'QUIT' or uinput == "":
            break

        # add ticker symbols to symbols list
        symbols.append(uinput)

        # Iterate
        j = j+1

    return symbols


def get_Google_articles(symbols):
    try:
        for symbol in symbols:
            if symbol != "^GSPC":
                with open("Stocks\ArticleGetter\Files\\" + symbol+"GoogleLinks.txt", 'r+') as f:
                    f.truncate(0)

                    url = ("https://www.google.com/finance/quote/"+symbol+":NYSE")

                    global soup, site

                    reqs = requests.get(url)
                    soup = BeautifulSoup(reqs.text, 'html.parser')

                    site = "Google Finance:"

                    links = []
                    for link in soup.findAll('a'):
                        links.append(link.get('href'))

                    f.writelines("MarketWatch Links:\n\n")

                    for link in links:
                        if "https:" in str(link):
                            f.write(link)
                        else:
                            pass
                f.close()
    except FileNotFoundError as e:
        print("Error getting articles: " + str(e))
        pass


def get_MW_Articles(symbol):
    if symbol != "^GSPC":

        base_url = 'https://www.marketwatch.com'
        search_url = f'{base_url}/search?q={symbol}'

        # Send a GET request to the search URL and get the response HTML content
        response = requests.get(search_url)
        html_content = response.content

        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find the article elements
        article_elements = soup.find_all(
            'h3', {'class': 'article__headline'})

        articles = []

        # Extract article information
        for article_element in article_elements:
            article_title = article_element.text.strip()
            article_url = base_url + article_element.find('a')['href']

            articles.append({'title': article_title, 'url': article_url})

        return articles


def get_Paragraphs(soup, site, symbol):

    with open("Stocks\ArticleGetter\Files\\"+symbol+"Bodies.txt", "w") as f:
        f.truncate()
        for data in soup.findAll('p'):
            try:
                if "company" in str(data):
                    f.writelines("\n" + "Description:" + ":\n\n")
                    f.write(str(data.getText()))

                    print(str(site) + ":\n\n")
                    print(data.getText())
                    print()
                    print('-----------------------------------------------')
                else:
                    pass
            except Exception as e:
                pass

            # print(data.getText())
    f.close()


def print_Articles(symbols):

    ask1 = input("Get Google Articles? (Y/N) : ")

    for symbol in symbols:
        if ask1 == "y" or ask1 == "Y" or ask1 == "yes" or ask1 == "Yes":
            get_Google_articles(symbol)
            get_Paragraphs
        else:
            pass

    ask2 = input("Get MarketWatch Articles? (Y/N) : ")

    for symbol in symbols:
        if ask2 == "y" or ask2 == "Y" or ask2 == "yes" or ask2 == "Yes":
            get_MW_Articles(symbol)
            get_Paragraphs(soup, site, symbol)
        else:
            pass
