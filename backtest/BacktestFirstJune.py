import matplotlib.pyplot as plt
import pandas as pd
from src.DeltaHedging import Delta_Hedging
from src.GammaScalping import Gamma_Scalping



if __name__ == '__main__':
    underlying =  pd.read_csv('data/btc_1m_first_june_data.csv')


    spot_path = underlying['Close']
    time_steps = underlying['Timestamp']
    
    starting_spot = spot_path.iloc[0]
    strike = starting_spot 
    initial_iv = 0.55
    total_time = 5.0 / 365.0
    position_size = 1

    current_perp_inventory = 0
    thresholds_to_test = [0.01, 0.05, 0.10, 0.25, 0.50]
    matrix_rows = []

    plt.figure(figsize=(14, 7))

    for th in thresholds_to_test:
        short_desk = Delta_Hedging(
            spot_price=starting_spot, strike_price=strike, total_time=total_time, sigma=initial_iv
        )

        short_res, metrics = short_desk.run_delta_hedging(
            spot_grid=spot_path, strike=strike, time_grid=time_steps, position_size=position_size, current_perp_inventory=current_perp_inventory, delta_threshold=th
        )
        

        plt.plot(short_res['Time Step'], short_res['Cumulative Net PnL'], label=f'Short MM (Th={th})', linestyle='--')

        matrix_rows.append({
            'Strategy': 'Short Straddle (MM)',
            'Threshold': th,
            'Hedge Count': metrics['hedge_count'],
            'Avg Hedging Error': f"{metrics['avg_hedging_error']:.4f}",
            'Transaction Cost': f"${metrics['total_tx_cost']:.2f}",
            'Final PnL': f"${short_res['Cumulative Net PnL'].iloc[-1]:.2f}"
        })

    for th in thresholds_to_test:
        long_desk = Gamma_Scalping(
            spot_price=starting_spot, strike_price=strike, total_time=total_time, sigma=initial_iv
        )
        long_res, metrics = long_desk.run_gamma_scalping(
            spot_grid=spot_path, strike=strike, time_grid=time_steps, position_size=position_size, delta_threshold=th
        )
        
        plt.plot(long_res['Time Step'], long_res['Cumulative Net PnL'], label=f'Long Scalper (Th={th})', linestyle='-')
        
        matrix_rows.append({
            'Strategy': 'Long Scalper',
            'Threshold': th,
            'Hedge Count': metrics['hedge_count'],
            'Avg Hedging Error': f"{metrics['avg_hedging_error']:.4f}",
            'Transaction Cost': f"${metrics['total_tx_cost']:.2f}",
            'Final PnL': f"${long_res['Cumulative Net PnL'].iloc[-1]:.2f}"
        })

    perf_matrix = pd.DataFrame(matrix_rows)
    
    print("\n" + "="*80)
    print("QUANT PERFORMANCE ATTRIBUTION MATRIX")
    print("="*80)
    print(perf_matrix.to_string(index=False))
    print("="*80 + "\n")
    
    perf_matrix.to_csv('backtest/performance_matrix.csv', index=False)
    print("Imported backtest/performance_matrix.csv")

    plt.axhline(0, color='black', linestyle='-', alpha=0.3)
    plt.title('Sandbox Arena PnL Tracking')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig('figures/First_June_Backtest.png')
    plt.show()