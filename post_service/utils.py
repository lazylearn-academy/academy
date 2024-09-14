import smtplib
from config import POST_USER, POST_PWD


def verify_email(user, code):
    login = POST_USER
    password = POST_PWD
    sent_from = login
    to = user
    subject = "Email Verification on LazyLearn Academy"
    body = f"Your verification code: {code}"
    email_text = """
    From: %s
    To: %s
    Subject: %s
    %s
    """ % (sent_from, to, subject, body)
    smtp_server = smtplib.SMTP_SSL("smtp.timeweb.ru", 465)
    smtp_server.ehlo()
    smtp_server.login(login, password)
    smtp_server.sendmail(sent_from, to, email_text)
    smtp_server.close()
