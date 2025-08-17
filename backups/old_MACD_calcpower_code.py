   if rises(macd[-macd_chwin:], 0):
      shift += zeroweight
      impact_counter['MACD-zeroX'] += 1
   elif falls(macd[-macd_chwin:], 0):
      shift -= zeroweight
      impact_counter['MACD-zeroX'] += 1
   if rises(histo[-histo_chwin:], 0):
      shift += histoweight
      impact_counter['MACD-sigX'] += 1
   elif falls(histo[-histo_chwin:], 0):
      shift -= histoweight
      impact_counter['MACD-sigX'] += 1


   # following would be a version imitating chwin == 2:
   if macd[-2] < 0 and macd[-1] >= 0:
      shift += zeroweight
      impact_counter['MACD-zeroX'] += 1
   elif macd[-2] >= 0 and macd[-1] < 0:
      shift -= zeroweight
      impact_counter['MACD-zeroX'] += 1
   if histo[-2] < 0 and histo[-1] >= 0:
      shift += histoweight
      impact_counter['MACD-sigX'] += 1
   elif histo[-2] >= 0 and histo[-1] < 0:
      shift -= histoweight
      impact_counter['MACD-sigX'] += 1
   if macd[-2] < macd[-1] and histo[-2] < histo[-1]:
      shift += comboweight
      impact_counter['MACD-combo'] += 1
   elif macd[-2] > macd[-1] and histo[-2] > histo[-1]:
      shift -= comboweight
      impact_counter['MACD-combo'] += 1