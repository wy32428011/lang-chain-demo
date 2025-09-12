from typing import Any

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Literal
from IPython.display import Image, display


class StockReport(BaseModel):
    model_config = ConfigDict(
        title="StockReport",
        description="A structured report containing comprehensive stock analysis results"
    )
    # 基础信息
    symbol: str = Field(..., description="股票代码", pattern=r"^\d{6}$")
    name: str = Field(..., description="股票名称", min_length=2, max_length=20)
    current_price: float = Field(..., description="当前价格", gt=0)
    analysis_date: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
    target_price: float = Field(..., description="目标价格", gt=0)
    # 分析维度（对应prompt要求的9个部分）
    price_trend_analysis: str = Field(..., description="价格趋势分析（含支撑/压力位、量价关系,markdown格式）",min_length=1500, max_length=2000)
    technical_indicators: str = Field(..., description="技术指标解读（MA5/10、MACD、RSI量化分析,markdown格式）",
                                      min_length=1450, max_length=1500)
    news_sentiment_analysis: str = Field(..., description="新闻情绪分析（情感极性量化、政策影响,markdown格式）",
                                         min_length=1500, max_length=2000)
    industry_comparison: str = Field(..., description="行业对比分析（相对强弱、同行业对比,markdown格式）", min_length=1500,
                                     max_length=2000)
    capital_flow_analysis: str = Field(..., description="资金动向分析（主力/北向/融资融券,markdown格式）", min_length=1500,
                                       max_length=2000)
    risk_assessment: str = Field(..., description="风险评估（波动率、Beta、VaR量化,markdown格式）", min_length=1450,
                                 max_length=1500)
    weekly_forecast: str = Field(..., description="未来一周预测（概率分布、目标价位,markdown格式）", min_length=1450,
                                 max_length=1500)
    operation_recommendation: str = Field(..., description="操作建议（建仓/加仓/减仓/清仓计划,markdown格式）",
                                          min_length=1450, max_length=1500)
    comprehensive_conclusion: str = Field(..., description="综合结论（投资评级、核心逻辑、风险提示等级,markdown格式）",
                                          min_length=1450, max_length=1500)

    # 量化指标
    trend_probability: dict = Field(
        default={"上涨": 0.33, "下跌": 0.33, "震荡": 0.34},
        description="趋势概率分布"
    )
    target_prices: dict = Field(
        default={"乐观": 0.0, "中性": 0.0, "悲观": 0.0},
        description="三种情景下的目标价位"
    )
    risk_level: Literal["低", "中", "高"] = Field(..., description="综合风险等级：低、中、高")
    investment_rating: Literal["强烈买入", "买入", "中性", "卖出", "强烈卖出"] = Field(...,
                                                                                       description="投资评级：强烈买入、买入、中性、卖出、强烈卖出,该字段必须存在")

    # 关键技术指标快照
    technical_snapshot: dict = Field(
        default={},
        description="技术指标快照：{'ma5': 0.0, 'ma10': 0.0, 'macd': 0.0, 'rsi': 0.0}"
    )
