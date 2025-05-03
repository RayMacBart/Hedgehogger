import unittest
from datetime import datetime
import pandas as pd
import os
import helpers
import DST_timehelper

class Test_get_pdfm(unittest.TestCase):
   def setUp(self):
      self.asset = 'EURUSD'
      self.candlesize = 'M5'
      self.clims = 60 if self.candlesize == 'H1' else int(self.candlesize[1:])

      self.volmean_df = pd.read_csv(os.path.join("volmean_data", f"volmean_{self.asset}_{self.candlesize}.csv"), sep="\t")
      self.vmmts = helpers.convert2VMMT_dict(self.volmean_df)
      print('type of vmmts in setUp:', type(self.vmmts))
      print("length of vmmts['winter'] in setUp:", len(self.vmmts['winter']))
   def test_get_pdfm(self):
      voldiff = 15
      span = 5
      TS = datetime(2023, 10, 21, 13, 15, 38)
      result = DST_timehelper.get_procentual_deviation_from_mean(voldiff, span, TS, self.vmmts, self.clims)
      last_calc_index = int((TS.hour*60+TS.minute)/self.clims)
      first_calc_index = last_calc_index-(span-1)
      print('vmmt @ first_index:', self.vmmts['winter'][first_calc_index])
      print('vmmt @ last_index:', self.vmmts['winter'][last_calc_index])
      print('% vmmt change:', (self.vmmts['winter'][last_calc_index]/(self.vmmts['winter'][first_calc_index]/100)-100))
      print('procentual deviation of actual volume:', voldiff)
      print('result:', result)
      print('repeated_testcalc:', voldiff - (self.vmmts['winter'][last_calc_index]/(self.vmmts['winter'][first_calc_index]/100)-100))
      self.assertAlmostEqual(result, voldiff - (self.vmmts['winter'][last_calc_index]/(self.vmmts['winter'][first_calc_index]/100)-100))

if __name__ == '__main__':
   unittest.main()