- compare backtrader performance with another backtesting frameworks/create framework
- investigate model performance via cerebro instance parameters
- data with testing results could be stored in some db for further investigation
- inspect other adddata parameters: cerebro.adddata(bt.feeds.PandasData(dataname=pandas_df, fromdate=datetime(2019, 1, 1)))
- define certain value as described in link below
 https://bittrex.zendesk.com/hc/en-us/articles/115003684371-BITTREX-SERVICE-FEES-AND-WITHDRAWAL-LIMITATIONS
 https://bitcoin.stackexchange.com/questions/67521/how-to-get-bittrex-commission-value-from-api
 '0.25%' commission on a trade
 BITTREX_COMMISSION = 0.001
