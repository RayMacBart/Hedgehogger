import helpers


def react(buy, sell, size, trades, T, trend, last, seclast, dir):
   longs, shorts = helpers.get_tradetypes(trades)
   if (T['RSI']['rsi'] > T['RSI']['high']):
      if longs:
         for trade in longs:
            trade.close  # such will be replaced by stop losses!
      if not shorts:
         sell()
   if (T['RSI']['rsi'] < T['RSI']['low']):
      if shorts:
         for trade in shorts:
            trade.close  # such will be replaced by stop losses!
      if not longs:
         buy()


