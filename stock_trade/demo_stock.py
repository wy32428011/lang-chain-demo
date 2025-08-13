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

from .demo_stock_sentiment import fetch_stock_news_selenium
from .stock_report import StockReport


# === 工具1：获取股票一周历史行情 ===
@tool
def get_stock_history(symbol: str) -> str:
    """
    获取近30天股票日线历史行情
    :param symbol: 股票编码
    :return:
    """
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



# === 3. 构建 LangChain 智能体 ===
# base_url = "https://api.siliconflow.cn/v1"
# api_key = "sk-iwcrqdyppclebjgtfpudagjdnkqhgfsauhxwjaalrvjpgnvt"
# model_name = "deepseek-ai/DeepSeek-R1"
def get_executor():
    base_url = "http://25t6y78134.oicp.vip/v1"
    api_key = "qwen"
    model_name = "qwen"
    llm = ChatOpenAI(
        model=model_name,
        temperature=0.3,
        max_retries=2,
        api_key=api_key,
        base_url=base_url
    )

    # 解析输出
    parser = PydanticOutputParser(pydantic_object=StockReport)

    prompt = (ChatPromptTemplate.from_messages([
        ("system", f"你是资深股票分析师。请根据历史行情、技术指标（计算MA5/MA10、MACD、RSI）、新闻，给出不少于2000字详尽的行情分析，"
                   f"请根据股票代码和新闻标题，分析股票的走势和新闻的情感倾向。并且通过自我反驳论证（至少三次或以上的自我反驳论证），做出最终判断: \n"
                   f"-- 历史行情数据 调用工具get_stock_history 来分析历史数据趋势\n"
                   f"-- 技术指标分析 调用工具tech_tool 计算MA5/MA10、MACD、RSI 来分析股票趋势\n"
                   f"-- 新闻情绪 调用工具fetch_stock_news_selenium 来分析新闻情感\n"
                   f"综合以上所有数据，进行详细分析，输出结果如下：\n"
                   f"1. 股票价格趋势分析：根据历史行情数据，判断股票价格的趋势是上升、下降还是平稳。\n"
                   f"2. 技术指标分析：根据计算得到的MA5、MA10、MACD、RSI指标，判断股票的趋势是向上、向下还是震荡。\n"
                   f"3. 新闻情绪分析：根据新闻标题的情感倾向，判断新闻对股票的影响是正面、负面还是中性。\n"
                   f"4. 综合判断：综合以上分析结果，给出最终的判断：买入、卖出、持有。\n"
                   f"5. 预测一周内股票价格趋势：根据以上分析，预测一周内股票价格的趋势是上升、下降还是平稳。\n"
                   f"6. 操作建议：根据以上分析，给出操作建议，包括买入、卖出、持有。\n"
                   f"7. 风险提示：根据以上分析，给出风险提示，包括风险系数、风险等级等。\n"
                   f"8. 分析总结：根据以上分析，给出总结，包括分析结果、操作建议、风险提示等。\n"
                   f"9. 总结报告：根据以上分析，给出汇总不少于2000字的分析报告\n"
         "最终输出格式必须符合以下JSON结构：\n{schema}"
         ),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
        .partial(schema=StockReport.model_json_schema())
    )

    agent = create_openai_tools_agent(llm, [get_stock_history, tech_tool, fetch_stock_news_selenium], prompt)
    executor = AgentExecutor(agent=agent, tools=[get_stock_history, tech_tool, fetch_stock_news_selenium], verbose=True)
    return executor

# === 4. 运行示例 ===
if __name__ == "__main__":
    stock_code = "000718"  # 万科A
    result = get_executor().invoke({"input": f"请分析 股票 {stock_code} 的近期行情"})
    print(result["output"])

    # 将分析结果保存到文件
    from datetime import datetime

    current_date = datetime.now().strftime("%Y%m%d")
    filename = f"{stock_code}_{current_date}.txt"

    # 确保output目录存在
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)

    file_path = os.path.join(output_dir, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(result["output"])
    print(f"分析结果已保存到: {file_path}")
