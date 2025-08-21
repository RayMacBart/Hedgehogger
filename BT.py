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
# (note about multiprocessing)[backups/note_about_multprocessing.txt]



def do_backtest(
                triggerpower,
                CSP_weight,
                MACD_zeroweight,
                MACD_histoweight,
                MACD_comboweight,
                VWAP_weight,
                fibo_weight,
               #  cama3_weight,
                cama4_weight,
                RSI_weight,
                CCI_weight,
                bbands_weight_out,
                logger
               #  param,
               #  minTSL,
               #  CHWIN,
               #  TRIP,
               #  randomized
                ):

   # (code for objective result data collection)[backups/code4objective_data_collection.txt]

   asset, candlesize = get_vars()
   
   dataspan = 40000
   pastshift = 0
   randomized = False

   adjufac = 100 if asset == "USDJPY" else 1  #(?)[docs/adjufac.txt]
   
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


   max_tries = 66

   # (1000 possible combinations cookbook)[docs/1000_combis_cookbook.txt]


   # WARNING: I HAVE SET 'SIZE' @ HEDGEHOG.PY TO 0.001 (INSTEAD OF 0.1) AND CASH @ BACKTEST() ABOVE TO 100.000 (INSTEAD OF 1.000)!!!
   stats = bt.optimize(

                  # FIRST WEIGHT OPTIMIZED SHIFT INDICATOR GROUP: CSP, VWAP, FIBO, CCI & BBout  (total weight currently at 9)
                  # SECOND WEIGHT OPTIMIZED SHIFT INDICATOR GROUP: MACD (3), CAMA (2), RSI

                  candlesize = [candlesize],
                  # "fos" = future optimization suggestion, "fhwt" = frequent hence worth try, "lar" = long average result
                  order_triggerpower = triggerpower,       # was 18 for first trend opt
                  close_triggerpower = 1, # was 
                  CSP_bodyshrink_factor = 4,
                  CSP_shadow2body_factor = 3,
                  CSP_shadowdiff_factor = 5,
                  CSP_reaction_win = 6,   # maybe consider less for fastness
                  CSP_weight = CSP_weight,
                  MACD_zeroweight = MACD_zeroweight, #[0,2], # was 1
                  MACD_histoweight = MACD_histoweight, #[1,3],   # way better results than zero & combo!   # was 2
                  MACD_comboweight = MACD_comboweight, #[0,2],   # was 2!   #(!)[docs/note_about_combo_macd.txt]
                  MACD_longwin = 5, #[4,10], #7
                  MACD_shortwin = 3, #[3,8], #6
                  MACD_signalwin = 3, #[2,7], #6
                  MACD_chwin = 2,
                  histo_chwin = 2,
                  combo_chwin = 2,
                  MACD_chval_th = 3,  # was 1! # only relevant for combo and zero
                  histo_chval_th = 2,  # only relevant for histo
                  vwap_expfac = 1,
                  VWAP_chwin = 2,
                  VWAP_weight = VWAP_weight,
                  fibo_chwin = 2,
                  fibo_weight = fibo_weight,
                  # cama3_weight = cama3_weight,  #(!)[docs/cama3_removed_note.txt]
                  cama4_weight = cama4_weight,# [0,2],  # was 2
                  RSI_win = 14,  # 14 = result for static. also try 6 (faster variant with bounddist=28),  # (modern static: 4)
                  RSI_chwin = 2,  # was 9,   fhwt: 5     # 3-10    # chwin only affects dynamic RSI !!
                  RSI_bound_distance = 18,  # 18 = result for static. also try 28 (faster variant with RSI-win=6)
                  RSI_chval_th = 7,   # only affects dynamic RSI
                  RSI_weight = RSI_weight,   # CHECK IF OMITTING DYN. RSI WORKS BETTER (STATIC HAS BETTER SCORES)
                  CCI_win = 10,
                  CCI_chwin = 2,  # only affects dynamic CCI    (dyn. fhwt: 4)
                  CCI_treshold_distance = 159,
                  CCI_chval_th = 100,  # only affects dynamic CCI
                  CCI_weight = CCI_weight,
                  bbands_win = 116, #  score: 45.3, trades: 7766  ||  shorter alternatives: 12 (score: 6.65, trades: 6060)  and  26 (score: 14.94, trades: 6257)
                  bbands_chwin_out = 1, # recently was 9,  # fhwt: 8  (if trying 'win' with 3 or 4, set chwin to 3)
                  bbands_weight_out = bbands_weight_out, # recently was 3,  # was 1  (bad performance)
                  ######################################
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
                  minTSLdist = 12, # minTSL   # best so far: (csp & macd_zero): 12 (or 8)

                  maximize = lambda stats: (
                     ((stats["SQN"]-sqn_mean)/sqn_std)*38 +
                     ((stats["Expectancy [%]"]-expec_mean)/expec_std)*22 +
                     ((stats["Calmar Ratio"]-calmar_mean)/calmar_std)*16 +
                     ((stats["Sortino Ratio"]-sortino_mean)/sortino_std)*13 +
                     ((stats["Profit Factor"]-profac_mean)/profac_std)*11
                  ),
                  #(old)[backups/old_optim_params.py]

                  # method='sambo',
                  # max_tries=max_tries,
                  # constraint=lambda p: p.MACD_signalwin <= p.MACD_shortwin < p.MACD_longwin
                  # constraint=lambda p: p.MACD_shortwin < p.MACD_longwin
               )
   

   param_opt_log_dict = {
                  'order_triggerpower': triggerpower,       # was 18 for first trend opt
                  'close_triggerpower': 1, # was 
                  'CSP_bodyshrink_factor': 4,
                  'CSP_shadow2body_factor': 3,
                  'CSP_shadowdiff_factor': 5,
                  'CSP_reaction_win': 6,   # maybe consider less for fastness
                  'CSP_weight': CSP_weight,
                  'MACD_zeroweight': MACD_zeroweight, #[0,2], # was 1
                  'MACD_histoweight': MACD_histoweight, #[1,3],   # way better results than zero & combo!   # was 2
                  'MACD_comboweight': MACD_comboweight, #[0,2],   # was 2!   #(!)[docs/note_about_combo_macd.txt]
                  'MACD_longwin': 5, #[4,10], #7
                  'MACD_shortwin': 3, #[3,8], #6
                  'MACD_signalwin': 3, #[2,7], #6
                  'MACD_chwin': 2,
                  'histo_chwin': 2,
                  'combo_chwin': 2,
                  'MACD_chval_th': 3,  # was 1! # only relevant for combo and zero
                  'histo_chval_th': 2,  # only relevant for histo
                  'vwap_expfac': 1,
                  'VWAP_chwin': 2,
                  'VWAP_weight': VWAP_weight,
                  'fibo_chwin': 2,
                  'fibo_weight': fibo_weight,
                  # 'cama3_weight': cama3_weight,# [0,2],  # was 1
                  'cama4_weight': cama4_weight,# [0,2],  # was 2
                  'RSI_win': 14,  # 14 = result for static. also try 6 (faster variant with bounddist=28),  # (modern static: 4)
                  'RSI_chwin': 2,  # was 9,   fhwt: 5     # 3-10    # chwin only affects dynamic RSI !!
                  'RSI_bound_distance': 18,  # 18 = result for static. also try 28 (faster variant with RSI-win=6)
                  'RSI_chval_th': 7,   # only affects dynamic RSI
                  'RSI_weight': RSI_weight,   # CHECK IF OMITTING DYN. RSI WORKS BETTER (STATIC HAS BETTER SCORES)
                  'CCI_win': 10,
                  'CCI_chwin': 2,  # only affects dynamic CCI    (dyn. fhwt: 4)
                  'CCI_treshold_distance': 159,
                  'CCI_chval_th': 100,  # only affects dynamic CCI
                  'CCI_weight': CCI_weight,
                  'bbands_win': 116, #  score: 45.3, trades: 7766  ||  shorter alternatives: 12 (score: 6.65, trades: 6060)  and  26 (score: 14.94, trades: 6257)
                  'bbands_chwin_out': 1, # recently was 9,  # fhwt: 8  (if trying 'win' with 3 or 4, set chwin to 3)
                  'bbands_weight_out': bbands_weight_out, # recently was 3,  # was 1  (bad performance)
                  'minTSLdist': 12,  # minTSL   # best so far for both csp & macd_zero is 12 though
                  'SLdist_redufac': 9,
                  'bbands_TSL_chwin': 7,
                  'PSAR_weight': 1,
                  'bbands_TSL_weight': 1,
                  'ATR_TSL_weight': 2,
                  'power_TSL_weight': 3
   }
   
                  

   time.sleep(20)

   print(f'Triggerpower: {triggerpower}, {logger} done.')

   # print(stats)

   # bt.plot()

   return {'asset': asset, 'candlesize': candlesize, 'pastshift': pastshift, 'dataspan': dataspan, 'stats': stats,
           'randomized': randomized,
         #   'objective': objective,
           'param_opt_log_dict': param_opt_log_dict}


