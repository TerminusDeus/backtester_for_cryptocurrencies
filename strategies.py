from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import backtrader as bt

# Working
# Data since 2019, 1, 1:
# Starting portfolio (BTC-NEO, fiveMin): 10000.00
# Final portfolio (BTC-NEO, fiveMin): 17036.00
# Starting portfolio (BTC-NEO, day): 10000.00
# Final portfolio (BTC-NEO, day): 1440.23
# Starting portfolio (BTC-NEO, oneMin): 10000.00
# Final portfolio (BTC-NEO, oneMin): 10570.51
# https://github.com/NicholasTanWeiHong/backtrader-with-brent-futures/blob/master/extensions/strategies.py
from backtrader.indicators import MovAv


class SmaCrossoverStrategy(bt.SignalStrategy):
    """
    Simple Moving Average Crossover Strategy.

    Description
    -----------
    This strategy generates a signal when the short SMA crosses the long SMA.
    A Buy trade is made when the short SMA crosses above the long SMA,
    and a Sell trade is made when the short SMA crosses below the long SMA.
    """

    params = (
        ('sma1_period', 10),
        ('sma2_period', 30),
        ('opt_mode', False)
    )

    def __init__(self):
        sma1 = bt.ind.SMA(period=self.params.sma1_period)
        sma2 = bt.ind.SMA(period=self.params.sma2_period)
        crossover_signal = bt.ind.CrossOver(sma1, sma2)
        self.signal_add(sigtype=bt.signal.SIGNAL_LONG, signal=crossover_signal)

    def stop(self):
        if self.params.opt_mode is True:
            param_1 = self.params.sma1_period
            param_2 = self.params.sma2_period
            port_value = round(self.broker.getvalue(), 2)
            print(
                'MA1 Period: %d, MA2 Period: %d, Final Portfolio Value: $%.2f'
                % (param_1, param_2, port_value))


# Working (but not for all tick intervals)
# https://github.com/NicholasTanWeiHong/backtrader-with-brent-futures/blob/master/extensions/strategies.py
class RSIMeanReversionSystem(bt.Strategy):
    """
    RSI Mean Reversion Strategy.

    Description
    -----------
    This strategy generates an 'RSI Index' based on the Close of the asset.
    When the RSI Index enters 'oversold' territory (i.e. < 30),
    a Buy trade is initiated.
    Conversely, when the RSI Index enters 'overbought' territory (i.e. > 70),
    a Sell trade is initiated.
    """

    params = (
        ('rsi_period', 14),
        ('opt_mode', False)
    )

    def __init__(self):
        self.rsi = bt.ind.RSI_SMA(
            self.data.close, period=self.params.rsi_period
        )

    def next(self):
        if not self.position:
            if self.rsi < 30:
                self.buy()
        else:
            if self.rsi > 70:
                self.sell()

    def stop(self):
        if self.params.opt_mode is True:
            param = self.params.rsi_period
            port_value = round(self.broker.getvalue(), 2)
            print('RSI Period: %d, Final Portfolio Value: $%.2f'
                  % (param, port_value))


# Working
# https://github.com/NicholasTanWeiHong/backtrader-with-brent-futures/blob/master/extensions/strategies.py
# result depends on time frame: the best one is for 'day':
# Starting portfolio value: 10000.00
# Final portfolio value: 46118.57
class ThreeSoldiersAndCrows(bt.Strategy):
    """
    Three Solders and Crows Strategy.

    Description
    -----------
    This strategy analyzes the number of consecutively bullish/bearish candles.
    If it encounters three consecutively bearish candles,
    a Buy trade is initiated.
    If it encounters three consecutively bullish candles,
    a Sell trade is initiated.
    """

    def __init__(self):
        self.dataclose = self.data.close

    def next(self):
        if not self.position:
            if self.dataclose[0] < self.dataclose[-1]:
                if self.dataclose[-1] < self.dataclose[-2]:
                    if self.dataclose[-2] < self.dataclose[-3]:
                        self.buy()
        else:
            if self.dataclose[0] > self.dataclose[-1]:
                if self.dataclose[-1] > self.dataclose[-2]:
                    if self.dataclose[-2] > self.dataclose[-3]:
                        self.sell()


# Not working
# https://towardsdatascience.com/backtesting-your-first-trading-strategy-ad3977f3f2a
# not works for my pandas.core.frame.DataFrame from bittrex
class SmaCross(bt.Strategy):
    # list of parameters which are configurable for the strategy:
    params = dict(
        pfast=10,  # period for the fast moving average
        pslow=30  # period for the slow moving average
    )

    def __init__(self):
        sma1 = bt.ind.SMA(period=self.p.pfast)  # fast moving average
        sma2 = bt.ind.SMA(period=self.p.pfast)  # slow moving average
        self.crossover = bt.ind.CrossOver(sma1, sma2)  # crossover signal

    def next(self):
        if not self.position:  # not in the market
            if self.crossover > 0:  # if fast crosses slow to the upside
                self.buy()  # enter long
            elif self.crossover < 0:  # in the market & cross to the downside
                self.close()  # close long position


class SmaCross2(bt.SignalStrategy):

    def log(self, txt, dt=None):
        dt = dt or self.data.datetime.date(0)
        print('{}, {}'.format(dt.isoformat(), txt))

    def __init__(self):
        self.dataclose = self.data.close
        self.sma = bt.ind.SMA(period=20)

    def next(self):
        self.log('Close, {:.2f}'.format(self.dataclose[0]))
        if self.sma > self.data.close:
            self.buy()

        elif self.sma < self.data.close:
            self.sell()


