import akshare as ak

# 获取所有A股实时行情数据（含股票代码）
# data = ak.stock_zh_a_spot_em()
# # 提取股票代码列
# stock_codes = data["代码"].tolist()
#
# print(f"共获取 {len(stock_codes)} 只A股股票代码")

# data[["代码", "名称"]].to_csv("A股股票列表.csv", index=False, encoding="utf_8")

import pandas as pd

# 读取整个CSV文件
df = pd.read_csv('A股股票列表.csv',
                 encoding='utf-8',
                 dtype={'代码': str, '名称': str})
# 提取单列数据（通过列名）
# column_data = df['代码']  # 例如 df['股票代码']
# 转换为列表
stock_codes = df.values.tolist()

print(stock_codes)