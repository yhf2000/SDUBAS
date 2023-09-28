#!/bin/bash
sudo su
sudo apt update
sudo apt install rpm
sudo apt install dnf

sudo apt-get install -y redis-server
sudo vim /etc/redis/redis/redis.conf

sudo apt install mysql-server
sudo /etc/init.d/mysql start
sudo mysql_secure_installation

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

gnome-terminal -t " send_email" -x bash -c "celery -A Celery.send_email worker --loglevel=INFO -P eventlet;exec bash;"
gnome-terminal -t " add_operation" -x bash -c "celery -A Celery.add_operation worker --loglevel=INFO -P eventlet;exec bash;"