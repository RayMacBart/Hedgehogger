import sys
import os
import numpy as np
import pandas as pd
import pandas_ta as ta
import helpers
import indicator_setups
# from mean_volume_moves import get_volmean_movetimes
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

asset = sys.argv[1] if len(sys.argv) > 1 else "EURUSD"
candlesize = sys.argv[2] if len(sys.argv) > 2 else "M5"
dataspan = sys.argv[3] if len(sys.argv) > 3 else "0-10k"

try:
    file_path = os.path.join("data", f"{asset}_{candlesize}_{dataspan}.csv")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    df = pd.read_csv(file_path, sep="\t", parse_dates=['Timestamp'], index_col='Timestamp')
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


clims = 60 if candlesize == 'H1' else int(candlesize[1:])

# df = df.map(helpers.remove_nocomma_anomaly)   --> leads to false manipulation of Volume data
df['Open'] = df['Open'].apply(helpers.remove_nocomma_anomaly)
df['High'] = df['High'].apply(helpers.remove_nocomma_anomaly)
df['Low'] = df['Low'].apply(helpers.remove_nocomma_anomaly)
df['Close'] = df['Close'].apply(helpers.remove_nocomma_anomaly)

df['Volume'] = helpers.adjust_volume_data(df['Volume']).set_axis(df.index)

impact_counter = {'MACD': 0, 'MACD-zeroX': 0, 'MACD-sigX': 0, 'VWAP': 0, 'FIBO': 0, 'RSI': 0, 'RSI-abs': 0, 'RSI-dyn': 0,
                  'CCI': 0, 'CCI-abs': 0, 'CCI-dyn': 0, 'BB-out': 0, 'BB-trend': 0, 'ADX': 0, 'ADX-abs': 0, 'ADX-dyn': 0,
                  'VOL': 0, 'CAMA': 0, 'PEAK': 0}

