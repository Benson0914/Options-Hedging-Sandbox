import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from src.GreeksandPrice import Greek_and_Price
from src.DataFetching import DataFetching
from src.DeltaHedging import Delta_Hedging

class Gamma_Scalping:
    def __init__(self, spot_price, strike_price, total_time, sigma, rate=0.0):
        self.S = float(spot_price)
        self.K = float(strike_price)
        self.T = float(total_time)
        self.sigma = float(sigma)
        self.r = float(rate)

    def run_gamma_scalping(self, spot_grid, strike, time_grid, position_size, initial_perp_inventory=0.0, delta_threshold=0.15):
        hedge_log = []
        total_steps = len(spot_grid)
        
        call_position = position_size
        put_position = position_size

        fee_rate = 0.0003
        slippage_btc = 0.5

        total_fees_paid = 0.0
        total_slippage_cost = 0.0
        last_options_value = None
        last_spot = None
        
        current_perp_inventory = float(initial_perp_inventory)

        for step in range(total_steps):
            Spots = spot_grid.iloc[step]
            time_left = self.T * (1 - (step / total_steps))

            if time_left <= 0: time_left = 1e-6

            call_engine = Greek_and_Price(spot_price=Spots, strike_price=strike, time=time_left, sigma=self.sigma, option_type="call")
            put_engine = Greek_and_Price(spot_price=Spots, strike_price=strike, time=time_left, sigma=self.sigma, option_type="put")
            
            call_metrics = call_engine.bs_greek_and_price()
            put_metrics = put_engine.bs_greek_and_price()
            
            current_straddle_price = call_metrics['price'] + put_metrics['price']
            current_options_value = current_straddle_price * position_size

            portfolio_delta = (call_metrics['delta'] * call_position) + (put_metrics['delta'] * put_position)
            total_delta_exposure = portfolio_delta + current_perp_inventory

            perp_trade_required = 0.0

            if abs(total_delta_exposure) > delta_threshold:
                perp_trade_required = -total_delta_exposure 

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

            step_raw_pnl = options_pnl + perp_pnl
            step_net_pnl = step_raw_pnl - step_fee - step_slippage

            current_perp_inventory += perp_trade_required

            last_options_value = current_options_value
            last_spot = Spots

            hedge_log.append({
                "Time Step": step + 1,
                "BTC Spot": Spots,
                "Net Options Delta": round(portfolio_delta, 4),
                "Current Perp Inv": round(current_perp_inventory, 4),
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
        return df