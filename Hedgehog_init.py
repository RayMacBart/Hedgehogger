import pandas_ta as ta
import helpers
import indicator_setups
import camafuncs
import fibofuncs
import sizegap
import sizepeak
import TSL
from power import powers


def __init__(self):
   
   self.candlesize = self._params['candlesize']
   
   self.impact_counter = {'DIR': 0, 'CSP': 0, 'MACD': 0, 'MACD-zeroX': 0, 'MACD-sigX': 0, 'MACD-combo': 0, 'VWAP': 0, 'FIBO': 0,
                          'RSI': 0, 'RSI-abs': 0, 'RSI-dyn': 0,'CCI': 0, 'CCI-abs': 0, 'CCI-dyn': 0, 'BB-out': 0, 'BB-trend': 0,
                          'ADX': 0, 'ADX-abs': 0, 'ADX-dyn': 0, 'VOL': 0, 'CAMA': 0, 'GAP': 0, 'PEAK': 0, 'ATR': 0, 'ATR-abs': 0, 'ATR-dyn': 0}

   self.real_minTSLdist = 0.00005*self.minTSLdist*self.adjufac  # opt steps:  0.00005, 0.0001, 0.00015, 0.0002, 0.00025 ...

   self.PSAR_df = ta.psar(self.data.High.s, self.data.Low.s, self.data.Close.s)
   self.PSAR = self.I(indicator_setups.PSAR, self.PSAR_df[f'PSARl_{self.PSAR_af0}_{self.PSAR_max_af}'], 
                        self.PSAR_df[f'PSARs_{self.PSAR_af0}_{self.PSAR_max_af}'], self.data.Close, name='PSAR')
   # self.RSI = self.I(ta.rsi, self.data.Close.s, self.RSI_win)
   # self.RSI_upper_bound = 50 + self.RSI_bound_distance
   # self.RSI_lower_bound = 50 - self.RSI_bound_distance
   # self.CCI = self.I(ta.cci, self.data.High.s, self.data.Low.s, self.data.Close.s, self.CCI_win)
   # self.CCI_upper_treshold = self.CCI_treshold_distance
   # self.CCI_lower_treshold = self.CCI_treshold_distance*(-1)
   self.MACD_df = ta.macd(self.data.Close.s, self.MACD_shortwin, self.MACD_longwin, self.MACD_signalwin)
   self.MACD_macd = self.I(lambda: self.MACD_df[f'MACD_{self.MACD_shortwin}_{self.MACD_longwin}_{self.MACD_signalwin}'], name='MACD')
   self.MACD_histogram = self.I(lambda: self.MACD_df[f'MACDh_{self.MACD_shortwin}_{self.MACD_longwin}_{self.MACD_signalwin}'], name='Histogram')
   ## self.MACD_signalline = self.I(lambda: self.MACD_df[f'MACDs_{self.MACD_shortwin}_{self.MACD_longwin}_{self.MACD_signalwin}'], name='Signalline')
   # self.VWAP = self.I(ta.vwap, self.data.High.s, self.data.Low.s, self.data.Close.s, self.data.Volume.s, name='VWAP')
   self.bbands_df = ta.bbands(self.data.Close.s, self.bbands_win)
   self.lowerband = self.I(indicator_setups.lowerband, self.bbands_df[f'BBL_{self.bbands_win}_2.0'], name='lower bband')
   self.upperband = self.I(indicator_setups.upperband, self.bbands_df[f'BBU_{self.bbands_win}_2.0'], name='upper bband')
   self.middleband = self.I(indicator_setups.middleband, self.bbands_df[f'BBM_{self.bbands_win}_2.0'], name='middle bband')
   self.bandwidth = self.I(indicator_setups.bandwidth, self.bbands_df[f'BBB_{self.bbands_win}_2.0'], name='bband width')
   self.ATR = self.I(ta.atr, self.data.High.s, self.data.Low.s, self.data.Close.s, self.ATR_win, name='ATR')
