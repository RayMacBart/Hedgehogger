# OLD VERSION (WITH A DIFFERENTIATION FROM REVERSAL CONFIRMATION BY CANDLE AMOUNT SINCE LAST SWING... NOT CONVINCING):
def PEAK_calcpower(pow, dir, uppeak, downpeak, acc, weight, last, close_val, swingdist):
   factor = 1
   if ((pow < 0 and dir[-1] < 0 and dir[-swingdist] > 0 and  # "dir[-swingdist]" implements distance of last swing
        # BELOW YOU MUST ADD THE PEAK VAL TO THE LAST SWINGS VAL!!!!
        (last - (downpeak - downpeak*(acc/200)) <= close_val <= (last - (downpeak + downpeak*(acc/200))))) or

        (pow > 0 and dir[-1] > 0 and dir[-swingdist] < 0 and 
         (last + (uppeak - uppeak*(acc/200)) <= last <= (last + (uppeak + uppeak*(acc/200)))))):
      factor += weight/5
   elif ((pow < 0 and all(d < 0 for d in dir[-swingdist:]) and # "after more than 'swingdist' candles into same dir"
          # BELOW YOU MUST SUBTRACT THE PEAK VAL TO THE LAST SWINGS VAL!!!!
         (downpeak - downpeak*(0.25/acc) <= (last - close_val) <= downpeak + downpeak*(0.25/acc))) or
         (pow > 0 and all(d > 0 for d in dir[-swingdist:]) and 
          (uppeak - uppeak*(0.25/acc) <= (close_val - last) <= uppeak + uppeak*(0.25/acc)))):
      factor -= weight/5
   return factor