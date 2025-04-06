import helpers
import numpy as np


def calc_fibo_dist(Close, last, seclast, factor, name):
   dist = []
   for idx in range(len(Close)):
      if not idx:
         dist.append(Close[0])
      if seclast[idx] - last[idx]:
         dist.append(last[idx] + (seclast[idx] - last[idx])*factor)
   helpers.fill_inclomplete_data(dist, Close, name)
   dist = helpers.trans_list_to_BT_array(dist, name)
   return dist


def fibo_dist2(Close, last, seclast):
   dist2 = calc_fibo_dist(Close, last, seclast, 1.236, 'fibodist2')
   return dist2
def fibo_dist4(Close, last, seclast):
   dist4 = calc_fibo_dist(Close, last, seclast, 1.382, 'fibodist4')
   return dist4
def fibo_dist6(Close, last, seclast):
   dist6 = calc_fibo_dist(Close, last, seclast, 1.618, 'fibodist6')
   return dist6
def fibo_dist8(Close, last, seclast):
   dist8 = calc_fibo_dist(Close, last, seclast, 1.764, 'fibodist8')
   return dist8


# def fibo_pricerange(Close, last, seclast, trend):
#    pricerange = []
#    for idx in range(len(Close)):
#       if not idx:
#          pricerange.append(0)
#       if last[idx] - seclast[idx]:
#          pricerange.append(abs(seclast[idx] - last[idx]))
#       else:
#          pricerange.append(pricerange[-1])
#    while len(pricerange) > len(Close):
#       pricerange.pop()
#    helpers.fill_inclomplete_data(pricerange, Close, 'fibo pricerange')
#    pricerange = helpers.trans_list_to_BT_array(pricerange, 'fibo pricerange')
#    return pricerange


# def create_fibolevel(Close, trend, dirs, pricerange, factor, name):
#    fibolevel = []
#    for idx in range(len(Close)):
#       if idx >= 1:
#          if trend[idx] == 1:
#             if dirs[idx] > 0:
#                fibolevel.append(Close[idx-1] - pricerange[idx]*factor)
#             else:
#                fibolevel.append(fibolevel[-1])
#          elif trend[idx] == -1:
#             if dirs[idx] < 0:
#                fibolevel.append(Close[idx-1] + pricerange[idx]*factor)
#             else:
#                fibolevel.append(fibolevel[-1])
#          else:
#             fibolevel.append(Close[idx-1]*0.9985) # fibonacci won't be used with no trend
#             # fibolevel.append(np.nan)
#       else:
#          fibolevel.append(Close[idx-1]*0.9985)
#    fibolevel = helpers.trans_list_to_BT_array(fibolevel, name)
#    return fibolevel


# def fibo_strongretrace(Close, trend, dirs, pricerange):
#    strongretrace = create_fibolevel(Close, trend, dirs, pricerange, 0.236, 'strongretrace')
#    return strongretrace


# def fibo_weakretrace(Close, trend, dirs, pricerange):
#    weakretrace = create_fibolevel(Close, trend, dirs, pricerange,0.382, 'weakretrace')
#    return weakretrace


# def fibo_weakend(Close, trend, dirs, pricerange):
#    weakend = create_fibolevel(Close, trend, dirs, pricerange, 0.618, 'weakend')
#    return weakend


# def fibo_strongend(Close, trend, dirs, pricerange):
#    strongend = create_fibolevel(Close, trend, dirs, pricerange, 0.764, 'strongend')
#    return strongend