from datetime import datetime, timedelta
from typing import  Annotated

from IPython.core.display import Image
from IPython.core.display_functions import display
from langgraph.constants import START, END
from typing_extensions import TypedDict
from langchain.chat_models import init_chat_model
from langchain_openai import ChatOpenAI
from langgraph.graph import add_messages, StateGraph
from langgraph.prebuilt import create_react_agent
import akshare as ak

def get_llm_model():
    base_url = "http://192.168.60.146:9090/v1"
    api_key = "qwen"
    model_name = "qwen"
    # base_url = "http://172.24.205.153:30000/v1"
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
        max_tokens=51200,
        max_completion_tokens=20480,
        # streaming=True,
    )
    return model


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

class State(TypedDict):
    messages: Annotated[list, add_messages]

def chatbot(state: State):
    llm = get_llm_model()
    return {"messages": [llm.invoke(state["messages"])]}

graph_builder = StateGraph(State)
graph_builder.add_node(chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)
graph = graph_builder.compile()
try:
    display(Image(graph.get_graph().draw_mermaid_png()))
except Exception:
    # This requires some extra dependencies and is optional
    pass

def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)


while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        stream_graph_updates(user_input)
    except:
        # fallback if input() is not available
        user_input = "What do you know about LangGraph?"
        print("User: " + user_input)
        stream_graph_updates(user_input)
        break