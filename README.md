# SDUBAS-backend
Blockchain based Academic System
## 每个异步任务均需单独使用一个终端
## 执行发送邮箱验证码异步任务的命令：
celery -A Celery.send_email worker --loglevel=INFO -P eventlet 
## 执行添加操作异步任务的命令：
celery -A Celery.add_operation worker --loglevel=INFO -P eventlet
## 加密方法：
### 密码加密方法：sha256，salt为用户的注册时间
### 操作加密方法：sha256，返回散列值的十六进制表示
### token：生成一个随机 UUID 并返回它的十六进制表示
### token_s6：生成六位随机数字
