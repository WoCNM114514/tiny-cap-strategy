# -*- coding: utf-8 -*-
"""
Created on Tue Jul 26 11:00:20 2023

@author: 20536
"""


'''
采用pb和profit两个指标的均线作为买卖依据

@ 回测时长: 2018-01-01  -----  2023-07-24
收益: 388.98%
年化: 34.20%
夏普: 1.170
最大回撤: 24.62%
'''


from jqdata import *
# 初始化函数，设定基准等等
def initialize(context):
    set_benchmark('000905.XSHG')
    set_option('use_real_price', True)
    set_option("avoid_future_data", True)
    log.set_level('system', 'error')
    set_slippage(PriceRelatedSlippage(0.00246),type='stock')
    set_order_cost(OrderCost(close_tax=0.001, open_commission=0.0003, close_commission=0.0003, min_commission=5), type='stock')
    run_weekly(trade,1)
    
def trade(context):
    stocks = get_index_stocks('000985.XSHG')
    df = get_fundamentals(query(valuation.code,
            valuation.pb_ratio,
            indicator.inc_net_profit_year_on_year,
            ).filter(
                valuation.code.in_(stocks),
                valuation.pb_ratio >0,
                indicator.roe >4,
            ))
    df = df.sort_values('pb_ratio', ascending=True)[:100]
    df = df.sort_values('inc_net_profit_year_on_year', ascending=False)[:50]
    stocks =df['code'].tolist()
    
    price = history(count=100,unit='20d',field='close',security_list=stocks)
    diff = price[-20:].mean() -  price.mean()
    df = pd.DataFrame(diff)
    buy = df[df<0.0].dropna().index
   
    for stock in context.portfolio.positions:
        if stock not in buy:
            order_target(stock,0)#手里有但不符合全清空
    
    to_buy=[stock for stock in buy if stock not in context.portfolio.positions]
    #这是符合条件但没有的
    if len(to_buy)>0:
        cash_per_stock=context.portfolio.available_cash/len(to_buy)#把现有的钱平分给这些股票
        for stock in to_buy:
            order_value(stock, cash_per_stock)
    print("现在持有股票数量：",len(context.portfolio.positions))
