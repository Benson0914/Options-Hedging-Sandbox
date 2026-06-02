import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from src.GreeksandPrice import Greek_and_Price

try:
    plt.style.use('seaborn-v0_8-whitegrid')
except:
    plt.style.use('default')

class Greeks_Surface_Engine:
    def __init__(self, strike_price, sigma, rate=0.0, option_type='call'):
        self.K = float(strike_price)
        self.sigma = float(sigma)
        self.r = float(rate)
        self.option_type = str(option_type).lower()

    def plot_3d_delta_vol_surface(self, spot_grid, vol_grid, fixed_time):
        """Maps Delta sensitivity against Spot Price and Implied Volatility."""
        Z_deltas = np.zeros((len(vol_grid), len(spot_grid)))

        for v_idx, v_val in enumerate(vol_grid):
            for s_idx, s_val in enumerate(spot_grid):
                engine = Greek_and_Price(s_val, self.K, fixed_time, v_val, self.r, self.option_type)
                metrics = engine.bs_greek_and_price()
                Z_deltas[v_idx, s_idx] = metrics['delta']
        
        X_spots, Y_vols = np.meshgrid(spot_grid, vol_grid)
        
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # 'plasma' highlights the transition boundary cleanly
        surface = ax.plot_surface(X_spots, Y_vols * 100, Z_deltas, 
                                  cmap='plasma', edgecolor='none', alpha=0.85)
        
        ax.set_title(f'3D {self.option_type.upper()} Delta ($\Delta$) Surface\nFixed Time to Expiration = {fixed_time*365:.1f} Days', 
                     fontsize=13, fontweight='bold', pad=15)
        ax.set_xlabel('Bitcoin Spot Price ($)', labelpad=12)
        ax.set_ylabel('Implied Volatility (IV %)', labelpad=12)
        ax.set_zlabel('Delta ($\Delta$)', labelpad=12)
        
        ax.view_init(elev=25, azim=-55)
        fig.colorbar(surface, ax=ax, shrink=0.5, aspect=12, label='Delta Sensitivity')
        
        plt.tight_layout()
        plt.savefig('figures/DeltaSurface.png')
        plt.show()

    def plot_3d_gamma_time_surface(self, spot_grid, time_grid):
        """Maps Gamma sensitivity against Spot Price and Time Decay."""
        Z_gammas = np.zeros((len(time_grid), len(spot_grid)))

        for t_idx, t_val in enumerate(time_grid):
            for s_idx, s_val in enumerate(spot_grid):
                engine = Greek_and_Price(s_val, self.K, t_val, self.sigma, self.r, self.option_type)
                metrics = engine.bs_greek_and_price()
                Z_gammas[t_idx, s_idx] = metrics['gamma']

        X_spots, Y_times = np.meshgrid(spot_grid, time_grid)
        
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # 'viridis' helps emphasize the vertical explosion of near-term ATM Gamma
        surface = ax.plot_surface(X_spots, Y_times * 365, Z_gammas, 
                                  cmap='viridis', edgecolor='none', alpha=0.85)
        
        ax.set_title(f'3D {self.option_type.upper()} Gamma ($\Gamma$) Acceleration Surface\nFixed Implied Volatility = {self.sigma*100:.0f}%', 
                     fontsize=13, fontweight='bold', pad=15)
        ax.set_xlabel('Bitcoin Spot Price ($)', labelpad=12)
        ax.set_ylabel('Time to Expiration (Days)', labelpad=12)
        ax.set_zlabel('Gamma ($\Gamma$)', labelpad=12)
        
        # Slightly steeper angle to look down into the exploding Gamma peak
        ax.view_init(elev=30, azim=-60)
        fig.colorbar(surface, ax=ax, shrink=0.5, aspect=12, label='Gamma Acceleration')
        
        plt.tight_layout()
        plt.savefig('figures/GammaSurface.png')
        plt.show()

    def plot_3d_theta_time_surface(self, spot_grid, time_grid):
        """Maps Theta decay against Spot Price and Time Horizon."""
        Z_thetas = np.zeros((len(time_grid), len(spot_grid)))

        for t_idx, t_val in enumerate(time_grid):
            for s_idx, s_val in enumerate(spot_grid):
                engine = Greek_and_Price(s_val, self.K, t_val, self.sigma, self.r, self.option_type)
                metrics = engine.bs_greek_and_price()
                Z_thetas[t_idx, s_idx] = metrics['theta']

        X_spots, Y_times = np.meshgrid(spot_grid, time_grid)
        
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # 'coolwarm' is ideal here because Theta maps bleeding premiums 
        surface = ax.plot_surface(X_spots, Y_times * 365, Z_thetas, 
                                  cmap='coolwarm', edgecolor='none', alpha=0.85)
        
        ax.set_title(f'3D {self.option_type.upper()} Theta ($\Theta$) Time Decay Surface\nFixed Implied Volatility = {self.sigma*100:.0f}%', 
                     fontsize=13, fontweight='bold', pad=15)
        ax.set_xlabel('Bitcoin Spot Price ($)', labelpad=12)
        ax.set_ylabel('Time to Expiration (Days)', labelpad=12)
        ax.set_zlabel('Daily Theta Bleed ($\Theta$)', labelpad=12)
        
        ax.view_init(elev=22, azim=-120)  # Rotated viewpoint to visualize the negative bleed trough
        fig.colorbar(surface, ax=ax, shrink=0.5, aspect=12, label='Daily Premium Decay (Cash/Day)')
        
        plt.tight_layout()
        plt.savefig('figures/ThetaSurface.png')
        plt.show()

    def plot_3d_vega_time_surface(self, spot_grid, time_grid):
        """Maps Vega volatility exposure against Spot Price and Time Horizon."""
        Z_vegas = np.zeros((len(time_grid), len(spot_grid)))

        for t_idx, t_val in enumerate(time_grid):
            for s_idx, s_val in enumerate(spot_grid):
                engine = Greek_and_Price(s_val, self.K, t_val, self.sigma, self.r, self.option_type)
                metrics = engine.bs_greek_and_price()
                Z_vegas[t_idx, s_idx] = metrics['vega']

        X_spots, Y_times = np.meshgrid(spot_grid, time_grid)
        
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        surface = ax.plot_surface(X_spots, Y_times * 365, Z_vegas, 
                                  cmap='magma', edgecolor='none', alpha=0.85)
        
        ax.set_title(f'3D {self.option_type.upper()} Vega ($\nu$) Volatility Sensitivity Surface\nFixed Implied Volatility = {self.sigma*100:.0f}%', 
                     fontsize=13, fontweight='bold', pad=15)
        ax.set_xlabel('Bitcoin Spot Price ($)', labelpad=12)
        ax.set_ylabel('Time to Expiration (Days)', labelpad=12)
        ax.set_zlabel('Vega ($\nu$)', labelpad=12)
        
        ax.view_init(elev=25, azim=-45)
        fig.colorbar(surface, ax=ax, shrink=0.5, aspect=12, label='Vega Value (Price change per 1% IV shift)')
        
        plt.tight_layout()
        plt.savefig('figures/VegaSurface.png')
        plt.show()

if __name__ == '__main__':
    spot_axis = np.linspace(60000, 90000, 60)
    time_axis = np.linspace(2 / 365.0, 120 / 365.0, 60)
    vol_axis  = np.linspace(0.10, 1.30, 60)

    engine = Greeks_Surface_Engine(strike_price=76000.0, sigma=0.25, rate=0.0, option_type='call')
    
    print("Generating Surface Maps...")
    engine.plot_3d_delta_vol_surface(spot_axis, vol_axis, fixed_time=30/365.0)
    engine.plot_3d_gamma_time_surface(spot_axis, time_axis)
    engine.plot_3d_theta_time_surface(spot_axis, time_axis)
    engine.plot_3d_vega_time_surface(spot_axis, time_axis)