#    self.ADX_df = ta.adx(self.data.High.s, self.data.Low.s, self.data.Close.s, self.ADX_win)
#    self.ADX_adx = self.I(indicator_setups.get_adx, self.ADX_df[f'ADX_{self.ADX_win}'], name='ADX')
#    self.ADX_DM_pos = self.I(indicator_setups.get_dmp, self.ADX_df[f'DMP_{self.ADX_win}'], name='DM+')
#    self.ADX_DM_neg = self.I(indicator_setups.get_dmn, self.ADX_df[f'DMN_{self.ADX_win}'], name='DM-')
   # cama_start_idxs, initday_usable = camafuncs.get_cama_startidx(self.data.index, self.candlesize)
   # cama_dailydata = camafuncs.get_cama_dailydata(self.data.index, self.data.High, self.data.Low,
   #                                         self.data.Close, cama_start_idxs, initday_usable)
   # self.cama_R4 = self.I(camafuncs.cama_R4, self.data.Close, cama_dailydata, cama_start_idxs, initday_usable)
   # self.cama_R3 = self.I(camafuncs.cama_R3, self.data.Close, cama_dailydata, cama_start_idxs, initday_usable)
   # self.cama_S3 = self.I(camafuncs.cama_S3, self.data.Close, cama_dailydata, cama_start_idxs, initday_usable)
   # self.cama_S4 = self.I(camafuncs.cama_S4, self.data.Close, cama_dailydata, cama_start_idxs, initday_usable)
   self.last_swing = self.I(helpers.last_swing, self.data.Open, self.data.Close)
   self.seclast_swing = self.I(helpers.seclast_swing, self.data.Close, self.last_swing)
