import json

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
from sqlalchemy.orm.session import Session
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import os
import talib as ta
from langchain_core.output_parsers import JsonOutputParser

from graph_demo.database import get_db
from graph_demo.models import InvestmentRating
from llm_stock.web_search import bocha_websearch_tool
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
    :极速版_股票历史行情: 股票编码
    :return: 股票信息
    """

    print("===============================开始获取股票基础数据=======================================")
    df = ak.stock_zh_a_spot_em()

    stock_info = df[df["代码"] == symbol]
    return stock_info.to_string(index=False)


@tool
def get_stock_info_csv(symbol: str):
    """
    获取股票信息
    :param symbol: 股票编码
    :return: 股票信息
    """
    df = pd.read_csv('./graph_demo/A股股票列表.csv',
                     encoding='utf-8',
                     dtype={'代码': str, '名称': str, '最新价': float})
    df = df[df["代码"] == symbol]
    return df.to_string(index=False)


# === 3. 构建 LangChain 智能体 ===
def get_executor():
    ## 本地
    base_url = "http://192.168.60.146:9090/v1"
    api_key = "qwen"
    model_name = "qwen"

    ## 硅基流动
    # base_url = "https://api.siliconflow.cn/v1"
    # api_key = "sk-iwcrqdyppclebjgtfpudagjdnkqhgfsauhxwjaalrvjpgnvt"
    # model_name = "deepseek-ai/DeepSeek-V3.1"

    llm = ChatOpenAI(
        model=model_name,
        temperature=0.6,
        api_key=api_key,
        base_url=base_url,
        top_p=0.1,
        # extra_body={
        #     "enable_thinking": True
        # }
    )
    # from langchain_ollama import ChatOllama
    # llm = ChatOllama(
    #     base_url="http://172.24.205.153:11434",
    #     model="gpt-oss:20b",
    #     temperature=0,
    #     top_p=0.1,
    #     reasoning=True
    # )
    # 启用结构化输出
    # llm = llm.with_structured_output(StockReport)
    stock_schema = str(StockReport.model_json_schema()).replace('{', '{{').replace('}', '}}')
    prompt = (ChatPromptTemplate.from_messages([
        ("system", f"""您是具有15年从业经验的资深股票分析师，具备CFA和FRM双重认证。请基于多维度数据进行专业分析，重点预测短期价格走向。
## 重要输出要求
- **必须使用中文回答**
- **您必须严格按照以下JSON格式输出分析结果，不要输出任何其他内容：**
{stock_schema}
## 分析框架
### 1. 数据收集（必须按顺序调用）
- **股票基础信息**：调用get_stock_info_csv获取股票基础信息（含最新价）
- **历史行情**：调用get_stock_history获取30日K线数据（收盘价、成交量）
- **技术指标**：调用tech_tool获取MA5/MA10、MACD（DIF/DEA/柱状体）、RSI指标  
- **新闻资讯**：调用bocha_websearch_tool获取近7天相关新闻（用于情感分析）

### 2. 分析维度（每项需量化说明对价格走向的影响权重）
| 维度         | 核心分析指标                                                                 | 预测权重 |
|--------------|----------------------------------------------------------------------------|----------|
| **价格趋势** | 30日收盘价趋势（斜率）、成交量与价格的同步性（量价背离/共振）、支撑位/压力位突破情况 | 35%      |
| **技术指标** | MA5/MA10金叉/死叉强度（差值绝对值）、MACD柱状体变化率（连续3日增减幅）、RSI区间（超买>70/超卖<30） | 40%      |
| **舆情影响** | 新闻情感极性（-1~1）、政策/事件类新闻占比（%）、重大利好/利空事件时效性（影响周期） | 25%      |

