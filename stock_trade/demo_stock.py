import akshare as ak
from datetime import datetime, timedelta

import pandas as pd
from ddgs import DDGS
from langchain.tools import tool
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import os
import talib as ta

from stock_trade.demo_stock_sentiment import fetch_stock_news_selenium
from stock_trade.stock_report import StockReport


# === 工具1：获取股票一周历史行情 ===
@tool
def get_stock_history(symbol: str) -> str:
    """
    获取近30天股票日线历史行情
    :param symbol: 股票编码
    :return:
    """
    print("===============================开始获取30天历史数据=======================================")
    end = datetime.now()
    start = end - timedelta(days=30)
    df = ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date=start.strftime("%Y%m%d"), adjust="")
    return df.tail(30).to_string(index=False)


# === 工具2：搜索股票相关新闻 ===
@tool
def search_stock_news(symbol: str) -> str:
    """
    搜索近7天与该股票相关的新闻标题
    :param symbol: 股票编码
    :return: 新闻标题列表
    """
    query = f"{symbol} 中国A股 股票 南方财富网 新浪财经 同花顺财经 最新新闻"
    results = DDGS().text(query, max_results=5)
    print(results)
    return "\n".join([f"{r['title']} - {r['href']}" for r in results])


# === 工具3：计算技术指标 ===
@tool
def tech_tool(symbol: str) -> dict:
    """
    计算技术指标：计算MA5/MA10、MACD、RSI
    :param symbol: 股票编码
    :return: 技术指标数据
    """
    print("===============================开始获取技术指标数据=======================================")
    df = ak.stock_zh_a_hist(symbol=symbol, period="daily",
                            start_date=(datetime.now() - timedelta(days=60)).strftime("%Y%m%d"), adjust="")
    close = pd.to_numeric(df["收盘"])

    ma5 = ta.MA(close, timeperiod=5)
    ma10 = ta.MA(close, timeperiod=10)
    macd, macd_signal, macd_hist = ta.MACD(close)
    rsi = ta.RSI(close, timeperiod=14)
    print(ma5)
    return {
        "MA5": ma5,
        "MA10": ma10,
        "MACD": macd,
        "RSI": rsi
    }


@tool
def get_stock_info(symbol: str) -> str:
    """
    获取股票信息
    :param symbol: 股票编码
    :return: 股票信息
    """

    print("===============================开始获取股票基础数据=======================================")
    df = ak.stock_zh_a_spot_em()

    stock_info = df[df["代码"] == symbol]
    return stock_info.to_string(index=False)


# === 3. 构建 LangChain 智能体 ===
# base_url = "https://api.siliconflow.cn/v1"
# api_key = "sk-iwcrqdyppclebjgtfpudagjdnkqhgfsauhxwjaalrvjpgnvt"
# model_name = "deepseek-ai/DeepSeek-R1"
def get_executor():
    base_url = "http://192.168.60.146:9090/v1"
    api_key = "qwen"
    model_name = "qwen"
    # base_url = "https://api.siliconflow.cn/v1"
    # api_key = "sk-iwcrqdyppclebjgtfpudagjdnkqhgfsauhxwjaalrvjpgnvt"
    # model_name = "deepseek-ai/DeepSeek-R1"
    llm = ChatOpenAI(
        model=model_name,
        temperature=0.3,
        max_retries=2,
        api_key=api_key,
        base_url=base_url
    )
    # llm.with_structured_output(StockReport.model_json_schema())
    # 解析输出
    # parser = PydanticOutputParser(pydantic_object=StockReport)

    prompt = (ChatPromptTemplate.from_messages([
        ("system", """您是具有15年从业经验的资深股票分析师，具备CFA和FRM双重认证。请基于多维度数据进行专业分析。

## 分析框架
### 1. 数据收集（必须按顺序调用）
- **实时行情**：调用get_stock_info获取实时行情数据及基本信息
- **历史行情**：调用get_stock_history获取30日K线数据
- **技术指标**：调用tech_tool获取MA5/MA10、MACD、RSI指标  
- **新闻舆情**：调用fetch_stock_news_selenium获取近7日新闻并进行情感分析

### 2. 分析维度（每项需量化说明）
| 维度 | 分析标准 | 权重 |
|---|---|---|
| **价格趋势** | 基于30日K线的支撑/压力位、成交量变化 | 30% |
| **技术指标** | MA5/MA10金叉死叉、MACD背离、RSI超买超卖 | 35% |
| **舆情影响** | 新闻情感极性(-1~1)、媒体关注度、政策导向 | 25% |
| **风险控制** | 波动率、Beta系数、行业相关性 | 10% |

### 3. 自我反驳论证要求
进行**三轮辩证分析**：
1. **多头视角**：基于当前数据的最乐观判断及依据
2. **空头视角**：基于当前数据的最悲观判断及依据  
3. **平衡视角**：综合多空因素的理性判断及依据

### 4. 输出规范
**必须包含以下9个部分**，每部分不少于500字：

1. **价格趋势分析**：
   - 30日价格区间、成交量变化
   - 关键支撑位/压力位识别
   - 量价关系评估

2. **技术指标解读**：
   - MA5/MA10：金叉/死叉状态及强度
   - MACD：DIF/DEA位置、柱状体变化、背离信号
   - RSI：当前值、超买超卖区间、历史分位数

3. **舆情情感分析**：
   - 新闻情感极性量化（-1极度负面~1极度正面）
   - 政策/行业影响评估
   - 重大事件影响周期预测

4. **行业对比**：
   - 相对行业强弱表现
   - 同行业龙头股对比
   - 行业景气度影响

5. **资金动向**：
   - 主力资金流向（大单/中单/小单）
   - 北向资金持仓变化
   - 融资融券余额变化

6. **风险评估**：
   - 波动率（20日年化）
   - Beta系数（相对沪深300）
   - VaR风险值（95%置信区间）

7. **未来一周预测**：
   - 概率分布：上涨/下跌/震荡概率
   - 目标价位：乐观/中性/悲观三种情景
   - 关键催化因素

8. **操作建议**：
   - 具体操作策略（建仓/加仓/减仓/清仓）
   - 分批次交易计划
   - 止损止盈设置

9. **综合结论**：
   - 投资评级（强烈买入/买入/中性/卖出/强烈卖出）
   - 核心逻辑总结
   - 风险提示等级（低/中/高）

### 5. 格式要求
- **总字数**：不少于2000字
- **数据引用**：所有分析必须基于实际获取的数据
- **量化表达**：避免主观描述，使用具体数值
- **JSON输出**：严格符合{schema}结构
"""),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),

    ])

              )
    tools = [get_stock_info, get_stock_history, tech_tool, fetch_stock_news_selenium]
    agent = create_openai_tools_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    return executor


# === 4. 运行示例 ===
if __name__ == "__main__":
    stock_code = "000718"  # 万科A
    result = get_executor().invoke({"input": f"请分析 股票 {stock_code} 的近期行情"})
    print("result---------------------->",result["output"])

    # 将分析结果保存到文件
    # from datetime import datetime
    #
    # current_date = datetime.now().strftime("%Y%m%d")
    # filename = f"{stock_code}_{current_date}.txt"
    #
    # # 确保output目录存在
    # output_dir = os.path.join(os.path.dirname(__file__), "output")
    # os.makedirs(output_dir, exist_ok=True)
    #
    # file_path = os.path.join(output_dir, filename)
    # with open(file_path, "w", encoding="utf-8") as f:
    #     f.write(result["output"])
    # print(f"分析结果已保存到: {file_path}")
