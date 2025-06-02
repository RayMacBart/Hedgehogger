from random import randrange
from random import choice
import os
import numpy as np
import pandas as pd
import helpers
from volfuncs import adjust_volume_data
from DST_timehelper import get_time_period


def get_candlesize_distribution_ranges(df, pricespan):
   candle_sizeclass_size = len(df) // 20
   csl = [abs(row['Close']-row['Open']) for row in df.itertuples()]  # 'csl' = candle size list
   sidicos = [0 for i in range(20)]  # size distribution counts (helper).  smallest = 0, biggest = 19
   sidiras = [[] for i in range(20)]  # size distribution ranges.  smallest = 0, biggest = 19
   cursidi = 0  # current size distribution
   for p in range(0, pricespan*100000+1):
      realval = p/100000  # = size in pipette dimension
      if csl:
         while min(csl) == realval:  
            if sidicos[cursidi] <= candle_sizeclass_size:
               sidicos[cursidi] += 1
               csl.remove(min(csl))
               if not csl:
                  break
            else:
               if cursidi == 0:
                  sidiras[0].append(0)
               sidiras[cursidi].append(realval)
               cursidi += 1
               if cursidi > 19:
                  break
               sidiras[cursidi].append(realval)
      else:
         break
   for idx, val in sidicos.enumerate():
      if val != candle_sizeclass_size:
         print(f'WARNING! Size Distribution Anomaly dedected @ "get_size_distributions:"\n \
               Distribution {idx} has {val} counts instead of {candle_sizeclass_size}!')
   # REMOVE POSSIBLE GAPS INSIDE SIDIRAS: IF END OF ONE SIZECLASS ISN'T START OF THE OTHER - CALC MID AND SET BOTH TO THIS SAME!
   return sidiras



def get_shadowsize_distribution_ranges(df, sidiras):
   shadow_vals = {'bullups': {'means': [], 'stds': []}, 'bulldowns': {'means': [], 'stds': []},
                  'bearups': {'means': [], 'stds': []}, 'beardowns': {'means': [], 'stds': []}}
   bullup_shadows = [[] for i in range(20)]
   bulldown_shadows = [[] for i in range(20)]
   bearup_shadows = [[] for i in range(20)]
   beardown_shadows = [[] for i in range(20)]
   for row in df.itertuples:
      bullish = True if row.Close - row.Open >= 0 else False  # candlesizes of 0 ("Dojis") will be in bullish records
      for idx in range(20):
         if abs(row.Close - row.Open)*100000 in range(sidiras[idx][0]*100000, sidiras[idx][1]*100000):
            if bullish:
               bullup_shadows[idx].append(row.High - row.Close)
               bulldown_shadows[idx].append(row.Open - row.Low)
            else:
               bearup_shadows[idx].append(row.High - row.Open)
               beardown_shadows[idx].append(row.Close - row.Low)
            break
   for idx in range(20):
      shadow_vals['bullups']['means'].append(np.mean(bullup_shadows[idx]))
      shadow_vals['bullups']['stds'].append(np.std(bullup_shadows[idx]))
      shadow_vals['bulldowns']['means'].append(np.mean(bulldown_shadows[idx]))
      shadow_vals['bulldowns']['stds'].append(np.std(bulldown_shadows[idx]))
      shadow_vals['bearups']['means'].append(np.mean(bearup_shadows[idx]))
      shadow_vals['bearups']['stds'].append(np.std(bearup_shadows[idx]))
      shadow_vals['beardowns']['means'].append(np.mean(beardown_shadows[idx]))
      shadow_vals['beardowns']['stds'].append(np.std(beardown_shadows[idx]))
   return shadow_vals