### 3. 价格走向预测逻辑（必须严格遵循）
#### 技术面预测信号（优先级：技术指标 > 价格趋势）
- **看涨信号**（需满足至少2项）：  
  1. MA5连续3日位于MA10上方，且MA5斜率>0  
  2. MACD柱状体由负转正，或连续3日扩大（增幅>5%）  
  3. RSI处于50-70区间（未超买）且呈上升趋势  
- **看跌信号**（需满足至少2项）：  
  1. MA5连续3日位于MA10下方，且MA5斜率<0  
  2. MACD柱状体由正转负，或连续3日缩小（降幅>5%）  
  3. RSI处于30-50区间（未超卖）且呈下降趋势  
- **震荡信号**：以上信号混杂，或关键指标（MA5/MA10、MACD）处于临界状态  

#### 舆情面修正规则  
- 若技术面看涨但新闻情感极性<-0.5，下调上涨概率10-15%  
- 若技术面看跌但新闻情感极性>0.5，下调下跌概率10-15%  
- 重大政策利好/利空新闻（如行业政策、公司财报）可直接提升对应方向概率20%  

### 4. 输出规范（核心章节，每部分1000-1500字，Markdown格式）
**必须包含以下7个部分**，每部分1000-1500字，使用Markdown格式（如#标题、**加粗**、列表、表格等）增强可读性：  

1. **价格趋势与量价关系**  
   - ## 30日收盘价趋势深度分析  
     - 斜率计算：(最新价-30日前价)/30日，结合历史分位数（近1年斜率分布）评估趋势强度  
     - 价格波动特征：最高价/最低价区间波动率（(最高价-最低价)/最低价×100%），与近3个月均值对比  
   - ## 关键价位突破动力学  
     - 支撑位验证：近30日最低价的成交量密集区分析（是否伴随放量反弹）  
     - 压力位测试：近30日最高价的历史抛压评估（前5次触及该价位的换手率均值）  
   - ## 量价同步性全景评估  
     - 健康信号案例：上涨日成交量较5日均量放大>20%的次数占比  
     - 背离风险预警：价格创新高但成交量较5日均量萎缩>15%的具体日期及后续走势  

2. **技术指标与价格信号**  
   - ## MA5/MA10趋势系统解析  
     - 金叉/死叉强度量化：MA5与MA10差值绝对值（>3%为强信号，1-3%为弱信号）  
     - 斜率对比表：MA5斜率（日涨幅均值）与MA10斜率的差值及历史概率分布  
   - ## MACD动能指标深度解构  
     - DIF与DEA位置关系：金叉后DIF上穿DEA的幅度（>0.5为强动能）  
     - 柱状体变化率：连续3日增减幅（如+8%→+12%→+15%为加速上涨信号）  
     - 背离信号图谱：价格与MACD背离的形态分类（顶背离/底背离）及历史修复周期  
   - ## RSI超买超卖区间交易逻辑  
     - 当前值精确分析：如RSI=65.2（处于50-70中性偏强区间）  
     - 历史分位数：当前RSI在近1年数据中的分位数（如前68%分位，表明偏强势）  

3. **舆情情感与价格影响**  
   - ## 新闻情感极性量化模型  
     - 关键词打分体系：如"业绩预增+50%"→+0.9，"监管调查"→-0.85（附具体新闻标题及打分明细）  
     - 情感分布表格：正面/中性/负面新闻数量占比（如正面40%、中性30%、负面30%）  
   - ## 事件类型时效性分析  
     - 政策类：行业补贴政策→影响周期7-15天（引用具体政策文件名称及发布时间）  
     - 业绩类：季度财报预告→影响周期3-7天（对比历史同期财报发布后的股价波动幅度）  
   - ## 舆情-技术面共振/冲突案例  
     - 共振案例：技术面MACD金叉（+40%权重）+ 正面舆情（+0.6极性）→上涨概率提升至75%  
     - 冲突案例：技术面RSI超买（72.5）+ 负面舆情（-0.7极性）→需警惕回调风险  

