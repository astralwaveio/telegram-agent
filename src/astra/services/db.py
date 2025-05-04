# 数据库服务
import sqlite3
import os

DB_PATH = os.getenv("DATABASE_URL", "data/astra.db").replace("sqlite:///", "")

def get_connection():
    return sqlite3.connect(DB_PATH)
