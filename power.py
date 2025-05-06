import helpers
from moves import is_rising_above as rises
from moves import is_falling_below as falls
from DST_timehelper import get_vol2mean_zscore_deviation
# import pdb


def MACD_calcpower(macd, histo, 
                   # signal,  #--> not used (yet?) 
                   zeroweight, histoweight, impact_counter):
   shift = 0
   if rises(macd, 0):
      shift += zeroweight
      impact_counter['MACD-zeroX'] += 1
   elif falls(macd, 0):
      shift -= zeroweight
      impact_counter['MACD-zeroX'] += 1
   if rises(histo, 0):
      shift += histoweight
      impact_counter['MACD-sigX'] += 1
   elif falls(histo, 0):
      shift -= histoweight
      impact_counter['MACD-sigX'] += 1
   return shift


def VWAP_calcpower(Closes, vwap, expfac, weight):
   shifting = 0
   for i in range(-1, -len(Closes)-1, -1):
      if rises(Closes, vwap[i]):
         shifting += 1
      elif falls(Closes, vwap[i]):
         shifting -= 1
      else:
         diff_widths = [Closes[i]-vwap[i] for i in range(len(Closes))]
         if diff_widths[0] > 0:
            if rises(diff_widths, diff_widths[0]*expfac):
               shifting += 1
         elif diff_widths[0] < 0:
            if falls(diff_widths, diff_widths[0]*expfac):
               shifting -= 1
   shift = 0
   if shifting > 0:
      shift += weight
   elif shifting < 0:
      shift -= weight
   return shift


def FIBO_calcpower(Close, dir, f2, f4, f6, f8, weight):
   shift = 0
   if dir < 0:
      if falls(Close, f8):
         shift -= weight*1.3
      elif falls(Close, f6):
         shift -= weight*1.1
      elif falls(Close, f4):
         shift -= weight*0.9
      elif falls(Close, f2):
         shift -= weight*0.7
   elif dir > 0:
      if rises(Close, f8):
         shift += weight*1.3
      elif rises(Close, f6):
         shift += weight*1.1
      elif rises(Close, f4):
         shift += weight*0.9
      elif rises(Close, f2):
         shift += weight*0.7
   return shift


def RSI_calcpower(rsi, low_th, high_th, weight, impact_counter):  # 'th': treshold
   shift = 0
   # static absolute impacts:
   if rsi > high_th: 
      shift -= weight
   elif rsi < low_th:
      shift += weight
   if rsi > high_th or rsi < low_th:
      impact_counter['RSI-abs'] += 1
   # dynamic movement impacts:
   if falls(rsi) and (rsi > low_th):
   # if falls(rsi) and (rsi > (low + (50-low)/3)):
      shift -= weight
      impact_counter['RSI-dyn'] += 1
   elif rises(rsi) and (rsi < high_th):
   # elif rises(rsi) and (rsi < (50 + ((high-50)/3)*2)):
      shift += weight
      impact_counter['RSI-dyn'] += 1
   return shift


def CCI_calcpower(cci, low_th, high_th, weight, impact_counter):  # 'th': treshold
   shift = 0
   # static absolute impacts:
   if cci > high_th: 
      shift += weight
   elif cci < low_th:
      shift -= weight
   if cci > high_th or cci < low_th:
      impact_counter['CCI-abs'] += 1
   # dynamic movement impacts:
   if falls(cci) and (cci < 0):
   # if falls(cci) and (cci < low_th/2):
      shift -= weight
      impact_counter['CCI-dyn'] += 1
   elif rises(cci) and (cci > 0):
   # elif rises(cci) and (cci > high_th/2):
      shift += weight
      impact_counter['CCI-dyn'] += 1
   return shift


def BB_outer_touch_calcpower(low, mid, high, Highs, Lows, dir, weight):
   shift = 0
   if dir > 0 and (Lows[-1] < mid[-1]):
   # old, pickier (maybe better!!!) version: (also removed below from check: rises(Closes) and replaced with dir>0 and Lows)
   # if dir > 0 and (Lows[-1] < ((mid[-1]*2 + low[-1]) / 3)): # below one third below mid
      touched = False
      for i in range(len(Lows)):
         if Lows[i] <= low[i]:
            touched = True
      if touched:
         shift += weight
   elif dir < 0 and (Highs[-1] > mid[-1]): # above one third above mid
   # old, pickier (maybe better!!!) version: (also removed below from check: falls(Closes) and replaced with dir<0 and Highs)
   # elif dir < 0 and (Highs[-1] > ((mid[-1]*2 + high[-1]) / 3)): # above one third above mid
      touched = False
      for i in range(len(Highs)):
         if Highs[i] >= high[i]:
            touched = True
      if touched:
         shift -= weight
   return shift

