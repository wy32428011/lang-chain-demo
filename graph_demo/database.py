from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# MySQL数据库配置
MYSQL_USER = os.getenv('MYSQL_USER', 'root')  # 替换为你的MySQL用户名
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'root')  # 替换为你的MySQL密码
MYSQL_HOST = os.getenv('MYSQL_HOST', '192.168.50.205')
MYSQL_PORT = os.getenv('MYSQL_PORT', '3306')
MYSQL_DB = os.getenv('MYSQL_DB', 'investment_ratings')

# 创建数据库连接
DATABASE_URL = f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 数据库依赖项
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
