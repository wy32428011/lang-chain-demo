import asyncio
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from threading import Lock
from time import sleep

import akshare as ak
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
import logging

from pandas import DataFrame
from tqdm import tqdm

from stock_trade.demo_stock_sentiment import fetch_stock_news_selenium
from stock_trade.stock_report import StockReport
import talib as ta

os.environ["http_proxy"] = "http://127.0.0.1:7890"  # HTTP代理
os.environ["https_proxy"] = "http://127.0.0.1:7890"  # HTTPS代理


def get_llm_model():
    base_url = "http://192.168.60.146:9090/v1"
    api_key = "qwen"
    model_name = "qwen"
    # base_url = "http://172.24.205.153:9090/v1"
    # api_key = "qwen"
    # model_name = "qwen"
    # base_url = "https://api.siliconflow.cn/v1"
    # api_key = "sk-iwcrqdyppclebjgtfpudagjdnkqhgfsauhxwjaalrvjpgnvt"
    # model_name = "Qwen/Qwen3-30B-A3B-Thinking-2507"
    model = ChatOpenAI(
        model=model_name,
        temperature=0.3,
        max_retries=2,
        api_key=api_key,
        base_url=base_url,
        # max_tokens=131072,
        # max_completion_tokens=20480,
        # timeout=20
        # streaming=True,
    )
    return model


async def get_stock_info():
    """
    获取股票信息
    :param symbol: 股票编码
    :return: 股票信息
    """
    # 获取所有A股实时行情数据（含股票代码）
    data = await ak.stock_zh_a_spot_em()
    # 提取股票代码列
    stock_codes = data["代码"].tolist()
    data_all = data[['序号', '代码', '名称', '最新价', '涨跌幅', '涨跌额', '成交量',
                     '成交额', '振幅', '最高', '最低', '今开', '昨收', '量比',
                     '换手率', '市盈率-动态', '市净率', '总市值', '流通市值', '涨速', '5分钟涨跌',
                     '60日涨跌幅', '年初至今涨跌幅']]
    print(f"共获取 {len(stock_codes)} 只A股股票代码")

    data_all.to_csv("A股股票列表.csv", index=False, encoding="utf_8")


async def get_stock_history(symbol: str) -> str:
    """
    获取近30天股票日线历史行情
    :param symbol: 股票编码
    :return:
    """
    print("\n=================get_stock_history start====================")
    end = datetime.now()
    start = end - timedelta(days=30)
    df = await ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date=start.strftime("%Y%m%d"), adjust="")
    return df.tail(30).to_string(index=False)


async def tech_tool(symbol: str) -> dict:
    """
    计算技术指标：计算MA5/MA10、MACD、RSI
    :param symbol: 股票编码
    :return: 技术指标数据
    """
    print("\n=================tech_tool start====================")
    df = await ak.stock_zh_a_hist(symbol=symbol, period="daily",
                            start_date=(datetime.now() - timedelta(days=60)).strftime("%Y%m%d"), adjust="")
    close = pd.to_numeric(df["收盘"])

    ma5 = ta.MA(close, timeperiod=5)
    ma10 = ta.MA(close, timeperiod=10)
    macd, macd_signal, macd_hist = ta.MACD(close)
    rsi = ta.RSI(close, timeperiod=14)
    return {
        "MA5": ma5,
        "MA10": ma10,
        "MACD": macd,
        "RSI": rsi
    }


def get_agent():
    # init_chat_model(model_name=model_name, api_key=api_key, base_url=base_url)
    tools = [get_stock_history, tech_tool, fetch_stock_news_selenium]
    agent = create_react_agent(
        model=get_llm_model(),
        tools=tools,
        prompt=
        """您是具有丰富经验的资深股票分析师，具备CFA和FRM双重认证。请基于多维度数据进行专业分析，所有的回答必须使用中文。
    
    ## 分析框架
    ### 1. 数据收集（必须按顺序调用，每个方法仅执行一次）
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
    **必须包含以下9个部分**，每部分不少于200字：
    
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
    - **总字数**：不超过200字
    - **数据引用**：所有分析必须基于实际获取的数据
    - **量化表达**：避免主观描述，使用具体数值""",
        response_format=StockReport.model_json_schema(),
    )

    return agent
    # res = agent.invoke(
    #     {"messages": [{"role": "user", "content": "分析股票000718的行情"}]}
    # )
    #
    # print(res)
    # print(res['structured_response'])
    # return


def do_execute():
    get_stock_info()
    # 读取整个CSV文件
    df = pd.read_csv('A股股票列表.csv',
                     encoding='utf-8',
                     dtype={'代码': str, '名称': str, '最新价': float})
    df = df[df['最新价'] < 15]
    df = df[df['涨跌幅'] > 5]
    # 提取单列数据（通过列名）
    column_data = df['代码']  # 例如 df['股票代码']
    # 转换为列表
    stock_codes = column_data.tolist()
    # agent = get_agent()
    total_size = len(stock_codes)
    print(f"总数：{total_size}")
    # 创建线程锁和线程池
    file_lock = Lock()
    max_workers = 3  # 根据API速率限制调整并发数

    async def process_stock(code):
        try:
            agent = get_agent()
            result_agent = await agent.ainvoke({
                "messages": [{"role": "user", "content": f"分析股票{code}的行情"}]
            })
            print(result_agent["structured_response"])
            result = result_agent["structured_response"]

            if result['investment_rating'] in ("买入", "强烈买入"):
                with file_lock:
                    current_date = datetime.now().strftime("%Y%m%d")
                    filename = f"{code}_{current_date}.txt"
                    output_dir = os.path.join(os.path.dirname(__file__), str(current_date))
                    os.makedirs(output_dir, exist_ok=True)
                    file_path = os.path.join(output_dir, filename)
                    with open(file_path, "w", encoding="utf-8") as f:
                        json_str = json.dumps(result, ensure_ascii=False, indent=4)
                        f.write(json_str)
            time.sleep(5)  # 保留单个任务休眠
        except Exception as e:
            print(f"处理股票{code}时出错: {e}")

    # 使用线程池并行处理
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(asyncio.run, process_stock(code)): code for code in stock_codes}
        for future in tqdm(as_completed(futures), total=len(futures), desc="股票分析进度", unit="只"):
            code = futures[future]
            try:
                future.result()
            except Exception as e:
                print(f"线程执行出错(股票{code}): {e}")


if __name__ == '__main__':
    do_execute()
    # res_list = []
    # for step in agent.stream({"messages": [{"role": "user", "content": "分析股票000718的行情"}]},
    #                          stream_mode="values",):
    #     print( step)
    #     step["messages"][-1].pretty_print()
