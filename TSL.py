import numpy as np
import helpers
from moves import is_rising_above as rises
from moves import is_falling_below as falls


def add_ATR_impact(reldist, atr, mincalcwin, chwin, win, TSLweight):
   shift = 0
   if len(atr) > win + chwin:
      # absolute, static impact
      if len(atr) >= mincalcwin + win:  # by the initial amount of NaNs longer - so min calcwin is based on actual values
         abs_current_zscore_ATR = abs((atr[-1] - np.nanmean(atr)) / np.nanstd(atr))  # these exclude NaNs from calc automatically
         shift += (reldist/10)*abs_current_zscore_ATR*TSLweight
      # relative, dynamic impact
      if rises(atr[-chwin:]) or falls(atr[-chwin:]):
         abs_prct_change = abs((atr[-1]/(atr[-chwin]/100)-100))
         shift += reldist*(abs_prct_change/100)*TSLweight
   return shift



def add_BB_width_impact(reldist, widths, TSLweight):  # TSLexpfac: Trailing Stop Loss width EXPansion FACtor
   shift = 0
   abs_prct_change = abs((widths[-1]/(widths[0]/100)-100))
   shift += reldist*(abs_prct_change/100)*TSLweight
   return shift


def add_power_impact(reldist, powers, minTSLdist, TSLweight):
   shift = 0
   abs_powdiff = abs(powers[-1] - powers[0])
   shift -= (reldist/10)*abs_powdiff*TSLweight  # this means (per weight): if power difference is 10, shift would be as big as reldist
   if reldist + shift < minTSLdist:  # note that shift is negative and hence this works like a substraction
      shift = (reldist-minTSLdist)*(-1)
   return shift



# indis for stopdist calc: PSAR, ATR, BB width, GAP
def get_distance(Close, T, powers, power_TSL_chwin, minTSLdist, power_TSL_weight):
   distances = []
   for idx in range(len(Close)):
      # if using Close for calculation, don't forget to use -1 or lower index than current.
      init_distpos = T['PSAR'][idx]
      reldist = init_distpos - Close[idx-1]
      reldist += add_ATR_impact(reldist, T['ATR']['atr'][:idx+1], T['ATR']['mincalcwin'], T['ATR']['chwin'], T['ATR']['win'], T['ATR']['TSL-weight'])
      if idx > 20:
         reldist += add_BB_width_impact(reldist, T['BB']['width'][idx-(T['BB']['TSL-chwin']-1):idx+1], T['BB']['TSL-weight'])
         reldist += add_power_impact(reldist, powers[idx-(power_TSL_chwin-1):idx+1], minTSLdist, power_TSL_weight)
      
      # ! until this point, distance calcs were only regarding absolute value - now determine direction pos/neg by applying 'decision' val
         
      distances.append(Close[idx-1] + reldist)
   distances = helpers.trans_list_to_BT_array(distances, 'distances')
   return distances



