import numpy as np
import helpers


def PSAR(PSARl, PSARs, close):
   PSAR = []
   for idx in range(len(close)):
      if np.isnan(PSARs[idx]) and np.isnan(PSARl[idx]):
         PSAR.append(np.nan)
      elif np.isnan(PSARs[idx]):
         PSAR.append(PSARl[idx])
      elif np.isnan(PSARl[idx]):
         PSAR.append(PSARs[idx])
   PSAR = helpers.trans_list_to_BT_array(PSAR, 'PSAR')
   return PSAR


def lowerband(band):
   return band
def upperband(band):
   return band
def middleband(band):
   return band
def bandwidth(band):
   return band


def get_adx(adx):
   return adx
def get_dmp(dmp):
   return dmp
def get_dmn(dmn):
   return dmn