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
    run_daily(trade,"9:30")
    
def trade(context):
    stocks = get_index_stocks('000985.XSHG')
    df = get_fundamentals(query(valuation.code,
            valuation.pb_ratio,
            indicator.inc_net_profit_year_on_year,
            ).filter(
                valuation.code.in_(stocks),
                valuation.pb_ratio >0,
                indicator.roe >5,
            ))
    df = df.sort_values('pb_ratio', ascending=True)[:100]
    df = df.sort_values('inc_net_profit_year_on_year', ascending=False)[:50]
    stocks =df['code'].tolist()
    # 删除ST,北交
    # 此处如果删除ST股，策略的净值将大打折扣，有待实际复盘确认为何策略不规避高退市风险的ST股
    stocks = filter_kcbj_stock(stocks)
    #stocks = filter_st_stock(stocks)
    
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

# 准备股票池
def prepare_stock_list(context):
    # 获取已持有列表
    g.high_limit_list = []
    g.low_limit_list = []
    hold_list = list(context.portfolio.positions)
    if hold_list:
        df = get_price(hold_list, end_date=context.previous_date, frequency='daily',
                       fields=['close', 'high_limit', 'low_limit', 'paused'],
                       count=1, panel=False)
        g.high_limit_list = df.query('close==high_limit and paused==0')['code'].tolist()
        g.low_limit_list = df.query('close==low_limit and paused==0')['code'].tolist()
        
#  调整昨日涨停股票
def check_limit_up(context):
    current_data = get_current_data()
    if g.high_limit_list:
        for stock in g.high_limit_list:
            if current_data[stock].last_price < current_data[stock].high_limit:
                log.info("[%s]涨停打开，卖出" % stock)
                position = context.portfolio.positions[stock]
                close_position(position)
            else:
                log.info("[%s]涨停，继续持有" % stock)
                
# 过滤停牌股票
def filter_paused_stock(stock_list):
    current_data = get_current_data()
    return [stock for stock in stock_list if not current_data[stock].paused]

# 过滤科创北交股票
def filter_kcbj_stock(stock_list):
    for stock in stock_list[:]:
        if stock[0] == '4' or stock[0] == '8' or stock[:2] == '68':
            stock_list.remove(stock)
    return stock_list
    
# 过滤ST及其他具有退市标签的股票
def filter_st_stock(stock_list):
    current_data = get_current_data()
    return [stock for stock in stock_list if not (
            current_data[stock].is_st or
            'ST' in current_data[stock].name or
            '*' in current_data[stock].name or
            '退' in current_data[stock].name)]
