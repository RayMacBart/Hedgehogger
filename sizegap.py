from backtesting._util import _Array
import helpers
import numpy as np


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


def get_current_upgap(last, seclast, gran):
   ups = []
   currentup = 0
   for idx in range(len(last)):
      if last[idx] >= seclast[idx]:
         if not (last[idx] - seclast[idx]) == currentup:
            ups.append(last[idx] - seclast[idx])
            currentup = ups[-1]
   upgap = get_gapmid(ups, gran)
   return upgap


def get_current_downgap(last, seclast, gran):
   downs = []
   currentdown = 0
   for idx in range(len(last)):
      if last[idx] < seclast[idx]:
         if not (seclast[idx] - last[idx]) == currentdown:
            downs.append(seclast[idx] - last[idx])
            currentdown = downs[-1]
   downgap = get_gapmid(downs, gran)
   return downgap


def get_move_sizegap(last, seclast, win, gran, current_gapfunc, name):
   gaps = []
   for idx in range(len(last)):
      if idx < win:
         gaps.append(np.nan)
      else:
         gap = current_gapfunc(last[idx-win:idx], seclast[idx-win:idx], gran)
         gaps.append(gap)
   helpers.fill_inclomplete_data(gaps, last, "gaps")
   helpers.trans_list_to_BT_array(gaps, name)
   return gaps


def sizegap_up(last, seclast, win, gran):
   return get_move_sizegap(last, seclast, win, gran, get_current_upgap, "upgaps")


def sizegap_down(last, seclast, win, gran):
   return get_move_sizegap(last, seclast, win, gran, get_current_downgap, "downgaps")