# pre-guessing version could work like:
   # if rises(Closes) and (Closes[-1] >= high[-1]) and pow < trend_treshold:  (would need "pow" and "trend_treshold" args)
   # implement price reversal guessings not only upon pow verification, but also only upon outer band touches if 
   # reversal direction is confirmed by mid band rise/fall!
   # observe wether this guessing or the confirming strategy works better and change other indicator to better strategy
   # (and compare effectiveness with old version)

def BB_trend_calcpower(pow, mids, widths, expfac, weight):  # expfac: width expansion factor
   factor = 1
   if (((pow > 0) and rises(mids)) or ((pow < 0) and falls(mids))) and rises(widths, widths[0]*expfac):
      factor += weight/6
   return factor


def VOL_calcpower(vols, mdfpwi, mpfpw, weight, TS, VMMTs, clims):  
   # mnfpwi: "max decreasing factor per weight impact"
   # mpfpw: "max positive factor per weight"
   zscore_volstart = (vols[0]-VMMTs['mean'])/VMMTs['std']
   zscore_volend = (vols[-1]-VMMTs['mean'])/VMMTs['std']
   zvoldiff = zscore_volend - zscore_volstart  # this is possible because absolute values are used here
   # ^ this would not be possible with the already relative values in VMMTs!
   ZSDFM = get_vol2mean_zscore_deviation(zvoldiff, len(vols), TS, VMMTs, clims) # ZSCORE DEVIATION FROM MEANS
   factor = 1
   if ZSDFM < 0:
      factor -= mdfpwi*(ZSDFM/VMMTs['min'])*weight
      if factor < 1 / abs(VMMTs['min'])*weight:
         factor = 1 / abs(VMMTs['min'])*weight
   elif ZSDFM > 0:
      factor += ZSDFM*weight
      if factor > mpfpw:
         factor = mpfpw
   return factor
   

   # with the new z score normalized version, the below defusing/adjusting isn't necessary anymore
   # dePDFM = helpers.defuse(abs(PDFM), defuse_lvl)
   # maxval = helpers.defuse(1000, defuse_lvl)
   # if ZSDFM > 0:
   #    factor += 0.2*(deZSDFM/maxval)*weight
   # elif ZSDFM < 0:
   #    factor -= 0.16666*(deZSDFM/maxval)*weight

   #  normdev = (PDFM - VMMTs['mean']) / VMMTs['std'] # z score normalization --> nice, but not really helping here
   # old idea with surpass treshold:
   # vpdf = get_volume_peak_defusing_factor(TS)
   # if rises(vols, vols[0]+(vols[0]*(mtcp/100))):
   #    grown_to_percentage = vols[-1]/(vols[0]/100)
   #    factor *= ((grown_to_percentage/100)/5)*weight*vpdf
   # return factor


def ADX_calcpower(pow, adx, dmp, dmn, treshold, abs_weight, dyn_weight, impact_counter):
   factor = 1
   if (pow > 0 and dmp > dmn) or (pow < 0 and dmp < dmn):
      # static absolute impacts:
      if adx[-1] >= treshold:
         factor += ((adx[-1] - treshold)/100)*(abs_weight)/1.67
         impact_counter['ADX-abs'] += 1
      elif adx[-1] <= 20:
         factor -= ((20 - adx[-1])/100)*(abs_weight)/1.67
      # dynamic movement impacts:
      if (dmp > dmn and rises(adx)) or (dmp < dmn and falls(adx)):
         prct_change = (adx[-1]/(adx[0]/100)-100)
         factor += (factor/100)*prct_change*(dyn_weight)/1.67
         impact_counter['ADX-dyn'] += 1
      # if adx <= 20:
      #    pass # here could be a 'confirmation' of a beginning range-bound phase take place.
   return factor



