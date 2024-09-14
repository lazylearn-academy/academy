import smtplib
from email.mime.text import MIMEText
from email.header import Header
from config import POST_USER, POST_PWD


def verify_email(user, code):
    login = POST_USER
    password = POST_PWD
    to = user
    subject = "Верификация в LazyLearn Academy"
    body = f"Ваш код подтверждения: {code}"
    msg = MIMEText(body, 'plain', 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = login
    msg['To'] = to
    smtp_server = smtplib.SMTP_SSL("smtp.timeweb.ru", 465)
    smtp_server.ehlo()
    smtp_server.login(login, password)
    smtp_server.sendmail(login, to, msg.as_string())
    smtp_server.close()
