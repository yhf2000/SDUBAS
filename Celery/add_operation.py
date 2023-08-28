import json
from celery import Celery
from service.user import OperationModel
from type.user import operation_interface, parameters_interface

broker = 'redis://127.0.0.1:6379/5'
backend = 'redis://127.0.0.1:6379/6'

add_operation_app = Celery(
    'tasks',
    broker=broker,
    backend=backend,
)
operation_model = OperationModel()


# 添加一个操作的接口
@add_operation_app.task()
def add_operation(service_type, service_id, func, parameters, oper_user_id):
    operation = operation_interface(service_type=service_type, service_id=service_id, func=func,
                                    parameters=parameters,
                                    oper_user_id=oper_user_id)
    operation_model.add_operation(operation)
