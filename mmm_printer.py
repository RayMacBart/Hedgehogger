# "mmm" = mean, max and min
import sys
import os
import numpy as np
import pandas as pd
import helpers
from volfuncs import adjust_volume_data

asset = sys.argv[1]
candlesize = sys.argv[2]

try:
   file_path = os.path.join("data", f"{asset}_{candlesize}.csv")
   if not os.path.exists(file_path):
      raise FileNotFoundError(f"File not found: {file_path}")
   df = pd.read_csv(file_path, sep="\t", parse_dates=['Timestamp'], index_col='Timestamp')
   print("Data successfully loaded!")
except Exception as e:
   print('Error occured during loading MAIN PRICE CHART data:\n', e)

df['Open'] = df['Open'].apply(helpers.remove_nocomma_anomaly)
df['High'] = df['High'].apply(helpers.remove_nocomma_anomaly)
df['Low'] = df['Low'].apply(helpers.remove_nocomma_anomaly)
df['Close'] = df['Close'].apply(helpers.remove_nocomma_anomaly)
df['Volume'] = adjust_volume_data(df['Volume']).set_axis(df.index)

pricewidths = [row.High - row.Low for row in df.itertuples()]
maxwidth = round(max(pricewidths), 5)
minwidth = round(min(pricewidths), 5)
widthmean = round(np.mean(pricewidths), 5)
maxprice = round(max(list(df['High'])), 5)
minprice = round(min(list(df['Low'])), 5)
closemean = round(np.mean(list(df['Close'])), 5)
maxvol = round(np.max(list(df['Volume'])), 5)
minvol = round(np.min(list(df['Volume'])), 5)
volmean = round(np.mean(list(df['Volume'])), 5)
print(f"- - - - - - -\n{asset} ({candlesize}):\n  price mean: {closemean}\n  \
price max: {maxprice}\n  price min: {minprice}\n")
print(f"  width mean: {widthmean}\n  \
width max: {maxwidth}\n  width min: {minwidth}\n")
print(f"  vol mean: {volmean}\n  \
vol max: {maxvol}\n  vol min: {minvol}\n- - - - - - -")