from celery import Celery
import email.utils
import hashlib
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from service.user import OperationModel
from type.user import operation_interface
broker = 'redis://127.0.0.1:6379/5'
backend = 'redis://127.0.0.1:6379/6'

add_operation_app = Celery(
    'tasks',
    broker=broker,
    backend=backend,
)
operation_model = OperationModel()
@add_operation_app.task()
def add_operation(service_type, service_id, func, parameters, oper_user_id,
                  url):  # 添加一个操作的接口,url可通过current_path = request.url.path获得
    operation = operation_interface(service_type=service_type, service_id=service_id, func=func,
                                    parameters=parameters,
                                    oper_user_id=oper_user_id, url='http://127.0.0.1:8000' + url)
    operation_model.add_operation(operation)