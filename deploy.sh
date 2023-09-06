#!/bin/bash
sudo su
current_directory=$(pwd)
cd /usr/local
wget http://download.redis.io/releases/redis-6.2.5.tar.gz
tar -zvxf redis-6.2.5.tar.gz
mv redis-6.2.5 redis/
cd redis/
make
make install
cd /usr/local/bin
cd /usr/local/redis
cp redis.conf redis.conf.bak
cd /usr/local/bin
redis-server /usr/local/redis/redis.conf

sudo apt update
sudo apt install mysql-server
sudo /etc/init.d/mysql start
sudo mysql_secure_installation

pip install -r requirements.txt

gnome-terminal -t " send_email" -x bash -c "celery -A Celery.send_email worker --loglevel=INFO -P eventlet;exec bash;"
gnome-terminal -t " add_operation" -x bash -c "celery -A Celery.add_operation worker --loglevel=INFO -P eventlet;exec bash;"
