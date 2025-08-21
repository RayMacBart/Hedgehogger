import helpers
from moves import is_rising_above as rises
from moves import is_falling_below as falls
from DST_timehelper import get_vol2mean_zscore_deviation
import numpy as np
# import pdb

#(DIR)[backups/dir_calcpower_definition.py]



def CSP_calcpower(Data, bodyshrink_factor, shadow2body_factor, shadowdiff_factor, weight):
   shift = 0
   idx = 0
   for row in Data.itertuples():
      if idx: # 0 = needed 'pre'-candle
         if abs(row.Close - row.Open) <= abs(Data.Close.iloc[idx-1] - Data.Open.iloc[idx-1]) / bodyshrink_factor:
            upshadow = row.High - row.Close if row.Close - row.Open >= 0 else row.High - row.Open
            downshadow = row.Open - row.Low if row.Close - row.Open >= 0 else row.Close - row.Low
            if Data.Close.iloc[idx-1] - Data.Open.iloc[idx-1] > 0:  # price was moving up
               if upshadow >= abs(row.Close - row.Open) * shadow2body_factor and upshadow >= downshadow * shadowdiff_factor:
                  shift -= weight
            else: # price was moving down
               if downshadow >= abs(row.Close - row.Open) * shadow2body_factor and downshadow >= upshadow * shadowdiff_factor:
                  shift += weight
                  #(!)[docs/note_at_CSP_calcpower.txt]
      idx += 1
   return shift



def MACD_calcpower(macd, histo, macd_chwin, histo_chwin, chval_treshold, histo_chval_th,
                   # signal,  #--> not used (yet?) 
                   zeroweight, histoweight, comboweight, impact_counter):  #(!)[docs/combo_chwin_note.txt]
   real_chval_th = chval_treshold/100000
   real_histo_chval_th = histo_chval_th/100000
   shift = 0
   if (abs(macd[-1] - macd[0]) >= real_chval_th):
      if rises(macd[-macd_chwin:], 0):
         shift += zeroweight
         impact_counter['MACD-zeroX'] += 1
      elif falls(macd[-macd_chwin:], 0):
         shift -= zeroweight
         impact_counter['MACD-zeroX'] += 1
   if abs(histo[-1] - histo[0]) >= real_histo_chval_th:
      if rises(histo[-histo_chwin:], 0):
         shift += histoweight
         impact_counter['MACD-sigX'] += 1
      elif falls(histo[-histo_chwin:], 0):
         shift -= histoweight
         impact_counter['MACD-sigX'] += 1
   if (abs(macd[-1] - macd[0]) >= real_chval_th) and (abs(histo[-1] - histo[0]) >= real_histo_chval_th):
      if rises(macd) and rises(histo):
         shift += comboweight
         impact_counter['MACD-combo'] += 1
      elif falls(macd) and falls(histo):
         shift -= comboweight
         impact_counter['MACD-combo'] += 1

   #(old)[backups/old_MACD_calcpower_code.py]
   return shift



def VWAP_calcpower(Closes, vwap, expfac, weight):
   real_expfac = (expfac/10)+1  # only 'expfac' is adjusted version to be integers usable with sambo opt.
   shifting = 0
   for i in range(-1, -len(Closes)-1, -1):
      if rises(Closes, vwap[i]):
         shifting += 1
      elif falls(Closes, vwap[i]):
         shifting -= 1
      else:
         diff_widths = [Closes[i]-vwap[i] for i in range(len(Closes))]
         if diff_widths[0] > 0:
            if rises(diff_widths, diff_widths[0]*real_expfac):
               shifting += 1
         elif diff_widths[0] < 0:
            if falls(diff_widths, diff_widths[0]*real_expfac):
               shifting -= 1
   shift = 0
   if shifting > 0:
      shift += weight
   elif shifting < 0:
      shift -= weight
   return shift



