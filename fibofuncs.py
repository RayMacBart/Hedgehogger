import numpy as np
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
   while len(pricerange) < len(Close):
      pricerange.append(pricerange[-1])
   pricerange = np.array(pricerange, dtype='float64')
   pricerange = _Array(pricerange, name='fibo_pricerange')
   return pricerange

def create_fibolevel(trend, pricerange, last, factor):
   fibolevel = []
   for idx in range(len(pricerange)):
      if trend[idx] == 1:
         fibolevel.append(last[idx] - pricerange[idx]*factor)
      elif trend[idx] == -1:
         fibolevel.append(last[idx] + pricerange[idx]*factor)
      else:
         fibolevel.append(last[idx]*0.9985) # fibonacci won't be used with no trend
   fibolevel = np.array(fibolevel, dtype='float64')
   return fibolevel

def fibo_strongretrace(trend, pricerange, last):
   strongretrace = create_fibolevel(trend, pricerange, last, 0.236)
   strongretrace = _Array(strongretrace, name='strongretrace')
   return strongretrace

def fibo_weakretrace(trend, pricerange, last):
   weakretrace = create_fibolevel(trend, pricerange, last, 0.382)
   weakretrace = _Array(weakretrace, name='weakretrace')
   return weakretrace

def fibo_weakend(trend, pricerange, last):
   weakend = create_fibolevel(trend, pricerange, last, 0.618)
   weakend = _Array(weakend, name='weakend')
   return weakend

def fibo_strongend(trend, pricerange, last):
   strongend = create_fibolevel(trend, pricerange, last, 0.764)
   strongend = _Array(strongend, name='strongend')
   return strongend