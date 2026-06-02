import ccxt
import pandas as pd
import numpy as np
import requests

class DataFetching:
    def __init__(self):
        self.btc_option_tickers = []
        self.exchange = ccxt.deribit({
            'enableRateLimit': True
        })

    def get_active_btc_options(self):

        try:
            markets = self.exchange.load_markets()
        except Exception as e:
            print(f'Error Fetching Option Symbol: {e}')
            return None
        
        for symbol, market_info in markets.items():
            if(market_info['base'] == 'BTC' and
              market_info['type'] == 'option' and
              market_info['active'] == True):
                self.btc_option_tickers.append(symbol)
        return self.btc_option_tickers
    
    def get_live_option_market_price(self, instrument_name):
        url = f"https://www.deribit.com/api/v2/public/get_order_book?instrument_name={instrument_name}"
        
        try:
            response = requests.get(url).json()
            result = response['result']
            
            mark_price_btc = result['mark_price']
            
            
            return mark_price_btc
            
        except Exception as e:
            print(f"Error fetching Deribit data: {e}")
            return None
    
    def get_underlying_btc(self, option_symbol='BTC/USDT', timeframe='1m', limit=100):
        try:
            ohlcv = self.exchange.fetch_ohlcv(option_symbol, timeframe=timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volumn'])
            # df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')

            df['Log_Return'] = np.log(df['Close']/df['Close'].shift(1))
            vol_sampled = df['Log_Return'].rolling(window=20).std()
            annual_factor = np.sqrt(365 * 24 * 60)
            df['Rolling_RV'] = vol_sampled * annual_factor
            latest_realized_vol = df['Rolling_RV'].iloc[-1]

            return df, latest_realized_vol
        
        except Exception as e:
            print(f'Error Fetching OHLCV: {e}')

            return None, None

    def fetch_option_order_book(self, option_symbol):
        try:
            order_book = self.exchange.fetch_order_book(option_symbol)
            return order_book
        except Exception as e:
            print(f"Error fetching order book for {option_symbol}: {e}")
            return None
        
if __name__ == "__main__":
    print("--- Starting Data Fetching Engine ---")
    client = DataFetching()
    tickers = client.get_active_btc_options()
    
    if tickers:
        print(f"Successfully found {len(tickers)} active BTC option contracts.\n")
        
        sample_ticker = tickers[0]
        print(f"Testing order book retrieval for: {sample_ticker}")

        order_book = client.fetch_option_order_book(sample_ticker)
        
        if order_book:
            print("\n--- Sample Order Book Data (Top of Book) ---")
            print(f"Highest Bid: {order_book['bids'][0] if order_book['bids'] else 'No Bids'}")
            print(f"Lowest Ask: {order_book['asks'][0] if order_book['asks'] else 'No Asks'}")
    else:
        print("No active tickers retrieved. Check your network or exchange connection.")

    timeframe_to_test = '1m'
    history_df, calculated_rv = client.get_underlying_btc(timeframe=timeframe_to_test, limit=50)
    
    if calculated_rv is not None:
        print("\n--- Underlying Price Data Sample ---")
        print(history_df[['Timestamp', 'Close', 'Log_Return']].tail(5))
        print("------------------------------------")
        print(f"Calculated Annualized Realized Volatility (RV) based on last 50 candles ({timeframe_to_test}): {calculated_rv * 100:.2f}%")

    live_price = client.get_live_option_market_price("BTC-26JUN26-70000-C")
    print(f"Deribit Live Option Mark Price (in BTC): {live_price}")