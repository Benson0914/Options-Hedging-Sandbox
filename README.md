# Options Dynamic Hedging & Volatility Sandbox Arena

A production-grade quantitative simulation environment written in Python to evaluate the structural performance, cost rebalancing, and PnL attribution of Option Volatility Arbitrage strategies under different market regimes. 

This repository simulates a dynamic battlefield between a **V1 Short Straddle Market Maker** (Negative Gamma) and a **V2 Multi-Threshold Gamma Scalper** (Positive Gamma) using continuous Black-Scholes Greek replication.

---

## 🚀 Installation & Quick Start

```bash
# Clone the repository
git clone [https://github.com/Benson0914/options-dynamic-hedging-sandbox.git](https://github.com/Benson0914/options-dynamic-hedging-sandbox.git)
cd options-dynamic-hedging-sandbox

# Install required mathematical & plotting frameworks
pip install -r requirements.txt

# Run the full Multi-Threshold Arena Simulation Matrix
python run_arena.py

