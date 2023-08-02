from celery import Celery
import email.utils
import hashlib
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
broker = 'redis://127.0.0.1:6379/4'
backend = 'redis://127.0.0.1:6379/3'
send_email_app = Celery(
    'tasks',
    broker=broker,
    backend=backend,
)


@send_email_app.task()
def send_email(Email, token):  # 异步发送邮件
    mail = MIMEMultipart()
    mail_content = '''
    <p>欢迎注册!</p>
    <p>您的验证码为:{}</p>
    '''.format(token)
    mail.attach(MIMEText(mail_content, 'html', 'utf-8'))
    mail['To'] = email.utils.formataddr(('小帅比', Email))
    mail['From'] = email.utils.formataddr(('大帅比', '13244445877@163.com'))
    mail['Subject'] = '欢迎注册'
    server = smtplib.SMTP_SSL('smtp.163.com', 465)
    server.login('13244445877@163.com', 'WZJQYMRTBMKUNGYL')
    server.set_debuglevel(True)
    try:
        server.sendmail('13244445877@163.com', Email, msg=mail.as_string())
    finally:
        server.quit()
