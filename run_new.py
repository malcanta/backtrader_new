import os, sys, argparse
import pandas as pd
import backtrader as bt
import math
from strategies.goldencross import MyIndicator
from strategies.goldencross import GoldenCross
from strategies.buyhold import buyhold

strategies = {
    "golden_cross": GoldenCross,
    "buy_hold": buyhold
}

class NoStrategy(bt.Strategy):
    params = (('period', 15), ('trixperiod', 15,), ('fast', 50), ('slow', 200), ('order_percentage', 0.95), ('ticker', 'SPY'))
    #other_params = (('fast', 50), ('slow', 200), ('order_percentage', 0.95), ('ticker', 'SPY'))

    def __init__(self):
        MyIndicator(self.data, period=self.p.trixperiod)

        ema1 = bt.indicators.EMA(self.data, period=self.p.period)
        ema2 = bt.indicators.EMA(ema1, period=self.p.period)
        ema3 = bt.indicators.EMA(ema2, period=self.p.period)

        self.fast_moving_average = bt.indicators.SMA(
            self.data.close, period=self.params.fast
        )

        self.slow_moving_average = bt.indicators.SMA(
            self.data.close, period=self.params.slow
        )

        self.sma_diff = ((self.fast_moving_average / self.slow_moving_average) / (self.data.close / self.fast_moving_average))
        self.ema = 100.0 * (ema3 - ema3(-1)) / ema3(-1)

        self.thresh = self.sma_diff

    def next(self):
        if self.position.size == 0:
            if (self.sma_diff > 1) or (self.sma_diff > self.thresh + 0.044):
                #print(thresh)
            #if self.sma_diff > 1:
            #if self.ema < 0:
                amount_to_invest = (self.params.order_percentage * self.broker.cash)
                self.size = math.floor(amount_to_invest / self.data.close)
                self.thresh = self.sma_diff[0]
                print("Buy {} shares of {} at {} with thresh at {}".format(self.size, self.params.ticker, self.data.close[0], self.thresh))

                self.buy(size=self.size)

        if self.position.size > 0:
            if (self.sma_diff < self.thresh - 0.04):
            #if self.sma_diff < 1:
                #print(thresh)
            #if self.ema > 0:
                self.thresh = self.sma_diff[0]
                print("Sell {} shares of {} at {} with thresh at {}".format(self.size, self.params.ticker, self.data.close[0], self.thresh))
                self.close()
# parser = argparse.ArgumentParser()
# parser.add_argument("strategy", help="which strategy to run", type=str)
# args = parser.parse_args()
#
# if not args.strategy in strategies:
#     print("invalid strategy, must be one of {}".format(strategies.keys()))
#     sys.exit()

cerebro = bt.Cerebro()
cerebro.broker.setcash(100000)

prices = pd.read_csv('/home/mark/trading/ticker_files/spy.csv', index_col='Date', parse_dates=True)

feed = bt.feeds.PandasData(dataname=prices)
cerebro.adddata(feed)

#cerebro.addstrategy(strategies[args.strategy])
cerebro.addstrategy(NoStrategy, trixperiod=15)
cerebro.run()

print(cerebro.broker.get_value())
cerebro.plot()
