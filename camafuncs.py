import numpy as np
import helpers
from backtesting._util import _Array


def get_hourly_HLCs(time, High, Low, Close, start_idx, length):
   candle_high = 0
   candle_low = 99999
   candle_close = None
   finished = False
   for idx in range(start_idx, start_idx+length):
      if High[idx] > candle_high:
         candle_high = High[idx]
      if Low[idx] < candle_low:
         candle_low = Low[idx]
      if (idx == len(Close)-1) or (idx == start_idx+length-1):
         candle_close = Close[idx]
         if idx == len(Close)-1:
            finished = True
         break
   return candle_high, candle_low, candle_close, finished


def create_cama(time, High, Low, Close, length, initval, func, name):
   cama = []
   for e in range(length):
      cama.append(Close[0]+Close[0]*initval)
   start_idx = 0
   while True:
      candle_high, candle_low, candle_close, finished = get_hourly_HLCs(time, High, Low, Close, start_idx, length)
      for idx in range(start_idx, start_idx+length):
         if len(cama) < len(Close):
            cama.append(func(candle_high, candle_low, candle_close))
         else:
            break
      if finished:
         break
      start_idx = start_idx+length
   cama = helpers.trans_list_to_BT_array(cama, name)
   return cama


def get_cama_R4(time, High, Low, Close, length):
   def calc_R4(high, low, close):
      return ((high - low) * 1.1 / 2 + close)
   cama_R4 = create_cama(time, High, Low, Close, length, 0.0008, calc_R4, 'cama_R4')
   return cama_R4


def get_cama_R3(time, High, Low, Close, length):
   def calc_R3(high, low, close):
      return ((high - low) * 1.1 / 4 + close)
   cama_R3 = create_cama(time, High, Low, Close, length, 0.0005, calc_R3, 'cama_R3')
   return cama_R3


def get_cama_S3(time, High, Low, Close, length):
   def calc_S3(high, low, close):
      return (close - (high - low) * 1.1 / 4)
   cama_S3 = create_cama(time, High, Low, Close, length, -0.0005, calc_S3, 'cama_S3')
   return cama_S3


def get_cama_S4(time, High, Low, Close, length):
   def calc_S4(high, low, close):
      return (close - (high - low) * 1.1 / 2)
   cama_S4 = create_cama(time, High, Low, Close, length, -0.0008, calc_S4, 'cama_S4')
   return cama_S4