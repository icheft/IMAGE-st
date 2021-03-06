from bs4 import BeautifulSoup
import time
from datetime import datetime
import requests
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from . import pws

import streamlit as st
from dateutil.relativedelta import relativedelta  # 日期上的運算


def app(stock_id="0050.TW"):
    stock_id = stock_id
    stock_obj = yf.Ticker(stock_id)

    st.write("你好，這裡是吳宗翰的網站")
    st.write(f'分析 {stock_obj.info["longName"]}')

    current_price = pws.get_price(stock_id)
    year, div_yield, total_div = pws.get_dividend_yield(stock_id)

    st.write(f"參考時價：{current_price}｜殖利率：{div_yield * 100}%")

    stock_df = stock_obj.history(
        start="2011-3-12", end="2021-3-12", auto_adjust=False
    )  # period="max"

    ock_df = stock_obj.history(
        start="2011-3-12", end="2021-3-12", auto_adjust=False
    )  # period="max"

    st.write("股市回測線：")
    st.line_chart(stock_df["Adj Close"])

    stock_monthly_returns = (
        stock_df["Adj Close"].resample("M").ffill().pct_change() * 100
    )
    stock_yearly_returns = (
        stock_df["Adj Close"].resample("Y").ffill().pct_change() * 100
    )

    stock_yearly_returns.index = stock_yearly_returns.index.strftime("%Y")
    st.write("年度報酬率ya：")
    st.bar_chart(stock_yearly_returns.dropna())
    stock_daily_return = stock_df["Adj Close"].ffill().pct_change()

    start = stock_daily_return.index[0]
    end = stock_daily_return.index[-1]

    year_difference = (
        relativedelta(end, start).years
        + (relativedelta(end, start).months) / 12
        + (relativedelta(end, start).days) / 365.2425
    )

    init_balance = balance = 3000
    total_balance = stock_daily_return.copy()
    total_balance[0] = 0

    for i in range(len(stock_daily_return)):
        balance = balance * (1 + total_balance[i])
        total_balance[i] = balance

    total_balance.rename("成長變化", inplace=True)
    st.line_chart(total_balance)

    return_rate = (total_balance[-1] - total_balance[0]) / total_balance[0]

    cgar = ((1 + return_rate) ** (1 / year_difference)) - 1

    st.write(f"經過 {year_difference} 年後，變成 {total_balance[-1]} 元｜年化報酬率為 {cgar * 100}%")
    stock_info = stock_obj.info
