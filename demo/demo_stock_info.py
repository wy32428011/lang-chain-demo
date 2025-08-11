from typing import Dict

import akshare as ak
from pandas import DataFrame


def get_stock_info(code: str) -> Dict:
    """
    根据股票代码获取股票的信息
    :param code: 股票代码
    :return: 股票的信息
    """
    df = ak.stock_zh_a_spot_em()
    df = df[df["代码"] == code]
    if df.empty:
        return {}
    return df.iloc[0].to_dict()

def get_stock_individual_info_em(symbol: str) -> str:
    """
    根据股票代码获取股票的信息
    :param symbol: 股票代码
    :return: 股票的信息
    """
    company_profile = ak.stock_individual_info_em(symbol=symbol)
    str_result = f"""
    ## 📊 股票基本信息
    - **股票名称**: {company_profile[company_profile['item'] == "股票简称"].values[0][1]}
    - **股票代码**: {company_profile[company_profile['item'] == "股票代码"].values[0][1]}
    - **上市时间**: {company_profile[company_profile['item'] == "上市时间"].values[0][1]}
    - **所属行业**: {company_profile[company_profile['item'] == "行业"].values[0][1]}
    - **总股本**: {company_profile[company_profile['item'] == "总股本"].values[0][1]}
    - **流通股**: {company_profile[company_profile['item'] == "流通股"].values[0][1]}
    - **总市值**: {company_profile[company_profile['item'] == "总市值"].values[0][1]}
    - **流通市值**: {company_profile[company_profile['item'] == "流通市值"].values[0][1]}
"""
    return str_result

def get_stock_financial_report_sina(stock: str) -> str:
    """
    根据股票代码获取股票的财务报告
    :param symbol: 股票代码
    :return: 股票的财务报告
    """
    financial_indicators = ak.stock_financial_analysis_indicator(symbol=stock,start_year='2024')
    print(financial_indicators)


print(get_stock_financial_report_sina("002735"))
