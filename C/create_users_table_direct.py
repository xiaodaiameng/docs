import asyncio
import aiomysql

async def main():
    # 创建连接池
    pool = await aiomysql.create_pool(
        host='localhost',
        port=3306,
        user='root',
        password='123456',
        db='test',
        charset='utf8mb4'
    )
    
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # 首先删除已存在的表（如果有）
            await cur.execute("DROP TABLE IF EXISTS users;")
            
            # 直接使用SQL语句创建users表
            create_table_sql = """
            CREATE TABLE users (
                id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
                username VARCHAR(12) UNIQUE NOT NULL COMMENT '用户名',
                password VARCHAR(100) NOT NULL COMMENT '密码(密文)',
                role ENUM('student', 'admin') NOT NULL DEFAULT 'student' COMMENT '角色',
                status BOOLEAN NOT NULL DEFAULT TRUE COMMENT '状态(正常/禁用)',
                realname VARCHAR(10) NOT NULL COMMENT '真实姓名',
                email VARCHAR(50) UNIQUE NOT NULL COMMENT '邮箱',
                create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
            );
            """
            
            await cur.execute(create_table_sql)
            await conn.commit()
            print("users表已成功创建！")
    
    pool.close()
    await pool.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())