def CAMA_calcpower(pow, close_val, R4, R3, S3, S4, w3, w4):
   factor = 1
   if (pow < 0 and close_val > R4) or (pow > 0 and close_val < S4):
      factor += w4/6
   elif (pow < 0 and close_val > R3) or (pow > 0 and close_val < S3):
      factor += w3/6
   elif (pow < 0 and close_val < S4) or (pow > 0 and close_val > R4):
      factor -= w4/8
   elif (pow < 0 and close_val < S3) or (pow > 0 and close_val > R3):
      factor -= w3/8
   return factor


def PEAK_calcpower(pow, dir_val, uppeak, downpeak, acc, weight, last_val, close_val):
   factor = 1
   if (((pow < 0 and dir_val < 0 and close_val < last_val) and 
        (last_val - (downpeak - close_val*(acc/200)) <= close_val <= (last_val - (downpeak + close_val*(acc/200))))) or
        ((pow > 0 and dir_val > 0 and close_val > last_val) and 
         (last_val + (uppeak - close_val*(acc/200)) <= last_val <= (last_val + (uppeak + close_val*(acc/200)))))):
      if weight/8 < 1:
         factor -= weight/8
      else:
         factor = 0
   return factor


# OLD VERSION (WITH A DIFFERENTIATION FROM REVERSAL CONFIRMATION BY CANDLE AMOUNT SINCE LAST SWING... NOT CONVINCING):
# def PEAK_calcpower(pow, dir, uppeak, downpeak, acc, weight, last, close_val, swingdist):
#    factor = 1
#    if ((pow < 0 and dir[-1] < 0 and dir[-swingdist] > 0 and  # "dir[-swingdist]" implements distance of last swing
#         # BELOW YOU MUST ADD THE PEAK VAL TO THE LAST SWINGS VAL!!!!
#         (last - (downpeak - downpeak*(acc/200)) <= close_val <= (last - (downpeak + downpeak*(acc/200))))) or

#         (pow > 0 and dir[-1] > 0 and dir[-swingdist] < 0 and 
#          (last + (uppeak - uppeak*(acc/200)) <= last <= (last + (uppeak + uppeak*(acc/200)))))):
#       factor += weight/5
#    elif ((pow < 0 and all(d < 0 for d in dir[-swingdist:]) and # "after more than 'swingdist' candles into same dir"
#           # BELOW YOU MUST SUBTRACT THE PEAK VAL TO THE LAST SWINGS VAL!!!!
#          (downpeak - downpeak*(0.25/acc) <= (last - close_val) <= downpeak + downpeak*(0.25/acc))) or
#          (pow > 0 and all(d > 0 for d in dir[-swingdist:]) and 
#           (uppeak - uppeak*(0.25/acc) <= (close_val - last) <= uppeak + uppeak*(0.25/acc)))):
#       factor -= weight/5
#    return factor


def detect_impact(impact_counter, power, lastpower, tech_ind):
   if power != lastpower:
      impact_counter[tech_ind] += 1
   # print(f'power after {tech_ind}:', power)
   return power


# FUTURE TEST FOR EFFECTIVENESS: NOT RELY ON ACTUAL DEDECTED MOVEMENTS (VIA DIR), BUT ACTUALLY GUESS/FORESEE REVERSALS
# FUTURE TEST FOR EFFECTIVENESS: define range-bound phases: they occur if "power" is near 0 or
# if a variable that measures the 'power' of trend indicators only is near 0.
# in such a range-bound phase, e.g. touching cama-points, fibo-points or outer BBs could be a reversal signal.

