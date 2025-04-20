import numpy as np
import pandas as pd
import pandas_ta as ta
import helpers
import indicator_setups
from mean_volume_moves import get_volmean_movetimes
import camafuncs
import fibofuncs
import sizegap
import sizepeak
import reaction
from power import powers
import TSL
from backtesting import Backtest, Strategy
from radar import radar
from backtesting.lib import crossover

candlesize = 'M5'

clims = 60 if candlesize == 'H1' else int(candlesize[1:])

df = pd.read_csv(".\data\EURUSD_"+candlesize+"_0-10k.csv", sep="\t", parse_dates=['Timestamp'], index_col='Timestamp')
df = df.map(helpers.remove_nocomma_anomaly)
df['Volume'] = helpers.adjust_volume_data(df['Volume'], 'Volume')



class Hedgehog(Strategy):

   RSI_upper_bound = 60
   RSI_lower_bound = 40
   CCI_upper_treshold = 100
   CCI_lower_treshold = -100

   RSI_win = 90
   CCI_win = 20
   MACD_shortwin = 12
   MACD_longwin = 26
   MACD_signalwin = 9
   psar_af0 = 0.02
   psar_af = 0.02
   psar_max_af = 0.2
   bbands_win = 20
   atr_win = 14
   adx_win = 14
   sizegap_win = 100
   sizegap_granularity = 10
   sizepeak_win = 100
   sizepeak_granularity = 10
   peak_accuracy = 3  # in % - the less, the more accurate
   macd_chwin = 5 # 3-8 'change measure window'
   histo_chwin = 5 # 3-8
   vwap_chwin = 5 # 3-8
   fibo_chwin = 5 # 3-8
   rsi_chwin = 5
   cci_chwin = 5
   vol_chwin = 5
   peak_swingdist = 3 # 2-?
   volume_trigger_min_change_percent = 20

   volume_up_weight = 1
   volume_down_weight = 1
   adx_weight = 1
   rsi_weight = 1
   cci_weight = 1
   macd_zeroweight = 1
   macd_histoweight = 1
   bb_weight = 1
   cama3_weight = 1
   cama4_weight = 1
   vwap_weight = 1
   atr_weight = 1
   gap_weight = 1
   peak_weight = 1
   fibo_weight = 1

   size = 0.33
   cc = -1
   stopdist = 0.0003

   volmean_movetimes = get_volmean_movetimes(df.itertuples(), clims)
   

   def init(self):
      self.PSAR_df = ta.psar(self.data.High.s, self.data.Low.s, self.data.Close.s)
      self.PSAR = self.I(indicator_setups.PSAR, self.PSAR_df[f'PSARl_{self.psar_af0}_{self.psar_max_af}'], 
                         self.PSAR_df[f'PSARs_{self.psar_af0}_{self.psar_max_af}'], self.data.Close, name='PSAR')
      self.RSI = self.I(ta.rsi, self.data.Close.s, self.RSI_win)
      self.CCI = self.I(ta.cci, self.data.High.s, self.data.Low.s, self.data.Close.s, self.CCI_win)
      self.MACD_df = ta.macd(self.data.Close.s, self.MACD_shortwin, self.MACD_longwin, self.MACD_signalwin)
      self.macd_macd = self.I(lambda: self.MACD_df[f'MACD_{self.MACD_shortwin}_{self.MACD_longwin}_{self.MACD_signalwin}'], name='MACD')
      self.macd_histogram = self.I(lambda: self.MACD_df[f'MACDh_{self.MACD_shortwin}_{self.MACD_longwin}_{self.MACD_signalwin}'], name='Histogram')
      # self.macd_signalline = self.I(lambda: self.MACD_df[f'MACDs_{self.MACD_shortwin}_{self.MACD_longwin}_{self.MACD_signalwin}'], name='Signalline')
      self.vwap = self.I(ta.vwap, self.data.High.s, self.data.Low.s, self.data.Close.s, self.data.Volume.s, name='VWAP')
      self.bbands_df = ta.bbands(self.data.Close.s, self.bbands_win)
      self.lowerband = self.I(indicator_setups.lowerband, self.bbands_df[f'BBL_{self.bbands_win}_2.0'], name='lower bband')
      self.upperband = self.I(indicator_setups.upperband, self.bbands_df[f'BBU_{self.bbands_win}_2.0'], name='upper bband')
      self.middleband = self.I(indicator_setups.middleband, self.bbands_df[f'BBM_{self.bbands_win}_2.0'], name='middle bband')
      self.bandwidth = self.I(indicator_setups.bandwidth, self.bbands_df[f'BBB_{self.bbands_win}_2.0'], name='bband width')
      self.atr = self.I(ta.atr, self.data.High.s, self.data.Low.s, self.data.Close.s, self.atr_win, name='atr')
      self.adx_df = ta.adx(self.data.High.s, self.data.Low.s, self.data.Close.s, self.adx_win)
      self.adx_adx = self.I(indicator_setups.get_adx, self.adx_df[f'ADX_{self.adx_win}'], name='ADX')
      self.adx_DM_pos = self.I(indicator_setups.get_dmp, self.adx_df[f'DMP_{self.adx_win}'], name='DM+')
      self.adx_DM_neg = self.I(indicator_setups.get_dmn, self.adx_df[f'DMN_{self.adx_win}'], name='DM-')
      cama_start_idxs, initday_usable = camafuncs.get_cama_startidx(self.data.index, candlesize)
      cama_dailydata = camafuncs.get_cama_dailydata(self.data.index, self.data.High, self.data.Low,
                                            self.data.Close, cama_start_idxs, initday_usable)
      self.cama_R4 = self.I(camafuncs.cama_R4, self.data.Close, cama_dailydata, cama_start_idxs, initday_usable)
      self.cama_R3 = self.I(camafuncs.cama_R3, self.data.Close, cama_dailydata, cama_start_idxs, initday_usable)
      self.cama_S3 = self.I(camafuncs.cama_S3, self.data.Close, cama_dailydata, cama_start_idxs, initday_usable)
      self.cama_S4 = self.I(camafuncs.cama_S4, self.data.Close, cama_dailydata, cama_start_idxs, initday_usable)
      self.last_swing = self.I(helpers.last_swing, self.data.Open, self.data.Close)
      self.seclast_swing = self.I(helpers.seclast_swing, self.data.Close, self.last_swing)
      self.sizegap_up = self.I(sizegap.sizegap_up, self.last_swing, self.seclast_swing, 
                                                  self.sizegap_win, self.sizegap_granularity, name='GAP+') 
      self.sizegap_down = self.I(sizegap.sizegap_down, self.last_swing, self.seclast_swing, 
                                                  self.sizegap_win, self.sizegap_granularity, name='GAP-')
      self.sizepeak_up = self.I(sizepeak.sizepeak_up, self.last_swing, self.seclast_swing, 
                                                  self.sizepeak_win, self.sizepeak_granularity, name='PEAK+') 
      self.sizepeak_down = self.I(sizepeak.sizepeak_down, self.last_swing, self.seclast_swing, 
                                                  self.sizepeak_win, self.sizepeak_granularity, name='PEAK-')
      self.fibo_dist2 = self.I(fibofuncs.fibo_dist2, self.data.Close, self.last_swing, self.seclast_swing)
      self.fibo_dist4 = self.I(fibofuncs.fibo_dist4, self.data.Close, self.last_swing, self.seclast_swing)
      self.fibo_dist6 = self.I(fibofuncs.fibo_dist6, self.data.Close, self.last_swing, self.seclast_swing)
      self.fibo_dist8 = self.I(fibofuncs.fibo_dist8, self.data.Close, self.last_swing, self.seclast_swing)
      # DISCOVERY: Breaking these fibos indicates overall trend in that direction where it broke through!
      self.dirs = self.I(helpers.dir, self.data.Close, self.last_swing, self.seclast_swing)
      self.indicators = {'PSAR': self.PSAR, 'DIR': self.dirs,
                         'VOL': {'volume': self.data.Volume, 'chwin': self.vol_chwin,
                                 'triggerminchange%': self.volume_trigger_min_change_percent,
                                 'upweight': self.volume_up_weight, 'downweight': self.volume_down_weight},
                         'VWAP': {'vwap': self.vwap, 'chwin': self.vwap_chwin, 'weight': self.vwap_weight}, 
                         'ATR': {'atr': self.atr,  'weight': self.atr_weight},
                         'ADX': {'adx': self.adx_adx, 'DM+': self.adx_DM_pos, 
                                 'DM-': self.adx_DM_neg, 'weight': self.adx_weight},
                         'RSI': {'rsi': self.RSI, 'low': self.RSI_lower_bound, 'high': self.RSI_upper_bound,
                                 'chwin': self.rsi_chwin, 'weight': self.rsi_weight},
                         'CCI': {'cci': self.CCI, 'low': self.CCI_lower_treshold, 'high': self.CCI_upper_treshold,
                                 'chwin': self.cci_chwin, 'weight': self.cci_weight},
                         'MACD': {'macd': self.macd_macd, 'histo': self.macd_histogram,
                                  #'signal': self.macd_signalline, # not used (yet?)
                                  'macd_chwin': self.macd_chwin, 'histo_chwin': self.histo_chwin,
                                  'zeroweight': self.macd_zeroweight, 'histoweight': self.macd_histoweight},
                         'BB': {'low': self.lowerband, 'high': self.upperband,'mid': self.middleband,
                                'width': self.bandwidth, 'weight': self.bb_weight},
                         'CAMA': {'R4': self.cama_R4, 'R3': self.cama_R3, 'S3': self.cama_S3,
                                  'S4': self.cama_S4, '3weight': self.cama3_weight, '4weight': self.cama4_weight},
                         'GAP': {'+': self.sizegap_up, '-': self.sizegap_down, 'weight': self.gap_weight},
                         'PEAK': {'+': self.sizepeak_up, '-': self.sizepeak_down, 'accuracy': self.peak_accuracy, 
                                  'swingdist': self.peak_swingdist, 'weight': self.peak_weight},
                         'FIBO': {2: self.fibo_dist2, 4: self.fibo_dist4, 6: self.fibo_dist6,
                                  8: self.fibo_dist8, 'chwin': self.fibo_chwin, 'weight': self.fibo_weight}
                        }
      self.powers = self.I(powers, self.data.Close, self.indicators, self.last_swing, self.data.index, self.volmean_movetimes, clims)

      # indis for stopdist calc: PSAR, ATR, BB width, GAP

      # self.trend = self.I(radar, self.data.Close, self.indicators)
      # self.TSL_distance = self.I(TSL.get_distance, self.data.Close, self.indicators) 
      # self.decisions = self.I(action.decisions, self.data.Close, self.orderscore)


   def next(self):
      # Calculate TSL-distances first:
      # distance = TSL.get_distance(self.data.Close, self.indicators)
      if self.dirs[-1] > 0:
         bought = 0
         for t in self.trades:
            if t.is_long:
               bought += 1
               t.sl = self.data.Close-self.stopdist
         if not bought:
            self.buy(size=self.size, sl=self.data.Close-self.stopdist)
      elif self.dirs[-1] < 0:
         sold = 0
         for t in self.trades:
            if t.is_short:
               sold += 1
               t.sl = self.data.Close+self.stopdist
         if not sold:
            self.sell(size=self.size, sl=self.data.Close+self.stopdist)

      # psar_distance = self.PSAR[-1] - self.data.Close[-1]
      # if psar_distance < 0:
      #    bought = 0
      #    for t in self.trades:
      #       if t.is_long:
      #          bought += 1
      #          t.sl = self.data.Close[-1] + psar_distance
      #    if not bought and self.dirs[-1] > 0:
      #       self.buy(size=self.size, sl=self.data.Close[-1] + psar_distance)
      # elif psar_distance > 0:
      #    sold = 0
      #    for t in self.trades:
      #       if t.is_short:
      #          sold += 1
      #          t.sl = self.data.Close[-1] + psar_distance
      #    if not sold  and self.dirs[-1] < 0:
      #       self.sell(size=self.size, sl=self.data.Close[-1] + psar_distance)

      # if self.scores > 100:
      #    bought = 0
      #    for t in self.trades:
      #       if t.is_long:
      #          bought += 1
      #    if not bought:
      #       self.buy(size=self.size)
            # --> set calculated trailing stop loss distance here!

      # elif self.scores < 100:
      #    sold = 0
      #    for t in self.trades:
      #       if t.is_long:
      #          sold += 1
      #    if not sold:
      #       self.sell(size=self.size)
            # --> set calculated trailing stop loss distance here!

      # self.cc += 1
      # T = helpers.get_current_indicator_data(self.indicators, self.cc)
      # dir = helpers.get_dir(self.data.Close[-1], self.last_swing[-1], self.seclast_swing[-1])
      # reaction.react(self.buy, self.sell, self.size, self.trades, T, self.trend[-1], self.last_swing[-1], self.seclast_swing[-1], dir)



bt = Backtest(df, Hedgehog, cash=1000, 
              commission=0.0001, 
              margin=0.033)

stats = bt.run()

# for optimization, include the objectives return%, profit factor, sharpe ratio, sortino ratio and calmar ratio
# and give each the same weight resulting into one single value to be optimized. This is done by calculating the
# z score - normalization of 30 optimization results of each objective. Then, the mean of all z scores (of every
# objective) is the final result to be used for the optimization functions.
# try your best regarding optimization of every objective when collecting the 30 needed results, but use the same
# inputs in the optimize() functions for every objective - this ensures a cross-objective consistent normalization 
# on a high, fastidious niveau.

# stats = bt.optimize(
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
   # RSI_upper_bound = range(55, 85, 10),
   # RSI_lower_bound = range(15, 45, 10),
   # RSI_win = range(10, 100, 10),
   # maximize = 'Return [%]',
   # constraint = lambda x: x = x
# )


# print('_______________________________')
print(stats._strategy)
print("stopdist:", stats._strategy.stopdist)
# print('_______________________________')

print('____________________________________________________________')
print(stats)
print('____________________________________________________________')

print('trades:', stats._trades)
# print('____________________________________________________________')
bt.plot()


