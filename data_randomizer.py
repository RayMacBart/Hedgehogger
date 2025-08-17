from random import randrange
from random import choice
import os
import numpy as np
import pandas as pd
import helpers
from volfuncs import adjust_volume_data
from DST_timehelper import get_time_period
import pdb


def get_candlesize_distribution_ranges(df, pricespan, SCG):
   candle_sizeclass_size = len(df) // SCG
   csl = [round(abs(row.Close-row.Open), 5) for row in df.itertuples()]  # 'csl' = candle size list
   sidicos = [0 for i in range(SCG)]  # size distribution counts (helper).  smallest = 0, biggest = SCG-1
   sidiras = [[] for i in range(SCG)]  # size distribution ranges.  smallest = 0, biggest = SCG-1
   cursidi = 0  # current size distribution
   # pdb.set_trace()
   for p in range(0, int(pricespan*100000+1)):
      realval = p/100000  # = size in pipette dimension
      if csl:
         # pdb.set_trace()
         while min(csl) == realval:  
            if sidicos[cursidi] < candle_sizeclass_size:
               # pdb.set_trace()
               sidicos[cursidi] += 1
               csl.remove(min(csl))
               if not csl:
                  sidiras[cursidi].append(realval) # => sidiras[SCG-1][1]
                  break
            else:
               if cursidi == 0:
                  sidiras[0].append(0)
               sidiras[cursidi].append(realval)
               # pdb.set_trace()
               cursidi += 1
               if cursidi > SCG-1:
                  break
               sidiras[cursidi].append(realval)
               # pdb.set_trace()
      else:
         break
   # pdb.set_trace()
   for idx, val in enumerate(sidicos):
      if val != candle_sizeclass_size:
         print(f'WARNING! Size Distribution Anomaly dedected @ "get_size_distributions:"\n \
               Distribution {idx} has {val} counts instead of {candle_sizeclass_size}!')
   for sc_idx in range(len(sidiras)):
      if sc_idx and sidiras[sc_idx-1][1] != sidiras[sc_idx][0]:
         midval = (sidiras[sc_idx-1][1] + sidiras[sc_idx][0]) / 2
         sidiras[sc_idx-1][1] = midval
         sidiras[sc_idx][0] = midval
   return sidiras