def FIBO_calcpower(Close, dir, f2, f4, f6, f8, weight):   # is this unconventional use of fibonacci even good? (test it)
   shift = 0
   if dir < 0:
      if falls(Close, f6):
         shift -= weight
   elif dir > 0:
      if rises(Close, f6):
         shift += weight
   # if dir < 0:
   #    if falls(Close, f8):
   #       shift -= weight*1.3
   #    elif falls(Close, f6):
   #       shift -= weight*1.1
   #    elif falls(Close, f4):
   #       shift -= weight*0.9
   #    elif falls(Close, f2):
   #       shift -= weight*0.7
   # elif dir > 0:
   #    if rises(Close, f8):
   #       shift += weight*1.3
   #    elif rises(Close, f6):
   #       shift += weight*1.1
   #    elif rises(Close, f4):
   #       shift += weight*0.9
   #    elif rises(Close, f2):
   #       shift += weight*0.7
   return shift



def CAMA_calcpower(close_val, R4, R3, S3, S4, w3, w4):  
   shift = 0
   if (close_val > R4):
      shift -= w4
   # elif (close_val > R3):
   #    shift -= w3
   # elif (close_val < S3):
   #    shift += w3
   elif (close_val < S4):
      shift += w4
   return shift

#(good alternative)[backups/confirming_CAMA_calcpower.py]



def RSI_calcpower(rsi, low_th, high_th, chval_treshold, weight, impact_counter):  # 'th': treshold
   shift = 0
   # static absolute impacts:
   if rsi[-1] > high_th: 
      shift -= weight
   elif rsi[-1] < low_th:
      shift += weight
   if rsi[-1] > high_th or rsi[-1] < low_th:
      impact_counter['RSI-abs'] += 1
   # dynamic movement impacts:
   if abs(rsi[-1] - rsi[0]) >= chval_treshold:
      if falls(rsi) and (rsi > low_th):
      # if falls(rsi) and (rsi > (low_th + (50-low_th)/3)):
         shift -= weight
         impact_counter['RSI-dyn'] += 1
      elif rises(rsi) and (rsi < high_th):
      # elif rises(rsi) and (rsi < (50 + ((high_th-50)/3)*2)):
         shift += weight
         impact_counter['RSI-dyn'] += 1
   return shift



def CCI_calcpower(cci, low_th, high_th, chval_treshold, weight, impact_counter):  # 'th': treshold
   shift = 0
   # static absolute impacts:
   if cci[-1] > high_th: 
      shift += weight
   elif cci[-1] < low_th:
      shift -= weight
   if cci[-1] > high_th or cci[-1] < low_th:
      impact_counter['CCI-abs'] += 1
   # dynamic movement impacts:
   if abs(cci[-1] - cci[0]) >= chval_treshold:
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

#(pre-guessing version idea)[docs/BB-preguessing.txt]




def BB_trend_calcpower(pow, mids, widths, expfac, weight):  # expfac: width expansion factor
   real_expfac = (expfac/10)+1  # only 'expfac' is adjusted version to be integers usable with sambo opt.
   factor = 1
   if (((pow > 0) and rises(mids)) or ((pow < 0) and falls(mids))) and rises(widths, widths[0]*real_expfac):
      abs_prct_change = abs((widths[-1]/(widths[0]/100)-100))
      DAPC = helpers.calc_special_defusion(abs_prct_change, 100, 560)  # Defused Absolute Percentual Change
      factor += (DAPC/100)*weight
   return factor



def VOL_calcpower(vols, mdfpwi, max_impact_zscore, weight, TS, VMMTs, clims):  
   # mdfpwi: "max decreasing factor per weight impact"
   # mpfpw: "max positive factor per weight"
   real_mdfpwi = mdfpwi/20  # only 'mdfpwi' is adjusted version to be integers usable with sambo opt.
   real_max_impact_zscore = max_impact_zscore/2
   zscore_volstart = (vols[0]-VMMTs['mean'])/VMMTs['std']
   zscore_volend = (vols[-1]-VMMTs['mean'])/VMMTs['std']
   zvoldiff = zscore_volend - zscore_volstart  # this is possible because absolute values are used here
   # ^ this would not be possible with the already relative values in VMMTs!
   ZSDFM = get_vol2mean_zscore_deviation(zvoldiff, len(vols), TS, VMMTs, clims) # ZSCORE DEVIATION FROM MEANS
   factor = 1
   if ZSDFM < 0:
      zsmin = (VMMTs['min']-VMMTs['mean'])/VMMTs['std']
      factor -= real_mdfpwi*(ZSDFM/zsmin)*weight
      # the old idea - nice, but a little unclear (and why this way at all?):
      # if factor < 1 / abs(zsmin)*weight:
      #    factor = 1 / abs(zsmin)*weight
   elif ZSDFM > 0:
      expodenom = helpers.get_zscore_defusion_expodenom(real_max_impact_zscore)  # 'expodenom' = exponent denominator
      DPZC = helpers.calc_special_defusion(ZSDFM, real_max_impact_zscore, expodenom)  # Defused Positive Z-Score Change
      factor += DPZC*weight
      # old, hard cutting version:
      # factor += ZSDFM*weight   # use variable "max logarithmic zscore goal (?) with helpers function "get_defuse_formula_val"
      # if factor > mpfpw:
      #    factor = mpfpw
   if factor < 0.75:  # NEW (+clear): 1 indicator can't decrease power more than 25%
      factor = 0.75
   return factor
   
   #(old)[backups/old_VOL_calcpower.py]



