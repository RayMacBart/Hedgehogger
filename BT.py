import os
import time
import helpers
import pandas as pd
from backtesting import Backtest
from Hedgehog import Hedgehog
import printer
from multiprocessing import Pool
import sambo


def do_backtest(paramlist):

   ### uncomment for use of automatic variable looping ###
   # asset = paramlist['asset']
   # candlesize = paramlist['candlesize']
   ###########################

   ### uncomment for manually adjustable variables (if wanted/not automated): ###
   asset = 'EURUSD'
   candlesize = 'M1'
   ###########################

   dataspan = 2600
   
   pastshift = paramlist['pastshift']
   adjufac = 100 if asset == "USDJPY" else 1  # adjustment factor for the USD/JPY pair which has a 100x higher pip-size!
   
   if dataspan*(pastshift+1) > 100000:
      raise helpers.insufficientDataError("Can't handle given dataspan and pastshift due to insufficient amount of data.")

   try:
      file_path = os.path.join("data", f"{asset}_{candlesize}.csv")
      if not os.path.exists(file_path):
         raise FileNotFoundError(f"File not found: {file_path}")
      df = pd.read_csv(file_path, sep="\t", parse_dates=['Timestamp'], index_col='Timestamp').iloc[-dataspan*(pastshift+1):
                                                                                                   (-dataspan*pastshift if pastshift else None)]
      print("Data successfully loaded!")
   except Exception as e:
      print('Error occured during loading MAIN PRICE CHART data:\n', e)

   try:
      file_path2 = os.path.join("volmean_data", f"volmean_{asset}_{candlesize}.csv")
      if not os.path.exists(file_path2):
         raise FileNotFoundError(f"File not found: {file_path2}")
      volmean_df = pd.read_csv(file_path2, sep="\t")
      print("Volmean Data successfully loaded!")
   except Exception as e:
      print('Error occured during loading VOLUME MEAN data:', e)


   clims = 60 if candlesize == 'H1' else int(candlesize[1:])  # clims = candle length in minutes

   # df = df.map(helpers.remove_nocomma_anomaly)   --> leads to false manipulation of Volume data

   df['Open'] = df['Open'].apply(helpers.remove_nocomma_anomaly)
   df['High'] = df['High'].apply(helpers.remove_nocomma_anomaly)
   df['Low'] = df['Low'].apply(helpers.remove_nocomma_anomaly)
   df['Close'] = df['Close'].apply(helpers.remove_nocomma_anomaly)

   df['Volume'] = helpers.adjust_volume_data(df['Volume']).set_axis(df.index)

   impact_counter = {'MACD': 0, 'MACD-zeroX': 0, 'MACD-sigX': 0, 'VWAP': 0, 'FIBO': 0, 'RSI': 0, 'RSI-abs': 0, 'RSI-dyn': 0,
                     'CCI': 0, 'CCI-abs': 0, 'CCI-dyn': 0, 'BB-out': 0, 'BB-trend': 0, 'ADX': 0, 'ADX-abs': 0, 'ADX-dyn': 0,
                     'VOL': 0, 'CAMA': 0, 'GAP': 0, 'PEAK': 0, 'ATR': 0, 'ATR-abs': 0, 'ATR-dyn': 0}



   bt = Backtest(df, Hedgehog, cash=1000, 
               commission=0.00012*adjufac, 
               margin=0.033, hedging=True)


   stats = bt.run(outvars={'volmean_df': volmean_df, 'clims': clims, 'impact_counter': impact_counter, 'adjufac': adjufac})

   # stats = bt.optimize(outvars={'volmean_df': volmean_df, 'clims': clims, 'impact_counter': impact_counter, 'adjufac': adjufac},
   #                MACD_shortwin = [3,25],
   #                MACD_longwin = [4,50],
   #                MACD_signalwin = [2,20],
   #                MACD_chwin = [3,8],
   #                maximize = 'Expectancy [%]',
   #             #    maximize = lambda stats: stats['Profit Factor'] 
   #             #    if stats['# Trades'] >= 100 else -np.inf,
   #                method='sambo',
   #                max_tries=500,
   #                constraint=lambda p: p.MACD_signalwin < p.MACD_shortwin < p.MACD_longwin
   #             )

   # bt.plot()

   return {'asset': asset, 'candlesize': candlesize, 'pastshift': pastshift, "stats": stats}
   


### code for automatic iteration through all variables: ###
# paramlist = []
# for asset in ['EURUSD', 'AUDUSD', 'USDJPY']:
#    for candlesize in ['M1', 'M5', 'M15']:
#       for pastshift in [0,1,2]:
#          paramlist.append({'asset': asset, 'candlesize': candlesize, 'pastshift': pastshift})
#############################################

### code for iteration through pastshift values only ###
paramlist = [0,1,2,3,4]
#############################################

if __name__ == '__main__':

   start_time = time.time()

   with Pool() as p:
      results = p.map(do_backtest, paramlist)

   time_taken = time.time() - start_time
   print(f'The backtesting took {time_taken} seconds.')
   printer.print_results(results)
   printer.dump_results(results)



   # for optimization, include the objectives return%, profit factor, sharpe ratio, sortino ratio and calmar ratio
   # and give each the same weight resulting into one single value to be optimized. This is done by calculating the
   # z score - normalization of 30 optimization results of each objective. Then, the mean of all z scores (of every
   # objective) is the final result to be used for the optimization functions.
   # try your best regarding optimization of every objective when collecting the 30 needed results, but use the same
   # inputs in the optimize() functions for every objective - this ensures a cross-objective consistent normalization 
   # on a high, fastidious niveau.

      #    stopdist = [
         # 0.00001, 0.00002, 0.00003, 0.00004, 0.00005, 0.00006, 0.00007, 0.00008, 0.00009, 0.0001, 
         #          0.00011, 0.00012, 0.00013, 0.00014, 0.00015, 0.00016, 0.00017, 0.00018, 0.00019, 0.0002,
         #          0.00021, 0.00022, 0.00023, 0.00024, 0.00025, 0.00026, 0.00027, 0.00028, 0.00029, 0.0003,
                  # 0.00031, 0.00032, 0.00033, 0.00034, 0.00035, 0.00036, 0.00037, 0.00038, 0.00039, 0.0004,
                  # 0.00041, 0.00042, 0.00043, 0.00044, 0.00045, 0.00046, 0.00047, 0.00048, 0.00049, 0.0005,
                  # 0.00051, 0.00052, 0.00053, 0.00054, 0.00055, 0.00056, 0.00057, 0.00058, 0.00059, 0.0006,
                  # 0.00061, 0.00062, 0.00063, 0.00064, 0.00065, 0.00066, 0.00067, 0.00068, 0.00069, 0.0007,
                  # 0.00071, 0.00072, 0.00073, 0.00074, 0.00075, 0.00076, 0.00077, 0.00078, 0.00079, 0.0008,
                  # 0.00081, 0.00082, 0.00083, 0.00084, 0.00085, 0.00086, 0.00087, 0.00088, 0.00089, 0.0009
                  # ],