class RanOutDSTDataError(Exception):
   """Custom exception to handle cases where DST data runs out."""
   pass


def get_DST_switch_startdays(year):
   """the days in the list are starting date days of the periods in following chronological order (with indexes):
   [0] = transition in spring, [1] = summer, [2] = transition in autumn, [3] = winter.
   Note that the months of these dates never change over the years
   (equivalent list with months always would be: [3,3,10,11])"""
   if year == 2020:
      return [8,29,25,1]
   elif year == 2021:
      return [14,28,31,7]
   elif year == 2022:
      return [13,27,30,6]
   elif year == 2023:
      return [12,26,29,5]
   elif year == 2024:
      return [10,31,27,3]
   elif year == 2025:
      return [9,30,26,2]
   elif year == 2026:
      return [8,29,25,1]
   elif year == 2027:
      return [14,28,31,7]
   elif year == 2028:
      return [12,26,29,5]
   elif year == 2029:
      return [11,25,28,4]
   elif year == 2030:
      return [10,31,27,3]
   elif year == 2031:
      return [9,30,26,2]
   elif year == 2032:
      return [14,28,31,7]
   elif year == 2033:
      return [13,27,30,6]
   elif year == 2034:
      return [12,26,24,1]
   elif year == 2035:
      return [11,25,28,4]
   elif year == 2036:
      return[9,30,26,2]
   elif year == 2037:
      return[8,29,25,1]
   elif year == 2038:
      print('WARNING! PLEASE IMPLEMENT MORE DST SWITCH DAY DATA @ FUNCTION "get_DST_switch_startdays" BEFORE 2041!')
      return[14,28,31,7]
   elif year == 2039:
      print('WARNING! PLEASE IMPLEMENT MORE DST SWITCH DAY DATA @ FUNCTION "get_DST_switch_startdays" BEFORE 2041!')
      return[13,27,30,6]
   elif year == 2040:
      print('URGENT WARNING! PLEASE IMPLEMENT MORE DST SWITCH DAY DATA @ FUNCTION "get_DST_switch_startdays" BEFORE 2041!')
      return[11,25,28,4]
   else:
      raise RanOutDSTDataError('RAN OUT DST SWITCH DATES! PLEASE IMPLEMENT MORE DST SWITCH DAY DATA @ FUNCTION "get_DST_switch_startdays"!')



def calc_pdfm(meanlist, voldiff, span, TS, clims):
   meanidx = None
   for i in meanlist:
      if (i*clims <= TS.hour*60+TS.minute < (i+1)*clims):
         meanidx = i
   first_diffmean = meanlist[(meanidx-span)+1] # works also over list end/begin
   # +1 because otherwise it would result in 1 more than span included item!
   voldiffmean = meanlist[meanidx]/(first_diffmean/100)-100
   return voldiff - voldiffmean


def get_procentual_deviation_from_mean(voldiff, span, TS, VMMTs, clims):
   PDFM = 0 # Procentual Deviation From Mean
   gsd = get_DST_switch_startdays
   if (((TS.month <= 3) and (TS.day < gsd(TS.year)[0])) or 
      ((TS.month >= 11) and (TS.day >= gsd(TS.year)[3]))):
      PDFM = calc_pdfm(VMMTs['winter'], voldiff, span, TS, clims)
   elif (((TS.month == 3) and (gsd(TS.year)[0] <= TS.day < gsd(TS.year)[1])) or
         (((TS.month == 10) and (gsd(TS.year)[2] <= TS.day)) or
            ((TS.month == 11) and (TS.day < gsd(TS.year)[3])))):
      PDFM = calc_pdfm(VMMTs['trans'], voldiff, span, TS, clims)
   elif (((TS.month == 3) and (TS.day >= gsd(TS.year)[1])) or
         ((TS.month == 10) and (TS.day < gsd(TS.year)[2])) or
         (3 < TS.month < 10)):
      PDFM = calc_pdfm(VMMTs['summer'], voldiff, span, TS, clims)
   return PDFM


   # old idea with surpass treshold:
   # if (((TS.month <= 3) and (TS.day < gsd(TS.year)[0])) or 
   #    ((TS.month >= 11) and (TS.day >= gsd(TS.year)[3]))):
   #    # liquidity peak in winter time is 15:00 UTC
   #    if (TS.hour in [14,15]) and (25 <= TS.minute < 35):
   #       vpdf = 0.9
   #    elif (((TS.hour == 14) and (35 <= TS.minute < 45)) or 
   #          ((TS.hour == 15) and (15 <= TS.minute < 25))):
   #       vpdf = 0.8
   #    elif (((TS.hour == 14) and (45 <= TS.minute < 55)) or 
   #          ((TS.hour == 15) and (5 <= TS.minute < 15))):
   #       vpdf = 0.7
   #    elif ((TS.hour == 14) and (55 <= TS.minute) or 
   #          ((TS.hour == 15) and (TS.minute < 5))):
   #       vpdf = 0.6
   # elif (((TS.month == 3) and (gsd(TS.year)[0] <= TS.day < gsd(TS.year)[1])) or
   #       (((TS.month == 10) and (gsd(TS.year)[2] <= TS.day)) or
   #          ((TS.month == 11) and (TS.day < gsd(TS.year)[3])))):
   #    # liquidity peak in transition periods is 14:30 UTC
   #    if (((TS.hour == 13) and (55 <= TS.minute)) or
   #          ((TS.hour == 14) and ((TS.minute < 5) or (55 <= TS.minute))) or
   #          ((TS.hour == 15) and (TS.minute < 5))):
   #       vpdf = 0.9
   #    elif ((TS.hour == 14) and ((5 <= TS.minute < 15) or (45 <= TS.minute < 55))):
   #       vpdf = 0.8
   #    elif ((TS.hour == 14) and ((15 <= TS.minute < 25) or (35 <= TS.minute < 45))):
   #       vpdf = 0.7
   #    elif ((TS.hour == 14) and (25 <= TS.minute < 35)):
   #       vpdf = 0.6
   # elif (((TS.month == 3) and (TS.day >= gsd(TS.year)[1])) or
   #       ((TS.month == 10) and (TS.day < gsd(TS.year)[2])) or
   #       (3 < TS.month < 10)):
   #    # liquidity peak in summer time is 14:00 UTC
   #    if (TS.hour in [13,14]) and (25 <= TS.minute < 35):
   #       vpdf = 0.9
   #    elif (((TS.hour == 13) and (35 <= TS.minute < 45)) or 
   #          ((TS.hour == 14) and (15 <= TS.minute < 25))):
   #       vpdf = 0.8
   #    elif (((TS.hour == 13) and (45 <= TS.minute < 55)) or 
   #          ((TS.hour == 14) and (5 <= TS.minute < 15))):
   #       vpdf = 0.7
   #    elif ((TS.hour == 13) and (55 <= TS.minute) or 
   #          ((TS.hour == 14) and (TS.minute < 5))):
   #       vpdf = 0.6
   # return vpdf