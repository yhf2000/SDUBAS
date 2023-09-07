#!/bin/bash
sudo su
sudo apt update

current_directory=$(pwd)
sudo apt-get install -y redis-server
sudo vim /etc/redis/redis/redis.conf

sudo apt install mysql-server
sudo /etc/init.d/mysql start
sudo mysql_secure_installation

pip install -r requirements.txt

gnome-terminal -t " send_email" -x bash -c "celery -A Celery.send_email worker --loglevel=INFO -P eventlet;exec bash;"
gnome-terminal -t " add_operation" -x bash -c "celery -A Celery.add_operation worker --loglevel=INFO -P eventlet;exec bash;"
