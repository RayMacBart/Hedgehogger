import helpers
from backtesting.lib import crossover


def radar(Close, ti):

   trend = [0,]
   for i in range(1, len(Close)):


      if ti['RSI']['low'] > ti['RSI']['rsi'][i]:
         trend.append(1)
      elif ti['RSI']['rsi'][i] > ti['RSI']['high']:
         trend.append(-1)
      elif 47 < ti['RSI']['rsi'][i] < 53:
         trend.append(0)
      else:
         trend.append(trend[-1])


   trend = helpers.trans_list_to_BT_array(trend, 'trend')
   return trend