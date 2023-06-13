import os
import re
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from docx import Document
from pykrx import stock
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


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


def send_email(sender_email, sender_password, receiver_email, subject, message, file_path):
    # SMTP 서버 설정
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    # MIME 멀티파트 메시지 생성
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # 메일 내용 추가
    msg.attach(MIMEText(message, 'plain'))

    # 파일 첨부
    attachment = open(file_path, 'rb')
    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % file_path)
    msg.attach(part)

    # SMTP 서버에 연결하여 이메일 보내기
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, receiver_email, msg.as_string())
    server.quit()


if __name__ == '__main__':
    try:
        start_time = time.time()  # 시작 시간 기록
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
        end_time = time.time()  # 종료 시간 기록
        elapsed_time = end_time - start_time  # 총 걸린 시간 계산
        print("총 걸린 시간:", elapsed_time, "초")

        filename = datetime.now().strftime("%Y-%m-%d")
        document.save(filename + '.docx')

        # Gmail 계정 정보 및 이메일 설정
        sender_email = 'jjmjh214@gmail.com'
        sender_password = 'vjacdipnxumpoycn'  # 구글 앱 비밀번호
        receiver_email = 'jjmjh214@gmail.com'
        subject = '첨부 파일 테스트'
        message = '안녕하세요, 파일 첨부 테스트입니다.'
        file_path = f'{filename}.docx'

        # 이메일 보내기
        send_email(sender_email, sender_password, receiver_email, subject, message, file_path)

    except Exception as e:
        print("Error: ", e)
