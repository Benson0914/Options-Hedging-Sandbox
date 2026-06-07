import ccxt
import pandas as pd
import numpy as np
import time


def fetch_historical_data(symbol, timeframe, start_date, end_date):
    exchange = ccxt.binance()
    
    since = exchange.parse8601(start_date)
    end = exchange.parse8601(end_date)
    
    all_ohlcv = []
    
    while since < end:
        print(f"Fetching data from {exchange.iso8601(since)}...")

        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since, limit=1000)
        
        if not ohlcv:
            break
            
        since = ohlcv[-1][0] + 60000
        all_ohlcv.extend(ohlcv)
        
        time.sleep(exchange.rateLimit / 1000)
        
    df = pd.DataFrame(all_ohlcv, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
    return df

df = fetch_historical_data('BTC/USDT', '1m', '2026-06-01T00:00:00Z', '2026-06-04T23:59:00Z')

df.to_csv('data/btc_1m_first_june_data.csv', index=False)
print("Downloaded btc_1m_first_june_data.csv")