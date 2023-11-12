FROM python:3.10
# 安装系统依赖
RUN apt-get update && apt-get install -y \
    sudo \
    apt-utils \
    rpm \
    dnf \
    uvicorn \
    redis-server \
    mysql-server \
    nginx \
    npm \
    nodejs\
    mc\
    
RUN sed -i 's/daemonize no/daemonize yes/g' /etc/redis/redis.conf \
    && sed -i 's/protected-mode yes/protected-mode no/g' /etc/redis/redis.conf \
    && echo "密码" >> /etc/redis/redis.conf
RUN chmod 777 /etc
CMD systemctl restart redis
CMD redis-server --protected-mode no --daemonize yes

RUN /etc/init.d/mysql start
RUN mysql -u root -p -e "CREATE DATABASE SDUBAS;"
RUN mysql -u root -p -e "CREATE USER 'handsome_boy'@'%' IDENTIFIED BY 'SDUBASmysql123!'; \
GRANT ALL PRIVILEGES ON SDUBAS.* TO 'handsome_boy'@'%'; \
FLUSH PRIVILEGES;"
RUN service mysql restart
RUN mysql_secure_installation
RUN systemctl restart mysql

RUN wget https://dl.min.io/server/minio/release/linux-amd64/archive/minio-20230920224955.0.0.x86_64.rpm -O minio.rpm \
    && dnf install -y minio.rpm
RUN mkdir -p /root/minio/data && chmod 777 /root/minio/data
WORKDIR /data
RUN touch minio.log
CMD nohup minio server ~/minio/data > ~/minio/data/minio.log 2>&1 &
ENV MINIO_ACCESS_KEY xxx
ENV MINIO_SECRET_KEY xxx

WORKDIR /home/ubuntu
RUN git clone https://gitee.com/mozhongdashuaibi/SDUBAS-backend.git
RUN git clone https://gitee.com/mozhongdashuaibi/SDUBAS-frontend.git

USER root
RUN echo "export PYTHONPATH=$PYTHONPATH:~/SDUBAS-backend" >> ~/.bashrc \
    && echo "export PATH=$PATH:~/SDUBAS-frontend" >> ~/.bashrc \
    && source ~/.bashrc
WORKDIR /home/ubuntu/SDUBAS-backend
RUN pip install -r requirements.txt
RUN python3 db_init.py
RUN nohup python3 main.py > /dev/null 2>&1 &

RUN npm install -g n && n 18.16.1
RUN npm install -g yarn
RUN ln -s /usr/local/bin/node/yarn /usr/local/bin/yarn
WORKDIR /home/ubuntu/SDUBAS-frontend
RUN yarn add all \
    && yarn build
RUN yarn global add serve
RUN service nginx start
RUN sed -i 's/# First attempt to serve request as file, then/# First attempt to serve request as file, then\n\t# as directory, then fall back to displaying a 404.\n\troot \/home\/ubuntu\/SDUBAS-frontend\/build;\n\tindex index.html;\n\ttry_files $uri $uri\/ =404;/g' /etc/nginx/sites-available/default
RUN sed -i 's/user nginx;/user root;/g' /etc/nginx/nginx.conf

CMD 
    celery -A Celery.upload_file worker --loglevel=INFO -P eventlet > upload_file_celery.log 2>&1 & \
    celery -A Celery.send_email worker --loglevel=INFO -P eventlet > send_email_celery.log 2>&1 & \
    celery -A Celery.add_operation worker --loglevel=INFO -P eventlet > add_operation_celery.log 2>&1 & 