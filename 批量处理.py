import pandas as pd
import glob
import warnings
warnings.filterwarnings('ignore')


# 批量读取
def read_files(path):
  file_list = glob.glob(path + '/*.xlsx')
  all_data = []
  for file in file_list:
    data = pd.read_excel(file)
    all_data.append(data)

  return all_data


# 批量处理: 改名, 计算日盈亏
def batch_process(all_data):
  new_col_names = {'时间':'Date',
                     '基准收益':'refer_profit',
                     '策略收益':'strategy_profit',
                     '当日盈利':'gain', 
                     '当日亏损':'loss',
                     '当日买入':'buy',
                     '当日卖出':'sell',
                     '超额收益(%)':'excess'}
  for data in all_data:
        data.rename(columns=new_col_names, inplace=True)
  # 每日盈亏 = 盈利 + 亏损
    for data in all_data:
        data['profit'] = data['gain'] + data['loss']


# 批量提取每日持仓
def pos_fetch(all_data):
    refresh = []
    for data in all_data:
        data['日期'] = pd.to_datetime(data['日期'])
        data = data.groupby('日期')['仓位'].sum().reset_index()
        refresh.append(data)
    return refresh
