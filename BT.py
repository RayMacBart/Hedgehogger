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


def do_backtest(
               #  param,
                minTSL,
                CHWIN
               #  TRIP,
               #  randomized
                ):

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


   # pastshift = param  # the only automatically iterated value


   asset, candlesize = get_vars()
   
   dataspan = 30000
   pastshift = 0
   # dataspan = 99900
   # dataspan = 8330
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


   bt = Backtest(df, Hedgehog, cash=100000,
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


   max_tries = 40

   # MAKE PARAMETER RANGES RESULTING IN ABOUT >1000 POSSIBLE COMBINATIONS.
   # WAYS TO DO THIS:   4 x 4 x 4 x 4 x 4 = 1024   |   4 x 6 x 6 x 7 = 1008   |   5 x 6 x 6 x 6 = 1080   |   5 x 5 x 6 x 7 = 1050   
   #                    3 x 3 x 4 x 5 x 6 = 1080   |   3 x 6 x 7 x 8 = 1008   |   3 x 7 x 7 x 7 = 1029   |   10 x 10 x 10 = 1000
   #                2 x 3 x 3 x 3 x 4 x 5 = 1080   |   4 x 4 x 8 x 8 = 1024   |   4 x 5 x 6 x 9 = 1080   |   3 x 3 x 3 x 5 x 8 = 1080
   #            2 x 2 x 2 x 3 x 3 x 3 x 5 = 1080   |   2 x 2 x 2 x 3 x 3 x 4 x 4 = 1152 (!)              |   4 x 4 x 6 x 11 = 1056
   #                           9 x 9 x 13 = 1053   |   2 ^ 10 = 1024                                     |   6 x 6 x 30 = 1080
   #                          7 x 12 x 12 = 1008   |   3 x 13 x 26 = 1014
   

   # WARNING: I HAVE SET 'SIZE' @ HEDGEHOG.PY TO 0.001 (INSTEAD OF 0.1) AND CASH @ BACKTEST() ABOVE TO 100.000 (INSTEAD OF 1.000)!!!
   stats = bt.optimize(

                  # FIRST WEIGHT OPTIMIZED SHIFT INDICATOR GROUP: CSP, VWAP, FIBO, CCI & BBout  (total weight currently at 9)
                  # SECOND WEIGHT OPTIMIZED SHIFT INDICATOR GROUP: MACD (3), CAMA (2), RSI

                  candlesize = [candlesize],
                  # "fos" = future optimization suggestion, "fhwt" = frequent hence worth try, "lar" = long average result
                  order_triggerpower = 1,       # was 18 for first trend opt
                  close_triggerpower = 1, # was 
                  # CHWIN = CHWIN,
                  # CSP_bodyshrink_factor = 4,
                  # CSP_shadow2body_factor = 3,
                  # CSP_shadowdiff_factor = 5,
                  # CSP_reaction_win = 6,   # maybe consider less for fastness
                  # CSP_weight = 1,

                  # MACD_zeroweight = 1, #[0,2], # was 1
                  # MACD_histoweight = 1, #[1,3],   # way better results than zero & combo!   # was 2
                  # MACD_comboweight = 2, #[0,2],   # was 1
                  # MACD_longwin = 5, #[4,10], #7
                  # MACD_shortwin = 3, #[3,8], #6
                  # MACD_signalwin = 3, #[2,7], #6
                  # MACD_chwin = 2,
                  # histo_chwin = 2,
                  # combo_chwin = 2,
                  # MACD_chval_th = 1,  # only relevant for combo.

                  vwap_expfac = [1,2,3,4,5,6,7,8,9,10],
                  VWAP_chwin = CHWIN, # was 3
                  VWAP_weight = 1,   # was 1  (bad performance)
                  # fibo_chwin = CHWIN, # recently was 3, # lar: 4, modern: 6
                  # fibo_weight = 1, # recently was 2, # was 4 (old)   # bad performance --> was 1 (new)
                  # cama3_weight = 1,# [0,2],  # was 1
                  # cama4_weight = 1,# [0,2],  # was 2
                  # RSI_win = 13,  # (modern static: 4)
                  # RSI_chwin = 9,  # fhwt: 5     # 3-10     (recently was 3)
                  # RSI_bound_distance = 30,  # = second best. optimize it again with other indicators. "5" came actually as best result
                  # RSI_chval_th = [1,20],  # first idea, can be altered
                  # RSI_weight = 1,# [1,3], # was 2 (old)  # good performance --> 3 (new)
                  # CCI_win = 4,
                  # CCI_chwin = CHWIN,  # (dyn. fhwt: 4)    (recently was choosen as 3)
                  # CCI_treshold_distance = 120,  # was 80 with fos: [40,85]
                  # CCI_chval_th = [10,50],  # first idea, can be altered
                  # CCI_weight = 1, # recently: 2  # was 3 (old), but CCI had very bad performance compared to RSI! --> middle-new was 1
                  # ############################
                  # bbands_win = 22, # fhwt: 3 & 4    # was 20 (!!! ALSO AFFECTS SL!!!)
                  # bbands_chwin_out = 1, # recently was 9,  # fhwt: 8  (if trying 'win' with 3 or 4, set chwin to 3)
                  # bbands_weight_out = 1, # recently was 3,  # was 1  (bad performance)
                  # bbands_chwin_trend = CHWIN,#[3,8], #6   # was 4
                  # bbands_expfac = 1,#[1,9],   # was 3 (only affects trend-BB, even not SL)
                  # bbands_weight_trend = 1, # was 20,
                  # vol_mdfpwi = 1,
                  # vol_max_impact_zscore = 4,
                  # vol_chwin = 2, # was 3, # 2-?
                  # volume_weight = 1,
                  # ADX_win = 20,
                  # ADX_chwin = 2, # was 7
                  # ADX_abs_weight = 1, # was 3
                  # ADX_dyn_weight = 1,
                  # sizegap_granularity = 12,
                  # sizepeak_granularity = 12,
                  # gap_accuracy = 5,  # area of gap value recognition in % --> the lower, the more accurate!
                  # peak_accuracy = 6,
                  # sizegap_win = 100,
                  # sizepeak_win = 100,
                  # gap_weight = 1,
                  # peak_weight = 3,
                  # ATR_win = 14,
                  # ATR_chwin = CHWIN, # was 3
                  # ATR_mincalcwin = 100,
                  # ATR_abs_weight = 1, # was 2
                  # ATR_dyn_weight = 1, # was 2
                  SLdist_redufac = 9,
                  bbands_TSL_chwin = 7,
                  PSAR_weight = 1,
                  bbands_TSL_weight = 1,
                  ATR_TSL_weight = 2,
                  power_TSL_weight = 3,
                  minTSLdist = minTSL, # minTSL   # best so far: (csp & macd_zero): 12 (or 8)

                  maximize = lambda stats: (
                     ((stats["SQN"]-sqn_mean)/sqn_std)*38 +
                     ((stats["Expectancy [%]"]-expec_mean)/expec_std)*22 +
                     ((stats["Calmar Ratio"]-calmar_mean)/calmar_std)*16 +
                     ((stats["Sortino Ratio"]-sortino_mean)/sortino_std)*13 +
                     ((stats["Profit Factor"]-profac_mean)/profac_std)*11
                  ),

                  # maximize = objective,
                  # maximize = lambda stats: (stats["Expectancy [%]"]-exp_mean)/exp_std + \
                  #                          (stats["Profit Factor"]-profac_mean)/profac_std + \
                  #                          (stats["SQN"]-SQN_mean)/SQN_std,
               #    if stats['# Trades'] >= 100 else -np.inf,

                  # method='sambo',
                  # max_tries=max_tries,
                  # constraint=lambda p: p.MACD_signalwin <= p.MACD_shortwin < p.MACD_longwin
                  # constraint=lambda p: p.MACD_shortwin < p.MACD_longwin
               )
   param_opt_log_dict = {
                  'order_triggerpower': 1,
                  'close_triggerpower': 1, # was 2
                  'minTSLdist': minTSL,  # minTSL   # best so far for both csp & macd_zero is 12 though
                  'VWAP_chwin': CHWIN, # was 3
                  'vwap_expfac': [1,2,3,4,5,6,7,8,9,10],
                  'VWAP_weight': 1,   # was 1  (bad performance)
                  'SLdist_redufac': 9,
                  'bbands_TSL_chwin': 7,
                  'PSAR_weight': 1,
                  'bbands_TSL_weight': 1,
                  'ATR_TSL_weight': 2,
                  'power_TSL_weight': 3
   }
   
                  

   time.sleep(20)

   print(f'CHWIN={CHWIN},  minTSL={minTSL}  done.')

   # print(stats)

   # bt.plot()

   return {'asset': asset, 'candlesize': candlesize, 'pastshift': pastshift, 'dataspan': dataspan, 'stats': stats,
           'randomized': randomized,
         #   'objective': objective,
           'param_opt_log_dict': param_opt_log_dict}
   



# paramlist = [0,0,0,0,0,0,0,0,0,0,
#              0,0,0,0,0,0,0,0,0,0,
#              0,0,0,0,0,0,0,0,0,0,
#              0,0,0,0,0,0,0,0,0,0,
#              0,0,0,0,0,0,0,0,0,0,
#              0,0,0,0,0,0,0,0,0,0,
#              0,0,0,0,0,0,0,0,0,0,
#              0,0,0,0,0,0,0,0,0,0,
#              0,0,0,0,0,0,0,0,0,0,
#              0,0,0,0,0,0,0,0,
            #  0,0,0,0,0,
            #  1,2,3,4,5,6,7,
            #  8,9,
            #  10,11,
            # 12,13,14,15,16,17,18,19
            #  ]

# synths = [False,False]

# triggerpowers = [2,2]


chwins = [2,2,2,2,2,2,2,2,2,2,2,2,2,2,
          3,3,3,3,3,3,3,3,3,3,3,3,3,3,
          4,4,4,4,4,4,4,4,4,4,4,4,4,4,]

minTSLs = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,
           1,2,3,4,5,6,7,8,9,10,11,12,13,14,
           1,2,3,4,5,6,7,8,9,10,11,12,13,14,]




if __name__ == '__main__':

   time_taken = None
   start_time = time.time()
   try:

      # with Pool() as p:                            # This only makes sense with huge datasets used with 'run()'
      #    results = p.map(do_backtest, paramlist)   # since 'optimize()' automatically comes with multiprocessing by default

      results = list(map(do_backtest,
                        #  paramlist,
                        #  macd_params,
                        #  chval_ths,
                         minTSLs,
                         chwins
                        #  triggerpowers,
                        #  synths
                         ))

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