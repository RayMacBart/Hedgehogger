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
   # randomized = random.choice([False, False, False, True])
   # objective = random.choice(['SQN', 'SQN', 'Expectancy [%]', 'Expectancy [%]',
   #                            'Profit Factor', 'Profit Factor', 'Avg. Trade [%]',
   #                            'Calmar Ratio', 'Calmar Ratio', 'Sortino Ratio', 'Sortino Ratio', 'Sharpe Ratio', 'Sharpe Ratio',
   #                            'Return [%]', 'Equity Final [$]', 'Equity Peak [$]', 'Win Rate [%]'
   #                            ])
   # dataspan = random.randrange(2000, 15000)
   # pastshift = random.randrange(0, 100000//dataspan)
   # asset = random.choice(['EURUSD', 'AUDUSD', 'USDJPY'])
   # candlesize = random.choice(['M1', 'M5', 'M15', 'M30', 'H1'])


   pastshift = param  # the only automatically iterated value

   asset, candlesize = get_vars()

   dataspan = 99900
   randomized = False


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


   sqn_mean = -0.3785497274953901
   sqn_std = 4.747979983466789
   expec_mean = 0.004989103069792843
   expec_std = 0.01702601309891024
   calmar_mean = -2.69410745786783
   calmar_std = 9.168788078754021
   sortino_mean = -4.2496372733703796
   sortino_std = 3.8935756666689505
   profac_mean = 2.2252850374777347
   profac_std = 4.455342645663837


   # stats = bt.run()


   max_tries = 260
   # MAKE PARAMETER RANGES RESULTING IN ABOUT >1000 POSSIBLE COMBINATIONS.
   # WAYS TO DO THIS:   4 x 4 x 4 x 4 x 4 = 1024   |   4 x 6 x 6 x 7 = 1008   |   5 x 6 x 6 x 6 = 1080   |   5 x 5 x 6 x 7 = 1050   
   #                    3 x 3 x 4 x 5 x 6 = 1080   |   3 x 6 x 7 x 8 = 1008   |   3 x 7 x 7 x 7 = 1029   |   10 x 10 x 10 = 1000
   #                2 x 3 x 3 x 3 x 4 x 5 = 1080   |   4 x 4 x 8 x 8 = 1024   |   4 x 5 x 6 x 9 = 1080   |   3 x 3 x 3 x 5 x 8 = 1080
   #            2 x 2 x 2 x 3 x 3 x 3 x 5 = 1080   |   2 x 2 x 2 x 3 x 3 x 4 x 4 = 1152 (!)              |   4 x 4 x 6 x 11 = 1056
   #                                               |   2 ^ 10 = 1024                                     |   6 x 6 x 30 = 1080

   stats = bt.optimize(
                  candlesize = [candlesize],
                  order_triggerpower = 28,
                  close_triggerpower = 2,
                  CSP_bodyshrink_factor = 6,
                  CSP_shadow2body_factor = 8,
                  CSP_shadowdiff_factor = 8,
                  CSP_reaction_win = 2,
                  CSP_weight = 2,
                  MACD_zeroweight = 1,
                  MACD_histoweight = 1,
                  MACD_comboweight = 1,
                  MACD_chwin = 3,
                  histo_chwin = 3,
                  MACD_shortwin = 6,
                  MACD_longwin = 15,
                  MACD_signalwin = 2,
                  vwap_expfac = 7,
                  VWAP_chwin = 8,
                  VWAP_weight = 1,
                  fibo_chwin = 3,
                  fibo_weight = 4,
                  cama3_weight = 1,
                  cama4_weight = 2,
                  RSI_win = 11,
                  RSI_chwin = 4, # 3-10
                  RSI_weight = 2,
                  CCI_win = 11,
                  CCI_chwin = 4, # 3-10
                  CCI_weight = 3,
                  ############################
                  bbands_expfac = 3,
                  bbands_win = 20,
                  bbands_weight_out = 1,
                  bbands_weight_trend = 1,
                  bbands_chwin_out = 4,
                  bbands_chwin_trend = 4,
                  vol_mdfpwi = 1,
                  vol_max_impact_zscore = 4,
                  vol_chwin = 3, # 2-?
                  volume_weight = 1,
                  ADX_win = 20,
                  ADX_chwin = 7,
                  ADX_abs_weight = 3,
                  ADX_dyn_weight = 1,
                  sizegap_granularity = 12,
                  sizepeak_granularity = 12,
                  gap_accuracy = 5,  # area of gap value recognition in % --> the lower, the more accurate!
                  peak_accuracy = 6,
                  sizegap_win = 100,
                  sizepeak_win = 100,
                  gap_weight = 1,
                  peak_weight = 3,
                  ATR_win = 14,
                  ATR_chwin = 3,
                  ATR_mincalcwin = 100,
                  ATR_abs_weight = 2,
                  ATR_dyn_weight = 2,
                  SLdist_redufac = [7,10], #4 was 8
                  bbands_TSL_chwin = [5,8], #4 was 7
                  PSAR_weight = [1,3],  #3 was 2
                  bbands_TSL_weight = [1,3], #3 was 2
                  ATR_TSL_weight = [2,4], #3 was 3
                  power_TSL_weight = [1,3], #3 was 2

                  maximize = (((stats["SQN"]-sqn_mean)/sqn_std)*38 + \
                              ((stats["Expectancy [%]"]-expec_mean)/expec_std)*22 + \
                              ((stats["Calmar Ratio"]-calmar_mean)/calmar_std)*16 + \
                              ((stats["Sortino Ratio"]-sortino_mean)/sortino_std)*13 + \
                              ((stats["Profit Factor"]-profac_mean)/profac_std)*11)

                  # maximize = objective,
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
                  'order_triggerpower': 28,
                  'close_triggerpower': 2,
                  'CSP_bodyshrink_factor': 6,
                  'CSP_shadow2body_factor': 8,
                  'CSP_shadowdiff_factor': 8,
                  'CSP_reaction_win': 2,
                  'CSP_weight': 2,
                  'MACD_zeroweight': 1,
                  'MACD_histoweight': 1,
                  'MACD_comboweight': 1,
                  'MACD_chwin': 3,
                  'histo_chwin': 3,
                  'MACD_shortwin': 6,
                  'MACD_longwin': 15,
                  'MACD_signalwin': 2,
                  'vwap_expfac': 7,
                  'VWAP_chwin': 8,
                  'VWAP_weight': 1,
                  'fibo_chwin': 3,
                  'fibo_weight': 4,
                  'cama3_weight': 1,
                  'cama4_weight': 2,
                  'RSI_win': 11,
                  'RSI_chwin': 4, # 3-10
                  'RSI_weight': 2,
                  'CCI_win': 11,
                  'CCI_chwin': 4, # 3-10
                  'CCI_weight': 3,
                  '############################
                  'bbands_expfac': 3,
                  'bbands_win': 20,
                  'bbands_weight_out': 1,
                  'bbands_weight_trend': 1,
                  'bbands_chwin_out': 4,
                  'bbands_chwin_trend': 4,
                  'vol_mdfpwi': 1,
                  'vol_max_impact_zscore': 4,
                  'vol_chwin': 3, # 2-?
                  'volume_weight': 1,
                  'ADX_win': 20,
                  'ADX_chwin': 7,
                  'ADX_abs_weight': 3,
                  'ADX_dyn_weight': 1,
                  'sizegap_granularity': 12,
                  'sizepeak_granularity': 12,
                  'gap_accuracy': 5,  # area of gap value recognition in % --> the lower, the more accurate!
                  'peak_accuracy': 6,
                  'sizegap_win': 100,
                  'sizepeak_win': 100,
                  'gap_weight': 1,
                  'peak_weight': 3,
                  'ATR_win': 14,
                  'ATR_chwin': 3,
                  'ATR_mincalcwin': 100,
                  'ATR_abs_weight': 2,
                  'ATR_dyn_weight': 2,
                  'SLdist_redufac': [7,10], #4 was 8
                  'bbands_TSL_chwin': [5,8], #4 was 7
                  'PSAR_weight': [1,3],  #3 was 2
                  'bbands_TSL_weight': [1,3], #3 was 2
                  'ATR_TSL_weight': [2,4], #3 was 3
                  'power_TSL_weight': [1,3], #3 was 2
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
#    3. LET IT RUN THROUGH 8 x 12.500 PASTSHIFTED OPTIMIZATIONS AND COMBINE THE PARAMETER RESULTS TO ONE RESULT, 
#                                     BUT WEIGHTED IN A CHRONOLOGICAL WAY: LET THE MOST RECENT DATA BE 8 TIMES WORTH THE OLDEST DATA.
#                                     FOR THIS, USE A LINEAR WEIGHT DECREASE (LOSING THE SAME ABSOLUTE WEIGHT EACH STEP ON THE WAY TO 1/8).
#                                     DECREMENT THE NUMERATOR OF 8/8 BY ONE EACH STEP!
#    2. LET IT RUN THROUGH 20 x 5000 PASTSHIFTED OPTIMIZATIONS AND COMBINE THE PARAMETER RESULTS TO ONE RESULT, 
#                                     BUT WEIGHTED IN A CHRONOLOGICAL WAY: LET THE MOST RECENT DATA BE 20 TIMES WORTH THE OLDEST DATA.
#                                     FOR THIS, USE A RECIPROCAL, HYPERBOLIC WEIGHT DECREASE (STARTING FAST, ENDING SLOW).
#                                     INCREMENT THE DENOMINATOR THE ORIGINAL, FIRST VALUE SHALL BE DIVIDED WITH BY ONE EACH STEP!
#    4. LET IT RUN THROUGH 10 x 10.000 RANDOMIZED DATA AND COMBINE THE RESULTS
#    5. COMBINE THE RESULTS OF 1-4.


paramlist = [0,
            #  1,2,3,4,5,6,7,
            #  8,9,
            #  10,11,12,13,14,15,16,17,18,19
             ]


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