4. **综合价格走向预测**  
   - ## 多维度信号加权决策模型  
     - 技术面信号得分：基于40%权重计算（如MA5金叉+15分，MACD强动能+20分，总分35/40）  
     - 舆情面修正系数：基于25%权重（如正面舆情+10分，总分10/25）  
     - 最终方向概率：上涨概率=技术面得分/40×40% + 舆情得分/25×25% + 价格趋势得分/35×35%  
   - ## 概率分布与置信区间  
     - 主方向概率：上涨65%、下跌20%、震荡15%（附蒙特卡洛模拟1000次的概率分布直方图描述）  
     - 关键驱动因素排序：1.MACD加速上涨（权重30%） 2.正面舆情占比提升（权重25%） 3.MA5斜率陡峭（权重20%）  

5. **目标价位与波动区间**  
   - ## 三级目标价测算模型  
     - 乐观目标价=当前价×(1+上涨概率×0.02)，附历史达成概率（近1年同条件下达成率68%）  
     - 中性目标价=当前价×(1+上涨概率×0.01)，基于技术面中性信号  
     - 悲观目标价=当前价×(1-下跌概率×0.02)，结合支撑位距离（如距支撑位3.2%）  
   - ## 波动区间突破条件  
     - 上破触发点：突破乐观目标价需成交量放大至5日均量的1.5倍以上  
     - 下破预警线：跌破悲观目标价且MACD柱状体转负，视为趋势反转信号  

6. **操作建议（基于预测）**  
   - ## 分批次建仓/减仓计划  
     - 看涨策略：首次建仓30%（当前价），突破压力位加仓40%，回踩MA5再加仓30%  
     - 看跌策略：跌破支撑位减仓50%，MACD死叉清仓剩余50%  
   - ## 止损止盈动态管理  
     - 止损位公式：悲观目标价×0.95（允许5%意外波动），附波动率调整系数（高波动股票×0.92）  
     - 止盈位阶梯：第一目标（中性价）止盈40%，第二目标（乐观价）止盈60%  
   - ## 特殊场景应对方案  
     - 横盘震荡：网格交易区间[支撑位, 压力位]，每下跌2%买入10%，每上涨2%卖出10%  

7. **预测风险提示**  
   - ## 技术面失效风险图谱  
     - 指标临界状态：MA5与MA10差值0.8%（弱信号），历史该状态下方向错误率42%  
     - 突发政策冲击：如行业监管政策出台导致技术指标失真的历史案例（附具体政策及股价波动幅度）  
   - ## 舆情延迟反应机制  
     - 新闻发布时间与市场消化周期：如盘后发布的业绩新闻可能导致次日高开低走（历史概率58%）  
   - ## 关键指标监控清单  
     - 每日必看指标：MA5斜率变化（阈值±1%）、MACD柱状体增减幅（阈值±5%）、舆情情感极性（阈值±0.3）  

