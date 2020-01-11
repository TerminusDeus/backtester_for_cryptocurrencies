from datetime import datetime
import backtrader as bt
import matplotlib as mpl

from bittrex_dataframe_fetcher import get_ticks_as_pandas_df, Tick_interval, Script_error, TICK_INTERVAL_LIST
from strategies import SmaCrossoverStrategy

# for plots visualization:
mpl.use('Qt5Agg')

MARKET = 'BTC-NEO'

MARKETS = ['USDT-BTC', 'USDT-BCC', 'USDT-ETC', 'USDT-OMG', 'USDT-XRP', 'USDT-LTC', 'USDT-ZEC', 'USDT-XMR', 'USDT-DASH',
           MARKET]

BITTREX_CASH = 10000.00

BITTREX_COMMISSION = 0.001


def main(tick_interval, market=MARKET):
    if tick_interval is None or tick_interval not in TICK_INTERVAL_LIST:
        raise Script_error('Tick interval is not defined')
    pandas_df = get_ticks_as_pandas_df(market=market, tick_interval=tick_interval)
    pandas_df.set_index(pandas_df['datetime'], inplace=True)  # set dt as index for cerebro
    pandas_df['openinterest'] = 0
    cerebro = bt.Cerebro()  # create a Cerebro engine instance
    cerebro.addstrategy(SmaCrossoverStrategy)
    cerebro.adddata(bt.feeds.PandasData(dataname=pandas_df, fromdate=datetime(2019, 1, 1)))
    cerebro.broker.setcommission(BITTREX_COMMISSION)
    cerebro.broker.setcash(BITTREX_CASH)
    print('Launching strategy {0}'.format(SmaCrossoverStrategy.__name__))
    print('Starting portfolio ({}, {}): {:.2f}'.format(market, tick_interval, cerebro.broker.getvalue()))
    cerebro.run()
    print('Final portfolio ({}, {}): {:.2f}'.format(market, tick_interval, cerebro.broker.getvalue()))
    cerebro.plot()  # plot performance is poor: misleading good and bad sells (e.g. ThreeSoldiersAndCrows)


for m in [MARKET]:
    main(Tick_interval.DAY, m)
