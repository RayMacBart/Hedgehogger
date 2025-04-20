import numpy as np
from DST_timehelper import get_DST_switch_startdays as gsd
from copy import deepcopy
from itertools import chain



def get_daytime_minute_dict(clims):
   assert 1440 % clims == 0, "clims must be a valid divisor of 1440 (minutes in a day)."
   return [ [] for m in range(0, 1440/clims) ]


def fill_appropriate_vols(dfrows, timetemplate, clims):
   '''fills the times with every occuring volume on all days, splitted up by filling each dict 
   only with data from the associated periods'''
   wintervols = deepcopy(timetemplate)
   transvols = deepcopy(timetemplate)
   summervols = deepcopy(timetemplate)
   for row in dfrows:
      if (((row.Index.month <= 3) and (row.Index.day < gsd(row.Index.year)[0])) or 
          ((row.Index.month >= 11) and (row.Index.day >= gsd(row.Index.year)[3]))):
         wintervols[(row.Index.hour*60+row.Index.minute)//clims].append(row.Volume)
      elif (((row.Index.month == 3) and (gsd(row.Index.year)[0] <= row.Index.day < gsd(row.Index.year)[1])) or
            (((row.Index.month == 10) and (gsd(row.Index.year)[2] <= row.Index.day)) or
             ((row.Index.month == 11) and (row.Index.day < gsd(row.Index.year)[3])))):
         transvols[(row.Index.hour*60+row.Index.minute)//clims].append(row.Volume)
      elif (((row.Index.month == 3) and (row.Index.day >= gsd(row.Index.year)[1])) or
         ((row.Index.month == 10) and (row.Index.day < gsd(row.Index.year)[2])) or
         (3 < row.Index.month < 10)):
         summervols[(row.Index.hour*60+row.Index.minute)//clims].append(row.Volume)
   return wintervols, transvols, summervols


def reduce2day_means(VT): # Volumedata Timelist
   return [ np.nan if not VT[m] else np.nanmean(VT[m]) for m in range(len(VT)) ]


def change_to_diffs2prior(vmmts):
   return [ (lambda prior, current: current/(prior/100)-100)(vmmts[(m-1) if (m > 0) else len(vmmts)-1], vmmts[m]) for m in range(len(vmmts)) ]


def get_volmean_movetimes(dfrows, clims): # clims = candle length in minutes
   timetemplate = get_daytime_minute_dict(clims)
   wintervols, transvols, summervols = fill_appropriate_vols(dfrows, timetemplate, clims)
   winterdaymeans, transdaymeans, summerdaymeans = map(reduce2day_means, [wintervols, transvols, summervols])
   volmean = np.nanmean(chain(winterdaymeans, transdaymeans, summerdaymeans))
   wintervmmts, transvmmts, summervmmts = map(change_to_diffs2prior, [winterdaymeans, transdaymeans, summerdaymeans])
   return {'winter': wintervmmts, 'trans': transvmmts, 'summer': summervmmts, 'volmean': volmean}




# hourly_list = {}
# hourly_averages = {}
# hourly_maxs = {}
# hourly_mins = {}
# for h in range(24):
#    hourly_list[h] = []

# for h in range(24):
#    for m in range(0,60,5):
#       hourly_list[h].append(time_mean_dict[h][m])
# for h in hourly_list:
#    hourly_averages[h] = np.mean(hourly_list[h])
   # hourly_maxs[h] = max(hourly_list[h])
   # hourly_mins[h] = min(hourly_list[h])

# for h in range(24):
#    print('_____________________')
#    print('')
#    print('HOUR:', h)
   # for m in range(0,60,5):
   #    print(f'   min {m}:', time_mean_dict[h][m])
   # print('AV:', hourly_averages[h])
   # print('MAX:', hourly_maxs[h])
   # print('MIN:', hourly_mins[h])

# overall_av = np.mean(list(hourly_averages.values()))
# print('overall average:', overall_av)
   