class Hedgehog(Strategy):

   # boundaries/tresholds:
   RSI_upper_bound = 60
   RSI_lower_bound = 40
   CCI_upper_treshold = 100
   CCI_lower_treshold = -100
   ADX_treshold = 25

   # indicator calculation windows
   RSI_win = 20
   CCI_win = 20
   MACD_shortwin = 12
   MACD_longwin = 26
   MACD_signalwin = 9
   PSAR_af0 = 0.02
   PSAR_af = 0.02
   PSAR_max_af = 0.2
   bbands_win = 20
   ATR_win = 14
   ADX_win = 14
   sizegap_win = 100
   sizepeak_win = 100

   # 'expfac:' expansion factors that shall be reacted upon - the lower the more sensitive/reactive. use 0.1 steps
   vwap_expfac = 1.2  # difference between price and vwap 
   bbands_expfac = 1.3  # width between outer bands

   # mnfpwi: "max decreasing factor per weight impact"
   vol_mdfpwi = 0.15  # 0.05 - 0.4  (in 0.05 steps)
   # mpfpw: "max positive factor per weight"
   vol_mpfpw = 1.5  # 1.2 - 2 (in 0.1 steps) - 3 (in 0.2 steps) - 4.2 (in 0.4 steps), 5
   sizegap_granularity = 10
   sizepeak_granularity = 10
   peak_accuracy = 5  # area of peak value recognition in % --> the lower, the more accurate!

   # change measure windows:
   MACD_chwin = 5 # 3-8 
   histo_chwin = 5 # 3-8
   VWAP_chwin = 8 # 3-8
   fibo_chwin = 5 # 3-8
   RSI_chwin = 5 # 3-10
   CCI_chwin = 5 # 3-10
   vol_chwin = 5 # 2-?
   ADX_chwin = 5 #?
   bbands_chwin_out = 5 #?
   bbands_chwin_trend = 5 # 3-8
   # peak_swingdist = 2 # 2-?

   # indicator weights
   volume_weight = 1
   ADX_abs_weight = 1
   ADX_dyn_weight = 1
   RSI_weight = 1
   CCI_weight = 1
   MACD_zeroweight = 1
   MACD_histoweight = 1
   bbands_weight_out = 1
   bbands_weight_trend = 1
   cama3_weight = 1
   cama4_weight = 1
   VWAP_weight = 1
   ATR_weight = 1
   gap_weight = 1
   peak_weight = 1
   fibo_weight = 1

   size = 0.1  # of buy/sell orders
   cc = -1  # candle counter
   stopdist = 0.0003

   volmean_movetimes = helpers.convert2VMMT_dict(volmean_df)
   


   def init(self):
      self.PSAR_df = ta.psar(self.data.High.s, self.data.Low.s, self.data.Close.s)
      self.PSAR = self.I(indicator_setups.PSAR, self.PSAR_df[f'PSARl_{self.PSAR_af0}_{self.PSAR_max_af}'], 
                         self.PSAR_df[f'PSARs_{self.PSAR_af0}_{self.PSAR_max_af}'], self.data.Close, name='PSAR')
      self.RSI = self.I(ta.rsi, self.data.Close.s, self.RSI_win)
      self.CCI = self.I(ta.cci, self.data.High.s, self.data.Low.s, self.data.Close.s, self.CCI_win)
      self.MACD_df = ta.macd(self.data.Close.s, self.MACD_shortwin, self.MACD_longwin, self.MACD_signalwin)
      self.MACD_macd = self.I(lambda: self.MACD_df[f'MACD_{self.MACD_shortwin}_{self.MACD_longwin}_{self.MACD_signalwin}'], name='MACD')
      self.MACD_histogram = self.I(lambda: self.MACD_df[f'MACDh_{self.MACD_shortwin}_{self.MACD_longwin}_{self.MACD_signalwin}'], name='Histogram')
      # self.MACD_signalline = self.I(lambda: self.MACD_df[f'MACDs_{self.MACD_shortwin}_{self.MACD_longwin}_{self.MACD_signalwin}'], name='Signalline')
      self.VWAP = self.I(ta.vwap, self.data.High.s, self.data.Low.s, self.data.Close.s, self.data.Volume.s, name='VWAP')
      self.bbands_df = ta.bbands(self.data.Close.s, self.bbands_win)
      self.lowerband = self.I(indicator_setups.lowerband, self.bbands_df[f'BBL_{self.bbands_win}_2.0'], name='lower bband')
      self.upperband = self.I(indicator_setups.upperband, self.bbands_df[f'BBU_{self.bbands_win}_2.0'], name='upper bband')
      self.middleband = self.I(indicator_setups.middleband, self.bbands_df[f'BBM_{self.bbands_win}_2.0'], name='middle bband')
      self.bandwidth = self.I(indicator_setups.bandwidth, self.bbands_df[f'BBB_{self.bbands_win}_2.0'], name='bband width')
      self.ATR = self.I(ta.atr, self.data.High.s, self.data.Low.s, self.data.Close.s, self.ATR_win, name='ATR')
      self.ADX_df = ta.adx(self.data.High.s, self.data.Low.s, self.data.Close.s, self.ADX_win)
      self.ADX_adx = self.I(indicator_setups.get_adx, self.ADX_df[f'ADX_{self.ADX_win}'], name='ADX')
      self.ADX_DM_pos = self.I(indicator_setups.get_dmp, self.ADX_df[f'DMP_{self.ADX_win}'], name='DM+')
      self.ADX_DM_neg = self.I(indicator_setups.get_dmn, self.ADX_df[f'DMN_{self.ADX_win}'], name='DM-')
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
                         'VOL': {'volume': self.data.Volume, 'chwin': self.vol_chwin, 'mdfpwi': self.vol_mdfpwi,
                                 'mpfpw': self.vol_mpfpw, 'weight': self.volume_weight},
                         'VWAP': {'vwap': self.VWAP, 'chwin': self.VWAP_chwin, 'weight': self.VWAP_weight,
                                  'expfac': self.vwap_expfac}, # difference expansion factor
                         'ATR': {'atr': self.ATR,  'weight': self.ATR_weight},
                         'ADX': {'adx': self.ADX_adx, 'DM+': self.ADX_DM_pos, 'DM-': self.ADX_DM_neg, 'chwin': self.ADX_chwin,
                                 'treshold': self.ADX_treshold, 'abs_weight': self.ADX_abs_weight, 'dyn_weight': self.ADX_dyn_weight},
                         'RSI': {'rsi': self.RSI, 'low': self.RSI_lower_bound, 'high': self.RSI_upper_bound,
                                 'chwin': self.RSI_chwin, 'weight': self.RSI_weight},
                         'CCI': {'cci': self.CCI, 'low': self.CCI_lower_treshold, 'high': self.CCI_upper_treshold,
                                 'chwin': self.CCI_chwin, 'weight': self.CCI_weight},
                         'MACD': {'macd': self.MACD_macd, 'histo': self.MACD_histogram,
                                  #'signal': self.MACD_signalline, # not used (yet?)
                                  'macd_chwin': self.MACD_chwin, 'histo_chwin': self.histo_chwin,
                                  'zeroweight': self.MACD_zeroweight, 'histoweight': self.MACD_histoweight},
                         'BB': {'low': self.lowerband, 'high': self.upperband,'mid': self.middleband,
                                'width': self.bandwidth, 'chwin-out': self.bbands_chwin_out, 'chwin-trend': self.bbands_chwin_trend,
                                'weight-out': self.bbands_weight_out, 'weight-trend': self.bbands_weight_trend,
                                'expfac': self.bbands_expfac},  # width expansion factor
                         'CAMA': {'R4': self.cama_R4, 'R3': self.cama_R3, 'S3': self.cama_S3,
                                  'S4': self.cama_S4, '3weight': self.cama3_weight, '4weight': self.cama4_weight},
                         'GAP': {'+': self.sizegap_up, '-': self.sizegap_down, 'weight': self.gap_weight},
                         'PEAK': {'+': self.sizepeak_up, '-': self.sizepeak_down, 'accuracy': self.peak_accuracy, 'weight': self.peak_weight
                                 #  , 'swingdist': self.peak_swingdist
                                  },
                         'FIBO': {2: self.fibo_dist2, 4: self.fibo_dist4, 6: self.fibo_dist6,
                                  8: self.fibo_dist8, 'chwin': self.fibo_chwin, 'weight': self.fibo_weight}
                        }
      self.powers = self.I(powers, self.data, self.indicators, self.last_swing, self.data.index, self.volmean_movetimes, clims, impact_counter)

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
              commission=0.00015, 
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

print('POWER IMPACT COUNTER:')
for k, v in impact_counter.items():
   print(f"{k}: {v}")


