import math
import backtrader as bt

class MyIndicator(bt.Indicator):
    lines = ('trix', 'sma_diff', 'sma_ema_diff')
    params = (('period', 15), ('fast', 50), ('slow', 200), ('order_percentage', 0.95), ('ticker', 'SPY'))

    def __init__(self):
        ema1 = bt.indicators.EMA(self.data, period=self.p.period)
        ema2 = bt.indicators.EMA(ema1, period=self.p.period)
        ema3 = bt.indicators.EMA(ema2, period=self.p.period)
        sma1 = bt.indicators.SMA(self.data.close, period=self.params.fast, plotname='50 day moving average')
        sma2 = bt.indicators.SMA(self.data.close, period=self.params.slow, plotname='200 day moving average')

        #self.lines.trix = 100.0 * (ema3 - ema3(-1)) / ema3(-1)
        self.lines.sma_diff = ((sma1 / sma2) / (self.data.close / sma1))

        #x = 100.0 * (ema3 - ema3(-1)) / ema3(-1)
        #y = ((sma1 / sma2) / (self.data.close / sma1))
        #self.lines.sma_ema_diff = y - x

class GoldenCross(bt.Strategy):
    params = (('fast', 50), ('slow', 200), ('order_percentage', 0.95), ('ticker', 'SPY'))

    def __init__(self):
        self.fast_moving_average = bt.indicators.SMA(
            self.data.close, period=self.params.fast, plotname='50 day moving average'
        )

        self.slow_moving_average = bt.indicators.SMA(
            self.data.close, period=self.params.slow, plotname='200 day moving average'
        )

        self.crossover = bt.indicators.CrossOver(self.fast_moving_average, self.slow_moving_average)

    def next(self):
        if self.position.size == 0:
            if self.crossover > 0:
                amount_to_invest = (self.params.order_percentage * self.broker.cash)
                self.size = math.floor(amount_to_invest / self.data.close)

                print("Buy {} shares of {} at {}".format(self.size, self.params.ticker, self.data.close[0]))

                self.buy(size=self.size)

        if self.position.size > 0:
            if self.crossover < 0:
                print("Sell {} shares of {} at {}".format(self.size, self.params.ticker, self.data.close[0]))
                self.close()
