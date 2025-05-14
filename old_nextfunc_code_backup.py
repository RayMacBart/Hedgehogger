# # Calculate TSL-distances first:
      # # distance = TSL.get_distance(self.data.Close, self.indicators)
      # if self.dirs[-1] > 0:
      #    bought = 0
      #    for t in self.trades:
      #       if t.is_long:
      #          bought += 1
      #          t.sl = self.data.Close-self.stopdist
      #    if not bought:
      #       self.buy(size=self.size, sl=self.data.Close-self.stopdist)
      # elif self.dirs[-1] < 0:
      #    sold = 0
      #    for t in self.trades:
      #       if t.is_short:
      #          sold += 1
      #          t.sl = self.data.Close+self.stopdist
      #    if not sold:
      #       self.sell(size=self.size, sl=self.data.Close+self.stopdist)

      # psar_distance = self.PSAR[-1] - self.data.Close[-1]
      # if psar_distance < 0:
      #    bought = 0
      #    for t in self.trades:
      #       if t.is_long:
      #          bought += 1
      #          t.sl = self.data.Close[-1] + psar_distance
      #    if not bought and self.dirs[-1] > 0:
      #       self.buy(size=self.size, sl=self.data.Close[-1] + psar_distance)
      # elif psar_distance > 0:
      #    sold = 0
      #    for t in self.trades:
      #       if t.is_short:
      #          sold += 1
      #          t.sl = self.data.Close[-1] + psar_distance
      #    if not sold  and self.dirs[-1] < 0:
      #       self.sell(size=self.size, sl=self.data.Close[-1] + psar_distance)

      # if self.scores > 100:
      #    bought = 0
      #    for t in self.trades:
      #       if t.is_long:
      #          bought += 1
      #    if not bought:
      #       self.buy(size=self.size)
            # --> set calculated trailing stop loss distance here!

      # elif self.scores < 100:
      #    sold = 0
      #    for t in self.trades:
      #       if t.is_long:
      #          sold += 1
      #    if not sold:
      #       self.sell(size=self.size)
            # --> set calculated trailing stop loss distance here!

      # self.cc += 1
      # T = helpers.get_current_indicator_data(self.indicators, self.cc)
      # dir = helpers.get_dir(self.data.Close[-1], self.last_swing[-1], self.seclast_swing[-1])
      # reaction.react(self.buy, self.sell, self.size, self.trades, T, self.trend[-1], self.last_swing[-1], self.seclast_swing[-1], dir)