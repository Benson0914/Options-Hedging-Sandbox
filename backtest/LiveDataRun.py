import matplotlib.pyplot as plt
import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))

if root_dir not in sys.path:
    sys.path.append(root_dir)

from src.DataFetching import DataFetching
from src.DeltaHedging import Delta_Hedging
from src.GammaScalping import Gamma_Scalping



if __name__ == '__main__':
    data_client = DataFetching()
    underlying, latest_rv = data_client.get_underlying_btc()

    spot_path = underlying['Close']
    time_steps = underlying['Timestamp']
    
    starting_spot = spot_path.iloc[0]
    strike = starting_spot 
    initial_iv = 0.55
    total_time = 5.0 / 365.0
    position_size = 1

    current_perp_inventory = 0

    plt.figure(figsize=(14, 7))

    thresholds_to_test = [0.02, 0.10, 0.25, 0.50]
    
    short_colors = ['#8B0000', '#FF0000', '#FF4500', '#FFA500']
    
    for idx, th in enumerate(thresholds_to_test):
        print(f"Short Straddle Testing (Threshold = {th})...")
        short_desk = Delta_Hedging(
            spot_price=starting_spot, 
            strike_price=strike, 
            total_time=total_time, 
            sigma=initial_iv
        )
        short_res = short_desk.run_delta_hedging(
            spot_grid=spot_path, 
            strike=strike, 
            time_grid=time_steps, 
            position_size=position_size,
            current_perp_inventory=current_perp_inventory,
            delta_threshold=th
        )
        plt.plot(
            short_res['Time Step'], 
            short_res['Cumulative Net PnL'], 
            label=f'Short MM (Th = {th})', 
            color=short_colors[idx], 
            linestyle='--'
        )


    long_colors = ['#006400', '#008000', '#2E8B57', '#008B8B']
    
    for idx, th in enumerate(thresholds_to_test):
        print(f"Gamma Scalping Testing (Threshold = {th})...")
        long_desk = Gamma_Scalping(
            spot_price=starting_spot, 
            strike_price=strike, 
            total_time=total_time, 
            sigma=initial_iv
        )
        long_res = long_desk.run_gamma_scalping(
            spot_grid=spot_path, 
            strike=strike, 
            time_grid=time_steps, 
            position_size=position_size,
            delta_threshold=th
        )
        plt.plot(
            long_res['Time Step'], 
            long_res['Cumulative Net PnL'], 
            label=f'Long Scalper (Th = {th})', 
            color=long_colors[idx], 
            linestyle='-'
        )

    plt.axhline(0, color='black', linestyle='-', alpha=0.4)
    plt.title('The Sandbox Arena: Short MM vs Long Scalper (Full Multi-Threshold Matrix)', fontsize=14)
    plt.xlabel('Time Steps (Intraday Realized Volatility Path)', fontsize=12)
    plt.ylabel('Cumulative Net PnL After Costs (USD)', fontsize=12)
    plt.grid(True, which='both', linestyle=':', alpha=0.5)

    plt.legend(fontsize=10, loc='upper left', bbox_to_anchor=(1, 1))
    plt.tight_layout()

    plt.savefig('figures/PnL_LiveData.png')
    plt.show()