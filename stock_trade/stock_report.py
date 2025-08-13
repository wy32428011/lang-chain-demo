from typing import Any

from pydantic import BaseModel, Field


class StockReport(BaseModel):
    symbol: str = Field(..., description="股票代码")
    name: str = Field(..., description="股票名称")
    news: str = Field(..., description="股票新闻，简要概括")
    # report: str = Field(..., description="股票报告")
    action:  str = Field(..., description="股票操作建议:买入|卖出|持有")
    target_price: float = Field(..., description="股票目标价格")
    buy_target_price: float = Field(..., description="股票买入目标价格")
    sell_target_price: float = Field(..., description="股票卖出目标价格")
    current_price: float = Field(..., description="股票当前价格")
    base_analysis:  str = Field(..., description="股票基本面分析,不少于1000字，以md的格式呈现")
    tech_analysis:  str = Field(..., description="股票技术指标分析,不少于1000字，以md的格式呈现")
    news_sentiment: str = Field(..., description="股票新闻情绪分析,不少于1000字，以md的格式呈现")
    action_analysis: str = Field(..., description="股票操作建议分析,不少于1000字，以md的格式呈现")
    risk: str = Field(..., description="股票风险提示,不少于1000字，以md的格式呈现")
    # summary_report: str = Field(..., description="股票分析总结报告，包含股票技术指标分析、股票新闻情绪分析、股票操作建议分析、股票风险提示，不少于2000字的分析报告，以md的格式呈现")
