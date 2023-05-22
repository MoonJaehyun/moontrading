import os
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from docx import Document
from pykrx import stock
from concurrent.futures import ThreadPoolExecutor

os.system('cls||clear')

def get_news(url: str, keyword: str):
    list_keyword_news = []
    list_news_area = []

    try:
        html = requests.get(url).text
        soup = BeautifulSoup(html, 'html.parser')

        list_news = soup.find('ul', {'class': 'list_news'})
        if list_news is not None and len(list_news) > 0:
            list_news_area = soup.find_all('div', {'class': 'news_area'})

            for news_area in list_news_area:
                news_tit = news_area.find('a', {'class': 'news_tit'})
                title = news_tit.attrs['title']

                if keyword in title:
                    href = news_tit.attrs['href']
                    list_keyword_news.append([title, href])

    except requests.exceptions.RequestException as e:
        print("Error occurred while fetching news:", e)
        return None, 0

    return list_keyword_news, len(list_news_area)


def fetch_news(search_url, search_keyword):
    stopped = True
    start_num = 1
    news_num_per_page = 5
    list_found_news = []
    results = []

    while True:
        target_url = search_url + str(start_num)
        r, items_num = get_news(target_url, search_keyword)

        if r is None or items_num == 0:
            break

        list_found_news.extend(r)

        if len(list_found_news) >= news_num_per_page:
            for count in range(news_num_per_page):
                title, href = list_found_news.pop(0)
                results.append(title)
                print(title)

            stopped = True
            break

        start_num += items_num
        
        time.sleep(1)

    if not stopped and r is not None and len(r) > 0:
        title, href = list_found_news.pop(0)
        results.append(title + ' ' + href)
        print(title + href)

    return results


def save_to_docx(filename, results):
    document = Document()

    for item in results:
        if item.strip():
            document.add_paragraph(item.strip())

    document.save(filename)


def main():
    try:
        print()

        # 코스피 종목 코드
        kospi_tickers = stock.get_market_ticker_list(market="KOSPI")

        # 코스닥 종목 코드
        kosdaq_tickers = stock.get_market_ticker_list(market="KOSDAQ")

        # 코스피와 코스닥 종목 코드 합치기
        ticker_list = kospi_tickers + kosdaq_tickers

        # 종목 코드를 종목명으로 변환
        ticker_names = [stock.get_market_ticker_name(ticker) for ticker in ticker_list]

        results = []
        with ThreadPoolExecutor() as executor:
            for ticker, ticker_name in zip(ticker_list, ticker_names):
                search_keyword = ticker_name
                quote_keyword = requests.utils.quote(search_keyword)
                search_url = f"https://search.naver.com/search.naver?where=news&sm=tab_pge&query={quote_keyword}&sort=1&photo=0&field=0&pd=4&ds=&de=&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so:dd,p:all,a:all&start="
                future = executor.submit(fetch_news, search_url, search_keyword)
                results.append((ticker, future))

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  # 타임스탬프 추가
        filename = timestamp + "_all.docx"
        save_to_docx(filename, [result for ticker, future in results for result in future.result()])
        print(f"Saved {filename}")

        time.sleep(1)

    except Exception as e:
        print("Error:", e)


if __name__ == '__main__':
    main()