def powers(Data, T, last, timestamps, VMMTs, clims, impact_counter):
   powers = []
   for idx in range(len(Data.Close)):
      power = 0
      lastpower = 0
      # if using Close for calculation, don't forget to use -1 or lower index than current.
      if idx > 15 and idx % 10 == 0:
         power += MACD_calcpower(T['MACD']['macd'][idx-(T['MACD']['macd_chwin']-1):idx+1], 
                                 T['MACD']['histo'][idx-(T['MACD']['histo_chwin']-1):idx+1], 
                                 # T['MACD']['signal'][idx-(T['MACD']['signal_chwin']-1):idx+1], # not used (yet?)
                                 T['MACD']['zeroweight'], T['MACD']['histoweight'], impact_counter)
         lastpower = detect_impact(impact_counter, power, lastpower, 'MACD')

         power += VWAP_calcpower(Data.Close[idx-(T['VWAP']['chwin']):idx], T['VWAP']['vwap'][idx-(T['VWAP']['chwin']-1):idx+1],
                                 T['VWAP']['expfac'], T['VWAP']['weight'])  # --> vwap misuse?
         lastpower = detect_impact(impact_counter, power, lastpower, 'VWAP')

         # I 'misuse' the fibonacci points in a unconventional way as breakthrough indicator.
         power += FIBO_calcpower(Data.Close[idx-(T['FIBO']['chwin']):idx], T['DIR'][idx], T['FIBO'][2][idx], T['FIBO'][4][idx],
                                      T['FIBO'][6][idx], T['FIBO'][8][idx], T['FIBO']['weight'])
         lastpower = detect_impact(impact_counter, power, lastpower, 'FIBO')

         power += RSI_calcpower(T['RSI']['rsi'][idx-(T['RSI']['chwin']-1):idx+1], T['RSI']['low'],
                                T['RSI']['high'], T['RSI']['weight'], impact_counter)
         lastpower = detect_impact(impact_counter, power, lastpower, 'RSI')

         power += CCI_calcpower(T['CCI']['cci'][idx-(T['CCI']['chwin']-1):idx+1], T['CCI']['low'],
                                T['CCI']['high'], T['CCI']['weight'], impact_counter)
         lastpower = detect_impact(impact_counter, power, lastpower, 'CCI')

         power += BB_outer_touch_calcpower(T['BB']['low'][idx-(T['BB']['chwin-out']-1):idx+1], T['BB']['mid'][idx-(T['BB']['chwin-out']-1):idx+1],
                                T['BB']['high'][idx-(T['BB']['chwin-out']-1):idx+1], Data.High[idx-(T['BB']['chwin-out']):idx], 
                                Data.Low[idx-(T['BB']['chwin-out']):idx], T['DIR'][idx], T['BB']['weight-out'])
         lastpower = detect_impact(impact_counter, power, lastpower, 'BB-out')
         power *= BB_trend_calcpower(power, T['BB']['mid'][idx-(T['BB']['chwin-trend']-1):idx+1], 
                                     T['BB']['width'][idx-(T['BB']['chwin-trend']-1):idx+1], T['BB']['expfac'], T['BB']['weight-trend'])
         lastpower = detect_impact(impact_counter, power, lastpower, 'BB-trend')

         power *= VOL_calcpower(T['VOL']['volume'][idx-(T['VOL']['chwin']):idx], T['VOL']['mdfpwi'],
                                T['VOL']['mpfpw'], T['VOL']['weight'], timestamps[idx-1], VMMTs, clims)
         lastpower = detect_impact(impact_counter, power, lastpower, 'VOL')

         power *= ADX_calcpower(power, T['ADX']['adx'][idx-(T['ADX']['chwin']-1):idx+1], T['ADX']['DM+'][idx], T['ADX']['DM-'][idx],
                                T['ADX']['treshold'], T['ADX']['abs_weight'], T['ADX']['dyn_weight'], impact_counter)
         lastpower = detect_impact(impact_counter, power, lastpower, 'ADX')

         power *= CAMA_calcpower(power, Data.Close[idx-1], T['CAMA']['R4'][idx], T['CAMA']['R3'][idx], T['CAMA']['S3'][idx],
                                 T['CAMA']['S4'][idx], T['CAMA']['3weight'], T['CAMA']['4weight'])
         lastpower = detect_impact(impact_counter, power, lastpower, 'CAMA')

         power *= PEAK_calcpower(power, T['DIR'][idx], T['PEAK']['+'], T['PEAK']['-'],
                                 T['PEAK']['accuracy'], T['PEAK']['weight'], last[idx], Data.Close[idx-1] #, T['PEAK']['swingdist']
         )
         lastpower = detect_impact(impact_counter, power, lastpower, 'PEAK')

         # print('_______________________________')
      powers.append(power)
   
   # floats = 0
   # ints = 0
   # elses = 0

   # for p in powers:
   #    print(p)
   #    if type(p) == float:
   #       floats += 1
   #    elif type(p) == int:
   #       ints += 1
   #    else:
   #       elses += 1
         # if isinstance(p, _Indicator):
         #    print('Indicator type found:', type(p), '  value:', p)
   # print('--------------\ntypes found:')
   # print('floats:', floats, '  ints:', ints, '  elses:', elses)
   # print('--------------')
   

   powers = helpers.trans_list_to_BT_array(powers, 'powers')
   return powers

