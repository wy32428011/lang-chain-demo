from langchain.tools import tool
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import akshare as ak
from datetime import datetime, timedelta

import setting

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

class LLMStockHistory:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=setting.CONFIG_SETTING["llm"]["model_name"],
            temperature=setting.CONFIG_SETTING["llm"]["temperature"],
            max_retries=2,
            max_tokens=setting.CONFIG_SETTING["llm"]["max_tokens"],
            api_key=setting.CONFIG_SETTING["llm"]["api_key"],
            base_url=setting.CONFIG_SETTING["llm"]["base_url"]
        )
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个专业的股票分析助手,你只能根据提供的工具来回答问题:\n
                1. get_stock_history: 获取近30天股票日线历史行情
                2. 根据该股票的历史行情数据，分析股票未来一周内的价格趋势
                3. 根据股票的历史行情数据，分析股票的技术指标，例如移动平均线、相对强弱指标、布林带等
                4. 根据股票的历史行情数据，分析股票的交易 volume 数据，例如移动平均线、相对强弱指标、布林带等
                5. 最后做出汇总，汇总报告不少于800字
            """),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        self.agent = create_openai_tools_agent(self.llm, [get_stock_history], self.prompt)
        self.agent_executor = AgentExecutor(agent=self.agent, tools=[get_stock_history], verbose=True)


    @staticmethod
    def get_result_stock_history(symbol: str) -> str:
        result = LLMStockHistory().agent_executor.invoke({"input":f"获取股票{symbol}近30天历史行情,并分析"})
        print(result)
        return result["output"]



LLMStockHistory.get_result_stock_history("000718")

