import pandas as pd
import pandas_ta as ta
import helpers
import indicator_setups
import camafuncs
import fibofuncs
import sizegap
from backtesting import Backtest, Strategy
from radar import radar


df = pd.read_csv(".\data\EURUSD_M1_90-100k.csv", sep="\t", parse_dates=['Timestamp'], index_col='Timestamp')
df = df.applymap(helpers.remove_nocomma_anomaly)


class Hedgehog(Strategy):

   RSI_upper_bound = 60
   RSI_lower_bound = 40
   RSI_window = 90
   MACD_shortwin = 12
   MACD_longwin = 26
   MACD_signalwin = 9
   cama_length = 11 # in minutes
   psar_af0 = 0.02
   psar_af = 0.02
   psar_max_af = 0.2
   bbands_window = 20
   atr_window = 14
   adx_window = 14
   sizegap_window = 100
   sizegap_granularity = 10
   

   def init(self):
      self.n = 0

      self.PSAR_df = ta.psar(self.data.High.s, self.data.Low.s, self.data.Close.s)
      self.PSAR = self.I(indicator_setups.PSAR, self.PSAR_df[f'PSARl_{self.psar_af0}_{self.psar_max_af}'], 
                         self.PSAR_df[f'PSARs_{self.psar_af0}_{self.psar_max_af}'], self.data.Close, name='PSAR')
      self.RSI = self.I(ta.rsi, self.data.Close.s, self.RSI_window)
      self.MACD_df = ta.macd(self.data.Close.s, self.MACD_shortwin, self.MACD_longwin, self.MACD_signalwin)
      self.macd_macd = self.I(lambda: self.MACD_df[f'MACD_{self.MACD_shortwin}_{self.MACD_longwin}_{self.MACD_signalwin}'], name='MACD')
      self.macd_histogram = self.I(lambda: self.MACD_df[f'MACDh_{self.MACD_shortwin}_{self.MACD_longwin}_{self.MACD_signalwin}'], name='Histogram')
      self.macd_signalline = self.I(lambda: self.MACD_df[f'MACDs_{self.MACD_shortwin}_{self.MACD_longwin}_{self.MACD_signalwin}'], name='Signalline')
      helpers.adjust_volume_data(self.data.Volume)
      self.vwap = self.I(ta.vwap, self.data.High.s, self.data.Low.s, self.data.Close.s, self.data.Volume.s, name='VWAP')
      self.bbands_df = ta.bbands(self.data.Close.s, self.bbands_window)
      self.lowerband = self.I(indicator_setups.lowerband, self.bbands_df[f'BBL_{self.bbands_window}_2.0'], name='lower bband')
      self.upperband = self.I(indicator_setups.upperband, self.bbands_df[f'BBU_{self.bbands_window}_2.0'], name='upper bband')
      self.middleband = self.I(indicator_setups.middleband, self.bbands_df[f'BBM_{self.bbands_window}_2.0'], name='middle bband')
      self.bandwidth = self.I(indicator_setups.bandwidth, self.bbands_df[f'BBB_{self.bbands_window}_2.0'], name='bband width')
      self.atr = self.I(ta.atr, self.data.High.s, self.data.Low.s, self.data.Close.s, self.atr_window)
      self.adx = self.I(ta.adx, self.data.High.s, self.data.Low.s, self.data.Close.s, self.adx_window)
      self.cama_R4 = self.I(camafuncs.get_cama_R4, self.data.index, self.data.High, self.data.Low, self.data.Close, self.cama_length)
      self.cama_R3 = self.I(camafuncs.get_cama_R3, self.data.index, self.data.High, self.data.Low, self.data.Close, self.cama_length)
      self.cama_S3 = self.I(camafuncs.get_cama_S3, self.data.index, self.data.High, self.data.Low, self.data.Close, self.cama_length)
      self.cama_S4 = self.I(camafuncs.get_cama_S4, self.data.index, self.data.High, self.data.Low, self.data.Close, self.cama_length)
      self.last_swing = self.I(helpers.last_swing, self.data.Open, self.data.Close)
      self.seclast_swing = self.I(helpers.seclast_swing, self.data.Close, self.last_swing)
      self.fibo_pricerange = self.I(fibofuncs.fibo_pricerange, self.data.Close,
                                    self.last_swing, self.seclast_swing, self.trend)
      self.fibo_strongretrace = self.I(fibofuncs.fibo_strongretrace, self.trend, self.fibo_pricerange, self.last_swing)
      self.fibo_weakretrace = self.I(fibofuncs.fibo_weakretrace, self.trend, self.fibo_pricerange, self.last_swing)
      self.fibo_weakend = self.I(fibofuncs.fibo_weakend, self.trend, self.fibo_pricerange, self.last_swing)
      self.fibo_strongend = self.I(fibofuncs.fibo_strongend, self.trend, self.fibo_pricerange, self.last_swing)
      self.sizegap_up, self.sizegap_down = self.I(sizegap.move_sizegaps, self.last_swing, self.seclast_swing, 
                                                  self.sizegap_window, self.sizegap_granularity)
      self.ti = {'PSAR': self.PSAR, 'VWAP': self.vwap, 'ATR': self.atr, 'ADX': self.adx,
                 'RSI': {'rsi': self.RSI, 'low': self.RSI_lower_bound, 'up': self.RSI_upper_bound},
                 'MACD': {'macd': self.macd_macd, 'histo': self.macd_histogram, 'signal': self.macd_signalline},
                 'BB': {'low': self.lowerband, 'high': self.upperband,'mid': self.middleband, 'width': self.bandwidth},
                 'CAMA': {'R4': self.cama_R4, 'R3': self.cama_R3, 'S3': self.cama_S3, 'S4': self.cama_S4},
                 'FIBO': {'2': self.fibo_strongretrace, '4': self.fibo_weakretrace,
                          '6': self.fibo_weakend, '8': self.fibo_strongend},
                 'GAP': {'up': self.sizegap_up, 'down': self.sizegap_down}}
      self.trend = self.I(radar, self.data.Close, self.ti)

   def next(self):
      self.n += 1
      ti = self.ti
      # if crossover(self.RSI, self.RSI_upper_bound):
      #    self.position.close()
      #    self.buy()
      # elif crossover(self.RSI_lower_bound, self.RSI):
      #    self.position.close()
      #    self.sell()


bt = Backtest(df, Hedgehog, cash=1000, commission=0.005)

stats = bt.run()

# stats = bt.optimize(
#    RSI_upper_bound = range(55, 85, 5),
#    RSI_lower_bound = range(15, 45, 5),
#    RSI_window = range(10, 100, 4),
#    maximize = 'Return [%]',
   # constraint = lambda x: x = x
# )
# print('_______________________________')
# print(stats._strategy)
# print('_______________________________')

print('____________________________________________________________')
# print(stats)
print('____________________________________________________________')

# print('trades:', stats._trades)
# print('____________________________________________________________')
bt.plot()


