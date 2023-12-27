import os
run_mode = os.environ.get("SDUBAS_RUN_MODE")
host_ip = os.environ.get("host_ip")
if run_mode == 'dev':
    SQLALCHEMY_DATABASE_URL = "mysql+pymysql://sdubas:sdubas@localhost:3306/sdubas"
    SQLALCHEMY_DATABASE_URL_MASTER = "mysql+pymysql://SDUBAS-admin:SDUBASmysql123!@localhost:3306/SDUBAS"
    SQLALCHEMY_DATABASE_URL_SLAVE = "mysql+pymysql://SDUBAS-admin:SDUBASmysql123!@localhost:3306/SDUBAS"
    # SQLALCHEMY_DATABASE_URL = "mysql+pymysql://handsome_boy:SDUBASmysql123!@43.138.34.119:3306/"
    development_ip = '127.0.0.1'
    server_ip = "43.138.34.119"
    base_url = "http://172.16.2.6:8000"
    redis_password = 'SDUBASredis123!'
else:
    SQLALCHEMY_DATABASE_URL = "mysql+pymysql://sdubas:sdubas@localhost:3306/sdubas"
    SQLALCHEMY_DATABASE_URL_MASTER = "mysql+pymysql://SDUBAS-admin:SDUBASmysql123!@172.16.2.6:3306/SDUBAS"
    SQLALCHEMY_DATABASE_URL_SLAVE = "mysql+pymysql://SDUBAS-admin:SDUBASmysql123!@localhost:3306/SDUBAS"
    # SQLALCHEMY_DATABASE_URL = "mysql+pymysql://handsome_boy:SDUBASmysql123!@43.138.34.119:3306/"
    development_ip = '127.0.0.1'
    server_ip = "111.15.182.56:41011"
    base_url = f"http://{host_ip}:8000"
    redis_password = 'SDUBASredis123!'
