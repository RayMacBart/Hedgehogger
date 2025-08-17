import helpers
import numpy as np


def generate_fibo_dists(Close, last, seclast, factor):
   for idx in range(len(Close)):
      if not idx:
         yield Close[0]
      if seclast[idx] - last[idx]:
         yield last[idx] + (seclast[idx] - last[idx])*factor

def calc_fibo_dist(Close, last, seclast, factor, name):
   dist = list(generate_fibo_dists(Close, last, seclast, factor))
   dist = list(helpers.fill_inclomplete_data(dist, Close, name))
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


#(old)[backups/old_fibo_funcs.txt]

