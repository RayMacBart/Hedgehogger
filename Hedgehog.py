from backtesting import Strategy
import Hedgehog_init
import Hedgehog_next
from var_config import get_vars

# pairs to use with IG.com due to their low spreads:  EURUSD,  AUDUSD,  USDJPY


class Hedgehog(Strategy):

   asset, candlesize = get_vars()

   # boundaries/tresholds:
   RSI_upper_bound = 60
   RSI_lower_bound = 40
   CCI_upper_treshold = 100
   CCI_lower_treshold = -100
   ADX_treshold = 25

   # indicator calculation windows
   RSI_win = 20
   CCI_win = 20
   MACD_shortwin = 4
   MACD_longwin = 7
   MACD_signalwin = 3
   PSAR_af0 = 0.02
   PSAR_af = 0.02
   PSAR_max_af = 0.2
   bbands_win = 20
   ATR_win = 14
   ADX_win = 14
   sizegap_win = 100
   sizepeak_win = 100

   # 'expfac:' expansion factors that shall be reacted upon - the lower the more sensitive/reactive. use 0.1 steps
   vwap_expfac = 1.2  # difference between price and vwap 
   bbands_expfac = 1.3  # width between outer bands

   # mnfpwi: "max decreasing factor per weight impact"
   vol_mdfpwi = 0.15  # 0.05 - 0.4  (in 0.05 steps)
   vol_max_impact_zscore = 3  # steps:  2,  2.5,  3,  3.5,  4,  4.5,  5,  5.5,  6
   # old:
   # mpfpw: "max positive factor per weight"
   # vol_mpfpw = 1.5  # 1.2 - 2 (in 0.1 steps) - 3 (in 0.2 steps) - 4.2 (in 0.4 steps), 5
   sizegap_granularity = 10
   sizepeak_granularity = 10
   gap_accuracy = 5  # area of gap value recognition in % --> the lower, the more accurate!
   peak_accuracy = 5  # area of peak value recognition in % --> the lower, the more accurate!

   # change measure windows:
   MACD_chwin = 8 # 3-8 
   histo_chwin = 5 # 3-8
   VWAP_chwin = 8 # 3-8
   fibo_chwin = 5 # 3-8
   RSI_chwin = 5 # 3-10
   CCI_chwin = 5 # 3-10
   vol_chwin = 5 # 2-?
   ADX_chwin = 5 #?
   ATR_chwin = 5
   ATR_mincalcwin = 100  # minimum of used data for zscore calculation for absolute valued indications
   bbands_chwin_out = 5 #?
   bbands_chwin_trend = 5 # 3-8
   bbands_TSL_chwin = 5  # 2-?
   power_TSL_chwin = 5
   # peak_swingdist = 2 # 2-?

   # indicator weights
   volume_weight = 1
   ADX_abs_weight = 1
   ADX_dyn_weight = 1
   RSI_weight = 1
   CCI_weight = 1
   MACD_zeroweight = 1
   MACD_histoweight = 1
   bbands_weight_out = 1
   bbands_weight_trend = 1
   cama3_weight = 1
   cama4_weight = 1
   VWAP_weight = 1
   ATR_abs_weight = 1
   ATR_dyn_weight = 1
   gap_weight = 1
   peak_weight = 1
   fibo_weight = 1

   bbands_TSL_weight = 1
   ATR_TSL_weight = 1
   power_TSL_weight = 1

   # following values must not be greater than 60
   neworder_stoptime_dist = 20
   order_closetime_dist = 5
   reenter_time_dist = 5

   close_triggerpower = 1
   order_triggerpower =  1

   size = 0.1  # of buy/sell orders

   # cc = -1  # candle counter
   # stopdist = 0.0003

   



   def init(self):
      Hedgehog_init.__init__(self)
   #    self.minTSLdist = 0.0001*self.outvars['adjufac']  # opt steps:  0.00005, 0.0001, 0.00015, 0.0002, 0.00025 ...

   #    self.PSAR_df = ta.psar(self.data.High.s, self.data.Low.s, self.data.Close.s)
   #    self.PSAR = self.I(indicator_setups.PSAR, self.PSAR_df[f'PSARl_{self.PSAR_af0}_{self.PSAR_max_af}'], 
   #                       self.PSAR_df[f'PSARs_{self.PSAR_af0}_{self.PSAR_max_af}'], self.data.Close, name='PSAR')
   #  #   self.RSI = self.I(ta.rsi, self.data.Close.s, self.RSI_win)
   #  #   self.CCI = self.I(ta.cci, self.data.High.s, self.data.Low.s, self.data.Close.s, self.CCI_win)
   #    self.MACD_df = ta.macd(self.data.Close.s, self.MACD_shortwin, self.MACD_longwin, self.MACD_signalwin)
   #    self.MACD_macd = self.I(lambda: self.MACD_df[f'MACD_{self.MACD_shortwin}_{self.MACD_longwin}_{self.MACD_signalwin}'], name='MACD')
   #    self.MACD_histogram = self.I(lambda: self.MACD_df[f'MACDh_{self.MACD_shortwin}_{self.MACD_longwin}_{self.MACD_signalwin}'], name='Histogram')
   #    # self.MACD_signalline = self.I(lambda: self.MACD_df[f'MACDs_{self.MACD_shortwin}_{self.MACD_longwin}_{self.MACD_signalwin}'], name='Signalline')
   #  #   self.VWAP = self.I(ta.vwap, self.data.High.s, self.data.Low.s, self.data.Close.s, self.data.Volume.s, name='VWAP')
   #  #   self.bbands_df = ta.bbands(self.data.Close.s, self.bbands_win)
   #  #   self.lowerband = self.I(indicator_setups.lowerband, self.bbands_df[f'BBL_{self.bbands_win}_2.0'], name='lower bband')
   #  #   self.upperband = self.I(indicator_setups.upperband, self.bbands_df[f'BBU_{self.bbands_win}_2.0'], name='upper bband')
   #  #   self.middleband = self.I(indicator_setups.middleband, self.bbands_df[f'BBM_{self.bbands_win}_2.0'], name='middle bband')
   #  #   self.bandwidth = self.I(indicator_setups.bandwidth, self.bbands_df[f'BBB_{self.bbands_win}_2.0'], name='bband width')
   #  #   self.ATR = self.I(ta.atr, self.data.High.s, self.data.Low.s, self.data.Close.s, self.ATR_win, name='ATR')
   #  #   self.ADX_df = ta.adx(self.data.High.s, self.data.Low.s, self.data.Close.s, self.ADX_win)
   #  #   self.ADX_adx = self.I(indicator_setups.get_adx, self.ADX_df[f'ADX_{self.ADX_win}'], name='ADX')
   #  #   self.ADX_DM_pos = self.I(indicator_setups.get_dmp, self.ADX_df[f'DMP_{self.ADX_win}'], name='DM+')
   #  #   self.ADX_DM_neg = self.I(indicator_setups.get_dmn, self.ADX_df[f'DMN_{self.ADX_win}'], name='DM-')
   #  #   cama_start_idxs, initday_usable = camafuncs.get_cama_startidx(self.data.index, candlesize)
   #  #   cama_dailydata = camafuncs.get_cama_dailydata(self.data.index, self.data.High, self.data.Low,
   #  #                                         self.data.Close, cama_start_idxs, initday_usable)
   #  #   self.cama_R4 = self.I(camafuncs.cama_R4, self.data.Close, cama_dailydata, cama_start_idxs, initday_usable)
   #  #   self.cama_R3 = self.I(camafuncs.cama_R3, self.data.Close, cama_dailydata, cama_start_idxs, initday_usable)
   #  #   self.cama_S3 = self.I(camafuncs.cama_S3, self.data.Close, cama_dailydata, cama_start_idxs, initday_usable)
   #  #   self.cama_S4 = self.I(camafuncs.cama_S4, self.data.Close, cama_dailydata, cama_start_idxs, initday_usable)
   #    self.last_swing = self.I(helpers.last_swing, self.data.Open, self.data.Close)
   #    self.seclast_swing = self.I(helpers.seclast_swing, self.data.Close, self.last_swing)
   #  #   self.sizegap_up = self.I(sizegap.sizegap_up, self.last_swing, self.seclast_swing, 
   #  #                                               self.sizegap_win, self.sizegap_granularity, name='GAP+') 
   #  #   self.sizegap_down = self.I(sizegap.sizegap_down, self.last_swing, self.seclast_swing, 
   #  #                                               self.sizegap_win, self.sizegap_granularity, name='GAP-')
   #  #   self.sizepeak_up = self.I(sizepeak.sizepeak_up, self.last_swing, self.seclast_swing, 
   #  #                                               self.sizepeak_win, self.sizepeak_granularity, name='PEAK+') 
   #  #   self.sizepeak_down = self.I(sizepeak.sizepeak_down, self.last_swing, self.seclast_swing, 
   #  #                                               self.sizepeak_win, self.sizepeak_granularity, name='PEAK-')
   #  #   self.fibo_dist2 = self.I(fibofuncs.fibo_dist2, self.data.Close, self.last_swing, self.seclast_swing)
   #  #   self.fibo_dist4 = self.I(fibofuncs.fibo_dist4, self.data.Close, self.last_swing, self.seclast_swing)
   #  #   self.fibo_dist6 = self.I(fibofuncs.fibo_dist6, self.data.Close, self.last_swing, self.seclast_swing)
   #  #   self.fibo_dist8 = self.I(fibofuncs.fibo_dist8, self.data.Close, self.last_swing, self.seclast_swing)
   #    # DISCOVERY: Breaking these fibos indicates overall trend in that direction where it broke through!
   #    self.dirs = self.I(helpers.dir, self.data.Close, self.last_swing, self.seclast_swing)
   #    self.indicators = {'PSAR': self.PSAR, 'DIR': self.dirs,
   #                      #  'VOL': {'volume': self.data.Volume, 'chwin': self.vol_chwin, 'mdfpwi': self.vol_mdfpwi,
   #                      #          'max_impact_zscore': self.vol_max_impact_zscore, 'weight': self.volume_weight},
   #                      #  'VWAP': {'vwap': self.VWAP, 'chwin': self.VWAP_chwin, 'weight': self.VWAP_weight,
   #                      #           'expfac': self.vwap_expfac}, # difference expansion factor
   #                      #  'ATR': {'atr': self.ATR,  'chwin': self.ATR_chwin, 'mincalcwin': self.ATR_mincalcwin, 'win': self.ATR_win,
   #                      #          'abs-weight': self.ATR_abs_weight, 'dyn-weight': self.ATR_dyn_weight, 'TSL-weight': self.ATR_TSL_weight},
   #                      #  'ADX': {'adx': self.ADX_adx, 'DM+': self.ADX_DM_pos, 'DM-': self.ADX_DM_neg, 'chwin': self.ADX_chwin,
   #                      #          'treshold': self.ADX_treshold, 'abs-weight': self.ADX_abs_weight, 'dyn-weight': self.ADX_dyn_weight},
   #                      #  'RSI': {'rsi': self.RSI, 'low': self.RSI_lower_bound, 'high': self.RSI_upper_bound,
   #                      #          'chwin': self.RSI_chwin, 'weight': self.RSI_weight},
   #                      #  'CCI': {'cci': self.CCI, 'low': self.CCI_lower_treshold, 'high': self.CCI_upper_treshold,
   #                      #          'chwin': self.CCI_chwin, 'weight': self.CCI_weight},
   #                       'MACD': {'macd': self.MACD_macd, 'histo': self.MACD_histogram,
   #                                #'signal': self.MACD_signalline, # not used (yet?)
   #                                'macd_chwin': self.MACD_chwin, 'histo_chwin': self.histo_chwin,
   #                                'zeroweight': self.MACD_zeroweight, 'histoweight': self.MACD_histoweight},
   #                      #  'BB': {'low': self.lowerband, 'high': self.upperband,'mid': self.middleband,
   #                      #         'width': self.bandwidth, 'chwin-out': self.bbands_chwin_out, 'chwin-trend': self.bbands_chwin_trend,
   #                      #         'weight-out': self.bbands_weight_out, 'weight-trend': self.bbands_weight_trend, 'TSL-weight': self.bbands_TSL_weight,
   #                      #         'TSL-chwin': self.bbands_TSL_chwin, 'expfac': self.bbands_expfac},  # width expansion factor
   #                      #  'CAMA': {'R4': self.cama_R4, 'R3': self.cama_R3, 'S3': self.cama_S3,
   #                      #           'S4': self.cama_S4, '3weight': self.cama3_weight, '4weight': self.cama4_weight},
   #                      #  'GAP': {'+': self.sizegap_up, '-': self.sizegap_down, 'accuracy': self.gap_accuracy, 'weight': self.gap_weight},
   #                      #  'PEAK': {'+': self.sizepeak_up, '-': self.sizepeak_down, 'accuracy': self.peak_accuracy, 'weight': self.peak_weight
   #                      #          #  , 'swingdist': self.peak_swingdist
   #                      #           },
   #                      #  'FIBO': {2: self.fibo_dist2, 4: self.fibo_dist4, 6: self.fibo_dist6,
   #                      #           8: self.fibo_dist8, 'chwin': self.fibo_chwin, 'weight': self.fibo_weight}
   #                      }
   #    self.powers = self.I(powers, self.data, self.indicators, self.last_swing, self.data.index, 
   #                         self.volmean_movetimes, self.outvars['clims'], self.outvars['impact_counter'])


   #    self.abs_SL_dists = self.I(TSL.stoplosses, self.data.Close, self.indicators, self.powers, self.power_TSL_chwin, 
   #                               self.minTSLdist, self.power_TSL_weight)
   #    self.current_sl = self.data.Close[0]



   def next(self):
      Hedgehog_next.next(self)
      # longs, shorts = helpers.get_tradetype_amounts(self.trades)
      # neworder_stoptime = DST_timehelper.is_stoptime(self.data.index[-1], self.neworder_stoptime_dist, 
      #                                                self.reenter_time_dist, self.outvars['clims'])  # clims = candle length in minutes
      # order_closetime = DST_timehelper.is_stoptime(self.data.index[-1], self.order_closetime_dist, self.reenter_time_dist,
      #                                              self.outvars['clims']) if neworder_stoptime else False
      # if longs:
      #    for trade in longs:
      #       if order_closetime:
      #          trade.close()
      #       elif self.data.Close[-1] - self.abs_SL_dists[-1] > self.current_sl:
      #          self.current_sl = self.data.Close[-1] - self.abs_SL_dists[-1]
      #          trade.sl = self.current_sl
      # if shorts:
      #    for trade in shorts:
      #       if order_closetime:
      #          trade.close()
      #       elif self.data.Close[-1] + self.abs_SL_dists[-1] < self.current_sl:
      #          self.current_sl = self.data.Close[-1] + self.abs_SL_dists[-1]
      #          trade.sl = self.current_sl
      # else:
      #    if self.powers[-1] <= -self.close_triggerpower:
      #       if longs:
      #          for trade in longs:
      #             trade.close()
      #       if (self.powers[-1] <= -self.order_triggerpower) and not neworder_stoptime:
      #          self.sell(size=self.size, sl=((self.data.Close[-1] + self.abs_SL_dists[-1]) if (self.abs_SL_dists[-1] > 0.0001) else 
      #                                        (self.data.Close[-1] + 0.0001)))  # multiple sell order accumulation intended!
      #    elif self.powers[-1] >= self.close_triggerpower:
      #       if shorts:
      #          for trade in shorts:
      #             trade.close()
      #       if (self.powers[-1] >= self.order_triggerpower) and not neworder_stoptime:
      #          self.buy(size=self.size, sl=((self.data.Close[-1] - self.abs_SL_dists[-1]) if (self.abs_SL_dists[-1] > 0.0001) else 
      #                                       (self.data.Close[-1] - 0.0001)))  # multiple buy order accumulation intended!




# old idea of handling the data_parameters:
# asset = sys.argv[1] if len(sys.argv) > 1 else "EURUSD"
# adjufac = 100 if asset == "USDJPY" else 1  # adjustment factor for the USD/JPY pair which has a 100x higher pip-size!
# candlesize = ("M"+str(sys.argv[2]) if int(sys.argv[2]) != 60 else "H1") if len(sys.argv) > 2 else "M5"
# dataspan = int(sys.argv[3]) if len(sys.argv) > 3 else 10000
# ... --> ! 3rd arg 'dataspan' must be min. 2580 with M1, min. 520 with M5,  min. 180 with M15...
# pastshift = int(sys.argv[4]) if len(sys.argv) > 4 else 0