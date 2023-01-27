import backtrader as bt

class buyhold(bt.Strategy):

    def next(self):
        if self.position.size == 0:
            size = int(self.broker.getcash() / self.data)
            self.buy(size=size)
