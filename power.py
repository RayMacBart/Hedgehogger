import helpers
from helpers import is_rising_above as rises
from helpers import is_falling_below as falls


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


def PEAK_calcpower(pow, dir, uppeak, downpeak, acc, weight, last):
   factor = 1
   if ((pow < 0 and dir[-1] < 0 and dir[-3] > 0 and  # "dir[-3]" because: swing must have been recently
        (uppeak - uppeak*(acc/200) <= last <= uppeak + uppeak*(acc/200))) or
       (pow > 0 and dir[-1] > 0 and dir[-3] < 0 and 
        (downpeak - downpeak*(acc/200) <= last <= downpeak + downpeak*(acc/200)))):
         factor += weight/5
   # implement power minimizing factors for nearing peaks (after more than 3 candles into same dir).
   return factor



def powers(Close, T, last):
   powers = []
   for idx in range(len(Close)):
      power = 0
      # if using Close for calculation, don't forget to use -1 or lower index than current.
      if idx > 15:
         power += MACD_calcpower(T['MACD']['macd'][idx-4:idx+1], T['MACD']['histo'][idx-4:idx+1], T['MACD']['signal'][idx-4:idx+1], 
                                 T['MACD']['zeroweight'], T['MACD']['histoweight'])
         power += VWAP_calcpower(Close[idx-1], T['VWAP']['vwap'][idx-4:idx+1], T['VWAP']['weight'])  # --> vwap misuse?
         # I 'misuse' the fibonacci points in a unconventional way as breakthrough indicator. 
         power += FIBO_calcpower(Close[idx-5:idx], T['DIR'][idx], T['FIBO'][2][idx], T['FIBO'][4][idx],
                                      T['FIBO'][6][idx], T['FIBO'][8][idx], T['FIBO']['weight'])
         #RSI
         #CCI: over 100 buy signal, under -100 sell signal
         # IDEA for RSI and CCI: use their value as direct relational influence of weight (RSI inverted)

         # use VOL risings and falls also as power factor, but adjust them for high traffic periods 
         # by analyzing historical data of multiple past days
         # idea for ADX: also calc after VOL but before BB as confirming factor -
         # but only do this if (power<0 and DM- > DM+ ) or (power>0 and DM+ > DM- ) --> for verification.
         # - use BB outer bands like camas (!) ( --> resistance/support focusses more on absolute values)
         # place BB outerband calc after ADX and before CAMA

         power *= CAMA_calcpower(power, Close[idx-1], T['CAMA']['R4'][idx], T['CAMA']['R3'][idx], T['CAMA']['S3'][idx],
                                 T['CAMA']['S4'][idx], T['CAMA']['3weight'], T['CAMA']['4weight'])
         power *= PEAK_calcpower(power, T['DIR'][idx-2:idx+1], T['PEAK']['+'], T['PEAK']['-'],
                                 T['PEAK']['accuracy'], T['PEAK']['weight'], last)
      else:
         powers.append(0)
   powers = helpers.trans_list_to_BT_array(powers, 'powers')
   return powers

