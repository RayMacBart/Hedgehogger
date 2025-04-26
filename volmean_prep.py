import numpy as np
import pandas as pd
import sys
import os
import helpers
from DST_timehelper import get_DST_switch_startdays as gsd
from copy import deepcopy



def get_daytime_minute_list(clims):
   print('clims:', clims)
   assert 1440 % clims == 0, "clims must be a valid divisor of 1440 (minutes in a day)."
   return [ [] for m in range(0, 1440//clims) ]


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
   return [ (lambda prior, current: (current/(prior/100)-100) if not (np.isnan(current) or np.isnan(prior)) else 0)\
           (vmmts[(m-1) if (m > 0) else len(vmmts)-1], vmmts[m]) for m in range(len(vmmts)) ]


def get_volmean_movetimes(asset, clims): # clims = candle length in minutes
   candlesize = f"M{clims}" if clims != 60 else "H1"
   # the DateFrame used for this volume mean calculation has 10x more rows than the df used in __main__
   try:
      file_path = os.path.join("data", f"{asset}_{candlesize}.csv") # full data with 100k rows
      if not os.path.exists(file_path):
         raise FileNotFoundError(f"File not found (in mean_volume_moves): {file_path}")
      
      df = pd.read_csv(file_path, sep="\t", parse_dates=['Timestamp'], index_col='Timestamp')
      print("Data for volume mean calc successfully loaded!")
   except Exception as e:
      print(e)
   # df = df.map(helpers.remove_nocomma_anomaly)   --> not needed here

   df['Volume'] = helpers.adjust_volume_data(df['Volume']).set_axis(df.index)

   dfrows = df.itertuples()

   timetemplate = get_daytime_minute_list(clims)
   wintervols, transvols, summervols = fill_appropriate_vols(dfrows, timetemplate, clims)
   winterdaymeans, transdaymeans, summerdaymeans = map(reduce2day_means, [wintervols, transvols, summervols])
   wintervmmts, transvmmts, summervmmts = map(change_to_diffs2prior, [winterdaymeans, transdaymeans, summerdaymeans])
   volmean_datadict = {'winter': wintervmmts, 'trans': transvmmts, 'summer': summervmmts}
   return pd.DataFrame.from_dict(volmean_datadict)


if __name__ == '__main__':
   asset = sys.argv[1]
   volmean_df = get_volmean_movetimes(asset, int(sys.argv[2]))
   candle = f'M{sys.argv[2]}' if sys.argv[2] != 60 else 'H1'
   volmean_df.to_csv(f'.\\volmean_data\\volmean_{asset}_{candle}.csv', sep='\t')



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
   