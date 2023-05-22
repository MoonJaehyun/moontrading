import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
#속보 하면 좋음
base_url = "https://search.naver.com/search.naver"
params = {
    "where": "news",
    "query": "\"단독\"",
    "sm": "tab_srt",
    "sort": "1",
    "photo": "0",
    "field": "0",
    "pd": "4",
    "ds": "",
    "de": "",
    "mynews": "0",
    "office_type": "0",
    "office_section_code": "0",
    "news_office_checked": "",
    "nso": "so:dd,p:24h,a:all",
    "start": "1",
}

# Set the date range for the past 24 hours
now = datetime.now()
yesterday = now - timedelta(days=1)
params["ds"] = yesterday.strftime("%Y.%m.%d")
params["de"] = now.strftime("%Y.%m.%d")

# Define the keyword to check for in the news titles
keyword = "단독"

def get_news_titles(page_number):
    params["start"] = str(1 + (page_number - 1) * 10)
    response = requests.get(base_url, params=params)
    soup = BeautifulSoup(response.text, "html.parser")

    news_titles = []
    for title in soup.select("a.news_tit"):
        if keyword in title["title"]:
            news_titles.append(title["title"])

    return news_titles

page = 1
all_news_titles = []

while True:
    titles = get_news_titles(page)
    if len(titles) == 0:  # If no new titles, break the loop
        break
    all_news_titles.extend(titles)
    page += 1

for title in all_news_titles:
    print(title)