### 5. 格式要求  
- **总字数**：7000-10500字（7部分×1000-1500字/部分）  
- **数据引用**：所有分析需标注数据来源（如"MA5斜率=0.023，来自tech_tool"）  
- **量化精确**：概率保留整数，价格保留2位小数，斜率保留4位小数  
- **Markdown格式**：使用#标题（如## 30日收盘价趋势分析）、**加粗关键词**、无序列表(-)、有序列表(1.)、表格（如量价关系评估表）等元素  
- **逻辑闭环**：每个结论需有"数据→分析→结论"完整链条，禁止无依据推测 
"""),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]))

    tools = [get_stock_info_csv, get_stock_history, tech_tool, bocha_websearch_tool]
    agent = create_openai_tools_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    return executor


# === 4. 运行示例 ===
if __name__ == "__main__":
    import concurrent.futures
    from tqdm import tqdm

    df = pd.read_csv('../graph_demo/A股股票列表.csv',
                     encoding='utf-8',
                     dtype={'代码': str, '名称': str, '最新价': float})
    df = df[df['昨收'] < 11]
    df = df[df['年初至今涨跌幅'] > 120]
    stock_codes = df['代码'].tolist()

    # 分块处理，每块10个股票代码
    chunk_size = 10
    chunks = [stock_codes[i:i + chunk_size] for i in range(0, len(stock_codes), chunk_size)]
    max_workers = 1


    def process_stock_chunk(chunk, pbar):
        """处理一个股票代码块的函数"""
        for stock_code in chunk:
            try:
                process_stock_chunk(stock_code)
            except Exception as e:
                print(f"股票 {stock_code} 分析失败: {e}")
            finally:
                # 更新进度条
                pbar.update(1)


    # 创建进度条
    with tqdm(total=len(stock_codes), desc="处理股票分析", unit="股票") as pbar:
        # 使用线程池执行器并行处理每个块
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有块到线程池，传递进度条对象
            futures = [executor.submit(process_stock_chunk, chunk, pbar) for chunk in chunks]

            # 等待所有任务完成
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()  # 获取结果，如果有异常会在这里抛出
                except Exception as e:
                    print(f"处理块时发生错误: {e}")


def process_stock_chunk(stock_code: str):
    """处理一个股票代码块的函数"""
    try:
        result = get_executor().invoke({"input": f"请分析 股票 {stock_code} 的近期行情",
                                        "chat_history": []})
        print(result)
        parser = JsonOutputParser(pydantic_object=StockReport)
        parsed_result = parser.parse(result["output"])
        print("parsed_result",parsed_result)
        db: Session = next(get_db())
        # 假设result中包含symbol和name信息
        rating_record = InvestmentRating(
            symbol=parsed_result.get('symbol', ''),
            name=parsed_result.get('name', ''),
            rating=parsed_result['investment_rating'],
            current_price=parsed_result.get('current_price', None),
            target_price=parsed_result.get('target_price', None),
            analysis_date=datetime.strptime(parsed_result.get('analysis_date', ''), '%Y-%m-%d') if result.get(
                'analysis_date') else None,
            result_json=parsed_result
        )
        db.add(rating_record)
        db.commit()
        db.refresh(rating_record)
        return parsed_result
    except Exception as e:
        print(f"股票 {stock_code} 分析失败: {e}")
        return None

from fastapi import WebSocket

async def process_stock_chunk_ws(stock_code: str,websocket: WebSocket):
    """处理一个股票代码块的函数"""
    try:
        # result = get_executor().invoke({"input": f"请分析 股票 {stock_code} 的近期行情",
        #                                 "chat_history": []})
        result = None
        async for chunk in get_executor().astream({"input": f"请分析 股票 {stock_code} 的近期行情",
                                    "chat_history": []}):
            try:
                print(chunk["messages"][-1])
                chunk["messages"][-1].pretty_print()
                result = chunk["messages"][-1].content
                await websocket.send_text(chunk["messages"][-1].content)
            except Exception as ex:
                print(f"发送股票 {stock_code} 分析失败: {ex}")
        print(result)
        parser = JsonOutputParser(pydantic_object=StockReport)
        parsed_result = parser.parse(result["output"])
        print("parsed_result",parsed_result)
        db: Session = next(get_db())
        # 假设result中包含symbol和name信息
        rating_record = InvestmentRating(
            symbol=parsed_result.get('symbol', ''),
            name=parsed_result.get('name', ''),
            rating=parsed_result['investment_rating'],
            current_price=parsed_result.get('current_price', None),
            target_price=parsed_result.get('target_price', None),
            analysis_date=datetime.strptime(parsed_result.get('analysis_date', ''), '%Y-%m-%d') if result.get(
                'analysis_date') else None,
            result_json=parsed_result
        )
        db.add(rating_record)
        db.commit()
        db.refresh(rating_record)
        return parsed_result
    except Exception as e:
        print(f"股票 {stock_code} 分析失败: {e}")
        return None