def get_shadowsize_distribution_ranges(df, SCG):
   shadow_vals = {'bullups': {'means': [], 'stds': []}, 'bulldowns': {'means': [], 'stds': []},
                  'bearups': {'means': [], 'stds': []}, 'beardowns': {'means': [], 'stds': []}}
   bullup_shadows = [[] for i in range(SCG)]
   bulldown_shadows = [[] for i in range(SCG)]
   bearup_shadows = [[] for i in range(SCG)]
   beardown_shadows = [[] for i in range(SCG)]
   

   print('ENTERING SHADOWSIZE DISTRIBUTION RANGE ASSIGNMENTS')
   datasize = len(list(df.iterrows()))
   copieddf = df.copy()
   copieddf['CS'] = abs(copieddf['Close'] - copieddf['Open'])
   sorted_copieddf = copieddf.sort_values(by='CS')

   print('sorted_copieddf:\n', sorted_copieddf.iloc[-70:])

   for idx in range(SCG):
      for row in sorted_copieddf.iloc[(datasize // SCG)*idx:(datasize // SCG)*(idx+1)].itertuples():
         if row.Close - row.Open >= 0:  # candlesizes of 0 ("Dojis") will be in bullish records
            bullup_shadows[idx].append(row.High - row.Close)
            bulldown_shadows[idx].append(row.Open - row.Low)
         else:
            bearup_shadows[idx].append(row.High - row.Open)
            beardown_shadows[idx].append(row.Close - row.Low)


   # pdb.set_trace()
   for idx in range(SCG):
      shadow_vals['bullups']['means'].append(round(np.mean(bullup_shadows[idx]), 5))
      shadow_vals['bullups']['stds'].append(round(np.std(bullup_shadows[idx]), 5))
      shadow_vals['bulldowns']['means'].append(round(np.mean(bulldown_shadows[idx]), 5))
      shadow_vals['bulldowns']['stds'].append(round(np.std(bulldown_shadows[idx]), 5))
      shadow_vals['bearups']['means'].append(round(np.mean(bearup_shadows[idx]), 5))
      shadow_vals['bearups']['stds'].append(round(np.std(bearup_shadows[idx]), 5))
      shadow_vals['beardowns']['means'].append(round(np.mean(beardown_shadows[idx]), 5))
      shadow_vals['beardowns']['stds'].append(round(np.std(beardown_shadows[idx]), 5))
   # pdb.set_trace()
   return shadow_vals



def get_infos(asset, candlesize, startpos, SCG):  # 'SCG' = Size Class Granularity
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
   initprice = df['Open'].iloc[-startpos]
   print('initprice:', initprice)
   maxprice = round(max(list(df['High'])), 5)
   minprice = round(min(list(df['Low'])), 5)
   meanprice = np.mean([row.Close for row in df.itertuples()])
   maxvol = round(np.max(list(df['Volume'])), 5)

   pricespan = maxprice-minprice
   
   sidiras = get_candlesize_distribution_ranges(df, pricespan, SCG)  # 'size distribution ranges'
   print('candlesize distributions done...')
   shadow_vals = get_shadowsize_distribution_ranges(df, SCG)

   return {'sidiras': sidiras, 'shadow_vals': shadow_vals, 'maxwidth': maxwidth, 'maxpriceabsmove': maxpriceabsmove, 'initprice': initprice,
           'maxprice': maxprice, 'minprice': minprice, 'meanprice': meanprice, 'maxvol': maxvol, 'pricespan': pricespan}


def is_after_break(TS):
   start_hour = 22 if get_time_period(TS) == 'winter' else 21
   if (TS.weekday == 6 and TS.hour == start_hour and TS.minute == 0):
      return True
   return False


def intercept_None_shadowvals(val, cs, shadow_interception_count):
   if not val:
      val = randrange(0, int((cs/2)*100000), 1)/100000
      shadow_interception_count *= 1
   # print('ATTENTION! A shadow mean- or std-value was set to another value due to being None!')
   return val, shadow_interception_count


def get_randomized_df(df, asset, candlesize, startpos):
   SCG = 1000  # Size Class Granularity: set the amount of size classes here!
   rdf = df.copy()
   infos = get_infos(asset, candlesize, startpos, SCG) 
   lastclose = None
   shadow_interception_count = 0

   for idx, row in rdf.iterrows():
      
      if not is_after_break(idx):
         randopen = lastclose + randrange(-3, 4, 1)/100000 if lastclose else row['Open']
      else:
         randopen = lastclose + randrange(int((-infos['pricespan']/3)*100000), int((infos['pricespan']/3)*100000+1), 1)/100000 if lastclose else row['Open']

      fractional_pos = (randopen - abs(infos['initprice']-(infos['pricespan']*2)))/(infos['pricespan']*4)
      if fractional_pos < 0:
         fractional_pos = 0
      elif fractional_pos > 1:
         fractional_pos = 1

      rand_candlesize_class = choice(infos['sidiras'])
      randclose = randrange(int((randopen - (rand_candlesize_class[1]+rand_candlesize_class[0])*fractional_pos)*100000),
                            int((randopen + (rand_candlesize_class[1]+rand_candlesize_class[0])*abs(fractional_pos-1))*100000)+1,
                            1)/100000
      
      rand_cs = abs(randclose-randopen)
      lastclose = randclose
      upshadow_mean = None
      upshadow_std = None
      downshadow_mean = None
      downshadow_std = None
      # sizeclass_index = None  # was used for old maxvoldev (below)

      candle_animal = 'bull' if randclose >= randopen else 'bear'
      for sc_idx in range(SCG):  # 'sizeclass index'
         if int(rand_cs*100000) in range(int(infos['sidiras'][sc_idx][0]*100000), int(infos['sidiras'][sc_idx][1]*100000)):
            # print(f'{candle_animal}ish upshadow mean & std @ sc_idx {sc_idx}:', infos['shadow_vals'][f'{candle_animal}ups']['means'][sc_idx], infos['shadow_vals'][f'{candle_animal}ups']['stds'][sc_idx])
            # print(f'{candle_animal}ish downshadow mean & std @ sc_idx {sc_idx}:', infos['shadow_vals'][f'{candle_animal}downs']['means'][sc_idx], infos['shadow_vals'][f'{candle_animal}downs']['stds'][sc_idx])
            upshadow_mean = infos['shadow_vals'][f'{candle_animal}ups']['means'][sc_idx]
            upshadow_std = infos['shadow_vals'][f'{candle_animal}ups']['stds'][sc_idx]
            downshadow_mean = infos['shadow_vals'][f'{candle_animal}downs']['means'][sc_idx]
            downshadow_std = infos['shadow_vals'][f'{candle_animal}downs']['stds'][sc_idx]
            # sizeclass_index = sc_idx  # was used for old maxvoldev (below)
            break
      # pdb.set_trace()

      upshadow_mean, shadow_interception_count = intercept_None_shadowvals(upshadow_mean, rand_cs, shadow_interception_count)
      upshadow_std, shadow_interception_count = intercept_None_shadowvals(upshadow_std, rand_cs, shadow_interception_count)
      downshadow_mean, shadow_interception_count = intercept_None_shadowvals(downshadow_mean, rand_cs, shadow_interception_count)
      downshadow_std, shadow_interception_count = intercept_None_shadowvals(downshadow_std, rand_cs, shadow_interception_count)

      rand_upshadow_size = randrange(int(((upshadow_mean-2*upshadow_std) if (upshadow_mean-2*upshadow_std) >= 0 else 0)*100000),
                                     int((upshadow_mean+2*upshadow_std)*100000+1), 1)/100000
      randhigh = randclose + rand_upshadow_size if candle_animal == 'bull' else randopen + rand_upshadow_size
      rand_downshadow_size = randrange(int(((downshadow_mean-2*downshadow_std) if (downshadow_mean-2*downshadow_std) >= 0 else 0)*100000),
                                     int((downshadow_mean+2*downshadow_std)*100000+1), 1)/100000
      randlow = randopen - rand_downshadow_size if candle_animal == 'bull' else randclose - rand_downshadow_size

      cs2vol_impact = None  # candlesize to volume impact

      max_cs = infos['sidiras'][SCG-1][1]
      cs2vol_impact = 0.35 + (rand_cs / max_cs) * 1.65  # simplified maxmin normalization: min cs not necessary cause it's 0 anyway.

      cs_influenced_vol = int(row['Volume'] * cs2vol_impact) if int(row['Volume'] * cs2vol_impact) > 0 else 1
      if cs_influenced_vol >= 2:
         maxvoldev = cs_influenced_vol // 2
         randvol = randrange(int(cs_influenced_vol - maxvoldev), int(cs_influenced_vol + maxvoldev) 
                             if cs_influenced_vol + maxvoldev < infos['maxvol'] - 200  # hardcoded val for when to begin attenuation earlier
                             else int(infos['maxvol'] + (cs_influenced_vol + maxvoldev - infos['maxvol']) // 2),  # large volume attenuation
                             1)
      else:
         randvol = randrange(1,3)

      rdf.loc[idx, 'Open'] = randopen
      rdf.loc[idx, 'High'] = randhigh
      rdf.loc[idx, 'Low'] = randlow
      rdf.loc[idx, 'Close'] = randclose
      rdf.loc[idx, 'Volume'] = randvol

   print('shadow_interception_count:', shadow_interception_count)
   return rdf




#(old way of doing candlesize to volume impact calc)[backups/candlesize_vol_impact_idea.py]

#(old: distributing shadows over candlesize classes)[backups/shadow_dist_over_candlesize_classes.py]
