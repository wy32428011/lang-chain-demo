from langchain import hub
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
# 新导入（推荐）
from ddgs import DDGS
from langchain_community.tools import DuckDuckGoSearchResults, DuckDuckGoSearchRun
from langchain.agents import AgentType, initialize_agent, create_tool_calling_agent, AgentExecutor, create_react_agent, \
    create_openai_tools_agent

base_url = "http://172.24.205.153:30000/v1"
api_key = "qwen"
#
# search = DuckDuckGoSearchRun()
#
# result = search.invoke("今天最火爆的新闻内容")

# print(result)
tools = [DuckDuckGoSearchResults()]
llm = ChatOpenAI(
    model="qwen",
    temperature=0,
    max_retries=2,
    api_key=api_key,
    base_url=base_url
)

# 3. 智能体提示模板（关键！）
prompt_template = ChatPromptTemplate.from_messages([
    ("system",
     "你是能实时联网的智能助手。需要最新信息时，请调用 DuckDuckGo 搜索工具并总结结果"
     "1. 用中文回答用户问题\n"
     "2. 使用DuckDuckGo搜索最新信息\n"
     "3. 对搜索结果进行分析\n"
     "4. 标注信息来源[[编号]]"),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),  # 工具返回的占位符
])
# 初始化智能体
# agent = create_react_agent(llm, tools, hub.pull("hwchase17/react"))
agent = create_openai_tools_agent(llm, tools, prompt_template)
# 构建智能体

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
# 执行问答
response = agent_executor.invoke({
    "input": "请帮我搜索中国A股，2025年股票代码为000718的股票信息，请列出股票的基本信息，并且帮我分析这只股票未来一周的价格趋势"
})
print("output----------->",response["output"])
