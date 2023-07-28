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
