from sqlalchemy import Column, Integer, String, DateTime, JSON, Float
from .database import Base
from datetime import datetime


class InvestmentRating(Base):
    __tablename__ = "investment_ratings"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), index=True, nullable=False)  # 股票代码
    name = Column(String(100))  # 股票名称
    rating = Column(String(20), nullable=False)  # 投资评级
    current_price = Column(Float)
    target_price = Column(Float)
    analysis_date = Column(DateTime, default=datetime.utcnow)  # 分析日期
    created_at = Column(DateTime, default=datetime.now())  # 记录创建时间
    result_json = Column(JSON)