def ADX_calcpower(pow, adx, dmp, dmn, treshold, abs_weight, dyn_weight, impact_counter):
   factor = 1
   # label = ''
   if (pow > 0 and dmp > dmn) or (pow < 0 and dmp < dmn):   # = trend confirming impact only
      # static absolute impacts:
      if adx[-1] >= treshold:
         factor += ((adx[-1] - treshold)/100)*(abs_weight)
         # /1.67
         impact_counter['ADX-abs'] += 1
         # label += 'stat+, '
      elif adx[-1] <= 20:
         factor -= ((20 - adx[-1])/100)*(abs_weight)
         # /1.67
         impact_counter['ADX-abs'] += 1
         # label += 'stat-, '
      # dynamic movement impacts:
      if (dmp > dmn and rises(adx)) or (dmp < dmn and falls(adx)):
         prct_change = (adx[-1]/(adx[0]/100)-100)
         abs_prct_change = abs(prct_change)
         DAPC = helpers.calc_special_defusion(abs_prct_change, 100, 560)  # Defused Absolute Percentual Change
         if (dmp > dmn and rises(adx)):
            factor += (DAPC/100)*(dyn_weight)
         elif (dmp < dmn and falls(adx)):
            factor -= (DAPC/100)*(dyn_weight)
         # /1.67
         impact_counter['ADX-dyn'] += 1
         # label += 'dyn, '
      # if pow*factor - pow:
      #    print(label+':', pow*factor - pow)
      # if adx <= 20:
      #    pass # here could be a 'confirmation' of a beginning range-bound phase take place.
   if factor < 0.75:   
      factor = 0.75  # NEW (+clear): 1 indicator can't decrease power more than 25%
   return factor



def GAP_calcpower(pow, dir_val, upgap_val, downgap_val, acc, weight, last_swing_val, close_val):
   factor = 1
   if (((pow < 0 and dir_val < 0 and close_val < last_swing_val) and 
        (last_swing_val - downgap_val <= close_val <= last_swing_val - downgap_val + close_val*(acc/100))) or # from acc % above to gap (down movement!)
        #(!)[docs/why_not_other_check_at_GAP_calcpower.txt]
        ((pow > 0 and dir_val > 0 and close_val > last_swing_val) and 
         (last_swing_val + upgap_val - close_val*(acc/100) <= last_swing_val <= last_swing_val + upgap_val))):
      factor += weight/5
   return factor



def PEAK_calcpower(pow, dir_val, uppeak_val, downpeak_val, acc, weight, last_swing_val, close_val): # PEAK IS ALLOWED TO TURN POWER TO NEGATIVE (?)
   factor = 1
   if (((pow < 0 and dir_val < 0 and close_val < last_swing_val) and 
        (last_swing_val - downpeak_val - close_val*(acc/200) <= close_val <= last_swing_val - downpeak_val + close_val*(acc/200))) or
        ((pow > 0 and dir_val > 0 and close_val > last_swing_val) and 
         (last_swing_val + uppeak_val - close_val*(acc/200) <= last_swing_val <= last_swing_val + uppeak_val + close_val*(acc/200)))):
      factor -= weight/6 if weight/6 < 0.25 else 0.25
   return factor

#(old)[backups/PEAK_calcpower_old.py]



