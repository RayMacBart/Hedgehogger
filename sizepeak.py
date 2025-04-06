from backtesting._util import _Array
import helpers
import numpy as np


def get_peakmid(swidata, gran):
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
   maxcount = max(swicounts)
   maxlevel = None
   for lvl in range(len(swicounts)):
      if swicounts[lvl] == maxcount:
         maxlevel = lvl
   return swimin+swistep*(maxlevel)+swistep/2


def get_current_uppeak(last, seclast, gran):
   ups = []
   currentup = 0
   for idx in range(len(last)):
      if last[idx] >= seclast[idx]:
         if not (last[idx] - seclast[idx]) == currentup:
            ups.append(last[idx] - seclast[idx])
            currentup = ups[-1]
   uppeak = get_peakmid(ups, gran)
   return uppeak


def get_current_downpeak(last, seclast, gran):
   downs = []
   currentdown = 0
   for idx in range(len(last)):
      if last[idx] < seclast[idx]:
         if not (seclast[idx] - last[idx]) == currentdown:
            downs.append(seclast[idx] - last[idx])
            currentdown = downs[-1]
   downpeak = get_peakmid(downs, gran)
   return downpeak


def get_move_sizepeak(last, seclast, win, gran, current_peakfunc, name):
   peaks = []
   for idx in range(len(last)):
      if idx < win:
         peaks.append(np.nan)
      else:
         peak = current_peakfunc(last[idx-win:idx], seclast[idx-win:idx], gran)
         peaks.append(peak)
   helpers.fill_inclomplete_data(peaks, last, "peaks")
   helpers.trans_list_to_BT_array(peaks, name)
   return peaks


def sizepeak_up(last, seclast, win, gran):
   return get_move_sizepeak(last, seclast, win, gran, get_current_uppeak, "uppeaks")


def sizepeak_down(last, seclast, win, gran):
   return get_move_sizepeak(last, seclast, win, gran, get_current_downpeak, "downpeaks")