# multi_strategy_stock_agent.py
import os, json, asyncio, akshare as ak, pandas as pd, talib as ta
from datetime import datetime, timedelta
from typing import List, Dict
from langchain_core.tools  import BaseTool
from langchain_core.prompts  import ChatPromptTemplate
from langchain.agents  import create_openai_tools_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from duckduckgo_search import DDGS


# ---------- 工具 1：历史行情 ----------
class HistoryTool(BaseTool):
    name = "history_price"
    description = "获取最近7日日线行情"
    def _run(self, code: str) -> Dict:
        df = ak.stock_zh_a_hist(symbol=code,  period="daily", start_date=(datetime.now()-timedelta(days=14)).strftime("%Y%m%d"),  adjust="")
        df = df.tail(7)
        return df.to_dict(orient="records")


# ---------- 工具 2：资金流向 ----------
class FundFlowTool(BaseTool):
    name = "fund_flow"
    description = "获取当日主力净流入(万元)"

    def _run(self, code: str) -> float:
        market = "sh" if code.startswith("6") else "sz"
        df = ak.stock_individual_fund_flow(stock=code, market=market)
        return float(df.iloc[0][" 主力净流入-净额"])


# ---------- 工具 3：新闻 ----------
class NewsTool(BaseTool):
    name = "news"
    description = "抓取最近20条相关新闻标题"

    def _run(self, code: str) -> List[str]:
        kw = f"{code} 股票"
        return [d["title"] for d in DDGS().text(kw, max_results=20)]


# ---------- 工具 4：技术指标 ----------
class TechTool(BaseTool):
    name = "tech_indicators"
    description = "计算MA5/MA10、MACD、RSI"

    def _run(self, code: str) -> Dict:
        df = ak.stock_zh_a_hist(symbol=code, period="daily",
                                start_date=(datetime.now() - timedelta(days=60)).strftime("%Y%m%d"), adjust="")
        close = pd.to_numeric(df[" 收盘"])
        ma5 = close.rolling(5).mean().iloc[-1]
        ma10 = close.rolling(10).mean().iloc[-1]
        macd = ta.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
        rsi = ta.RSI(close, timeperiod=14)
        return {"MA5": ma5, "MA10": ma10, "MACD": macd, "RSI": rsi}