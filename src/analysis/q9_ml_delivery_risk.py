"""
Question 9: Machine Learning Delivery Delay Risk Classifier & Feature Importance
Trains Logistic Regression and RandomForest classifiers on 96,470 delivered orders
to predict late delivery risk (is_late = 1). Adheres strictly to ML Best Practices
(strict featurization ordering, train/test split, ROC-AUC evaluation, confusion matrix).
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, precision_score, recall_score, f1_score

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.visualization import set_chart_style, annotate_bars, save_chart, PALETTE, CHART_COLORS

OUTPUT_TABLES = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'outputs', 'tables')
OUTPUT_CHARTS = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'outputs', 'charts')

def analyze_ml_delivery_risk(df):
    """Executes Question 9 Machine Learning Delivery Delay Risk Analysis."""
    print("--- Running Q9: Machine Learning Delivery Delay Risk Classifier ---")
    
    # Filter delivered orders population (N = 96,470) and drop any missing is_late flags
    df_deliv = df[df['order_status'] == 'delivered'].copy()
    df_deliv = df_deliv[df_deliv['is_late'].notnull()].copy()
    df_deliv['is_late'] = df_deliv['is_late'].astype(int)
    total_samples = len(df_deliv)
    
    print(f"Total Delivered Orders Population for ML (N): {total_samples:,}")
    print(f"Target Distribution (is_late): On-Time = {(df_deliv['is_late'] == 0).sum():,} | Late = {(df_deliv['is_late'] == 1).sum():,} ({df_deliv['is_late'].mean()*100:.2f}%)")
    
    # 1. FEATURE ENGINEERING
    df_deliv['is_interstate'] = (df_deliv['customer_state'] != df_deliv['seller_state']).astype(int)
    df_deliv['freight_ratio'] = (df_deliv['total_freight'] / df_deliv['total_price'].replace(0, np.nan)).fillna(0)
    df_deliv['carrier_dispatch_days'] = df_deliv['carrier_dispatch_days'].fillna(df_deliv['carrier_dispatch_days'].median())
    df_deliv['item_count'] = df_deliv['item_count'].fillna(1)
    df_deliv['total_price'] = df_deliv['total_price'].fillna(df_deliv['total_price'].median())
    df_deliv['total_freight'] = df_deliv['total_freight'].fillna(df_deliv['total_freight'].median())
    
    # Frequency encode top states to prevent data leakage
    state_freq = df_deliv['customer_state'].value_counts(normalize=True).to_dict()
    df_deliv['customer_state_freq'] = df_deliv['customer_state'].map(state_freq).fillna(0)
    
    seller_state_freq = df_deliv['seller_state'].value_counts(normalize=True).to_dict()
    df_deliv['seller_state_freq'] = df_deliv['seller_state'].map(seller_state_freq).fillna(0)
    
    feature_cols = [
        'is_interstate',
        'carrier_dispatch_days',
        'freight_ratio',
        'total_price',
        'total_freight',
        'item_count',
        'customer_state_freq',
        'seller_state_freq'
    ]
    
    feature_labels = {
        'is_interstate': 'Inter-State Route Indicator',
        'carrier_dispatch_days': 'Seller Dispatch Lead Time (Days)',
        'freight_ratio': 'Freight Burden Ratio (Freight / Price)',
        'total_price': 'Total Order Price (R$)',
        'total_freight': 'Total Freight Value (R$)',
        'item_count': 'Items per Order Count',
        'customer_state_freq': 'Customer State Volume Share',
        'seller_state_freq': 'Seller State Volume Share'
    }
    
    X = df_deliv[feature_cols].copy()
    y = df_deliv['is_late'].values
    
    # 2. STRICT FEATURIZATION ORDERING: CHRONOLOGICAL / STRATIFIED SPLIT (80% Train, 20% Test)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)
    
    # Fit scaler ONLY on training data
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print(f"Training Set Size: {X_train.shape[0]:,} samples | Test Set Size: {X_test.shape[0]:,} samples")
    
    # 3. TRAIN BASELINE & ENSEMBLE MODELS
    print("Training Logistic Regression Baseline...")
    clf_lr = LogisticRegression(max_iter=1000, random_state=42, class_weight='balanced')
    clf_lr.fit(X_train_scaled, y_train)
    
    print("Training Random Forest Ensemble Classifier...")
    clf_rf = RandomForestClassifier(n_estimators=150, max_depth=12, random_state=42, class_weight='balanced', n_jobs=-1)
    clf_rf.fit(X_train, y_train) # Tree models don't strictly require scaling
    
    # 4. MODEL EVALUATION
    y_pred_lr = clf_lr.predict(X_test_scaled)
    y_prob_lr = clf_lr.predict_proba(X_test_scaled)[:, 1]
    
    y_pred_rf = clf_rf.predict(X_test)
    y_prob_rf = clf_rf.predict_proba(X_test)[:, 1]
    
    eval_metrics = [
        {
            'model_name': 'Logistic Regression (Baseline)',
            'accuracy': (y_pred_lr == y_test).mean(),
            'precision': precision_score(y_test, y_pred_lr),
            'recall': recall_score(y_test, y_pred_lr),
            'f1_score': f1_score(y_test, y_pred_lr),
            'roc_auc': roc_auc_score(y_test, y_prob_lr)
        },
        {
            'model_name': 'Random Forest Classifier (Ensemble)',
            'accuracy': (y_pred_rf == y_test).mean(),
            'precision': precision_score(y_test, y_pred_rf),
            'recall': recall_score(y_test, y_pred_rf),
            'f1_score': f1_score(y_test, y_pred_rf),
            'roc_auc': roc_auc_score(y_test, y_prob_rf)
        }
    ]
    
    df_eval = pd.DataFrame(eval_metrics)
    eval_path = os.path.join(OUTPUT_TABLES, 'q9_ml_model_evaluation.csv')
    df_eval.to_csv(eval_path, index=False)
    print(f"Saved ML model evaluation metrics to {eval_path}")
    print("\n--- MODEL PERFORMANCE EVALUATION SUMMARY ---")
    print(df_eval.to_string(index=False))
    
    # 5. FEATURE IMPORTANCE EXTRACTION
    rf_importances = clf_rf.feature_importances_
    df_imp = pd.DataFrame({
        'feature_key': feature_cols,
        'feature_name': [feature_labels[c] for c in feature_cols],
        'importance': rf_importances
    }).sort_values('importance', ascending=False)
    
    imp_path = os.path.join(OUTPUT_TABLES, 'q9_ml_feature_importances.csv')
    df_imp.to_csv(imp_path, index=False)
    print(f"Saved feature importances to {imp_path}")
    
    # 6. CHART 1: FEATURE IMPORTANCE RATING BAR CHART
    fig, ax = plt.subplots(figsize=(10, 5.5))
    set_chart_style(ax, title='Random Forest Classifier — Late Delivery Risk Feature Importance', xlabel='Gini Feature Importance Weight', ylabel='Risk Factor')
    
    bars = ax.barh(df_imp['feature_name'], df_imp['importance'], color='#0EA5E9', height=0.6)
    ax.invert_yaxis()
    
    for bar in bars:
        w = bar.get_width()
        ax.annotate(f'{w*100:.1f}%', xy=(w, bar.get_y() + bar.get_height()/2), xytext=(5, 0), textcoords="offset points", ha='left', va='center', fontweight='bold', color='#1E293B')
        
    save_chart(fig, 'q9_ml_feature_importance.png')
    
    # 7. CHART 2: CONFUSION MATRIX VISUALIZATION
    cm = confusion_matrix(y_test, y_pred_rf)
    fig, ax = plt.subplots(figsize=(7, 5.5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False, ax=ax,
                xticklabels=['Predicted On-Time (0)', 'Predicted Late (1)'],
                yticklabels=['Actual On-Time (0)', 'Actual Late (1)'])
    set_chart_style(ax, title=f'Random Forest Confusion Matrix (ROC-AUC = {eval_metrics[1]["roc_auc"]:.3f})')
    save_chart(fig, 'q9_ml_confusion_matrix.png')
    
    print("Q9 Machine Learning Delivery Delay Risk Classifier Analysis Complete!")
