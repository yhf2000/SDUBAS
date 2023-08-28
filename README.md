# SDUBAS-backend
Blockchain based Academic System
## 每个异步任务均需单独使用一个终端
## 执行发送邮箱验证码异步任务的指令：
celery -A Celery.send_email worker --loglevel=INFO -P eventlet 
## 执行添加操作异步任务的指令：
celery -A Celery.add_operation worker --loglevel=INFO -P eventlet
