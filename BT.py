import os
import time
import pandas as pd
import helpers
from backtesting import Backtest
from Hedgehog import Hedgehog
from var_config import get_vars
import printer
import sambo
# from multiprocessing import Pool  
# multiprocessing.Pool only makes sense with huge datasets used with 'run()'
# since 'optimize()' automatically comes with multiprocessing by default


def do_backtest(param):

   pastshift = param  # the only automatically iterated value
   asset, candlesize = get_vars()
   dataspan = 2600

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


   # df = df.map(helpers.remove_nocomma_anomaly)   --> leads to false manipulation of Volume data
   df['Open'] = df['Open'].apply(helpers.remove_nocomma_anomaly)
   df['High'] = df['High'].apply(helpers.remove_nocomma_anomaly)
   df['Low'] = df['Low'].apply(helpers.remove_nocomma_anomaly)
   df['Close'] = df['Close'].apply(helpers.remove_nocomma_anomaly)

   df['Volume'] = helpers.adjust_volume_data(df['Volume']).set_axis(df.index)


   bt = Backtest(df, Hedgehog, cash=1000, 
               commission=0.00012*adjufac,
               margin=0.033, hedging=True)


   # stats = bt.run()

   stats = bt.optimize(
                  MACD_shortwin = [3,25],
                  MACD_longwin = [4,50],
                  MACD_signalwin = [2,20],
                  MACD_chwin = [3,8],
                  maximize = 'Expectancy [%]',
               #    maximize = lambda stats: stats['Profit Factor'] 
               #    if stats['# Trades'] >= 100 else -np.inf,
                  # method='sambo',
                  # max_tries=500,
                  constraint=lambda p: p.MACD_signalwin < p.MACD_shortwin < p.MACD_longwin
               )

   bt.plot()

   return {'asset': asset, 'candlesize': candlesize, 'pastshift': pastshift, "stats": stats}
   



paramlist = [0,1,2,3,4]

if __name__ == '__main__':

   start_time = time.time()

   # with Pool() as p:                            # This only makes sense with huge datasets used with 'run()'
   #    results = p.map(do_backtest, paramlist)   # since 'optimize()' automatically comes with multiprocessing by default

   results = list(map(do_backtest, paramlist))

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


###### old idea but has complications so far:  #####
### code for automatic iteration through all variables: ###
# paramlist = []
# for asset in ['EURUSD', 'AUDUSD', 'USDJPY']:
#    for candlesize in ['M1', 'M5', 'M15']:
#       for pastshift in [0,1,2]:
#          paramlist.append({'asset': asset, 'candlesize': candlesize, 'pastshift': pastshift})
#############################################

### code for iteration through pastshift values only ###
# paramlist = [0,1,2,3,4]
#############################################