import pandas as pd
import numpy as np
from DST_timehelper import get_DST_switch_startdays as gsd

candlesize = 'M5'

df = pd.read_csv(".\data\EURUSD_"+candlesize+".csv", sep="\t", parse_dates=['Timestamp'], index_col='Timestamp')


def get_daytime_structured_dict():
   return { h: { m: [] for m in range(0,60,5)} for h in range(24) }


def fill_appropriate_vols(dfrows, timetemplate):
   '''fills the times with every occuring volume on all days, splitted up by filling each dict 
   only with data from the associated periods'''
   # wintervols = { h: { m: [row.Volume]}}

   wintervols = timetemplate.deepcopy()
   transvols = timetemplate.deepcopy()
   summervols = timetemplate.deepcopy()
   for row in dfrows:
      if (((row.Index.month <= 3) and (row.Index.day < gsd(row.Index.year)[0])) or 
          ((row.Index.month >= 11) and (row.Index.day >= gsd(row.Index.year)[3]))):
         wintervols[row.Index.hour][row.Index.minute].append(row.Volume)
      elif (((row.Index.month == 3) and (gsd(row.Index.year)[0] <= row.Index.day < gsd(row.Index.year)[1])) or
            (((row.Index.month == 10) and (gsd(row.Index.year)[2] <= row.Index.day)) or
             ((row.Index.month == 11) and (row.Index.day < gsd(row.Index.year)[3])))):
         transvols[row.Index.hour][row.Index.minute].append(row.Volume)
      elif (((row.Index.month == 3) and (row.Index.day >= gsd(row.Index.year)[1])) or
         ((row.Index.month == 10) and (row.Index.day < gsd(row.Index.year)[2])) or
         (3 < row.Index.month < 10)):
         summervols[row.Index.hour][row.Index.minute].append(row.Volume)
   return wintervols, transvols, summervols


def reduce2day_means(VT): # Volumedata Timedictionary
   return { h: { m: np.mean(VT[h][m]) for m in VT[h] } for h in VT }


def change_to_diffs2prior(dtms):
   return {h:{m:(lambda p: p[1]/(p[0]/100)-100)((dtms[(h-1 if h!=0 else 23) if m==0 else h][m-5 if m!=0 else 55], dtms[h][m])) for m in dtms[h]} for h in dtms}
# old way:
# def change_to_diffs2prior(dtms):
#    diffs2prior = {}
#    for h in range(24):
#       diffs2prior[h] = {}
#    former = dtms[23][55]
#    for h in range(24):
#       for m in range(0,60,5):
#          diffs2prior[h][m] = dtms[h][m]/(former/100)-100  #procentual difference to former
#          former = dtms[h][m]
#    return diffs2prior


def calc_daytimemeans(df):
   timetemplate = get_daytime_structured_dict()
   wintervols, transvols, summervols = fill_appropriate_vols(df.itertuples(), timetemplate)
   winterdaymeans, transdaymeans, summerdaymeans = map(reduce2day_means, [wintervols, transvols, summervols])
   winterdtms, transdtms, summerdtms = map(change_to_diffs2prior, [winterdaymeans, transdaymeans, summerdaymeans])



daytimemean_dict = calc_daytimemeans(df)




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
   