import hashlib
import hmac
import http.client
import json
import os
import time
import urllib
import pandas as pd
import requests

# bittrex API data:
API_URL = 'bittrex.com'
API_VERSION = 'v1.1'
API_KEY = os.getenv("BITTREX_API_KEY")
API_SECRET = os.getenv("BITTREX_API_SECRET")


# custom exception class:
class Script_error(Exception):
    pass


class Tick_interval:
    DAY = 'day'
    ONE_MIN = 'oneMin'
    FIVE_MIN = 'fiveMin'
    HOUR = 'hour'
    THIRTY_MIN = 'thirtyMin'


TICK_INTERVAL_LIST = [
    Tick_interval.DAY,
    Tick_interval.FIVE_MIN,
    Tick_interval.ONE_MIN,
    Tick_interval.HOUR,
    Tick_interval.THIRTY_MIN
]


# for calling bittrex API v1.1:
def call_bittrex_api(**kwargs):
    http_method = kwargs.get('http_method') if kwargs.get('http_method', '') else 'POST'
    method = kwargs.get('method')
    nonce = str(int(round(time.time())))
    payload = {
        'nonce': nonce
    }
    if kwargs:
        payload.update(kwargs)
    # call private bittrex API:
    uri = "https://" + API_URL + "/api/" + API_VERSION + method + '?apikey=' + API_KEY + '&nonce=' + nonce
    uri += urllib.parse.urlencode(payload)
    payload = urllib.parse.urlencode(payload)
    api_sign = hmac.new(API_SECRET,
                        uri.encode(),
                        hashlib.sha512).hexdigest()
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Key": API_KEY,
               "apisign": api_sign}
    conn = http.client.HTTPSConnection(API_URL, timeout=60)
    conn.request(http_method, uri, payload, headers)
    response = conn.getresponse().read()
    conn.close()
    try:
        obj = json.loads(response.decode('utf-8'))
        if 'error' in obj and obj['error']:
            raise Script_error(obj['error'])
        return obj
    except json.decoder.JSONDecodeError:
        raise Script_error('JSON decoding error: ', response)


# get: data from exchange and use it for indicators create
# returns: pandas.core.frame.DataFrame
def get_ticks_as_pandas_df(market, tick_interval=Tick_interval.FIVE_MIN, custom_columns=None):
    if custom_columns is None:
        custom_columns = ['BV', 'close', 'high', 'low', 'open', 'datetime', 'volume']

    # call request from public API v2.0 in order to get candles data:
    res = requests.get(
        "https://bittrex.com/Api/v2.0/pub/market/GetTicks?marketName=" + market + "&tickInterval=" + tick_interval)

    # chart_data_list data looks like this:
    # {'O': 4108.35, 'H': 4127.3505856, 'L': 4107.48140511, 'C': 4119.94932639, 'V': 11.89918058,
    # 'T': '2019-02-23T20:00:00', 'BV': 48970.62666842}

    chart_data_list = json.loads(res.text)['result']  # <class 'list'>
    chart_data_pandas_df = pd.DataFrame(chart_data_list)

    #  expected df.head() is:
    #        O         H         L         C            V                    T         BV
    # 0  0.006900  0.080000  0.006667  0.007000  3123.423352  2015-08-14T00:00:00  29.545465

    chart_data_pandas_df = chart_data_pandas_df.dropna()  # drop the missing values in the dataset using the dropna()
    try:
        # mask defined columns
        chart_data_pandas_df.columns = ['BV', 'close', 'high', 'low', 'open', 'datetime', 'volume']
    except ValueError:
        return

    chart_data_pandas_df = chart_data_pandas_df[custom_columns]  # select only custom columns
    chart_data_pandas_df['datetime'] = pd.to_datetime(chart_data_pandas_df['datetime'])

    #  expected df.head() is:
    #     T             BV     close      high       low         open   datetime     volume  openinterest
    # 2015-08-14  0.006900  0.080000  0.006667  0.007000  3123.423352 2015-08-14  29.545465             0

    return chart_data_pandas_df
