import os
import re
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from docx import Document
from pykrx import stock

os.system('cls||clear')


def get_news(url: str, keyword: str):
    list_keyword_news = list()
    list_news_area = list()
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
    except:
        return None, 0

    return list_keyword_news, len(list_news_area)


if __name__ == '__main__':
    try:
        print()

        # 코스피 종목 코드
        kospi_tickers = stock.get_market_ticker_list(market="KOSPI")

        # 코스닥 종목 코드
        kosdaq_tickers = stock.get_market_ticker_list(market="KOSDAQ")

        # 코스피와 코스닥 종목 코드 합치기
        ticker_list = kospi_tickers + kosdaq_tickers

        # 종목 코드를 종목명으로 변환
        a = [stock.get_market_ticker_name(ticker) for ticker in ticker_list]

        document = Document()

        for i in a:
            search_keyword = i
            quote_keyword = requests.utils.quote(search_keyword)
            search_url = f"https://search.naver.com/search.naver?where=news&sm=tab_pge&query={quote_keyword}&sort=1&photo=0&field=0&pd=4&ds=&de=&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so:dd,p:all,a:all&start="

            stopped = True
            start_num = 1
            news_num_per_page = 1
            list_found_news = list()
            results = list()
            print('', end='')

            while True:
                print('', end='')
                target_url = search_url + str(start_num)
                r, items_num = get_news(target_url, search_keyword)
                if r is None or items_num == 0:
                    print()
                    break

                list_found_news.extend(r)
                if len(list_found_news) >= news_num_per_page:
                    print()
                    for count in range(news_num_per_page):
                        title, href = list_found_news.pop(0)
                        results.append(title)
                        print(title)

                    stopped = True
                    break

                print(' ', end='')
                start_num += items_num

            if stopped is not True and r is not None and len(r) > 0:
                title, href = list_found_news.pop(0)
                results.append(title + ' ' + href)
                print(title + href)

            combined_results = '\n'.join(results)
            cleaned_results = re.sub(r'\n{2,}', '\n', combined_results)

            for result in results:
                if result.strip():
                    document.add_paragraph(result.strip())

            time.sleep(1)
            print(i)

        filename = datetime.now().strftime("%Y-%m-%d")
        document.save(filename + '.docx')

    except Exception as e:
        print("Error: ", e)
