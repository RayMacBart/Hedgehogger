# from backtesting.lib import resample_apply as reapp, barssince
from backtesting._util import _Array
import numpy as np
import pandas as pd


def trans_list_to_BT_array(data, name):
   data = np.array(data, dtype='float64')
   data = _Array(data, name=name)
   return data


def fill_inclomplete_data(data, ref, name):
   for i in data:
      yield i
   if len(data) < len(ref):
      for i in range(len(ref) - len(data)):
         yield data[-1]
         if i == len(ref) - len(data) - 1:
            print(f"FILLED UP DATA OF COLUMN '{name}' WITH IT'S LAST VALUE UNTIL THE END!")


def remove_nocomma_anomaly(x):
    if pd.isna(x) or not isinstance(x, (int, float)):
        return x
    return x / 1000 if x > 1000 else x


def adjust_volume_data(vol_series):
   adjusted_vols = [(round(vol) if not pd.isna(vol) and isinstance(vol, (int, float)) and not vol.is_integer()\
                     and (round(vol)-0.001 < vol < round(vol)+0.001) else vol) for vol in vol_series]
   for vol in adjusted_vols:
      if not isinstance(vol, (int, float)):
         print('CAUTION: NON-NUMERIC VOLUME DATA DEDECTED!!!')
      elif not (round(vol)-0.001 < vol < round(vol)+0.001):
         print('CAUTION: NOT NEAR INTEGER VOLUME DATA DEDECTED!!!')
   return pd.Series(adjusted_vols)


def convert2VMMT_dict(volmean_df):
    return {'winter': volmean_df['winter'].tolist(),
            'trans': volmean_df['trans'].tolist(),
            'summer': volmean_df['summer'].tolist(),
            'mean': np.mean(pd.concat([volmean_df['winter'], volmean_df['trans'], volmean_df['summer']], ignore_index=True)),
            'std': np.std(pd.concat([volmean_df['winter'], volmean_df['trans'], volmean_df['summer']], ignore_index=True))}



def defuse(val, lvl):
    i_vals = np.arange(int(val) + 1)
    results = 1 / ((1 + (lvl / 100)) ** i_vals)
    results[-1] *= (val - int(val))  # Adjust fractional part
    return np.sum(results)


# def convert2VMMT_zscore_dict(volmean_df):
#     full_data = pd.concat([volmean_df['winter'], volmean_df['trans'], volmean_df['summer']], ignore_index=True)
#     mean_all = np.mean(full_data)
#     std_all = np.std(full_data)
#     return {col: ((volmean_df[col]-mean_all)/std_all).tolist() for col in ['winter', 'trans', 'summer']}



def last_swings_generator(Open, Close):
   last_swing_value = Close[0]
   for idx in range(len(Close)):
      if idx in [0,1]:
         yield Close[0]
      else:
         swing_dedected = ((Close[idx-1] > Open[idx-1] and Close[idx-2] <= Open[idx-2]) or 
                           (Close[idx-1] < Open[idx-1] and Close[idx-2] >= Open[idx-2]))
         if not swing_dedected:
            yield last_swing_value
         else:
            last_swing_value = Open[idx-1]  # still pure because only local variable is mutated
            yield last_swing_value

def last_swing(Open, Close):
   last_swing = list(last_swings_generator(Open, Close))
   last_swing = trans_list_to_BT_array(last_swing, 'last swing')
   return last_swing


def seclast_swing_generator(Close, last_swing):
   last_seclast_swing_value = Close[0]
   yield Close[0]
   for idx in range(1, len(last_swing)):
      if last_swing[idx] != last_swing[idx-1]:
         last_seclast_swing_value = last_swing[idx-1] # still pure because only local variable is mutated
         yield last_seclast_swing_value
      else:
         yield last_seclast_swing_value

def seclast_swing(Close, last_swing):
   seclast_swing = list(seclast_swing_generator(Close, last_swing))
   return seclast_swing

def seclast_swing(Close, last_swing):
   seclast_swing = []
   seclast_swing.append(Close[0])
   for idx in range(1, len(last_swing)):
      if last_swing[idx] != last_swing[idx-1]:
         seclast_swing.append(last_swing[idx-1])
      else:
         seclast_swing.append(seclast_swing[-1])
   seclast_swing = trans_list_to_BT_array(seclast_swing, 'seclast swing')
   return seclast_swing


def dir(Close, last, seclast):
   dirs = []
   for idx in range(len(Close)):
      if idx >= 1:
         if last[idx] <= seclast[idx]:
            if Close[idx-1] > last[idx]:
               # dirs.append(Close[idx]*1.0015)
               dirs.append(1)
            elif Close[idx-1] < last[idx]:
               dirs.append(dirs[-1])
            else:
               dirs.append(dirs[0])
         elif last[idx] > seclast[idx]:
            if Close[idx-1] < last[idx]:
               # dirs.append(Close[idx]*0.9985)
               dirs.append(-1)
            elif Close[idx-1] > last[idx]:
               dirs.append(dirs[-1])
            else:
               dirs.append(dirs[0])
      else:
         dirs.append(Close[0])
   dirs = trans_list_to_BT_array(dirs, 'dirs')
   return dirs


def get_tradetypes(trades):
   longs = []
   shorts = []
   for trade in trades:
      if trade.is_long:
          longs.append(trade)
      elif trade.is_short:
          shorts.append(trade)
   return longs, shorts


def get_current_indicator_data(ti, cc):
   T = {}
   T['PSAR'] = ti['PSAR'][cc]
   T['VWAP'] = ti['VWAP'][cc]
   T['ATR'] = ti['ATR'][cc]
   T['ADX'] = {}
   T['ADX']['adx'] = ti['ADX']['adx'][cc]
   T['ADX']['DM+'] = ti['ADX']['DM+'][cc]
   T['ADX']['DM-'] = ti['ADX']['DM-'][cc]
   T['RSI'] = {}
   T['RSI']['rsi'] = ti['RSI']['rsi'][cc]
   T['RSI']['low'] = ti['RSI']['low']
   T['RSI']['high'] = ti['RSI']['high']
   T['MACD'] = {}
   T['MACD']['macd'] = ti['MACD']['macd'][cc]
   T['MACD']['histo'] = ti['MACD']['histo'][cc]
   T['MACD']['signal'] = ti['MACD']['signal'][cc]
   T['BB'] = {}
   T['BB']['low'] = ti['BB']['low'][cc]
   T['BB']['high'] = ti['BB']['high'][cc]
   T['BB']['mid'] = ti['BB']['mid'][cc]
   T['BB']['width'] = ti['BB']['width'][cc]
   T['CAMA'] = {}
   T['CAMA']['R4'] = ti['CAMA']['R4'][cc]
   T['CAMA']['R3'] = ti['CAMA']['R3'][cc]
   T['CAMA']['S3'] = ti['CAMA']['S3'][cc]
   T['CAMA']['S4'] = ti['CAMA']['S4'][cc]
   T['GAP'] = {}
   T['GAP']['+'] = ti['GAP']['+'][cc]
   T['GAP']['-'] = ti['GAP']['-'][cc]
   T['FIBO'] = {}
   T['FIBO'][2] = ti['FIBO'][2][cc]
   T['FIBO'][4] = ti['FIBO'][4][cc]
   T['FIBO'][6] = ti['FIBO'][6][cc]
   T['FIBO'][8] = ti['FIBO'][8][cc]
   return T