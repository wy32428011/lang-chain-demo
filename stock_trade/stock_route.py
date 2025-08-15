import json

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
    # result = agent.invoke({"messages": [{"role": "user", "content": f"分析股票{param.symbol}的行情"}]})
    # print(result["structured_response"])
    res_list = []
    for step in agent.stream({"messages": [{"role": "user", "content": f"分析股票{param.symbol}的行情"}]},
                             stream_mode="values"):
        res_list.append(step)
        step["messages"][-1].pretty_print()
    # print(res_list)
    return res_list[-1]["structured_response"]
