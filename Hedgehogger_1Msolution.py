from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import pandas as pd
import pandas_ta as ta
import numpy as np


df = pd.read_csv("./EURUSD_M1.csv", sep="\t", parse_dates=True, index_col='Timestamp')

resampled_df = df.resample('15T').mean()
resampled_df = resampled_df.interpolate().dropna()

class Hedgehog(Strategy):
    upper_bound = 70
    lower_bound = 30

    def init(self):
      #   self.RSI = self.I(ta.rsi, self.data.Close.s, 14)
        rsi_series = ta.rsi(self.data.df['Close'], length=14).fillna(0).to_numpy()
        self.RSI = self.I(lambda: rsi_series)

    def next(self):
        if crossover(self.RSI, self.upper_bound):
            self.position.close()
        elif crossover(self.lower_bound, self.RSI):
            self.buy(size=0.5)

bt = Backtest(resampled_df, Hedgehog, cash=1000, commission=0.002)

stats = bt.run()
print(stats)
bt.plot()
