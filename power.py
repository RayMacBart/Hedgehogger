import helpers


def MACD_calcpower(macd, histo, signal, zeroweight, histoweight):
   shift = 0
   if macd[-1] >= 0 and all(m < 0 for m in macd[-4:-1]):
      shift += zeroweight
   elif macd[-1] <= 0 and all(m > 0 for m in macd[-4:-1]):
      shift -= zeroweight
   if histo[-1] >= 0 and all(h < 0 for h in histo[-4:-1]):
      shift += histoweight
   elif histo[-1] <= 0 and all(h > 0 for h in histo[-4:-1]):
      shift -= histoweight
   return shift


def VWAP_calcpower(Close, vwap, weight):
   shift = 0
   if Close > vwap:
      shift += weight
   elif Close < vwap:
      shift -= weight
   return shift


def FIBO_calcpower(Close, dir, f2, f4, f6, f8, weight):
   shift = 0
   if dir < 0:
      if Close <= f8:
         shift -= weight*1.3
      elif Close <= f6:
         shift -= weight*1.1
      elif Close <= f4:
         shift -= weight*0.9
      elif Close <= f2:
         shift -= weight*0.7
   elif dir > 0:
      if Close >= f8:
         shift += weight*1.3
      elif Close >= f6:
         shift += weight*1.1
      elif Close >= f4:
         shift += weight*0.9
      elif Close >= f2:
         shift += weight*0.7
   return shift


def CAMA_calcpower(fibo, R4, R3, S3, S4, w3, w4):
   pass


def powers(Close, T):
   powers = []
   for idx in range(len(Close)):
      power = 0
      # if using Close for calculation, don't forget to use -1 or lower index than current.
      if idx > 15:
         power += MACD_calcpower(T['MACD']['macd'][idx-4:idx], T['MACD']['histo'][idx-4:idx], T['MACD']['signal'][idx-4:idx], 
                                 T['MACD']['zeroweight'], T['MACD']['histoweight'])
         power += VWAP_calcpower(Close[idx-1], T['VWAP']['vwap'][idx], T['VWAP']['weight'])  # --> vwap misuse?
         # I 'misuse' the fibonacci points in a unconventional way. 
         power += FIBO_calcpower(Close[idx-1], T['DIR'][idx], T['FIBO'][2][idx], T['FIBO'][4][idx],
                                      T['FIBO'][6][idx], T['FIBO'][8][idx], T['FIBO']['weight'])
         #ADX
         #BB
         #RSI
         #CCI: over 100 buy signal, under -100 sell signal
         #GAP ? Inversion to most occuring swings?

         # power += fibo_effect  # ( = for cama idea 2 )
         power += CAMA_calcpower(power, T['CAMA']['R4'][idx], T['CAMA']['R3'][idx], T['CAMA']['S3'][idx],
                                 T['CAMA']['S4'][idx], T['CAMA']['3weight'], T['CAMA']['4weight'])
         # cama idea1: Using 'power', determine if or how strong (inverse relation) the CAMAs shall be applied (and how and why?).
         # cama idea2: if FIBO is broke through, it indicates trend movement that 'knocks out'/disables CAMA!
         # idea for non-directional indicators like adx: calc them after all others and 
         # just strengthen the already existing pos/neg value of power (pass power as arg)
      else:
         powers.append(0)
   powers = helpers.trans_list_to_BT_array(powers, 'powers')
   return powers

