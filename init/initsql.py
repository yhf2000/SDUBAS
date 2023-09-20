import os
import mysql.connector
import json

file_path = './config.json'
with open(file_path, 'r') as file:
    json_data = file.read()

# 解析 JSON 数据
data = json.loads(json_data)
data = data['database']
# 建立数据库连接
conn = mysql.connector.connect(
    host=data['host'],
    user=data['user'],
    password=data['password'],
    database=data['database'],
    port=data['port']
)

# 创建游标对象
cursor = conn.cursor()

# 指定SQL文件所在的目录
sql_directory = './sql/'

# 遍历目录下的所有.sql文件
for filename in os.listdir(sql_directory):
    if filename.endswith(".sql"):
        file_path = os.path.join(sql_directory, filename)

        # 打开.sql文件并读取SQL语句
        with open(file_path, 'r', encoding='utf-8') as file:
            sql_statements = file.read().split(';')

            # 执行每个SQL语句
            for sql_statement in sql_statements:
                sql_statement = sql_statement.strip()

                if sql_statement:
                    cursor.execute(sql_statement)
                    conn.commit()

# 关闭游标和数据库连接
cursor.close()
conn.close()
