from typing import Any

from pydantic import BaseModel, Field


class StockReport(BaseModel):
    symbol: str = Field(..., description="股票代码")
    name: str = Field(..., description="股票名称")
    news: str = Field(..., description="股票新闻")
    report: str = Field(..., description="股票报告")
    action:  str = Field(..., description="股票操作建议:买入|卖出|持有")
    buy_target_price: float = Field(..., description="股票买入目标价格")
    sell_target_price: float = Field(..., description="股票卖出目标价格")
    current_price: float = Field(..., description="股票当前价格")
    tech_analysis:  Any = Field(..., description="股票技术指标分析")
    news_sentiment: Any = Field(..., description="股票新闻情绪分析")
    action_analysis: Any = Field(..., description="股票操作建议分析")
    risk: Any = Field(..., description="股票风险提示")
    summary_report: Any = Field(..., description="股票分析总结报告，包含所有内容的分析结果，不少于5000字的分析报告，以md的格式呈现")
