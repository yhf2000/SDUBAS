#!/bin/bash
sudo su
sudo apt update
sudo apt install rpm
sudo apt install dnf
sudo apt install uvicorn

sudo apt-get install -y redis-server
sudo vim /etc/redis/redis.conf
# 将daemonize修改为yes，将127.0.0.1改为0.0.0.0，将protect mode改为no
sudo chmod 777 /etc
sudo systemctl restart redis
redis-server --protected-mode no --daemonize yes

sudo apt install mysql-server
sudo /etc/init.d/mysql start
sudo mysql -u root -p
CREATE DATABASE SDUBAS;
CREATE USER 'handsome_boy'@'%' IDENTIFIED BY 'SDUBASmysql123!';
#用户名和密码
GRANT ALL PRIVILEGES ON SDUBAS.* TO 'handsome_boy'@'%';
flush privileges;
exit;
sudo vim /etc/mysql/mysql.conf.d/mysqld.cnf
# server-id=1
# log_bin=mysql-bin
sudo service mysql restart
sudo mysql_secure_installation
sudo systemctl restart mysql


wget https://dl.min.io/server/minio/release/linux-amd64/archive/minio-20230920224955.0.0.x86_64.rpm -O minio.rpm
sudo dnf install minio.rpm
mkdir ~/minio
chmod +x minio
chmod 777 ~/minio
mkdir data
cd data
touch minio.log
sudo apt install mc
nohup minio server  ~/minio/data > ~/minio/data/minio.log 2>&1 &

#配置用户名和密码(将xxx替换掉)
export MINIO_ACCESS_KEY=   xxx
export MINIO_SECRET_KEY=   xxx

pip install -r requirements.txt
vim ~/.bashrc
#在最后一行添加下述路径
export PYTHONPATH=$PYTHONPATH:~/SDUBAS-backend
export PATH=$PATH:~/SDUBAS-frontend
source ~/.bashrc

cd ~/SDUBAS-backend
python3 db_init.py
nohup python3 main.py > /dev/null 2>&1 &

sudo apt install npm
sudo apt install nodejs
sudo npm install -g n
sudo n 18.16.1
sudo npm install yarn -g
ln -s /usr/local/bin/node/yarn /usr/local/bin/yarn
cd ~/SDUBAS-frontend
yarn add all
yarn build
yarn global add serve
sudo apt-get install nginx
sudo systemctl start nginx
sudo vim /etc/nginx/sites-available/default
#添加以下内容：location / {# First attempt to serve request as file, then# as directory, then fall back to displaying a 404.root /home/ubuntu/SDUBAS-frontend/build;index index.html;try_files $uri $uri/ =404;}
sudo vim /etc/nginx/nginx.conf
#将user改为root

nohup celery -A Celery.upload_file worker --loglevel=INFO -P eventlet > upload_file_celery.log 2>&1 &
nohup celery -A Celery.send_email worker --loglevel=INFO -P eventlet > send_email_celery.log 2>&1 &
nohup celery -A Celery.add_operation worker --loglevel=INFO -P eventlet > add_operation_celery.log 2>&1 &
