from backtesting._util import _Array
import numpy as np


def fill_inclomplete_data(data, ref, name):
   while len(data) < len(ref):
      data.append(data[-1])
      print(f"AMOUNT OF DATA ERROR: FILLED UP '{name}' WITH IT'S LAST VALUE TILL END!")

def trans_list_to_BT_array(list, name):
   list = np.array(list, dtype='float64')
   list = _Array(list, name=name)
   return list


def get_gapmid(swidata, gran):
   swimin = min(swidata)
   swiwidth = max(swidata) - swimin
   swistep = swiwidth / gran
   swicounts = []
   for g in range(gran):
      swicounts.append(0)
   for u in swidata:
      for level in range(1, gran+1):
         if swimin <= u < swimin+swistep*(level):
            swicounts[level-1] += 1
   mincount = min(swicounts)
   minlevel = None
   for lvl in range(len(swicounts)):
      if swicounts[lvl] == mincount:
         minlevel = lvl
   return swimin+swistep*(minlevel)+swistep/2


def get_current_sizegaps(last, seclast, gran):
   ups = []
   downs = []
   currentup = 0
   currentdown = 0
   for idx in range(len(last)):
      if last[idx] >= seclast[idx]:
         if not (last[idx] - seclast[idx]) == currentup:
            ups.append(last[idx] - seclast[idx])
            currentup = ups[-1]
      elif last[idx] < seclast[idx]:
         if not (seclast[idx] - last[idx]) == currentdown:
            downs.append(seclast[idx] - last[idx])
            currentdown = downs[-1]
   # print(ups[2:5])
   # print(downs[2:5])
   upgap = get_gapmid(ups, gran)
   downgap = get_gapmid(downs, gran)
   return upgap, downgap


def move_sizegaps(last, seclast, win, gran):
   upgaps = []
   downgaps = []
   for idx in range(len(last)):
      if idx < win:
         upgaps.append(np.nan)
         downgaps.append(np.nan)
      else:
         upgap, downgap = get_current_sizegaps(last[win*(-1):], seclast[win*(-1):], gran)
         upgaps.append(upgap)
         downgaps.append(downgap)
   fill_inclomplete_data(upgaps, last, "upgaps")
   fill_inclomplete_data(downgaps, last, "downgaps")
   trans_list_to_BT_array(upgaps, "upgaps")
   trans_list_to_BT_array(downgaps, "downgaps")
   return upgaps, downgaps