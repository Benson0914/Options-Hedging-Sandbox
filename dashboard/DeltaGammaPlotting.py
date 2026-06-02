import numpy as np
import matplotlib.pyplot as plt

from src.GreeksandPrice import Greek_and_Price

try:
    plt.style.use('seaborn-v0_8-whitegrid')
except:
    plt.style.use('default')

class Delta_Gamma_Plotting_Suite:
    def __init__(self, strike_price, rate=0.0, option_type='call'):
        self.K = float(strike_price)
        self.r = float(rate)
        self.option_type = str(option_type).lower()

    def generate_risk_dashboard(self, spot_grid, vol_grid, time_horizons):
        fig, axes = plt.subplots(2, 3, figsize=(16, 10), sharex=True)

        delta_axes = axes[0]
        gamma_axes = axes[1]

        for i, t_val in enumerate(time_horizons):
            ax_delta = delta_axes[i]
            ax_gamma = gamma_axes[i]

            for vol in vol_grid:
                current_deltas = []
                current_gammas = []
                
                for s in spot_grid:
                    engine = Greek_and_Price(s, self.K, t_val, vol, self.r, self.option_type)
                    metrics = engine.bs_greek_and_price()
                    
                    current_deltas.append(metrics['delta'])
                    current_gammas.append(metrics['gamma'])
                
                ax_delta.plot(spot_grid, current_deltas, label=f'IV = {vol*100:.0f}%', lw=2)
                ax_gamma.plot(spot_grid, current_gammas, label=f'IV = {vol*100:.0f}%', lw=2)
            
            ax_delta.axvline(x=self.K, color='red', linestyle='--', alpha=0.6)
            ax_delta.set_title(f'Delta ($\Delta$) | Time: {t_val*365:.1f} Days', fontsize=11, fontweight='bold')
            ax_delta.grid(True, linestyle=':', alpha=0.5)
            if i == 0:
                ax_delta.set_ylabel('Delta Exposure Scale', fontweight='bold')
                ax_delta.legend(loc='lower right', fontsize='small')

            ax_gamma.axvline(x=self.K, color='red', linestyle='--', alpha=0.6)
            ax_gamma.set_title(f'Gamma ($\Gamma$) | Time: {t_val*365:.1f} Days', fontsize=11, fontweight='bold')
            ax_gamma.set_xlabel('Bitcoin Spot Price ($)', labelpad=10)
            ax_gamma.grid(True, linestyle=':', alpha=0.5)
            if i == 0:
                ax_gamma.set_ylabel('Gamma Acceleration Scale', fontweight='bold')

        plt.suptitle(f'Institutional {self.option_type.upper()} Position Risk Matrix (Strike: ${self.K:.0f})', 
                     fontsize=14, fontweight='bold', y=0.96)
        plt.tight_layout(rect=[0, 0.03, 1, 0.93])

        plt.savefig('figures/Delta_Gamma_Plotting.png')
        plt.show()

if __name__ == '__main__':
    spot_axis = np.linspace(60000, 90000, 100)
    vols_to_simulate = [0.15, 0.35, 0.75, 1.20]

    operational_horizons = [2 / 365.0, 15 / 365.0, 60 / 365.0]

    dashboard = Delta_Gamma_Plotting_Suite(strike_price=76000.0, option_type='call')
    
    print("Compiling 6-Graph Risk Dashboard Matrix...")
    dashboard.generate_risk_dashboard(spot_axis, vols_to_simulate, operational_horizons)