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
        # --- Stage 1: Newton-Raphson Loop (Fast Convergence) ---
        current_vol = 0.50  # Initial guess (50% IV)
        
        for _ in range(20): # 20 iterations are more than enough for Newton to converge
            # Instantiate engine with the dynamically changing current_vol
            engine = Greek_and_Price(self.S, self.K, self.T, current_vol, self.r, self.option_type)
            metrics = engine.bs_greek_and_price()
            
            price_diff = metrics['price'] - self.market_price
            vega = metrics['vega']
            
            # Precision tolerance check
            if abs(price_diff) < 1e-5:
                return current_vol
                
            # Avoid division by zero if vega collapses to 0 (Deep OTM/ITM options)
            if abs(vega) < 1e-6:
                break
                
            # Correct Newton-Raphson adjustment: step = diff / vega
            current_vol = current_vol - (price_diff / vega)
            
            # Boundary defense: if vol goes negative or too high, abort Newton and switch to Bisection
            if current_vol <= 0.0001 or current_vol > 3.0:
                break
        
        # --- Stage 2: Bisection Loop (Fallback Safety Net) ---
        low_vol, high_vol = 0.0001, 5.0
        
        for _ in range(60): # 60 iterations provide extreme numerical precision
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

    # Verification Step:
    # Let's generate a theoretical call price using an active engine at 55% IV first
    test_S = 76000.0
    test_K = 76000.0
    test_T = 2 / 365.0
    test_true_iv = 0.2
    
    pricing_engine = Greek_and_Price(test_S, test_K, test_T, test_true_iv, rate=0.0, option_type='call')
    generated_market_price = pricing_engine.bs_greek_and_price()['price']
    
    print(f"Generated Benchmark Market Price: ${generated_market_price:.4f}")

    # Now, use our Implied_Volatility engine to see if it can back out the exact 55% IV
    iv_solver = Implied_Volatility(
        market_price=generated_market_price,
        spot_price=test_S,
        strike_price=test_K,
        time_to_expiry=test_T,
        option_type='call'
    )
    
    calculated_iv = iv_solver.calculate_IV()
    print(f"Solved Implied Volatility: {calculated_iv * 100:.2f}%")