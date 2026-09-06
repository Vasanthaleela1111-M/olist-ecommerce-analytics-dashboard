"""
Olist Analytics Hackathon Master Pipeline Runner
Executes data ingestion, feature engineering, master dataset generation,
and all six core analysis modules sequentially with automated verification.
"""

import os
import sys
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data_loader import load_raw_data, audit_data_integrity
from src.build_master import build_master_orders_dataset
from src.analysis.q1_marketplace_performance import analyze_marketplace_performance
from src.analysis.q2_delivery_performance import analyze_delivery_performance
from src.analysis.q3_seller_geographic import analyze_seller_geographic_patterns
from src.analysis.q4_product_category import analyze_product_category_performance
from src.analysis.q5_payment_behavior import analyze_payment_behavior
from src.analysis.q6_root_cause_reviews import analyze_root_cause_low_reviews
from src.analysis.q7_customer_cohorts import analyze_customer_cohorts
from src.analysis.q9_ml_delivery_risk import analyze_ml_delivery_risk
from src.analysis.q10_seller_health import analyze_seller_health_scorecard

def main():
    print("=========================================================================")
    print("      OLIST BRAZILIAN E-COMMERCE DATA ANALYTICS HACKATHON PIPELINE      ")
    print("=========================================================================\n")
    
    start_time = time.time()
    
    # 1. Data Loader & Integrity Audit
    print("STEP 1: Ingesting raw CSVs and performing Data Integrity Audit...")
    datasets = load_raw_data()
    audit_df = audit_data_integrity(datasets)
    audit_path = os.path.join('outputs', 'tables', 'q0_data_integrity_audit.csv')
    os.makedirs(os.path.dirname(audit_path), exist_ok=True)
    audit_df.to_csv(audit_path, index=False)
    print(f"Data audit complete. Saved table to {audit_path}\n")
    
    # 2. Feature Engineering & Master Dataset Creation
    print("STEP 2: Building Master Analytical Dataset at order_id grain...")
    master_df = build_master_orders_dataset()
    print(f"Master dataset generated successfully! Shape: {master_df.shape}\n")
    
    # 3. Question 1: Marketplace Performance
    print("STEP 3: Executing Q1 - Marketplace Performance Analysis...")
    analyze_marketplace_performance(master_df)
    print("Q1 Analysis Complete!\n")
    
    # 4. Question 2: Delivery Performance
    print("STEP 4: Executing Q2 - Delivery Performance Analysis...")
    analyze_delivery_performance(master_df)
    print("Q2 Analysis Complete!\n")
    
    # 5. Question 3: Seller & Geographic Patterns
    print("STEP 5: Executing Q3 - Seller & Geographic Patterns Analysis...")
    analyze_seller_geographic_patterns(master_df)
    print("Q3 Analysis Complete!\n")
    
    # 6. Question 4: Product Category Performance
    print("STEP 6: Executing Q4 - Product Category Performance Analysis...")
    analyze_product_category_performance(master_df)
    print("Q4 Analysis Complete!\n")
    
    # 7. Question 5: Payment Behavior Analysis
    print("STEP 7: Executing Q5 - Payment Behavior Analysis...")
    analyze_payment_behavior(master_df)
    print("Q5 Analysis Complete!\n")
    
    # 8. Question 6: Root-Cause Analysis of Low Review Scores
    print("STEP 8: Executing Q6 - Root-Cause Analysis of Low Review Scores...")
    analyze_root_cause_low_reviews(master_df)
    print("Q6 Analysis Complete!\n")
    
    # 9. Question 7: Customer Cohort & Repeat Purchase Analysis
    print("STEP 9: Executing Q7 - Customer Cohort & Repeat Purchase Analysis...")
    analyze_customer_cohorts(master_df)
    print("Q7 Analysis Complete!\n")
    
    # 10. Question 9: Machine Learning Delivery Delay Risk Classifier
    print("STEP 10: Executing Q9 - Machine Learning Delivery Delay Risk Classifier...")
    analyze_ml_delivery_risk(master_df)
    print("Q9 Analysis Complete!\n")
    
    # 11. Question 10: Seller SLA Health Scorecard & Automated Badge System
    print("STEP 11: Executing Q10 - Seller SLA Health Scorecard & Automated Badge System...")
    analyze_seller_health_scorecard(master_df)
    print("Q10 Analysis Complete!\n")
    
    elapsed = time.time() - start_time
    print("=========================================================================")
    print(f"   HACKATHON PIPELINE COMPLETED SUCCESSFULLY IN {elapsed:.2f} SECONDS   ")
    print("=========================================================================")

if __name__ == '__main__':
    main()