def ATR_calcpower(atr, mincalcwin, chwin, win, abs_weight, dyn_weight, impact_counter):
   factor = 1
   if len(atr) > win + chwin:
      # absolute, static triggering
      if len(atr) >= mincalcwin + win:  # by the initial amount of NaNs longer - so min calcwin is based on actual values
         current_zscore_ATR = (atr[-1] - np.nanmean(atr)) / np.nanstd(atr)  # these exclude NaNs from calc automatically
         if current_zscore_ATR > 1:
            factor += ((current_zscore_ATR - 1)/4)*abs_weight
            impact_counter['ATR-abs'] += 1
         elif current_zscore_ATR < -1:
            factor += ((current_zscore_ATR + 1)/5)*abs_weight
            impact_counter['ATR-abs'] += 1
      # relative, dynamic triggering
      if rises(atr[-chwin:]) or falls(atr[-chwin:]):
         prct_change = (atr[-1]/(atr[-chwin]/100)-100)
         abs_prct_change = abs(prct_change)
         DAPC = helpers.calc_special_defusion(abs_prct_change, 100, 560)  # Defused Absolute Percentual Change
         impact_counter['ATR-dyn'] += 1
         if rises(atr[-chwin:]) and (prct_change > 0):
            factor += (DAPC/100)*dyn_weight
         elif falls(atr[-chwin:]) and (prct_change < 0):
            factor -= (DAPC/100)*dyn_weight
   if factor < 0.75:  # NEW (+clear): 1 indicator can't decrease power more than 25%
      factor = 0.75
   return factor




def detect_impact(impact_counter, power, lastpower, tech_ind):
   if power != lastpower:
      impact_counter[tech_ind] += 1
   # if power - lastpower:
   #    print(f'impact of {tech_ind}:', power - lastpower)
      # if tech_ind == 'ATR':
      #    print(f'impact of {tech_ind}:', power - lastpower)
   return power



#(!)[docs/note_future_foresee_strat.txt]



