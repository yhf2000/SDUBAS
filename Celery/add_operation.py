from celery import Celery

from service.user import OperationModel
from type.user import operation_interface

broker = 'redis://127.0.0.1:6379/5'  # 消息队列
backend = 'redis://127.0.0.1:6379/6'  # 存储结果

add_operation_app = Celery(
    'tasks',
    broker=broker,
    backend=backend,
)
operation_model = OperationModel()


# 添加一个操作的异步任务，通过输入service_type, service_id, func, oper_user_id；并通过获取parameters的函数来进行添加
@add_operation_app.task()
def add_operation(service_type, service_id, func, parameters, oper_user_id):
    operation = operation_interface(service_type=service_type, service_id=service_id, func=func,
                                    parameters=parameters,
                                    oper_user_id=oper_user_id)
    operation_model.add_operation(operation)
