import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from src.GreeksandPrice import Greek_and_Price
from src.DataFetching import DataFetching

class Delta_Hedging:
    def __init__(self, spot_price, strike_price, total_time, sigma, rate=0.0):
        self.S = float(spot_price)
        self.K = float(strike_price)
        self.T = float(total_time)
        self.sigma = float(sigma)
        self.r = float(rate)

    def run_delta_hedging(self, spot_grid, strike, time_grid, position_size, current_perp_inventory=0.0, delta_threshold = 0.15):
        hedge_log = []
        total_steps = len(spot_grid)
        
        call_position = -position_size
        put_position = -position_size

        fee_rate = 0.0003
        slippage_btc = 0.5

        total_fees_paid = 0.0
        total_slippage_cost = 0.0
        hedge_count = 0
        hedging_errors = []
        
        last_options_value = None
        last_spot = None

        for step in range(total_steps):
            Spots = spot_grid.iloc[step]
            time_left = self.T * (1 - (step / total_steps))

            if time_left <= 0: time_left = 1e-6

            call_engine = Greek_and_Price(spot_price=Spots, strike_price=strike, time=time_left, sigma=self.sigma, option_type="call")
            put_engine = Greek_and_Price(spot_price=Spots, strike_price=strike, time=time_left, sigma=self.sigma, option_type="put")
            
            call_metrics = call_engine.bs_greek_and_price()
            put_metrics = put_engine.bs_greek_and_price()
            
            current_straddle_price = call_metrics['price'] + put_metrics['price']
            current_options_value = current_straddle_price * (-position_size)

            portfolio_delta = (call_metrics['delta'] * call_position) + (put_metrics['delta'] * put_position)
            
            total_delta_exposure = portfolio_delta + current_perp_inventory
            hedging_errors.append(abs(total_delta_exposure))

            perp_trade_required = 0.0
            if abs(total_delta_exposure) > delta_threshold:
                perp_trade_required = -total_delta_exposure
                hedge_count += 1

            options_pnl = 0.0
            perp_pnl = 0.0
            step_fee = 0.0
            step_slippage = 0.0

            if step > 0:
                options_pnl = current_options_value - last_options_value
                perp_pnl = current_perp_inventory * (Spots - last_spot)
                
            if abs(perp_trade_required) > 1e-6:
                step_fee = abs(perp_trade_required) * Spots * fee_rate
                step_slippage = abs(perp_trade_required) * slippage_btc
                
                total_fees_paid += step_fee
                total_slippage_cost += step_slippage
                
                current_perp_inventory += perp_trade_required

            step_raw_pnl = options_pnl + perp_pnl
            step_net_pnl = step_raw_pnl - step_fee - step_slippage

            last_options_value = current_options_value
            last_spot = Spots

            hedge_log.append({
                "Time Step": step + 1,
                "BTC Spot": Spots,
                "Net Options Delta": round(portfolio_delta, 4),
                "Current Perp Inventory": round(current_perp_inventory, 4),
                "Trade Executed (Perps)": round(perp_trade_required, 4),
                "Options PnL": round(options_pnl, 2),
                "Perp PnL": round(perp_pnl, 2),
                "Trading Fee Paid": round(step_fee, 4),
                "Slippage Cost": round(step_slippage, 4),
                "Raw PnL (No Cost)": round(step_raw_pnl, 2),
                "Net PnL (After Cost)": round(step_net_pnl, 2),
            })
            
        df = pd.DataFrame(hedge_log)

        df['Cumulative Raw PnL'] = df['Raw PnL (No Cost)'].cumsum()
        df['Cumulative Net PnL'] = df['Net PnL (After Cost)'].cumsum()

        metrics_summary = {
            "hedge_count": hedge_count,
            "avg_hedging_error": np.mean(hedging_errors),
            "total_tx_cost": total_fees_paid + total_slippage_cost
        }
        
        return df, metrics_summary

if __name__ == '__main__':
    data_client = DataFetching()
    underlying, latest_rv = data_client.get_underlying_btc()

    starting_spot = underlying['Close'].iloc[0]
    strike = starting_spot 
    initial_iv = 0.55
    total_time = 5.0 / 365.0

    spot_path = underlying['Close']
    time_steps = underlying['Timestamp']
    position_size = 10
    current_perp_inventory = 0

    DELTAHEDGING = Delta_Hedging(
        spot_price=starting_spot, 
        strike_price=strike, 
        total_time=total_time,
        sigma=initial_iv
    )
    
    test_result_df = DELTAHEDGING.run_delta_hedging(
        spot_grid=spot_path, 
        strike=strike, 
        time_grid=time_steps, 
        position_size=position_size, 
        current_perp_inventory=current_perp_inventory
    )
    
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    print(test_result_df.head(20))