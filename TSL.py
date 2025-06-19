import numpy as np
import helpers
from moves import is_rising_above as rises
from moves import is_falling_below as falls


def add_PSAR_impact(reldist, psar, close, weight):
   psardist = abs(psar-close)
   change_factor = (psardist/reldist) - 1
   return ((reldist*change_factor)/8)*weight


def add_ATR_impact(reldist, atr, mincalcwin, chwin, win, TSLweight):
   shift = 0
   if len(atr) > win + chwin:
      # absolute, static impact
      if len(atr) >= mincalcwin + win:  # by the initial amount of NaNs longer - so min calcwin is based on actual values
         current_zscore_ATR = (atr[-1] - np.nanmean(atr)) / np.nanstd(atr)  # these exclude NaNs from calc automatically
         shift += (reldist/8)*current_zscore_ATR*TSLweight
      # relative, dynamic impact
      if rises(atr[-chwin:]) or falls(atr[-chwin:]):
         prct_change = (atr[-1]/(atr[-chwin]/100)-100)
         shift += reldist*(prct_change/100)*TSLweight
   return shift



def add_BB_width_impact(reldist, widths, TSLweight):  # TSLexpfac: Trailing Stop Loss width EXPansion FACtor
   shift = 0
   prct_change = (widths[-1]/(widths[0]/100)-100)
   shift += reldist*(prct_change/100)*TSLweight
   return shift


def add_power_impact(reldist, powers, minTSLdist, TSLweight):
   abs_power = abs(powers[-1])  # the powers list of size chwin (see below) is a relict from the old idea, preserved here but not really needed anymore.
   shift = 0
   if reldist - (abs_power*(reldist/30))*TSLweight < minTSLdist: # this means (per weight): if power was 30, shift would be as big as reldist
      shift -= abs(reldist-minTSLdist)
   else:
      shift -= (abs_power*(reldist/30))*TSLweight
   return shift

# old idea: dynamic power impact --> but absolute impact (see above) may be clearer and more concise
# def add_power_impact(reldist, powers, minTSLdist, TSLweight):
   # here it should be intended that the higher the power difference is to stronger power (+ or - !), the closer the distance should get ( --> subtraction),
   # and the higher the power difference is to weaker power (+ or - !), the closer the distance should get ( --> subtraction).
   # shift = 0
   # abs_powdiff = abs(powers[-1] - powers[0])
   # shift -= (reldist/10)*abs_powdiff*TSLweight  # this means (per weight): if power difference is 10, shift would be as big as reldist
   # if reldist + shift < minTSLdist:  # note that shift is negative and hence this works like a substraction
   #    shift = (reldist-minTSLdist)*(-1)
   # return shift


def former_spans_impact(Highs, Lows):
   dist = 0
   amount = len(Highs)
   for idx in range(amount):
      dist += (Highs[idx]-Lows[idx])
   dist /= amount
   return dist


# indis for stopdist calc: PSAR, ATR, BB width, GAP
def stoplosses(Close, High, Low, T, spanswin, SLdist_redufac, powers, power_TSL_chwin, minTSLdist, power_TSL_weight):
   abs_SL_dists = []
   for idx in range(len(Close)):
      # if using Close for calculation, don't forget to use -1 or lower index than current.
      reldist = 0.0005
      # new:
      if idx > 8:
         reldist = former_spans_impact(High[idx-spanswin:idx], Low[idx-spanswin:idx])
      
      reldist += add_PSAR_impact(reldist, T['PSAR']['psar'][idx], Close[idx-1], T['PSAR']['weight'])

      reldist += add_ATR_impact(reldist, T['ATR']['atr'][:idx+1], T['ATR']['mincalcwin'], T['ATR']['chwin'], T['ATR']['win'], T['ATR']['TSL-weight'])
      if idx > 20:
         reldist += add_BB_width_impact(reldist, T['BB']['width'][idx-(T['BB']['TSL-chwin']-1):idx+1], T['BB']['TSL-weight'])
         reldist += add_power_impact(reldist, powers[idx-(power_TSL_chwin-1):idx+1], minTSLdist, power_TSL_weight)
      
      # ! until this point, distance calcs were only regarding absolute value - now determine direction pos/neg by applying 'decision' val
         
      abs_SL_dists.append(abs(reldist)/(SLdist_redufac/10))
   abs_SL_dists = helpers.trans_list_to_BT_array(abs_SL_dists, 'stop loss values')
   return abs_SL_dists
   # --> why returning absolute distances and not the "ready" stoploss values (Close[idx-1] + reldist)?
   # ...because it is safer and hence better to determine the stoploss direction upon actual, active trades (dedected in next())!



