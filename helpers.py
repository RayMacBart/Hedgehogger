# from backtesting.lib import resample_apply as reapp, barssince
from backtesting._util import _Array
import numpy as np


def trans_list_to_BT_array(list, name):
   list = np.array(list, dtype='float64')
   list = _Array(list, name=name)
   return list


def fill_inclomplete_data(data, ref, name):
   while len(data) < len(ref):
      data.append(data[-1])
      print(f"AMOUNT OF DATA ERROR: FILLED UP '{name}' WITH IT'S LAST VALUE TILL END!")


def PSAR(PSARl, PSARs, close):
   PSAR = []
   for idx in range(len(close)):
      if np.isnan(PSARs[idx]) and np.isnan(PSARl[idx]):
         PSAR.append(np.nan)
      elif np.isnan(PSARs[idx]):
         PSAR.append(PSARl[idx])
      elif np.isnan(PSARl[idx]):
         PSAR.append(PSARs[idx])
   PSAR = trans_list_to_BT_array(PSAR, 'PSAR')
   return PSAR


def lowerband(band):
   return band
def upperband(band):
   return band
def middleband(band):
   return band
def bandwidth(band):
   return band


def trend(Close, upper_RSI, lower_RSI, RSI):
   trend = [0,]
   for idx in range(1, len(Close)):
      if lower_RSI > RSI[idx]:
         trend.append(1)
      elif RSI[idx] > upper_RSI:
         trend.append(-1)
      elif 47 < RSI[idx] < 53:
         trend.append(0)
      else:
         trend.append(trend[-1])
   trend = trans_list_to_BT_array(trend, 'trend')
   return trend



def remove_nocomma_anomaly(x):
   if x > 1000:
      return x/1000
   else:
      return x


def adjust_volume_data(V):
   n = 0
   for x in V:
      if not x.is_integer():
         V[n] = x*1000
      n += 1


def last_swing(Open, Close):
   last_swing = []
   for idx in range(len(Close)):
      if idx in [0,1]:
         last_swing.append(Close[0])
      else:
         swing_dedected = ((Close[idx] > Open[idx] and Close[idx-1] <= Open[idx-1]) or 
                           (Close[idx] < Open[idx] and Close[idx-1] >= Open[idx-1]))
         if not swing_dedected:
            last_swing.append(last_swing[-1])
         else:
            last_swing.append(Open[idx])
   last_swing = trans_list_to_BT_array(last_swing, 'last swing')
   return last_swing


def seclast_swing(Close, last_swing):
   seclast_swing = []
   seclast_swing.append(Close[0])
   for idx in range(1, len(last_swing)):
      if last_swing[idx] != last_swing[idx-1]:
         seclast_swing.append(last_swing[idx-1])
      else:
         seclast_swing.append(seclast_swing[-1])
   seclast_swing = trans_list_to_BT_array(seclast_swing, 'seclast swing')
   return seclast_swing