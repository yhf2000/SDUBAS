CREATE USER 'replication_root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'SDUBASmysql123!';
CREATE USER 'replication_root'@'43.138.34.119' IDENTIFIED WITH mysql_native_password BY 'SDUBASmysql123!';
GRANT REPLICATION SLAVE ON *.* TO 'replication_root'@'localhost';
GRANT REPLICATION SLAVE ON *.* TO 'replication_root'@'43.138.34.119';
FLUSH PRIVILEGES;

