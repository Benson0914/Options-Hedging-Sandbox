import numpy as np
from scipy.stats import norm
from src.GreeksandPrice import Greek_and_Price

class Implied_Volatility:
    def __init__(self, market_price, spot_price, strike_price, time_to_expiry, rate=0.0, option_type='call'):
        self.market_price = float(market_price)
        self.S = float(spot_price)
        self.K = float(strike_price)
        self.T = float(time_to_expiry)
        self.r = float(rate)
        self.option_type = str(option_type).lower()
    
    def calculate_IV(self):
        current_vol = 0.50
        
        for _ in range(20):
            engine = Greek_and_Price(self.S, self.K, self.T, current_vol, self.r, self.option_type)
            metrics = engine.bs_greek_and_price()
            
            price_diff = metrics['price'] - self.market_price
            vega = metrics['vega']
            
            # Precision tolerance check
            if abs(price_diff) < 1e-5:
                return current_vol

            if abs(vega) < 1e-6:
                break
                
            current_vol = current_vol - (price_diff / vega)
            
            if current_vol <= 0.0001 or current_vol > 3.0:
                break
        low_vol, high_vol = 0.0001, 5.0
        
        for _ in range(60):
            mid_vol = (low_vol + high_vol) / 2
            
            engine = Greek_and_Price(self.S, self.K, self.T, mid_vol, self.r, self.option_type)
            mid_price = engine.bs_greek_and_price()['price']
            
            if abs(mid_price - self.market_price) < 1e-5:
                return mid_vol
                
            if mid_price > self.market_price:
                high_vol = mid_vol
            else:
                low_vol = mid_vol

        return mid_vol
    
if __name__ == '__main__':
    print("Executing IV mathematical engine...")

    test_S = 76000.0
    test_K = 76000.0
    test_T = 2 / 365.0
    test_true_iv = 0.2
    
    pricing_engine = Greek_and_Price(test_S, test_K, test_T, test_true_iv, rate=0.0, option_type='call')
    generated_market_price = pricing_engine.bs_greek_and_price()['price']
    
    print(f"Generated Benchmark Market Price: ${generated_market_price:.4f}")

    iv_solver = Implied_Volatility(
        market_price=generated_market_price,
        spot_price=test_S,
        strike_price=test_K,
        time_to_expiry=test_T,
        option_type='call'
    )
    
    calculated_iv = iv_solver.calculate_IV()
    print(f"Solved Implied Volatility: {calculated_iv * 100:.2f}%")