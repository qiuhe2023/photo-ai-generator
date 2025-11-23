import os
import pymysql
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 从环境变量中获取数据库配置
database_url = os.getenv('DATABASE_URL')
print(f"尝试连接数据库: {database_url}")

# 解析数据库URL
connection = None
try:
    # 从URL中提取连接信息
    db_info = database_url.replace('mysql+pymysql://', '')
    user_pass, host_db = db_info.split('@')
    user, password = user_pass.split(':')
    host_port, db_name = host_db.split('/')
    host, port = host_port.split(':')
    
    # 首先连接到MySQL服务器（不指定数据库）
    print(f"尝试连接到MySQL服务器: {host}:{port} 用户名: {user}")
    connection = pymysql.connect(
        host=host,
        port=int(port),
        user=user,
        password=password,
        cursorclass=pymysql.cursors.DictCursor
    )
    
    # 检查并创建数据库
    with connection.cursor() as cursor:
        # 检查数据库是否存在
        cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")
        result = cursor.fetchone()
        
        if not result:
            print(f"数据库 {db_name} 不存在，正在创建...")
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"数据库 {db_name} 创建成功！")
        else:
            print(f"数据库 {db_name} 已存在")
    
    # 关闭当前连接
    connection.close()
    
    # 重新连接到指定的数据库
    print(f"尝试连接到数据库 {db_name}...")
    connection = pymysql.connect(
        host=host,
        port=int(port),
        user=user,
        password=password,
        database=db_name,
        cursorclass=pymysql.cursors.DictCursor
    )
    
    print("数据库连接成功！")
    
    # 测试查询
    with connection.cursor() as cursor:
        # 尝试执行一个简单的查询
        cursor.execute("SELECT 1 AS test")
        result = cursor.fetchone()
        print(f"查询测试成功，结果: {result}")
        
    print("数据库配置正确，连接测试通过！")
    
except Exception as e:
    print(f"数据库操作失败: {str(e)}")
    print("请检查以下几点:")
    print("1. MySQL服务是否已启动")
    print("2. 用户名(root)和密码(12345)是否正确")
    print("3. MySQL配置是否允许root用户本地连接")
finally:
    if connection:
        connection.close()
        print("数据库连接已关闭。")