#    self.sizegap_up = self.I(sizegap.sizegap_up, self.last_swing, self.seclast_swing, 
#                             self.sizegap_win, self.sizegap_granularity, name='GAP+') 
#    self.sizegap_down = self.I(sizegap.sizegap_down, self.last_swing, self.seclast_swing, 
#                               self.sizegap_win, self.sizegap_granularity, name='GAP-')
#    self.sizepeak_up = self.I(sizepeak.sizepeak_up, self.last_swing, self.seclast_swing, 
#                              self.sizepeak_win, self.sizepeak_granularity, name='PEAK+') 
#    self.sizepeak_down = self.I(sizepeak.sizepeak_down, self.last_swing, self.seclast_swing, 
#                                self.sizepeak_win, self.sizepeak_granularity, name='PEAK-')
   # self.fibo_dist2 = self.I(fibofuncs.fibo_dist2, self.data.Close, self.last_swing, self.seclast_swing)
   # self.fibo_dist4 = self.I(fibofuncs.fibo_dist4, self.data.Close, self.last_swing, self.seclast_swing)
   # self.fibo_dist6 = self.I(fibofuncs.fibo_dist6, self.data.Close, self.last_swing, self.seclast_swing)
   # self.fibo_dist8 = self.I(fibofuncs.fibo_dist8, self.data.Close, self.last_swing, self.seclast_swing)
   # DISCOVERY: Breaking these fibos indicates overall trend in that direction where it broke through!
   self.dirs = self.I(helpers.dir, self.data.Close, self.last_swing, self.seclast_swing)
   self.indicators = {'PSAR': {'psar': self.PSAR, 'weight': self.PSAR_weight},
                      'DIR': {'dir' :self.dirs, 'weight': self.DIR_weight},
                #       'VOL': {'volume': self.data.Volume, 'chwin': self.vol_chwin, 'mdfpwi': self.vol_mdfpwi,
                #               'max_impact_zscore': self.vol_max_impact_zscore, 'weight': self.volume_weight},
                     #  'VWAP': {'vwap': self.VWAP, 'chwin': self.VWAP_chwin, 'weight': self.VWAP_weight,
                     #           'expfac': self.vwap_expfac}, # difference expansion factor
                      'ATR': {'atr': self.ATR,  'chwin': self.ATR_chwin, 'mincalcwin': self.ATR_mincalcwin, 'win': self.ATR_win,
                              'abs-weight': self.ATR_abs_weight, 'dyn-weight': self.ATR_dyn_weight, 'TSL-weight': self.ATR_TSL_weight},
                #       'ADX': {'adx': self.ADX_adx, 'DM+': self.ADX_DM_pos, 'DM-': self.ADX_DM_neg, 'chwin': self.ADX_chwin,
                #               'treshold': self.ADX_treshold, 'abs-weight': self.ADX_abs_weight, 'dyn-weight': self.ADX_dyn_weight},
                     #  'RSI': {'rsi': self.RSI, 'low': self.RSI_lower_bound, 'high': self.RSI_upper_bound,
                     #          'chwin': self.RSI_chwin, 'chval_treshold': self.RSI_chval_th, 'weight': self.RSI_weight},
                     #  'CCI': {'cci': self.CCI, 'low': self.CCI_lower_treshold, 'high': self.CCI_upper_treshold,
                     #          'chwin': self.CCI_chwin, 'chval_treshold': self.CCI_chval_th, 'weight': self.CCI_weight},
                     #  'CSP': {'reaction_win': self.CSP_reaction_win, 'bodyshrink_factor': self.CSP_bodyshrink_factor,
                     #          'shadow2body_factor': self.CSP_shadow2body_factor, 'shadowdiff_factor': self.CSP_shadowdiff_factor,
                     #          'weight': self.CSP_weight}, # 'CSP': Candle Stick Pattern
                      'MACD': {'macd': self.MACD_macd, 'histo': self.MACD_histogram,
                               #'signal': self.MACD_signalline, # not used (yet?)
                               'macd_chwin': self.MACD_chwin, 'histo_chwin': self.histo_chwin, 'combo_chwin': self.combo_chwin,
                               'chval_treshold': self.MACD_chval_th, 'histo_chval_th': self.histo_chval_th, 'zeroweight': self.MACD_zeroweight,
                               'histoweight': self.MACD_histoweight, 'comboweight': self.MACD_comboweight},
                      'BB': {'low': self.lowerband, 'high': self.upperband,'mid': self.middleband,
                             'width': self.bandwidth, 'chwin-out': self.bbands_chwin_out, 'chwin-trend': self.bbands_chwin_trend,
                             'weight-out': self.bbands_weight_out, 'weight-trend': self.bbands_weight_trend, 'TSL-weight': self.bbands_TSL_weight,
                             'TSL-chwin': self.bbands_TSL_chwin, 'expfac': self.bbands_expfac},  # width expansion factor
                     #  'CAMA': {'R4': self.cama_R4, 'R3': self.cama_R3, 'S3': self.cama_S3,
                     #           'S4': self.cama_S4, '3weight': self.cama3_weight, '4weight': self.cama4_weight},
                #       'GAP': {'+': self.sizegap_up, '-': self.sizegap_down, 'accuracy': self.gap_accuracy, 'weight': self.gap_weight},
                #       'PEAK': {'+': self.sizepeak_up, '-': self.sizepeak_down, 'accuracy': self.peak_accuracy, 'weight': self.peak_weight
                #               #  , 'swingdist': self.peak_swingdist
                #                },
                     #  'FIBO': {2: self.fibo_dist2, 4: self.fibo_dist4, 6: self.fibo_dist6,
                     #           8: self.fibo_dist8, 'chwin': self.fibo_chwin, 'weight': self.fibo_weight}
                     }
   self.powers = self.I(powers, self.data, self.indicators, self.last_swing, self.data.index, 
                        self.volmean_movetimes, self.clims, self.impact_counter)


   self.abs_SL_dists = self.I(TSL.stoplosses, self.data.Close, self.data.High, self.data.Low, self.indicators, self.SL_formerspans_win, 
                              self.SLdist_redufac, self.powers, self.power_TSL_chwin, self.real_minTSLdist, self.power_TSL_weight)
   # self.current_sl = self.data.Close[0]