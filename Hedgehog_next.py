import helpers
import DST_timehelper
# import value_dumper as valdump

def next(self):
   longs, shorts = helpers.get_tradetype_amounts(self.trades)
   neworder_stoptime = DST_timehelper.is_stoptime(self.data.index[-1], self.neworder_stoptime_dist, 
                                                   self.reenter_time_dist, self.clims)  # clims = candle length in minutes
   order_closetime = DST_timehelper.is_stoptime(self.data.index[-1], self.order_closetime_dist, self.reenter_time_dist,
                                                self.clims) if neworder_stoptime else False
   if longs:
      for trade in longs:
         if order_closetime:
            trade.close()
            # valdump.tradelog('Long', 'closed', self.data.Close[-1])
         elif self.data.Close[-1] - self.abs_SL_dists[-1] > trade.sl:
            trade.sl = self.data.Close[-1] - self.abs_SL_dists[-1]
         # elif self.data.Close[-1] - self.abs_SL_dists[-1] > self.current_sl:
         #    self.current_sl = self.data.Close[-1] - self.abs_SL_dists[-1]
         #    trade.sl = self.current_sl
   if shorts:
      for trade in shorts:
         if order_closetime:
            trade.close()
            # valdump.tradelog('Short', 'closed', self.data.Close[-1])
         elif self.data.Close[-1] + self.abs_SL_dists[-1] < trade.sl:
            trade.sl = self.data.Close[-1] + self.abs_SL_dists[-1]
         # elif self.data.Close[-1] + self.abs_SL_dists[-1] < self.current_sl:
         #    self.current_sl = self.data.Close[-1] + self.abs_SL_dists[-1]
         #    trade.sl = self.current_sl
   else:
      if self.powers[-1] <= -self.close_triggerpower:
         if longs:
            for trade in longs:
               trade.close()
               # valdump.tradelog('Long', 'closed', self.data.Close[-1])
         if (self.powers[-1] <= -self.order_triggerpower) and not neworder_stoptime:
            self.sell(size=self.size, sl=((self.data.Close[-1] + self.abs_SL_dists[-1]) if (self.abs_SL_dists[-1] > 0.0001*self.adjufac) else 
                                          (self.data.Close[-1] + 0.0001*self.adjufac)))  # multiple sell order accumulation intended!
            # valdump.tradelog('Short', 'opened', self.data.Close[-1])
      elif self.powers[-1] >= self.close_triggerpower:
         if shorts:
            for trade in shorts:
               trade.close()
               # valdump.tradelog('Short', 'closed', self.data.Close[-1])
         if (self.powers[-1] >= self.order_triggerpower) and not neworder_stoptime:
            self.buy(size=self.size, sl=((self.data.Close[-1] - self.abs_SL_dists[-1]) if (self.abs_SL_dists[-1] > 0.0001*self.adjufac) else 
                                          (self.data.Close[-1] - 0.0001*self.adjufac)))  # multiple buy order accumulation intended!
            # valdump.tradelog('Long', 'opened', self.data.Close[-1])