import datetime
import json
import re

from celery import Celery
from const import development_ip, redis_password
from service.user import OperationModel
from type.functions import block_chains_login, block_chains_upload, block_chains_judge_complete, get_user_name
from type.user import operation_interface

broker = f'redis://:{redis_password}@172.16.2.10:6379/14'  # 消息队列
backend = f'redis://:{redis_password}@172.16.2.10:6379/15'  # 存储结果

add_operation_app = Celery(
    'tasks',
    broker=broker,
    backend=backend,
)
operation_model = OperationModel()


# 添加一个操作的异步任务，通过输入service_type, service_id, operation_type,func, parameters,oper_user_id；并通过获取parameters的函数来进行添加
@add_operation_app.task()
def add_operation(service_type, service_id, operation_type, func, parameters, oper_user_id):
    id_pattern = r'用户(\d+)'
    ids = re.findall(id_pattern, func)
    for id in ids:
        username = get_user_name(int(id))
        func = func.replace(id, username, 1)
    time = datetime.datetime.now()
    str = time.strftime("%Y-%m-%d %H:%M:%S") +f"访问{parameters['url']}输入参数{parameters['para'] if parameters['body'] == '' else parameters['body']}"
    func = func.replace('xxx', str)
    operation = operation_interface(service_type=service_type, service_id=service_id, operation_type=operation_type,
                                    func=func,
                                    parameters=json.dumps(parameters,ensure_ascii=False),
                                    oper_user_id=oper_user_id, oper_dt=time)
    oper_hash = operation.get_oper_hash()
    operation.oper_hash = oper_hash
    headers = block_chains_login()
    receipt = block_chains_upload(oper_hash, func, headers)
    block_chains_judge_complete(receipt, headers)
    operation_model.add_operation(operation)
