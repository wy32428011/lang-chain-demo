import requests
from bs4 import BeautifulSoup
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# @tool
async def fetch_stock_news_selenium(stock_code: str, max_count=10):
    """
    使用 Selenium 从东方财富网爬取指定股票代码的财经新闻，以应对反爬措施。

    :param stock_code: 股票代码 (e.g., "600519")
    :param max_count: 最多返回的新闻数量
    :return: 一个包含新闻字典的列表
    """
    print("\n使用 Selenium 爬取财经新闻...")
    url = f"https://so.eastmoney.com/news/s?keyword={stock_code}&type=title"

    # 设置 Chrome 浏览器选项，例如无头模式（在后台运行）
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--log-level=3')  # 仅显示严重错误

    driver = None
    try:
        # 自动安装并设置 ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        driver.get(url)

        # 等待新闻条目加载完成，最长等待10秒
        WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".news_item"))
        )

        # 获取页面源代码并用 BeautifulSoup 解析
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        news_list = []
        for item in soup.select('.news_item'):
            title_tag = item.select_one('.news_item_t a')
            summary_tag = item.select_one('.news_item_c')

            if title_tag:
                title = title_tag.text.strip()
                # if stock_code in title or (summary_tag and stock_code in summary_tag.text)
                news = {
                    'title': title,
                    'url': title_tag['href'],
                    'summary': summary_tag.text.strip() if summary_tag else '无摘要'
                }
                news_list.append(news)

            if len(news_list) >= max_count:
                break
        return news_list

    except Exception as e:
        print(f"使用 Selenium 爬取时发生错误: {e}")
        return []
    finally:
        if driver:
            driver.quit()  # 确保浏览器被关闭

# base_url = "https://api.siliconflow.cn/v1"
# api_key = "sk-iwcrqdyppclebjgtfpudagjdnkqhgfsauhxwjaalrvjpgnvt"
# model_name = "deepseek-ai/DeepSeek-R1"
# # base_url = "http://172.24.205.153:30000/v1"
# # api_key = "qwen"
# # model_name = "qwen"
# llm = ChatOpenAI(
#     model=model_name,
#     temperature=0.3,
#     max_retries=2,
#     api_key=api_key,
#     base_url=base_url
# )
#
# prompt = ChatPromptTemplate.from_messages([
#     ("system", f"你是一个金融分析助手。你可以使用工具来获取股票新闻并分析其情绪。请注意，工具需要的是股票代码，而不是公司名称。\n"
#                f"1. 新闻情绪 调用工具fetch_stock_news_selenium \n"
#                f"2. 最终结构输出总结该股票的新闻情绪：正面、负面、中性 \n"
#                ),
#     ("user", "{input}"),
#     MessagesPlaceholder(variable_name="agent_scratchpad")
# ])
#
# agent = create_openai_tools_agent(llm, [fetch_stock_news_selenium], prompt)
# executor = AgentExecutor(agent=agent, tools=[fetch_stock_news_selenium], verbose=True)
#
# stock_code = "002735"  # 万科A
# result = executor.invoke({"input": f"请分析 {stock_code} 的新闻情绪"})
# print(result["output"])

# fetch_stock_news_selenium("002735")
