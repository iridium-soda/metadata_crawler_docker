"""
To check if the database is working properly.
"""

from pymongo import MongoClient
import os

# MongoDB连接信息
host = "localhost"
port = 27017  # 你的MongoDB容器映射的端口
username = None  # 如果有用户名，设置为相应的值
password = None  # 如果有密码，设置为相应的值


# 构建MongoDB连接URI
mongo_host = "localhost"
mongo_port = int(os.getenv("mongo", 27017))
database_name = "analysis_db"

# 尝试连接MongoDB
try:
    client = MongoClient(mongo_host, mongo_port)
    db = client[database_name]
    print("成功连接到MongoDB")
    print(f"MongoDB版本: {client.server_info()['version']}")
except Exception as e:
    print(f"连接失败: {e}")
finally:
    if "client" in locals():
        client.close()