def get_infos(asset, candlesize):
   try:
      file_path = os.path.join("data", f"{asset}_{candlesize}.csv")
      if not os.path.exists(file_path):
         raise FileNotFoundError(f"File not found: {file_path}")
      df = pd.read_csv(file_path, sep="\t", parse_dates=['Timestamp'], index_col='Timestamp')
      print("Data successfully loaded!")
   except Exception as e:
      print('Error occured during loading MAIN PRICE CHART data:\n', e)

   df['Open'] = df['Open'].apply(helpers.remove_nocomma_anomaly)
   df['High'] = df['High'].apply(helpers.remove_nocomma_anomaly)
   df['Low'] = df['Low'].apply(helpers.remove_nocomma_anomaly)
   df['Close'] = df['Close'].apply(helpers.remove_nocomma_anomaly)
   df['Volume'] = adjust_volume_data(df['Volume']).set_axis(df.index)
   pricewidths = [row.High - row.Low for row in df.itertuples()]
   maxwidth = round(max(pricewidths), 5)
   priceabsmoves = [abs(row.Close - row.Open) for row in df.itertuples()]
   maxpriceabsmove = round(max(priceabsmoves), 5)
   maxprice = round(max(list(df['High'])), 5)
   minprice = round(min(list(df['Low'])), 5)
   maxvol = round(np.max(list(df['Volume'])), 5)

   pricespan = maxprice-minprice
   
   sidiras = get_candlesize_distribution_ranges(df, pricespan)  # 'size distribution ranges'
   shadow_vals = get_shadowsize_distribution_ranges(df, sidiras)

   return {'sidiras': sidiras, 'shadow_vals': shadow_vals, 'maxwidth': maxwidth, 'maxpriceabsmove': maxpriceabsmove,
           'maxprice': maxprice, 'minprice': minprice, 'maxvol': maxvol, 'pricespan': pricespan}


def is_after_break(TS):
   start_hour = 22 if get_time_period(TS) == 'winter' else 21
   if (TS.weekday == 6 and TS.hour == start_hour and TS.minute == 0):
      return True
   return False


def get_randomized_df(df, asset, candlesize):
   rdf = df.copy()
   infos = get_infos(asset, candlesize)
   lastclose = None

   for idx, row in rdf.iterrows():
      
      if not is_after_break(idx):
         randopen = lastclose + randrange(-3, 4, 1)/100000 if lastclose else row['Open']
      else:
         randopen = lastclose + randrange(int((-infos['pricespan']/3)*100000), int((infos['pricespan']/3)*100000+1), 1)/100000 if lastclose else row['Open']

      fractional_pos = (randopen - infos['minprice'])/infos['pricespan']
      if fractional_pos < 0:
         fractional_pos = 0
      elif fractional_pos > 1:
         fractional_pos = 1

      rand_candlesize = choice(infos['sidiras'])
      randclose = randrange(int((randopen - (rand_candlesize[1]-rand_candlesize[0])*fractional_pos)*100000),
                            int((randopen + (rand_candlesize[1]-rand_candlesize[0])*abs(fractional_pos-1))*100000)+1,
                            1)/100000
      
      lastclose = randclose

      candle_animal = 'bull' if randclose >= randopen else 'bear'
      for sc_idx in range(20):  # 'sizeclass index'
         if abs(randclose-randopen)*100000 in range(infos['sidiras'][sc_idx][0]*100000, infos['sidiras'][sc_idx][1]*100000):
            upshadow_mean = infos['shadow_vals'][f'{candle_animal}ups']['means'][sc_idx]
            upshadow_std = infos['shadow_vals'][f'{candle_animal}ups']['stds'][sc_idx]
            downshadow_mean = infos['shadow_vals'][f'{candle_animal}downs']['means'][sc_idx]
            downshadow_std = infos['shadow_vals'][f'{candle_animal}downs']['stds'][sc_idx]
      rand_upshadow_size = randrange(((upshadow_mean-2*upshadow_std) if (upshadow_mean-2*upshadow_std) >= 0 else 0)*100000,
                                     (upshadow_mean+2*upshadow_std)*100000+1)/100000
      randhigh = randclose + rand_upshadow_size if candle_animal == 'bull' else randopen + rand_upshadow_size
      rand_downshadow_size = randrange(((downshadow_mean-2*downshadow_std) if (downshadow_mean-2*downshadow_std) >= 0 else 0)*100000,
                                     (downshadow_mean+2*downshadow_std)*100000+1)/100000
      randlow = randopen - rand_downshadow_size if candle_animal == 'bull' else randclose - rand_downshadow_size


      # LET MAXVOLDEV BE INFLUENCED BY CANDLESIZE SOMEHOW
      maxvoldev = row['Volume']//2 if row['Volume'] >= 2 else 1
      randvol = randrange(int(row['Volume']-maxvoldev) if row['Volume']-maxvoldev > 0 else 1,
                          int(row['Volume']+maxvoldev) if row['Volume']+maxvoldev < infos['maxvol']*1.2 else int(infos['maxvol']*1.2),
                          1)
      rdf.loc[idx, 'Open'] = randopen
      rdf.loc[idx, 'High'] = randhigh
      rdf.loc[idx, 'Low'] = randlow
      rdf.loc[idx, 'Close'] = randclose
      rdf.loc[idx, 'Volume'] = randvol

   return rdf

      