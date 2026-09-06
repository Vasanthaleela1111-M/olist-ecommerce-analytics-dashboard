"""
Standalone CLI runner for Question 10: Seller SLA Health Scorecard & Automated Badge System.
"""

import os
import sys
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.analysis.q10_seller_health import analyze_seller_health_scorecard

MASTER_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'outputs', 'exports', 'master_orders.csv')

def main():
    if not os.path.exists(MASTER_PATH):
        print(f"Error: Master orders dataset not found at {MASTER_PATH}. Run run_analysis.py first.")
        sys.exit(1)
        
    print(f"Loading master orders dataset from {MASTER_PATH}...")
    df = pd.read_csv(MASTER_PATH)
    analyze_seller_health_scorecard(df)

if __name__ == '__main__':
    main()
