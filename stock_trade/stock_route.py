import json
import os

import pandas as pd
from fastapi import APIRouter
from pydantic import BaseModel, Field

from graph_demo.llm_init import get_agent
from stock_trade.demo_stock import get_executor

stock_router = APIRouter()
class ReportParam(BaseModel):
    symbol: str = Field(..., description="股票代码")
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

@stock_router.post("/agent")
def get_agent_report(param: ReportParam):
    """
    获取股票报告
    :param param: 股票编码
    :return: 股票报告
    """
    agent = get_agent()
    # result = agent.invoke({"messages": [{"role": "user", "content": f"分析股票{param.symbol}的行情"}]},)
    # print(result["structured_response"])
    # return result["structured_response"]
    # 读取整个CSV文件
    df = pd.read_csv('A股股票列表.csv',
                     encoding='utf-8',
                     dtype={'代码': str, '名称': str})
    # 提取单列数据（通过列名）
    column_data = df['代码']  # 例如 df['股票代码']
    # 转换为列表
    stock_codes = column_data.tolist()
    res_list = []
    for step in agent.stream({"messages": [{"role": "user", "content": f"分析股票{param.symbol}的行情"}]},
                             stream_mode="values",):
        res_list.append(step)
        step["messages"][-1].pretty_print()
    # print(res_list)
    return res_list[-1]["structured_response"]


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
