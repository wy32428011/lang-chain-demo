import asyncio
import json
import os
from typing import List

import pandas as pd
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from graph_demo import llm_init
from graph_demo.database import get_db
from graph_demo.llm_init import get_agent
from graph_demo.models import InvestmentRating
from stock_trade.demo_stock import get_executor, process_stock_chunk

stock_router = APIRouter()
class ReportParam(BaseModel):
    symbol: str = Field(..., description="股票代码")

class InvestmentRatingResponse(BaseModel):
    id: int
    symbol: str
    name: str
    rating: str
    current_price: float
    target_price: float
    analysis_date: str
    created_at: str

class PaginatedResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[InvestmentRatingResponse]
@stock_router.post("/stock")
def get_stock_report(param: ReportParam):
    """
    获取股票报告
    :param param: 股票编码
    :return: 股票报告
    """
    executor = get_executor()
    result = executor.invoke({"input": f"请分析 股票 {param.symbol} 的近期行情"})
    print(result["output"])
    return json.loads(result["output"])

class RatingQueryParams(BaseModel):
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页大小")

@stock_router.post("/ratings")
def get_investment_ratings(
    params: RatingQueryParams,
):
    """
    获取投资评级列表（分页）
    :param params: 分页参数
    :return: 分页的投资评级列表
    """
    db: Session = next(get_db())
    # 计算偏移量
    offset = (params.page - 1) * params.page_size
    
    # 获取总记录数
    total = db.query(InvestmentRating).count()
    
    # 获取分页数据
    ratings = db.query(InvestmentRating).order_by(InvestmentRating.created_at.desc()).offset(offset).limit(params.page_size).all()
    
    # 转换日期字段为字符串格式
    items = []
    for rating in ratings:
        items.append({
            "id": rating.id,
            "symbol": rating.symbol,
            "name": rating.name,
            "rating": rating.rating,
            "current_price": rating.current_price,
            "target_price": rating.target_price,
            "analysis_date": rating.analysis_date.isoformat() if rating.analysis_date else None,
            "created_at": rating.created_at.isoformat() if rating.created_at else None
        })
    
    # 计算总页数
    total_pages = (total + params.page_size - 1) // params.page_size
    
    return {
        "total": total,
        "page": params.page,
        "page_size": params.page_size,
        "total_pages": total_pages,
        "items": items
    }

@stock_router.post("/agent")
def get_agent_report(param: ReportParam):
    """
    获取股票报告
    :param param: 股票编码
    :return: 股票报告
    """
    # agent = get_agent()
    # # result = agent.invoke({"messages": [{"role": "user", "content": f"分析股票{param.symbol}的行情"}]},)
    # # print(result["structured_response"])
    # # return result["structured_response"]
    # # 读取整个CSV文件
    # df = pd.read_csv('A股股票列表.csv',
    #                  encoding='utf-8',
    #                  dtype={'代码': str, '名称': str})
    # # 提取单列数据（通过列名）
    # column_data = df['代码']  # 例如 df['股票代码']
    # # 转换为列表
    # stock_codes = column_data.tolist()
    # res_list = []
    # for step in agent.stream({"messages": [{"role": "user", "content": f"分析股票{param.symbol}的行情"}]},
    #                          stream_mode="values",):
    #     res_list.append(step)
    #     step["messages"][-1].pretty_print()
    # # print(res_list)
    # return res_list[-1]["structured_response"]
    return process_stock_chunk(param.symbol)

@stock_router.post("/graph")
def get_stock_by_graph(code: str):

    return asyncio.run(llm_init.graph_stock(code))

@stock_router.post("/chain")
def get_stock_by_chain(code: str):
    return process_stock_chunk(code)



def get_all_stock_report():
    """
    获取所有股票报告
    :return: 所有股票报告
    """

    agent = get_agent()
    # 读取整个CSV文件
    df = pd.read_csv('../demo/A股股票列表.csv',
                     encoding='utf-8',
                     dtype={'代码': str, '名称': str})
    # 提取单列数据（通过列名）
    column_data = df['代码']  # 例如 df['股票代码']
    # 转换为列表
    stock_codes = column_data.tolist()

    for code in stock_codes:
        res_list = []
        for step in agent.stream({"messages": [{"role": "user", "content": f"分析股票{code}的行情"}]},
                                 stream_mode="values",):
            res_list.append(step)
            step["messages"][-1].pretty_print()
        # print(res_list[-1]["structured_response"])
        # return res_list[-1]["structured_response"]
        print(res_list[-1]["structured_response"])
        result = res_list[-1]["structured_response"]
        if result['investment_rating']  == "买入" or result['investment_rating']  == "强烈买入":
            # 将分析结果保存到文件
            from datetime import datetime

            current_date = datetime.now().strftime("%Y%m%d")
            filename = f"{code}_{current_date}.txt"

            # 确保output目录存在
            output_dir = os.path.join(os.path.dirname(__file__), "output")
            os.makedirs(output_dir, exist_ok=True)

            file_path = os.path.join(output_dir, filename)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(result["output"])


if __name__ == "__main__":
    get_all_stock_report()