triggerpowers = [
                 3,4,5,6,
                 3,4,5,6,4,5,6,7,4,5,6,7,8,4,5,6,7,8,9,
                 3,4,5,6,4,5,6,7,4,5,6,7,8,4,5,6,7,8,9,
                 3,4,5,6,4,5,6,7,4,5,6,7,8,4,5,6,7,8,9,
                 3,4,5,6,4,5,6,7,4,5,6,7,8,4,5,6,7,8,9,
                 3,4,5,6,4,5,6,7,4,5,6,7,8,4,5,6,7,8,9,
                 3,4,5,6,4,5,6,7,4,5,6,7,8,4,5,6,7,8,9,
                 3,4,5,6,4,5,6,7,4,5,6,7,8,4,5,6,7,8,9,
                 3,4,5,6,4,5,6,7,4,5,6,7,8,4,5,6,7,8,9,
                 3,4,5,6,4,5,6,7,4,5,6,7,8,4,5,6,7,8,9,
                 3,4,5,6,4,5,6,7,4,5,6,7,8,4,5,6,7,8,9,
                 ]

CSP_weights = [
               1,1,1,1,
               0,0,0,0,2,2,2,2,3,3,3,3,3,4,4,4,4,4,4,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               ]
MACD_zeroweights = [
               1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               0,0,0,0,2,2,2,2,3,3,3,3,3,4,4,4,4,4,4,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               ]
