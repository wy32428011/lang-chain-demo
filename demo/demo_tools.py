from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, ToolMessage
base_url="http://172.24.205.153:30000/v1"
api_key="qwen"
# prompt = ChatPromptTemplate.from_messages(
#     [
#         (
#             "system",
#             "You are a helpful assistant that translates {input_language} to {output_language}.",
#         ),
#         ("human", "{input}"),
#     ]
# )

llm = ChatOpenAI(
    model="qwen",
    temperature=0.3,
    max_retries=2,
    api_key=api_key,
    base_url=base_url
)

class GetWeather(BaseModel):
    """获取当前位置天气"""
    location: str = Field(..., description="城市和省份，例如：江苏 无锡")

@tool
def add(a: int, b: int) -> int:
    """加法"""
    return a + b
tools = [GetWeather, add]
chain =  llm.bind_tools(tools)
messages = [HumanMessage(content="今天南京的天气？")]
ai_msg = chain.invoke(messages)
messages.append(ai_msg)
for tool_call in ai_msg.tool_calls:
    selected_tool = {"getweather": GetWeather, "add": add}[tool_call["name"].lower()]
    tool_output = selected_tool.invoke(tool_call["args"])
    messages.append(ToolMessage(tool_output, tool_call_id=tool_call["id"]))
result = chain.invoke(messages)
print(result.content)



