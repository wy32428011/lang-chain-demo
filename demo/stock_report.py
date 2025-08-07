from pydantic import BaseModel, Field


class StockReport(BaseModel):
    symbol: str = Field(..., description="股票代码")
    name: str = Field(..., description="股票名称")
    news: str = Field(..., description="股票新闻")
    report: str = Field(..., description="股票报告")
    action:  str = Field(..., description="股票操作建议:买入|卖出|持有")
    tech_analysis:  str = Field(..., description="股票技术指标分析")
    news_sentiment: str = Field(..., description="股票新闻情绪分析")
    action_analysis: str = Field(..., description="股票操作建议分析")
    risk: str = Field(..., description="股票风险提示")
    summary: str = Field(..., description="股票分析总结，包含以上所有内容，不少于800字，内容详细，细节丰富")
