import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

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

# Gmail 계정 정보 및 이메일 설정
sender_email = 'jjmjh214@gmail.com'
sender_password = 'vjacdipnxumpoycn'#구글 앱 비밀번호
receiver_email = 'jjmjh214@gmail.com'
subject = '첨부 파일 테스트'
message = '안녕하세요, 파일 첨부 테스트입니다.'
file_path = 'C:/Users/Moon/Desktop/python연습/p4.py'

# 이메일 보내기
send_email(sender_email, sender_password, receiver_email, subject, message, file_path)
