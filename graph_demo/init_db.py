from graph_demo.database import engine, Base
from graph_demo.models import InvestmentRating

# 创建所有数据库表
Base.metadata.create_all(bind=engine)
print("数据库表创建成功!")