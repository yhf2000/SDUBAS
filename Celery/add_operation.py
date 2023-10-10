import datetime
import json
import pickle

from celery import Celery
from fastapi import Request
from service.user import OperationModel
from type.user import operation_interface, parameters_interface

broker = 'redis://127.0.0.1:6379/14'  # 消息队列
backend = 'redis://127.0.0.1:6379/15'  # 存储结果

add_operation_app = Celery(
    'tasks',
    broker=broker,
    backend=backend,
)
operation_model = OperationModel()


# 添加一个操作的异步任务，通过输入service_type, service_id, operation_type,func, parameters,oper_user_id；并通过获取parameters的函数来进行添加
@add_operation_app.task()
def add_operation(service_type, service_id, operation_type, func, parameters, oper_user_id):
    time = datetime.datetime.now()
    operation = operation_interface(service_type=service_type, service_id=service_id, operation_type=operation_type,
                                    func=func.replace('qpzm7913', time.strftime("%Y-%m-%d %H:%M:%S")),
                                    parameters=parameters,
                                    oper_user_id=oper_user_id, oper_dt=time)
    operation_model.add_operation(operation)
