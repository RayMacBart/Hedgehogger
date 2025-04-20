import helpers
from moves import is_rising_above as rises
from moves import is_falling_below as falls
from DST_timehelper import get_volume_peak_defusing_factor


def MACD_calcpower(macd, histo, 
                   # signal,  #--> not used (yet?) 
                   zeroweight, histoweight):
   shift = 0
   if rises(macd, 0):
      shift += zeroweight
   elif falls(macd, 0):
      shift -= zeroweight
   if rises(histo, 0):
      shift += histoweight
   elif falls(histo, 0):
      shift -= histoweight
   return shift


def VWAP_calcpower(close_val, vwap, weight):
   shift = 0
   if falls(vwap, close_val):
      shift += weight
   elif rises(vwap, close_val):
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


def RSI_calcpower(rsi, low, high, weight):
   shift = 0
   # static absolute impacts:
   if rsi > high: 
      shift -= weight
   elif rsi < low:
      shift += weight
   # dynamic movement impacts:
   if falls(rsi) and (rsi > (low + (50-low)/2)):
      shift -= weight
   elif rises(rsi) and (rsi < (50 + (high-50)/2)):
      shift += weight
   return shift


def CCI_calcpower(cci, low, high, weight):
   # static absolute impacts:
   if cci > high: 
      shift += weight
   elif cci < low:
      shift -= weight
   # dynamic movement impacts:
   if falls(cci) and (cci < low/2):
      shift -= weight
   elif rises(cci) and (cci > high/2):
      shift += weight
   return shift


def VOL_down_calcpower(vols, weight, mtcp):
   shift = 0
   if falls(vols, vols[0]-(vols[0]*(mtcp/100))):
      shift -= weight
   return shift


def VOL_up_calcpower(vols, weight, mtcp, TS, VMMTs, clims):
   voldiff = vols[-1]/(vols[0]/100)-100
   factor = 1
   PDFM = get_volume_peak_defusing_factor(voldiff, len(vols), TS, VMMTs, clims)
   # --> here I would react upon this Procentual Deviation From Mean


   # vpdf = get_volume_peak_defusing_factor(TS)
   # if rises(vols, vols[0]+(vols[0]*(mtcp/100))):
   #    grown_to_percentage = vols[-1]/(vols[0]/100)
   #    factor *= ((grown_to_percentage/100)/5)*weight*vpdf
   # return factor


def CAMA_calcpower(pow, close_val, R4, R3, S3, S4, w3, w4):
   factor = 1
   if (pow < 0 and close_val > R4) or (pow > 0 and close_val < S4):
      factor += w4/5
   elif (pow < 0 and close_val > R3) or (pow > 0 and close_val < S3):
      factor += w3/5
   # maybe it's better to remove the following, since 
   # camas could also act as confirmer of breakouts -
   # in this case, also pow check can be removed here.
   elif (pow < 0 and close_val < S4) or (pow > 0 and close_val > R4):
      factor -= w4/5
   elif (pow < 0 and close_val < S3) or (pow > 0 and close_val > R3):
      factor -= w3/5
   return factor


def PEAK_calcpower(pow, dir, uppeak, downpeak, acc, weight, last, close_val, swingdist):
   factor = 1
   if ((pow < 0 and dir[-1] < 0 and dir[-swingdist] > 0 and  # "dir[-swingdist]" implements distance of last swing
        (uppeak - uppeak*(acc/200) <= last <= uppeak + uppeak*(acc/200))) or
        (pow > 0 and dir[-1] > 0 and dir[-swingdist] < 0 and 
         (downpeak - downpeak*(acc/200) <= last <= downpeak + downpeak*(acc/200)))):
      factor += weight/5
   elif ((pow < 0 and all(d < 0 for d in dir[-swingdist:]) and # "after more than 'swingdist' candles into same dir"
         (downpeak - downpeak*(acc/200) <= (last - close_val) <= downpeak + downpeak*(acc/200))) or
         (pow > 0 and all(d > 0 for d in dir[-swingdist:]) and 
          (uppeak - uppeak*(acc/200) <= (close_val - last) <= uppeak + uppeak*(acc/200)))):
      factor -= weight/5
   return factor



def powers(Close, T, last, timestamps, VMMTs, clims):
   powers = []
   for idx in range(len(Close)):
      power = 0
      # if using Close for calculation, don't forget to use -1 or lower index than current.
      if idx > 15:
         power += MACD_calcpower(T['MACD']['macd'][idx-(T['MACD']['macd_chwin']-1):idx+1], 
                                 T['MACD']['histo'][idx-(T['MACD']['histo_chwin']-1):idx+1], 
                                 # T['MACD']['signal'][idx-(T['MACD']['signal_chwin']-1):idx+1], # not used (yet?)
                                 T['MACD']['zeroweight'], T['MACD']['histoweight'])
         power += VWAP_calcpower(Close[idx-1], T['VWAP']['vwap'][idx-(T['VWAP']['chwin']-1):idx+1], T['VWAP']['weight'])  # --> vwap misuse?
         # I 'misuse' the fibonacci points in a unconventional way as breakthrough indicator. 
         power += FIBO_calcpower(Close[idx-(T['FIBO']['chwin']):idx], T['DIR'][idx], T['FIBO'][2][idx], T['FIBO'][4][idx],
                                      T['FIBO'][6][idx], T['FIBO'][8][idx], T['FIBO']['weight'])
         power += RSI_calcpower(T['RSI']['rsi'][idx-(T['RSI']['chwin']-1):idx+1], T['RSI']['low'],
                                T['RSI']['high'], T['RSI']['weight'])
         power += CCI_calcpower(T['CCI']['cci'][idx-(T['CCI']['chwin']-1):idx+1], T['CCI']['low'],
                                T['CCI']['high'], T['CCI']['weight'])
         power += VOL_down_calcpower(T['VOL']['volume'][idx-(T['VOL']['chwin']):idx], T['VOL']['downweight'], T['VOL']['triggerminchange%'])
         power *= VOL_up_calcpower(T['VOL']['volume'][idx-(T['VOL']['chwin']):idx], T['VOL']['upweight'], 
                                T['VOL']['triggerminchange%'], timestamps[idx-1], VMMTs, clims)
         # VOL: analyze historical data of multiple past days and adjust DST_timehelper.get_volume_peak_defusing_factor()
         # idea for ADX: also calc after VOL but before BB as confirming factor -
         # but only do this if (power<0 and DM- > DM+ ) or (power>0 and DM+ > DM- ) --> for verification.
         # - use BB outer bands like camas (!) ( --> resistance/support focusses more on absolute values)
         # place BB outerband calc after ADX and before CAMA

         power *= CAMA_calcpower(power, Close[idx-1], T['CAMA']['R4'][idx], T['CAMA']['R3'][idx], T['CAMA']['S3'][idx],
                                 T['CAMA']['S4'][idx], T['CAMA']['3weight'], T['CAMA']['4weight'])
         power *= PEAK_calcpower(power, T['DIR'][idx-(T['PEAK']['swingdist']-1):idx+1], T['PEAK']['+'], T['PEAK']['-'],
                                 T['PEAK']['accuracy'], T['PEAK']['weight'], last, Close[idx-1], T['PEAK']['swingdist'])
      else:
         powers.append(0)
   powers = helpers.trans_list_to_BT_array(powers, 'powers')
   return powers

