import time
import os
import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from docx import Document
from pykrx import stock

os.system('cls||clear')


def get_news(keyword: str):
    list_keyword_news = []
    try:
        search_keyword = requests.utils.quote(keyword)
        search_url = f"https://search.naver.com/search.naver?where=news&sm=tab_pge&query={search_keyword}&sort=1&photo=0&field=0&pd=4&ds=&de=&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so:dd,p:all,a:all&start="

        stopped = True
        start_num = 1
        news_num_per_page = 1
        list_found_news = []
        results = []

        while True:
            target_url = search_url + str(start_num)
            r, items_num = get_news_from_url(target_url)
            if r is None or items_num == 0:
                break

            list_found_news.extend(r)
            if len(list_found_news) >= news_num_per_page:
                for count in range(news_num_per_page):
                    title, href = list_found_news.pop(0)
                    results.append(title)

                stopped = True
                break

            start_num += items_num

        if stopped is not True and r is not None and len(r) > 0:
            title, href = list_found_news.pop(0)
            results.append(title + ' ' + href)

        return results

    except Exception as e:
        print("Error: ", e)
        return None


def get_news_from_url(url: str):
    try:
        html = requests.get(url).text
        soup = BeautifulSoup(html, 'html.parser')

        list_news = soup.find('ul', {'class': 'list_news'})
        if list_news is not None and len(list_news) > 0:
            list_news_area = soup.find_all('div', {'class': 'news_area'})
            list_keyword_news = []
            for news_area in list_news_area:
                news_tit = news_area.find('a', {'class': 'news_tit'})
                title = news_tit.attrs['title']
                href = news_tit.attrs['href']
                list_keyword_news.append([title, href])
            return list_keyword_news, len(list_news_area)

    except Exception as e:
        print("Error: ", e)

    return None, 0


if __name__ == '__main__':
    try:
        print()

        # 코스피 종목 코드
        kospi_tickers = stock.get_market_ticker_list(market="KOSPI")

        # 코스닥 종목 코드
        kosdaq_tickers = stock.get_market_ticker_list(market="KOSDAQ")

        # 코스피와 코스닥 종목 코드 합치기
        ticker_list = kospi_tickers + kosdaq_tickers

        document = Document()

        for ticker in ticker_list:
            stock_name = stock.get_market_ticker_name(ticker)
            print(stock_name)

            news_results = get_news(stock_name)
            if news_results is not None and len(news_results) > 0:
                for result in news_results:
                    if result.strip():
                        document.add_paragraph(result.strip())

            time.sleep(1)

        filename = datetime.now().strftime("%Y-%m-%d")
        document.save(filename + '.docx')

    except Exception as e:
        print("Error: ", e)
