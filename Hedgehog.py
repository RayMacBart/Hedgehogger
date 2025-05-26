from backtesting import Strategy
import Hedgehog_init
import Hedgehog_next
from var_config import get_vars
from volfuncs import get_vmmts

# pairs to use with IG.com due to their low spreads:  EURUSD,  AUDUSD,  USDJPY


class Hedgehog(Strategy):

   asset, candlesize = get_vars()
   volmean_movetimes = get_vmmts(asset, candlesize)
   adjufac = 100 if asset == "USDJPY" else 1  # adjustment factor for the USD/JPY pair which has a 100x higher pip-size!
   clims = 60 if candlesize == 'H1' else int(candlesize[1:])  # clims = candle length in minutes
   
   # boundaries/tresholds:
   RSI_upper_bound = 70
   RSI_lower_bound = 30
   CCI_upper_treshold = 100
   CCI_lower_treshold = -100
   ADX_treshold = 25

   # indicator calculation windows
   RSI_win = 20
   CCI_win = 20
   MACD_shortwin = 3
   MACD_longwin = 7
   MACD_signalwin = 2
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
   MACD_chwin = 3 # 3-8 
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
   MACD_comboweight = 1
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


   def next(self):
      Hedgehog_next.next(self)




# old idea of handling the data_parameters:
# asset = sys.argv[1] if len(sys.argv) > 1 else "EURUSD"
# adjufac = 100 if asset == "USDJPY" else 1  # adjustment factor for the USD/JPY pair which has a 100x higher pip-size!
# candlesize = ("M"+str(sys.argv[2]) if int(sys.argv[2]) != 60 else "H1") if len(sys.argv) > 2 else "M5"
# dataspan = int(sys.argv[3]) if len(sys.argv) > 3 else 10000
# ... --> ! 3rd arg 'dataspan' must be min. 2580 with M1, min. 520 with M5,  min. 180 with M15...
# pastshift = int(sys.argv[4]) if len(sys.argv) > 4 else 0