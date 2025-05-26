import os
import pandas as pd

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
   vmmt_dict = {'winter': volmean_df['winter'].tolist(), 'trans': volmean_df['trans'].tolist(), 'summer': volmean_df['summer'].tolist(),
                'mean': volmean_df['mean'][0], 'std': volmean_df['std'][0]}
   vmmt_dict['min'] = min(vmmt_dict['winter'] + vmmt_dict['trans'] + vmmt_dict['summer'])
   return vmmt_dict


def get_vmmts(asset, candlesize):
   try:
      file_path = os.path.join("volmean_data", f"volmean_{asset}_{candlesize}.csv")
      if not os.path.exists(file_path):
         raise FileNotFoundError(f"File not found: {file_path}")
      volmean_df = pd.read_csv(file_path, sep="\t")
      print("Volmean Data successfully loaded!")
   except Exception as e:
      print('Error occured during loading VOLUME MEAN data:', e)
   return convert2VMMT_dict(volmean_df)