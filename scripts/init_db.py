# 初始化数据库脚本
import sqlite3
import os

DB_PATH = os.getenv("DATABASE_URL", "data/astra.db").replace("sqlite:///", "")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # 创建用户表
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        username TEXT
    )
    ''')
    # 创建消息表
    c.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        text TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()
    print("数据库初始化完成")

if __name__ == "__main__":
    init_db()