MACD_histoweights = [
               1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               0,0,0,0,2,2,2,2,3,3,3,3,3,4,4,4,4,4,4,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               ]
MACD_comboweights = [
               1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               0,0,0,0,2,2,2,2,3,3,3,3,3,4,4,4,4,4,4,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               ]
VWAP_weights = [
               1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               0,0,0,0,2,2,2,2,3,3,3,3,3,4,4,4,4,4,4,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               ]
fibo_weights = [
               1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               0,0,0,0,2,2,2,2,3,3,3,3,3,4,4,4,4,4,4,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               ]
cama4_weights = [     #(!)[docs/cama3_removed_note.txt]
               1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               0,0,0,0,2,2,2,2,3,3,3,3,3,4,4,4,4,4,4,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               ]
RSI_weights = [
               1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               0,0,0,0,2,2,2,2,3,3,3,3,3,4,4,4,4,4,4,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               ]
CCI_weights = [
               1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               0,0,0,0,2,2,2,2,3,3,3,3,3,4,4,4,4,4,4,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               ]
bbands_weights_out = [
               1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
               0,0,0,0,2,2,2,2,3,3,3,3,3,4,4,4,4,4,4,
               ]
loggers = [
           'all indicators equal', 'all indicators equal', 'all indicators equal', 'all indicators equal',
          'CSP_weight: 0', 'CSP_weight: 0', 'CSP_weight: 0', 'CSP_weight: 0',
          'CSP_weight: 2', 'CSP_weight: 2', 'CSP_weight: 2', 'CSP_weight: 2',
          'CSP_weight: 3', 'CSP_weight: 3', 'CSP_weight: 3', 'CSP_weight: 3', 'CSP_weight: 3',
          'CSP_weight: 4', 'CSP_weight: 4', 'CSP_weight: 4', 'CSP_weight: 4', 'CSP_weight: 4', 'CSP_weight: 4',
          'MACD_zeroweight: 0', 'MACD_zeroweight: 0', 'MACD_zeroweight: 0', 'MACD_zeroweight: 0',
          'MACD_zeroweight: 2', 'MACD_zeroweight: 2', 'MACD_zeroweight: 2', 'MACD_zeroweight: 2',
          'MACD_zeroweight: 3', 'MACD_zeroweight: 3', 'MACD_zeroweight: 3', 'MACD_zeroweight: 3', 'MACD_zeroweight: 3',
          'MACD_zeroweight: 4', 'MACD_zeroweight: 4', 'MACD_zeroweight: 4', 'MACD_zeroweight: 4', 'MACD_zeroweight: 4', 'MACD_zeroweight: 4',
          'MACD_histoweight: 0', 'MACD_histoweight: 0', 'MACD_histoweight: 0', 'MACD_histoweight: 0',
          'MACD_histoweight: 2', 'MACD_histoweight: 2', 'MACD_histoweight: 2', 'MACD_histoweight: 2',
          'MACD_histoweight: 3', 'MACD_histoweight: 3', 'MACD_histoweight: 3', 'MACD_histoweight: 3', 'MACD_histoweight: 3',
          'MACD_histoweight: 4', 'MACD_histoweight: 4', 'MACD_histoweight: 4', 'MACD_histoweight: 4', 'MACD_histoweight: 4', 'MACD_histoweight: 4',
          'MACD_comboweight: 0', 'MACD_comboweight: 0', 'MACD_comboweight: 0', 'MACD_comboweight: 0',
          'MACD_comboweight: 2', 'MACD_comboweight: 2', 'MACD_comboweight: 2', 'MACD_comboweight: 2',
          'MACD_comboweight: 3', 'MACD_comboweight: 3', 'MACD_comboweight: 3', 'MACD_comboweight: 3', 'MACD_comboweight: 3',
          'MACD_comboweight: 4', 'MACD_comboweight: 4', 'MACD_comboweight: 4', 'MACD_comboweight: 4', 'MACD_comboweight: 4', 'MACD_comboweight: 4',
          'VWAP_weight: 0', 'VWAP_weight: 0', 'VWAP_weight: 0', 'VWAP_weight: 0',
          'VWAP_weight: 2', 'VWAP_weight: 2', 'VWAP_weight: 2', 'VWAP_weight: 2',
          'VWAP_weight: 3', 'VWAP_weight: 3', 'VWAP_weight: 3', 'VWAP_weight: 3', 'VWAP_weight: 3',
          'VWAP_weight: 4', 'VWAP_weight: 4', 'VWAP_weight: 4', 'VWAP_weight: 4', 'VWAP_weight: 4', 'VWAP_weight: 4',
          'fibo_weight: 0', 'fibo_weight: 0', 'fibo_weight: 0', 'fibo_weight: 0',
          'fibo_weight: 2', 'fibo_weight: 2', 'fibo_weight: 2', 'fibo_weight: 2',
          'fibo_weight: 3', 'fibo_weight: 3', 'fibo_weight: 3', 'fibo_weight: 3', 'fibo_weight: 3',
          'fibo_weight: 4', 'fibo_weight: 4', 'fibo_weight: 4', 'fibo_weight: 4', 'fibo_weight: 4', 'fibo_weight: 4',
          'cama4_weight: 0', 'cama4_weight: 0', 'cama4_weight: 0', 'cama4_weight: 0',
          'cama4_weight: 2', 'cama4_weight: 2', 'cama4_weight: 2', 'cama4_weight: 2',
          'cama4_weight: 3', 'cama4_weight: 3', 'cama4_weight: 3', 'cama4_weight: 3', 'cama4_weight: 3',
          'cama4_weight: 4', 'cama4_weight: 4', 'cama4_weight: 4', 'cama4_weight: 4', 'cama4_weight: 4', 'cama4_weight: 4',
          'RSI_weight: 0', 'RSI_weight: 0', 'RSI_weight: 0', 'RSI_weight: 0',
          'RSI_weight: 2', 'RSI_weight: 2', 'RSI_weight: 2', 'RSI_weight: 2',
          'RSI_weight: 3', 'RSI_weight: 3', 'RSI_weight: 3', 'RSI_weight: 3', 'RSI_weight: 3',
          'RSI_weight: 4', 'RSI_weight: 4', 'RSI_weight: 4', 'RSI_weight: 4', 'RSI_weight: 4', 'RSI_weight: 4',
          'CCI_weight: 0', 'CCI_weight: 0', 'CCI_weight: 0', 'CCI_weight: 0',
          'CCI_weight: 2', 'CCI_weight: 2', 'CCI_weight: 2', 'CCI_weight: 2',
          'CCI_weight: 3', 'CCI_weight: 3', 'CCI_weight: 3', 'CCI_weight: 3', 'CCI_weight: 3',
          'CCI_weight: 4', 'CCI_weight: 4', 'CCI_weight: 4', 'CCI_weight: 4', 'CCI_weight: 4', 'CCI_weight: 4',
          'bbands_weight_out: 0', 'bbands_weight_out: 0', 'bbands_weight_out: 0', 'bbands_weight_out: 0',
          'bbands_weight_out: 2', 'bbands_weight_out: 2', 'bbands_weight_out: 2', 'bbands_weight_out: 2',
          'bbands_weight_out: 3', 'bbands_weight_out: 3', 'bbands_weight_out: 3', 'bbands_weight_out: 3', 'bbands_weight_out: 3',
          'bbands_weight_out: 4', 'bbands_weight_out: 4', 'bbands_weight_out: 4', 'bbands_weight_out: 4', 'bbands_weight_out: 4', 'bbands_weight_out: 4',
          ]


# (unused parameter lists)[backups/unused_paramlists.txt]







if __name__ == '__main__':

   time_taken = None
   start_time = time.time()
   try:



      results = list(map(do_backtest,
                         triggerpowers,
                         CSP_weights,
                         MACD_zeroweights,
                         MACD_histoweights,
                         MACD_comboweights,
                         VWAP_weights,
                         fibo_weights,
                        #  cama3_weights,
                         cama4_weights,
                         RSI_weights,
                         CCI_weights,
                         bbands_weights_out,
                         loggers
                        #  chwins,
                        #  paramlist,
                        #  macd_params,
                        #  chval_ths,
                        #  minTSLs,
                        
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



# (old, complicated parameter loop idea)[backups/old_paramloop_idea.txt]
