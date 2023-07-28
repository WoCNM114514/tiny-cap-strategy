import pandas as pd
from batch_preprocess import *


# 收益信息
folder_path = r'C:\Users\20536\Desktop\rock\策略研究\小市值_聚宽' 
data_list = read_files(folder_path)
batch_process(data_list)
for file_path, data in zip(glob.glob(folder_path+'/*.xlsx'), data_list):
    data.to_excel(file_path, index=False)
  
# 持仓信息
pos_path = r'C:\Users\20536\Desktop\rock\策略研究\小市值_聚宽\持仓'
pos_list = read_files(pos_path)
refresh = pos_fetch(pos_list)
for path, datas in zip(glob.glob(pos_path+'/*.xlsx'), refresh):
    datas.to_excel(path, index=False)

