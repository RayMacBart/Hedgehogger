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


def get_dir(Close, last, seclast):
   dir = 0
   if last <= seclast:
      if Close > last:
         dir = 1
   elif last > seclast:
      if Close < last:
         dir = -1
   return dir


def get_tradetypes(trades):
   longs = []
   shorts = []
   for trade in trades:
      if trade.is_long:
          longs.append(trade)
      elif trade.is_short:
          shorts.append(trade)
   return longs, shorts


def get_current_indicator_data(ti, cc):
   T = {}
   T['PSAR'] = ti['PSAR'][cc]
   T['VWAP'] = ti['VWAP'][cc]
   T['ATR'] = ti['ATR'][cc]
   T['ADX'] = {}
   T['ADX']['adx'] = ti['ADX']['adx'][cc]
   T['ADX']['DM+'] = ti['ADX']['DM+'][cc]
   T['ADX']['DM-'] = ti['ADX']['DM-'][cc]
   T['RSI'] = {}
   T['RSI']['rsi'] = ti['RSI']['rsi'][cc]
   T['RSI']['low'] = ti['RSI']['low']
   T['RSI']['high'] = ti['RSI']['high']
   T['MACD'] = {}
   T['MACD']['macd'] = ti['MACD']['macd'][cc]
   T['MACD']['histo'] = ti['MACD']['histo'][cc]
   T['MACD']['signal'] = ti['MACD']['signal'][cc]
   T['BB'] = {}
   T['BB']['low'] = ti['BB']['low'][cc]
   T['BB']['high'] = ti['BB']['high'][cc]
   T['BB']['mid'] = ti['BB']['mid'][cc]
   T['BB']['width'] = ti['BB']['width'][cc]
   T['CAMA'] = {}
   T['CAMA']['R4'] = ti['CAMA']['R4'][cc]
   T['CAMA']['R3'] = ti['CAMA']['R3'][cc]
   T['CAMA']['S3'] = ti['CAMA']['S3'][cc]
   T['CAMA']['S4'] = ti['CAMA']['S4'][cc]
   T['GAP'] = {}
   T['GAP']['+'] = ti['GAP']['+'][cc]
   T['GAP']['-'] = ti['GAP']['-'][cc]
   T['FIBO'] = {}
   T['FIBO'][2] = ti['FIBO'][2][cc]
   T['FIBO'][4] = ti['FIBO'][4][cc]
   T['FIBO'][6] = ti['FIBO'][6][cc]
   T['FIBO'][8] = ti['FIBO'][8][cc]
   return T