# Working
# BTC-ETH: show best results with increase of tick interval; anyway all of them are bad
# https://github.com/narala558/documents/blob/4be1361df83d8028155dab0a5d7f5647499a3e06/python/btstrategies.py
class BBandsStrategy(bt.Strategy):
    params = (('BBandsperiod', 20),)

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.redline = None
        self.blueline = None

        # Add a BBand indicator
        self.bband = bt.indicators.BBands(self.datas[0], period=self.params.BBandsperiod)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enougth cash
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        if self.dataclose < self.bband.lines.bot and not self.position:
            self.redline = True

        if self.dataclose > self.bband.lines.top and self.position:
            self.blueline = True

        if self.dataclose > self.bband.lines.mid and not self.position and self.redline:
            # BUY, BUY, BUY!!! (with all possible default parameters)
            self.log('BUY CREATE, %.2f' % self.dataclose[0])
            # Keep track of the created order to avoid a 2nd order
            self.order = self.buy()

        if self.dataclose > self.bband.lines.top and not self.position:
            # BUY, BUY, BUY!!! (with all possible default parameters)
            self.log('BUY CREATE, %.2f' % self.dataclose[0])
            # Keep track of the created order to avoid a 2nd order
            self.order = self.buy()

        if self.dataclose < self.bband.lines.mid and self.position and self.blueline:
            # SELL, SELL, SELL!!! (with all possible default parameters)
            self.log('SELL CREATE, %.2f' % self.dataclose[0])
            self.blueline = False
            self.redline = False
            # Keep track of the created order to avoid a 2nd order
            self.order = self.sell()


# Working (but only for usd(t)-btc pairs)
# https://github.com/verybadsoldier/backtrader_plotting/blob/87034bf4dc12ba70bafea9cf7aea0fd03cd1421c/tests/test_issue10.py
class MACDStrategy(bt.Strategy):
    params = (
        # Standard MACD Parameters
        ('macd1', 12),
        ('macd2', 26),
        ('macdsig', 9),
    )

    def __init__(self):
        self.macd = bt.indicators.MACD(self.data,
                                       period_me1=self.p.macd1,
                                       period_me2=self.p.macd2,
                                       period_signal=self.p.macdsig)
        # backtrader.LinePlotterIndicator(macd, name='MACD')
        # Cross of macd.macd and macd.signal
        self.mcross = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)

    # backtrader.LinePlotterIndicator(mcross, name='MACDCross')

    def start(self):
        self.order = None  # sentinel to avoid operations on pending order

    def log(self, txt, dt=None):
        """ Logging function for this strategy
        """
        dt = dt or self.datas[0].datetime.date(0)
        time = self.datas[0].datetime.time()
        print('%s,%s' % (dt.isoformat(), txt))

    def next(self):
        if self.order:
            return  # pending order execution

        if not self.position:  # not in the market
            if self.mcross[0] > 0.0 and self.macd.lines.signal[0] > 0 and self.macd.lines.macd[0] > 0:
                self.order = self.buy()
                self.log('BUY CREATED, %.2f' % self.data[0])
        # else:
        # 	if self.mcross[0] > 0.0 and self.macd.lines.signal[0] < 0 and self.macd.lines.macd[0] < 0:
        # 		self.order = self.buy()
        # 		self.log('BUY CREATED, %.2f' % self.data[0])

        else:  # in the market
            if self.mcross[0] < 0.0 and self.macd.lines.signal[0] < 0 and self.macd.lines.macd[0] < 0:
                self.sell()  # stop met - get out
                self.log('BUY CREATED, %.2f' % self.data[0])
        # else:
        # 	if self.mcross[0] < 0.0 and self.macd.lines.signal[0] > 0 and self.macd.lines.macd[0] > 0:
        # 		self.sell()  # stop met - get out
        # 		self.log('BUY CREATED, %.2f' % self.data[0]


#######################################################################################################################
################################## UNKNOWN STRATEGIES #################################################################
#######################################################################################################################
# Not checked
# https://github.com/narala558/documents/blob/4be1361df83d8028155dab0a5d7f5647499a3e06/python/sm_backtrader.py
class SmaCross3(bt.SignalStrategy):
    params = (('pfast', 10), ('pslow', 30),)

    def __init__(self):
        sma1, sma2 = bt.ind.SMA(period=self.p.pfast), bt.ind.SMA(period=self.p.pslow)
        self.signal_add(bt.SIGNAL_LONG, bt.ind.CrossOver(sma1, sma2))


# Not checked
# https://github.com/narala558/documents/blob/4be1361df83d8028155dab0a5d7f5647499a3e06/python/sm_backtrader.py
class SupertrendCross(bt.SignalStrategy):
    params = ()

    def __init__(self):
        sma1, sma2 = bt.ind.SMA(period=self.p.pfast), bt.ind.SMA(period=self.p.pslow)
        self.signal_add(bt.SIGNAL_LONG, bt.ind.CrossOver(sma1, sma2))


# Not checked
# https://github.com/narala558/documents/blob/4be1361df83d8028155dab0a5d7f5647499a3e06/python/sm_backtrader.py
class RenkoCross(bt.SignalStrategy):
    params = ()

    def __init__(self):
        sma1, sma2 = bt.ind.SMA(period=self.p.pfast), bt.ind.SMA(period=self.p.pslow)
        self.signal_add(bt.SIGNAL_LONG, bt.ind.CrossOver(sma1, sma2))


class QFL(bt.SignalStrategy):
    params = ()
