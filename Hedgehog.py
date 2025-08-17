from backtesting import Strategy
import Hedgehog_init
import Hedgehog_next
from var_config import get_vars
from volfuncs import get_vmmts



class Hedgehog(Strategy):

   asset, candlesize = get_vars()
   volmean_movetimes = get_vmmts(asset, candlesize)
   adjufac = 100 if asset == "USDJPY" else 1  #(?)[docs/adjufac.txt]
   clims = 60 if candlesize == 'H1' else int(candlesize[1:])  # clims = candle length in minutes
   
   # boundaries/tresholds:
   RSI_bound_distance = 30
   CCI_treshold_distance = 100
   ADX_treshold = 25

   CHWIN = 3

   # indicator calculation windows
   RSI_win = 11
   CCI_win = 11
   MACD_shortwin = 6
   MACD_longwin = 15
   MACD_signalwin = 2
   PSAR_af0 = 0.02
   PSAR_af = 0.02
   PSAR_max_af = 0.2
   bbands_win = 20
   ATR_win = 14
   ADX_win = 20
   sizegap_win = 100
   sizepeak_win = 100

   CSP_bodyshrink_factor = 5# was 6
   CSP_shadow2body_factor = 8# was 8
   CSP_shadowdiff_factor = 4# was 8

   #(?)[docs/chval_th.txt]
   MACD_chval_th = 5  #(!)[docs/th_convert_note.txt] 
   histo_chval_th = 2  #(!)[docs/th_convert_note.txt] 
   RSI_chval_th = 8
   CCI_chval_th = 15

   #(?)[docs/expfac.txt]
   vwap_expfac = 7  # difference between price and vwap 
   bbands_expfac = 3  # width between outer bands

   # mnfpwi: "max decreasing factor per weight impact"
   vol_mdfpwi = 1
   vol_max_impact_zscore = 4  # steps:  4 - 12
   #(old)[backups/old_vol_props.txt]

   sizegap_granularity = 12
   sizepeak_granularity = 12
   gap_accuracy = 5  #(?)[docs/accuracy_props.txt] 
   peak_accuracy = 6  #(?)[docs/accuracy_props.txt]

   # change measure windows:
   CSP_reaction_win = 2  # recommended to STAY like this
   MACD_chwin = 3 # 3-8 
   histo_chwin = 3 # 3-8
   combo_chwin = 6  # 3-10  #(!)[docs/combo_chwin_note.txt]
   VWAP_chwin = 8 # 3-8
   fibo_chwin = 3 # 3-8
   RSI_chwin = 4 # 3-10
   CCI_chwin = 4 # 3-10
   vol_chwin = 3 # 2-?
   ADX_chwin = 7 #?
   ATR_chwin = 3
   ATR_mincalcwin = 100  #(?)[docs/ATR_mincalcwin.txt]
   bbands_chwin_out = 4 #?
   bbands_chwin_trend = 4 # 3-8

   SL_formerspans_win = 1 # keep

   bbands_TSL_chwin = 7  # 2-?
   power_TSL_chwin = 5 # DEPRECATED: NOT NEEDED ANYMORE
   # peak_swingdist = 2 # 2-?

   # indicator weights
   DIR_weight = 1
   CSP_weight = 1 # was 2
   MACD_zeroweight = 1
   MACD_histoweight = 1
   MACD_comboweight = 1
   VWAP_weight = 1
   fibo_weight = 4
   cama3_weight = 1
   cama4_weight = 2
   RSI_weight = 2
   CCI_weight = 3
   bbands_weight_out = 1
   bbands_weight_trend = 1
   volume_weight = 1
   ADX_abs_weight = 1
   ADX_dyn_weight = 1
   gap_weight = 1
   peak_weight = 3
   ATR_abs_weight = 2
   ATR_dyn_weight = 2

   PSAR_weight = 2
   bbands_TSL_weight = 2
   ATR_TSL_weight = 3
   power_TSL_weight = 2
   minTSLdist = 2

   SLdist_redufac = 8  # StopLoss distance reduction factor * 10  (to have integers for sambo optimization)

   # following values must not be greater than 60
   neworder_stoptime_dist = 20
   order_closetime_dist = 5
   reenter_time_dist = 5

   close_triggerpower = 1 # was 2 # close_triggerpower must always be <= order_triggerpower. It also can be negative ( --> closes before power reaches 0!).
   order_triggerpower =  1 # was 28

   size = 0.001  # of buy/sell orders

   # cc = -1  # candle counter
   # stopdist = 0.0003

   


   def init(self):
      Hedgehog_init.__init__(self)


   def next(self):
      Hedgehog_next.next(self)


#(old idea regarding data parameter handling)[backups/handle_dataparams_idea.txt]
