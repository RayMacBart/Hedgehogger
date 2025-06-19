import os
import time
import pandas as pd
import helpers
import random
from backtesting import Backtest
from Hedgehog import Hedgehog
from volfuncs import adjust_volume_data
from var_config import get_vars
import printer
import sambo
from data_randomizer import get_randomized_df
from messager import send_msg
from copy import deepcopy
# from multiprocessing import Pool  
# multiprocessing.Pool only makes sense with huge datasets used with 'run()'
# since 'optimize()' automatically comes with multiprocessing by default


def do_backtest(param):

   # for objective result data collection:
   randomized = random.choice([False, False, False, True])
   objective = random.choice(['SQN', 'SQN', 'SQN', 'SQN', 'Expectancy [%]', 'Expectancy [%]', 'Expectancy [%]',
                              'Profit Factor', 'Profit Factor', 'Profit Factor', 'Avg. Trade [%]', 'Avg. Trade [%]',
                              'Calmar Ratio', 'Calmar Ratio', 'Sortino Ratio', 'Sortino Ratio', 'Sharpe Ratio', 'Sharpe Ratio',
                              'Return [%]', 'Equity Final [$]', 'Equity Peak [$]', 'Win Rate [%]'
                              ])
   dataspan = random.randrange(2000, 15000)
   pastshift = random.randrange(0, 100000//dataspan)
   asset = random.choice(['EURUSD', 'AUDUSD', 'USDJPY'])
   candlesize = random.choice(['M1', 'M5', 'M15', 'M30', 'H1'])
   

   # pastshift = param  # the only automatically iterated value   # REUSE AFTER MAX_TRIES RESEARCH!

   # asset, candlesize = get_vars()
   # dataspan = 10000

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

   df['Volume'] = adjust_volume_data(df['Volume']).set_axis(df.index)

   if randomized:
      df = get_randomized_df(df, asset, candlesize, dataspan*(pastshift+1))


   bt = Backtest(df, Hedgehog, cash=1000,
               commission=0.00012, # *adjufac,
               margin=0.033, hedging=True)


   # stats = bt.run()


   # exp_mean = 0.04478376247033701
   # exp_std = 0.0785345476064135
   # profac_mean = 10.646798066188657
   # profac_std = 11.569063820793623
   # SQN_mean = 1.1334995423126992
   # SQN_std = 0.45195832041663986


   max_tries = 162
   # MAKE PARAMETER RANGES RESULTING IN ABOUT >1000 POSSIBLE COMBINATIONS.
   # WAYS TO DO THIS:   4 x 4 x 4 x 4 x 4 = 1024   |   4 x 6 x 6 x 7 = 1008   |   5 x 6 x 6 x 6 = 1080   |   5 x 5 x 6 x 7 = 1050   
   #                    3 x 3 x 4 x 5 x 6 = 1080   |   3 x 6 x 7 x 8 = 1008   |   3 x 7 x 7 x 7 = 1029   |   10 x 10 x 10 = 1000

   stats = bt.optimize(
                  order_triggerpower = [3,6], #4
                  close_triggerpower = [-1,1], #3
                  MACD_shortwin = [3,7], #5
                  MACD_longwin = [7,12], #6
                  MACD_signalwin = [2,4], #3
                  MACD_zeroweight = 1,
                  MACD_histoweight = 1,
                  MACD_comboweight = 1,
                  MACD_chwin = 3,
                  histo_chwin = 3, # was 5
                  CSP_bodyshrink_factor = 6,
                  CSP_shadow2body_factor = 8,
                  CSP_shadowdiff_factor = 8,
                  CSP_weight = 1,
                  RSI_win = 20,
                  RSI_chwin = 3, # was 5
                  RSI_weight = 1,
                  CCI_win = 20,
                  CCI_chwin = 3, # was 5
                  CCI_weight = 1,
                  SLdist_redufac = 10,
                  bbands_TSL_chwin = 6,
                  ATR_chwin = 7,
                  PSAR_weight = 2,
                  bbands_TSL_weight = 2,
                  ATR_TSL_weight = 3,
                  power_TSL_weight = 3,

                  maximize = objective,
                  # maximize = lambda stats: (stats["Expectancy [%]"]-exp_mean)/exp_std + \
                  #                          (stats["Profit Factor"]-profac_mean)/profac_std + \
                  #                          (stats["SQN"]-SQN_mean)/SQN_std,
               #    if stats['# Trades'] >= 100 else -np.inf,

                  method='sambo',
                  max_tries=max_tries,
                  # constraint=lambda p: p.MACD_signalwin <= p.MACD_shortwin < p.MACD_longwin
                  # constraint=lambda p: p.MACD_shortwin < p.MACD_longwin
               )
   param_opt_log_dict = {
                  'order_triggerpower': [3,6], #4
                  'close_triggerpower': [-1,1], #3
                  'MACD_shortwin': [3,7], #5
                  'MACD_longwin': [7,12], #6
                  'MACD_signalwin': [2,4], #3
                  'MACD_zeroweight': 1,
                  'MACD_histoweight': 1,
                  'MACD_comboweight': 1,
                  'MACD_chwin': 3,
                  'histo_chwin': 3, # was 5
                  'CSP_bodyshrink_factor': 6,
                  'CSP_shadow2body_factor': 8,
                  'CSP_shadowdiff_factor': 8,
                  'CSP_weight': 1,
                  'RSI_win': 20,
                  'RSI_chwin': 3, # was 5
                  'RSI_weight': 1,
                  'CCI_win': 20,
                  'CCI_chwin': 3, # was 5
                  'CCI_weight': 1,
                  'SLdist_redufac': 10,
                  'bbands_TSL_chwin': 6,
                  'ATR_chwin': 7,
                  'PSAR_weight': 2,
                  'bbands_TSL_weight': 2,
                  'ATR_TSL_weight': 3,
                  'power_TSL_weight': 3,
   }
   

   print(f'{param} done.')

   # print(stats)

   # bt.plot()

   return {'asset': asset, 'candlesize': candlesize, 'pastshift': pastshift, 'dataspan': dataspan, 'stats': stats,
           'randomized': randomized, 'objective': objective, 'param_opt_log_dict': param_opt_log_dict}
   



# USE 25 AS DIFFERENT AS POSSIBLE STRATEGY CONFIGURATIONS, AND FOR EACH ONE, LOOP THROUGH ALL 10 PASTSHIFTS (dataspan=10.000 each),
# WITH DIFFERENT OBJECTIVES OPTIMIZED FOR EACH PASTSHIFT. WHEN CHANGING THE STRATEGY CONFIGURATIONS, ALSO CHANGE THE ORDER OF THE USED
# OBJECTIVES OVER THE PASTSHIFTS. THE DIFFERENT STRATEGY CONFIGURATIONS SHALL SAMBO OPTIMIZE 1.000 POSSIBLE COMBINATIONS WITH MAX_TRIES
# SET TO 200 (=20%) EACH. FOR EVERY SINGLE OPTIMIZATION, COLLECT RESULT DATA FROM ALL OBJECTIVES FOR LATER Z-SCORE USE.


# WHEN IT COMES TO THE REAL OPTIMIZATION, USE A ZSCORE NORMALIZED COMBINATION OF OBJECTIVES WITH 5 OBJECTIVES MELTED TOGETHER IN WEIGHTED WAY:
# SQN: 38%,   EXPECTANCY: 22%,   CALMAR RATIO: 16%,   SORTINO RATIO: 13%,   PROFIT FACTOR: 11%

# OPTIMIZE EACH SINGLE INDICATOR BY LETTING IT RUN THROUGH THE WHOLE 100.000 DATAPOINTS.
# 
# WHEN IT COMES TO THE OVERALL OPTIMIZATION:
#    1. LET IT RUN THROUGH THE WHOLE 100.000 DATAPOINTS
#    2. LET IT RUN THROUGH 8 x 12.500 PASTSHIFTED OPTIMIZATIONS AND COMBINE THE PARAMETER RESULTS TO ONE RESULT, 
#                                     BUT WEIGHTED IN A CHRONOLOGICAL WAY: LET THE MOST RECENT DATA BE 8 TIMES WORTH THE OLDEST DATA.
#    3. LET IT RUN THROUGH 10 x 10.000 RANDOMIZED DATA AND COMBINE THE RESULTS
#    4. COMBINE THE RESULTS OF 1-3.


paramlist = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,
            #  17,18,19,20
             ]
            # for using dataspan 2600 but usage of full data (100.000): use here up to 37


if __name__ == '__main__':

   time_taken = None
   start_time = time.time()
   try:

      # with Pool() as p:                            # This only makes sense with huge datasets used with 'run()'
      #    results = p.map(do_backtest, paramlist)   # since 'optimize()' automatically comes with multiprocessing by default

      results = list(map(do_backtest, paramlist))

      time_taken = time.time() - start_time

      printer.print_results(results)
      printer.dump_results(results)

      time_repr = f'{int(time_taken)} sec' if time_taken < 60 else f'{int(time_taken//60)} mins  {int(time_taken%60)} secs'
      print(f'The backtesting took  {time_repr}')
      send_msg(f'Calculations finished successfully!\nDuration (in seconds):\n{time_repr}')

   except Exception as e:
      time_taken = time.time() - start_time
      time_repr = f'{int(time_taken)} sec' if time_taken < 60 else f'{int(time_taken//60)} mins   {int(time_taken%60)} secs'
      send_msg(f'Calculations finished due to Error:\n{str(e)}\nDuration (in seconds):\n{time_repr}')
      raise e





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