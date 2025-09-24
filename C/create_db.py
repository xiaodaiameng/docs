import pymysql
from pymysql.cursors import DictCursor

# 数据库连接配置
config = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'charset': 'utf8mb4'
}

# 创建数据库的SQL语句
create_db_sql = "CREATE DATABASE IF NOT EXISTS test DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_unicode_ci;"

# 尝试连接MySQL服务器并创建数据库
try:
    # 连接到MySQL服务器（不指定数据库）
    connection = pymysql.connect(**config, cursorclass=DictCursor)
    print("成功连接到MySQL服务器")
    
    # 创建游标对象
    with connection.cursor() as cursor:
        # 执行创建数据库语句
        cursor.execute(create_db_sql)
        print("成功创建test数据库")
    
    # 提交事务
    connection.commit()
    
    # 关闭连接
    connection.close()
    print("MySQL连接已关闭")
    
    # 尝试连接刚创建的test数据库
    test_config = config.copy()
    test_config['database'] = 'test'
    
    test_connection = pymysql.connect(**test_config, cursorclass=DictCursor)
    print("成功连接到test数据库")
    test_connection.close()
    print("test数据库连接已关闭")
    
    print("test数据库创建和验证完成")
    
except Exception as e:
    print(f"创建数据库时发生错误: {str(e)}")
    print("请检查MySQL服务是否正在运行，以及用户名和密码是否正确")