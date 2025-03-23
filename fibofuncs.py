import numpy as np
import helpers
from backtesting._util import _Array


def fibo_pricerange(Close, last, seclast, trend):
   pricerange = []
   for idx in range(len(Close)):
      if trend[idx] == 1:
         if last[idx] - seclast[idx] > 0:
            pricerange.append(abs(seclast[idx] - last[idx]))
         elif last[idx] - seclast[idx] < 0:
            pricerange.append(pricerange[-1]) # because taking range from downward movement in an uptrend makes no sense
      elif trend[idx] == -1:
         if last[idx] - seclast[idx] < 0:
            pricerange.append(abs(seclast[idx] - last[idx]))
         elif last[idx] - seclast[idx] > 0:
            pricerange.append(pricerange[-1]) # because taking range from upward movement in an downtrend makes no sense
      else:
         pricerange.append(0) # won't be used anyway
   helpers.fill_inclomplete_data(pricerange, Close, 'fibo pricerange')
   pricerange = helpers.trans_list_to_BT_array(pricerange, 'fibo pricerange')
   return pricerange


def create_fibolevel(trend, pricerange, last, factor, name):
   fibolevel = []
   for idx in range(len(pricerange)):
      if trend[idx] == 1:
         fibolevel.append(last[idx] - pricerange[idx]*factor)
      elif trend[idx] == -1:
         fibolevel.append(last[idx] + pricerange[idx]*factor)
      else:
         fibolevel.append(last[idx]*0.9985) # fibonacci won't be used with no trend
   fibolevel = helpers.trans_list_to_BT_array(fibolevel, name)
   return fibolevel


def fibo_strongretrace(trend, pricerange, last):
   strongretrace = create_fibolevel(trend, pricerange, last, 0.236, 'strongretrace')
   return strongretrace


def fibo_weakretrace(trend, pricerange, last):
   weakretrace = create_fibolevel(trend, pricerange, last, 0.382, 'weakretrace')
   return weakretrace


def fibo_weakend(trend, pricerange, last):
   weakend = create_fibolevel(trend, pricerange, last, 0.618, 'weakend')
   return weakend


def fibo_strongend(trend, pricerange, last):
   strongend = create_fibolevel(trend, pricerange, last, 0.764, 'strongend')
   return strongend