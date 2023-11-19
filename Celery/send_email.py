import email.utils
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from celery import Celery
from const import development_ip
from service.user import SessionModel

broker = f'redis://{development_ip}:6379/12'
backend = f'redis://{development_ip}:6379/13'
send_email_app = Celery(
    'tasks',
    broker=broker,
    backend=backend,
)

session_model = SessionModel()


# 异步发送邮件，Email为邮箱，token可能为token或token_s6，type为发送邮箱时的操作类型
@send_email_app.task()
def send_email(Email, token, type):
    mail = MIMEMultipart()
    mail_content = ''
    if type == 0:  # 用户激活
        mail_content = '''
                    <p>欢迎激活!</p>
                    <p>您的验证码为:{}</p>
                    '''.format(token)
        mail['Subject'] = '欢迎激活'
    elif type == 1:  # 修改绑定邮箱
        mail_content = '''
                    <p>修改绑定邮箱!</p>
                    <p>您的验证码为:{}</p>
                    '''.format(token)
        mail['Subject'] = '修改绑定邮箱'
    elif type == 2:  # 找回密码时发送链接
        username = session_model.get_user_name_by_token(token)[0]
        mail_content = '''
                <p>找回密码!</p>
                <p><a href="http://{}/c/set_password/{}/{}" target=blank>www.SDUBAS.com</a>，\
                请点击该链接设置密码！</p>
                '''.format(f'{development_ip}', username, token)
        mail['Subject'] = '找回密码'
    mail.attach(MIMEText(mail_content, 'html', 'utf-8'))
    mail['To'] = email.utils.formataddr(('您好', Email))
    mail['From'] = email.utils.formataddr(('SDUBAS', '13244445877@163.com'))  # 偶滴邮箱
    server = smtplib.SMTP_SSL('smtp.163.com', 465)
    server.login('13244445877@163.com', 'WZJQYMRTBMKUNGYL')
    server.set_debuglevel(True)
    try:
        server.sendmail('13244445877@163.com', Email, msg=mail.as_string())  # 发送邮箱
    finally:
        server.quit()
