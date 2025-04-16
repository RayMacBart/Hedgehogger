import numpy as np
import pandas as pd
import pandas_ta as ta
import helpers
import indicator_setups
import camafuncs
import fibofuncs
import sizegap
import reaction
from power import powers
import TSL
from backtesting import Backtest, Strategy
from radar import radar
from backtesting.lib import crossover


candlesize = 'M15'

df = pd.read_csv(".\data\EURUSD_"+candlesize+"_0-10k.csv", sep="\t", parse_dates=['Timestamp'], index_col='Timestamp')
df = df.map(helpers.remove_nocomma_anomaly)



def get_Min_Amount_Candle_Cama_Basis(candlesize):
   MACB = None
   match candlesize:
      case 'M1':
         MACB = 1200
      case 'M5':
         MACB = 240
      case 'M15':
         MACB = 80
      case 'M30':
         MACB = 40
      case 'H1':
         MACB = 20
   return MACB


def get_cama_startidx(timestamps, candlesize):
   indx = -1
   daystart_indexes = []
   MACB = get_Min_Amount_Candle_Cama_Basis(candlesize)
   initday_usable = False
   for ts in timestamps:
      indx += 1
      if all(t == 0 for t in [ts.second, ts.minute]) and ts.hour == 22:
         if not daystart_indexes:
            if indx >= MACB:
               initday_usable = True
         daystart_indexes.append(indx)
   return daystart_indexes, initday_usable


def get_cama_dailydata(timestamps, High, Low, Close, starts, initday_usable):
   dailydata = []
   beginwith = 0 if initday_usable else starts[0]
   for s in starts:
      if not initday_usable and s == starts[0]:
         continue
      dayhigh, daylow = 0, 9999999
      for idx in range(beginwith, s):
         if High[idx] > dayhigh:
            dayhigh = High[idx]
         if Low[idx] < daylow:
            daylow = Low[idx]
      dailydata.append({'High': dayhigh, 'Low': daylow, 'Close': Close[s]})
      beginwith = s
   return dailydata


def cama_R4(Close, dailydata, starts, initday_usable):
   R4_camas = []
   initvalue_filled = False
   dayidx = 0
   for s in starts:
      if not initday_usable and s == starts[0]:
         continue
      if not initvalue_filled:
         for i in range(s):
            R4_camas.append(Close[i]*(1.002))
            initvalue_filled = True
      else:
         current_R4_cama = (dailydata[dayidx]['High'] - dailydata[dayidx]['Low']) * 1.1 / 2 + dailydata[dayidx]['Close']
         for i in range(len(R4_camas), s):
            R4_camas.append(current_R4_cama)
         dayidx += 1
   last_R4_cama = (dailydata[dayidx]['High'] - dailydata[dayidx]['Low']) * 1.1 / 2 + dailydata[dayidx]['Close']
   for i in range(len(R4_camas), len(Close)):
      R4_camas.append(last_R4_cama)
   R4_camas = helpers.trans_list_to_BT_array(R4_camas, 'Cama R4')
   return R4_camas



class Hedgehog(Strategy):

   def init(self):
      # cama_start_idxs, initday_usable = get_cama_startidx(self.data.index, candlesize)
      # cama_dailydata = get_cama_dailydata(self.data.index, self.data.High, self.data.Low,
      #                                       self.data.Close, cama_start_idxs, initday_usable)
      # self.cama_R4 = self.I(cama_R4, self.data.Close, cama_dailydata, cama_start_idxs, initday_usable)
      print(self.data.Volume)
      print(type(self.data.Volume))

      




   def next(self):
      pass

bt = Backtest(df, Hedgehog, cash=1000, 
              commission=0.0001, 
              margin=0.033)

stats = bt.run()
# bt.plot()