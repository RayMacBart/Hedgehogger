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


def get_full_data_infos(winter, trans, summer):
   full_data = winter + trans + summer
   return np.nanmean(full_data), np.nanstd(full_data)


def convert_daymeans2zscore_lists(winter, trans, summer, mean_all, std_all):
    zscores_winter = [((val-mean_all)/std_all) for val in winter]
    zscores_trans = [((val-mean_all)/std_all) for val in trans]
    zscores_summer = [((val-mean_all)/std_all) for val in summer]
    return zscores_winter, zscores_trans, zscores_summer


def change_to_diffs2prior(zdms):
   return [ zdms[i] - (zdms[i-1] if i > 0 else 0) for i in range(len(zdms)) ]

#(procentual old way)[backups/change_to_diffs2prior_old_procentual.py]


# def convert_infos_to_lists(length, mean_all, std_all):                         # not necessary
#    return [mean_all for i in range(length)], [std_all for i in range(length)]


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
   mean_all, std_all = get_full_data_infos(winterdaymeans, transdaymeans, summerdaymeans)
   winter_z_daymeans, trans_z_daymeans, summer_z_daymeans = convert_daymeans2zscore_lists(winterdaymeans, transdaymeans, summerdaymeans, mean_all, std_all)
   winter_z_vmmts, trans_z_vmmts, summer_z_vmmts = map(change_to_diffs2prior, [winter_z_daymeans, trans_z_daymeans, summer_z_daymeans])
   # mean_all_list, std_all_list = convert_infos_to_lists(len(timetemplate), mean_all, std_all)  # not necessary
   volmean_datadict = {'winter': winter_z_vmmts, 'trans': trans_z_vmmts, 'summer': summer_z_vmmts, 
                       'mean': mean_all, 'std': std_all}
                     #   'mean': mean_all_list, 'std': std_all_list}  # not necessary
   return pd.DataFrame.from_dict(volmean_datadict)


if __name__ == '__main__':
   asset = sys.argv[1]
   volmean_df = get_volmean_movetimes(asset, int(sys.argv[2]))
   candle = f'M{sys.argv[2]}' if sys.argv[2] != 60 else 'H1'
   volmean_df.to_csv(f'.\\volmean_data\\volmean_{asset}_{candle}.csv', sep='\t')


#(old)[backups/get_volmean_movetimes_old_code.py]

   