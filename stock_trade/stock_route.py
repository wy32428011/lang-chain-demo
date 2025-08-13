import json

from fastapi import APIRouter
from pydantic import BaseModel, Field

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