def powers(Data, T, last, timestamps, VMMTs, clims, impact_counter):
   powers = []
   for idx in range(len(Data.Close)):
      power = 0
      lastpower = 0
      # if using Close for calculation, don't forget to use -1 or lower index than current.
      if idx > 20:
         # and idx % 10 == 0:
         #(DIR)[backups/dir_calcpower_call.py]


         power += CSP_calcpower(Data.df.iloc[idx-(T['CSP']['reaction_win']-1):idx+1],  T['CSP']['bodyshrink_factor'], # changed 'data' object to df via '.df'
                                T['CSP']['shadow2body_factor'], T['CSP']['shadowdiff_factor'], T['CSP']['weight'])
                                 # Amount of focussed on candles is 1 more than action_win because 1 'pre'-candle is needed.  
         lastpower = detect_impact(impact_counter, power, lastpower, 'CSP')

         power += MACD_calcpower(T['MACD']['macd'][idx-(T['MACD']['combo_chwin']-1):idx+1], 
                                 T['MACD']['histo'][idx-(T['MACD']['combo_chwin']-1):idx+1],
                                 T['MACD']['macd_chwin'], T['MACD']['histo_chwin'],
                                 T['MACD']['chval_treshold'], T['MACD']['histo_chval_th'],
                                 # T['MACD']['signal'][idx-(T['MACD']['signal_chwin']-1):idx+1], # not used (yet?)
                                 T['MACD']['zeroweight'], T['MACD']['histoweight'], T['MACD']['comboweight'], impact_counter)
         lastpower = detect_impact(impact_counter, power, lastpower, 'MACD')

         power += VWAP_calcpower(Data.Close[idx-(T['VWAP']['chwin']):idx], T['VWAP']['vwap'][idx-(T['VWAP']['chwin']-1):idx+1],
                                 T['VWAP']['expfac'], T['VWAP']['weight'])  # --> vwap misuse?
         lastpower = detect_impact(impact_counter, power, lastpower, 'VWAP')

         power += FIBO_calcpower(Data.Close[idx-(T['FIBO']['chwin']):idx], T['DIR']['dir'][idx], T['FIBO'][2][idx], T['FIBO'][4][idx],  #(!)[docs/fibo_misuse_note.txt]
                                      T['FIBO'][6][idx], T['FIBO'][8][idx], T['FIBO']['weight'])
         lastpower = detect_impact(impact_counter, power, lastpower, 'FIBO')

         power += CAMA_calcpower(Data.Close[idx-1], T['CAMA']['R4'][idx], T['CAMA']['R3'][idx], T['CAMA']['S3'][idx],
                                 T['CAMA']['S4'][idx], T['CAMA']['3weight'], T['CAMA']['4weight'])
         lastpower = detect_impact(impact_counter, power, lastpower, 'CAMA')

         power += RSI_calcpower(T['RSI']['rsi'][idx-(T['RSI']['chwin']-1):idx+1], T['RSI']['low'],
                                T['RSI']['high'], T['RSI']['chval_treshold'], T['RSI']['weight'], impact_counter)
         lastpower = detect_impact(impact_counter, power, lastpower, 'RSI')

         power += CCI_calcpower(T['CCI']['cci'][idx-(T['CCI']['chwin']-1):idx+1], T['CCI']['low'],
                                T['CCI']['high'], T['CCI']['chval_treshold'], T['CCI']['weight'], impact_counter)
         lastpower = detect_impact(impact_counter, power, lastpower, 'CCI')

         power += BB_outer_touch_calcpower(T['BB']['low'][idx-(T['BB']['chwin-out']-1):idx+1], T['BB']['mid'][idx-(T['BB']['chwin-out']-1):idx+1],
                                T['BB']['high'][idx-(T['BB']['chwin-out']-1):idx+1], Data.High[idx-(T['BB']['chwin-out']):idx], 
                                Data.Low[idx-(T['BB']['chwin-out']):idx], T['DIR']['dir'][idx], T['BB']['weight-out'])
         lastpower = detect_impact(impact_counter, power, lastpower, 'BB-out')
         # power *= BB_trend_calcpower(power, T['BB']['mid'][idx-(T['BB']['chwin-trend']-1):idx+1], 
         #                             T['BB']['width'][idx-(T['BB']['chwin-trend']-1):idx+1], T['BB']['expfac'], T['BB']['weight-trend'])
         # lastpower = detect_impact(impact_counter, power, lastpower, 'BB-trend')

         # power *= VOL_calcpower(T['VOL']['volume'][idx-(T['VOL']['chwin']):idx], T['VOL']['mdfpwi'],
         #                        T['VOL']['max_impact_zscore'], T['VOL']['weight'], timestamps[idx-1], VMMTs, clims)
         # lastpower = detect_impact(impact_counter, power, lastpower, 'VOL')

         # power *= ADX_calcpower(power, T['ADX']['adx'][idx-(T['ADX']['chwin']-1):idx+1], T['ADX']['DM+'][idx], T['ADX']['DM-'][idx],
         #                        T['ADX']['treshold'], T['ADX']['abs-weight'], T['ADX']['dyn-weight'], impact_counter)
         # lastpower = detect_impact(impact_counter, power, lastpower, 'ADX')

         # (good old cama version)[backups/good_old_cama_calcpower_version_call.py]

         # power *= GAP_calcpower(power, T['DIR']['dir'][idx], T['GAP']['+'][idx], T['GAP']['-'][idx],
         #                         T['GAP']['accuracy'], T['GAP']['weight'], last[idx], Data.Close[idx-1] #, T['GAP']['swingdist']
         # )
         # lastpower = detect_impact(impact_counter, power, lastpower, 'GAP')

         # power *= PEAK_calcpower(power, T['DIR']['dir'][idx], T['PEAK']['+'][idx], T['PEAK']['-'][idx],
         #                         T['PEAK']['accuracy'], T['PEAK']['weight'], last[idx], Data.Close[idx-1] #, T['PEAK']['swingdist']
         # )
         # lastpower = detect_impact(impact_counter, power, lastpower, 'PEAK')


         # power *= ATR_calcpower(T['ATR']['atr'][:idx+1], T['ATR']['mincalcwin'], T['ATR']['chwin'], T['ATR']['win'], 
         #                        T['ATR']['abs-weight'], T['ATR']['dyn-weight'], impact_counter)
         # lastpower = detect_impact(impact_counter, power, lastpower, 'ATR')

         # print('_______________________________')
      # print(power)
      powers.append(power)
   

   #(code: powers batchwork)[backups/powers_batchwork.py]


   powers = helpers.trans_list_to_BT_array(powers, 'powers')
   return powers

