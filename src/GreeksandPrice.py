import numpy as np
from scipy.stats import norm

class Greek_and_Price:
    def __init__(self, spot_price, strike_price, time, sigma, rate=0.0, option_type='call'):
        self.S = float(spot_price)
        self.K = float(strike_price)
        self.T = float(time)
        self.sigma = float(sigma)
        self.r = float(rate)
        self.option_type = str(option_type)

    def bs_greek_and_price(self):
        if self.T <= 0 or self.sigma <= 0:
            if self.option_type == 'call':
                price = max(0, self.S - self.K)
                delta = 1 if self.S > self.K else 0
            else:
                price = max(0, self.K - self.S)
                delta = -1 if self.S < self.K else 0
            return {'price': price, 'delta': delta, 'gamma': 0, 'vega': 0, 'theta': 0}
        
        d1 = (np.log(self.S/self.K) + (self.r + self.sigma**2/2)*self.T)/(self.sigma*np.sqrt(self.T))
        d2 = d1 - self.sigma*np.sqrt(self.T)

        N_d1 = norm.cdf(d1)
        N_d2 = norm.cdf(d2)
        n_prime_d1 = norm.pdf(d1)

        result = {}

        if self.option_type == 'call':
            result['price'] = self.S*N_d1 - self.K*np.exp(-self.r*self.T)*N_d2
            result['delta'] = N_d1
            theta_call = (- (self.S * n_prime_d1 * self.sigma) / (2 * np.sqrt(self.T)) 
                      - self.r * self.K * np.exp(-self.r * self.T) * N_d2)
            result['theta'] = theta_call/365
            
        elif self.option_type == 'put':
            result['price'] = self.K * np.exp(-self.r * self.T) * norm.cdf(-d2) - self.S * norm.cdf(-d1)
            result['delta'] = N_d1 - 1
            theta_call = (- (self.S * n_prime_d1 * self.sigma) / (2 * np.sqrt(self.T)) 
                     + self.r * self.K * np.exp(-self.r * self.T) * norm.cdf(-d2))
            result['theta'] = theta_call/365
        else:
            raise ValueError("option_type must be either 'call' or 'put'")

        result['gamma'] = n_prime_d1 / (self.S*self.sigma*np.sqrt(self.T))
        result['vega'] = (self.S*np.sqrt(self.T)*n_prime_d1) / 100

        return result

if __name__ == '__main__':
    print("Executing Black-Scholes mathematical engine...")

    spot_test = 76000.0
    strike_test = 76000.0
    expiry_test = 2 / 365.0
    vol_test = 0.5
    
    call_greeks = Greek_and_Price(
        spot_price=spot_test, 
        strike_price=strike_test, 
        time=expiry_test, 
        sigma=vol_test, 
        option_type="call")
    
    put_greeks = Greek_and_Price(
        spot_price=spot_test, 
        strike_price=strike_test, 
        time=expiry_test, 
        sigma=vol_test, 
        option_type="put")
    
    print("\n--- ATM Call Metrics ---")
    for greek, val in call_greeks.bs_greek_and_price().items():
        print(f"{greek.capitalize():<8}: {val:.4f}")
        
    print("\n--- ATM Put Metrics ---")
    for greek, val in put_greeks.bs_greek_and_price().items():
        print(f"{greek.capitalize():<8}: {val:.4f}")
