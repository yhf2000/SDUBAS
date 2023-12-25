import datetime
import json
import re
from celery import Celery
from sqlalchemy import func

from const import development_ip, redis_password
from service.user import OperationModel
from type.functions import block_chains_login, block_chains_upload, block_chains_judge_complete, get_user_name, \
    get_time_now
from type.user import operation_interface

broker = f'redis://:{redis_password}@127.0.0.1:6379/14'  # 消息队列
backend = f'redis://:{redis_password}@127.0.0.1:6379/15'  # 存储结果
add_operation_app = Celery(
    'tasks',
    broker=broker,
    backend=backend,
)
operation_model = OperationModel()


# 添加一个操作的异步任务，通过输入service_type, service_id, operation_type,func, parameters,oper_user_id；并通过获取parameters的函数来进行添加
@add_operation_app.task()
def add_operation(service_type, service_id, operation_type, funcs, parameters, oper_user_id):
    id_pattern = r'用户(\d+)'
    ids = re.findall(id_pattern, funcs)
    for id in ids:
        username = get_user_name(int(id))
        funcs = funcs.replace(id, username, 1)
    time = datetime.datetime.utcfromtimestamp(get_time_now('days', 0))
    keys_to_check = ['password', 'new_password', 'old_password']
    for key in keys_to_check:
        if key in parameters['para']:
            parameters['para'][key] = ''
    for key in keys_to_check:
        if key in parameters['body']:
            parameters['body'][key] = ''
    str = time.strftime("%Y-%m-%d %H:%M:%S") +f"访问{parameters['url']}输入参数{parameters['para'] if parameters['body'] == '' else parameters['body']}"
    funcs = funcs.replace('xxx', str)
    operation = operation_interface(service_type=service_type, service_id=service_id, operation_type=operation_type,
                                    func=funcs,
                                    parameters=json.dumps(parameters,ensure_ascii=False),
                                    oper_user_id=oper_user_id, oper_dt=time)
    oper_hash = operation.get_oper_hash()
    operation.oper_hash = oper_hash
    headers = block_chains_login()
    receipt = block_chains_upload(oper_hash, funcs, headers)
    block_chains_judge_complete(receipt, headers)
    operation_model.add_operation(operation)