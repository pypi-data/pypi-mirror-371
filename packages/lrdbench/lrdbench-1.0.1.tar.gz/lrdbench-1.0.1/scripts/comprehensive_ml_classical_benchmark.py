#!/usr/bin/env python3
"""
Comprehensive ML vs Classical Estimators Benchmarking Script

This script compares the best performing ML estimators with classical estimators
for Hurst parameter estimation.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os
import time
import warnings
from datetime import datetime
import argparse
warnings.filterwarnings('ignore')

# Import models
from models.data_models.fgn.fgn_model import FractionalGaussianNoise
from models.data_models.fbm.fbm_model import FractionalBrownianMotion

# Import classical estimators
from analysis.temporal.dfa.dfa_estimator import DFAEstimator
from analysis.temporal.rs.rs_estimator import RSEstimator
from analysis.temporal.dma.dma_estimator import DMAEstimator
from analysis.spectral.periodogram.periodogram_estimator import PeriodogramEstimator
from analysis.spectral.gph.gph_estimator import GPHEstimator
from analysis.wavelet.cwt.cwt_estimator import CWTEstimator

# Import best ML estimators
from analysis.machine_learning.random_forest_estimator import RandomForestEstimator
from analysis.machine_learning.gradient_boosting_estimator import GradientBoostingEstimator
from analysis.machine_learning.svr_estimator import SVREstimator
from analysis.machine_learning.lstm_estimator import LSTMEstimator
from analysis.machine_learning.gru_estimator import GRUEstimator


def generate_test_data(n_samples=200, data_length=1024, seed=42):
    """
    Generate test data with known Hurst parameters.
    
    Parameters
    ----------
    n_samples : int
        Number of test samples
    data_length : int
        Length of each time series
    seed : int
        Random seed for reproducibility
        
    Returns
    -------
    tuple
        (X_test, y_test, model_info)
    """
    print(f"Generating {n_samples} test samples...")
    
    np.random.seed(seed)
    
    X_test = []
    y_test = []
    model_info = []
    
    # Generate data from different models with various Hurst parameters
    hurst_values = np.linspace(0.1, 0.9, 9)  # 9 different H values
    
    samples_per_hurst = n_samples // len(hurst_values)
    
    for i, H in enumerate(hurst_values):
        print(f"Generating data for H = {H:.1f}...")
        
        # Generate fGn data
        fgn = FractionalGaussianNoise(H=H)
        for _ in range(samples_per_hurst // 2):
            data = fgn.generate(data_length)
            X_test.append(data)
            y_test.append(H)
            model_info.append({'model': 'fGn', 'H': H})
        
        # Generate fBm increment data
        fbm = FractionalBrownianMotion(H=H)
        for _ in range(samples_per_hurst // 2):
            fbm_data = fbm.generate(data_length + 1)
            data = fbm.get_increments(fbm_data)
            X_test.append(data)
            y_test.append(H)
            model_info.append({'model': 'fBm', 'H': H})
    
    return np.array(X_test), np.array(y_test), model_info


def generate_training_data(n_samples=500, data_length=1024, seed=42):
    """
    Generate training data for ML estimators.
    
    Parameters
    ----------
    n_samples : int
        Number of training samples
    data_length : int
        Length of each time series
    seed : int
        Random seed for reproducibility
        
    Returns
    -------
    tuple
        (X_train, y_train)
    """
    print(f"Generating {n_samples} training samples...")
    
    np.random.seed(seed)
    
    X_train = []
    y_train = []
    
    # Generate data from different models with various Hurst parameters
    hurst_values = np.linspace(0.1, 0.9, 9)  # 9 different H values
    
    samples_per_hurst = n_samples // len(hurst_values)
    
    for i, H in enumerate(hurst_values):
        # Generate fGn data
        fgn = FractionalGaussianNoise(H=H)
        for _ in range(samples_per_hurst // 2):
            data = fgn.generate(data_length)
            X_train.append(data)
            y_train.append(H)
        
        # Generate fBm increment data
        fbm = FractionalBrownianMotion(H=H)
        for _ in range(samples_per_hurst // 2):
            fbm_data = fbm.generate(data_length + 1)
            data = fbm.get_increments(fbm_data)
            X_train.append(data)
            y_train.append(H)
    
    return np.array(X_train), np.array(y_train)


def create_estimators():
    """
    Create estimators for comparison.
    
    Returns
    -------
    dict
        Dictionary of estimators
    """
    print("Creating estimators...")
    
    estimators = {}
    
    # Classical estimators
    estimators['DFA'] = DFAEstimator()
    estimators['R/S'] = RSEstimator()
    estimators['DMA'] = DMAEstimator()
    estimators['Periodogram'] = PeriodogramEstimator()
    estimators['GPH'] = GPHEstimator()
    estimators['CWT'] = CWTEstimator()
    
    # Best ML estimators
    estimators['Random Forest'] = RandomForestEstimator(
        feature_extraction_method='statistical',
        n_estimators=50,
        random_state=42
    )
    
    estimators['Gradient Boosting'] = GradientBoostingEstimator(
        feature_extraction_method='statistical',
        n_estimators=50,
        learning_rate=0.1,
        random_state=42
    )
    
    estimators['SVR (RBF)'] = SVREstimator(
        feature_extraction_method='statistical',
        kernel='rbf',
        C=1.0
    )

    # Deep learning baselines (currently on hold due to poor performance)
    # LSTM and GRU models need further tuning before inclusion
    
    return estimators


def _get_model_paths(model_dir: str = "saved_models"):
    """Return filepaths for ML estimators' saved models."""
    Path(model_dir).mkdir(parents=True, exist_ok=True)
    return {
        'Random Forest': os.path.join(model_dir, 'random_forest_statistical.joblib'),
        'Gradient Boosting': os.path.join(model_dir, 'gradient_boosting_statistical.joblib'),
        'SVR (RBF)': os.path.join(model_dir, 'svr_rbf_statistical.joblib'),
    }


def train_ml_estimators(estimators, X_train, y_train, model_dir: str = "saved_models", force_retrain: bool = False):
    """
    Train machine learning estimators.
    
    Parameters
    ----------
    estimators : dict
        Dictionary of estimators
    X_train : np.ndarray
        Training features
    y_train : np.ndarray
        Training targets
        
    Returns
    -------
    dict
        Training results
    """
    print("Training/Loading ML estimators...")
    
    training_results = {}
    model_paths = _get_model_paths(model_dir)
    
    for name, estimator in estimators.items():
        if name in ['Random Forest', 'Gradient Boosting', 'SVR (RBF)']:
            model_path = model_paths.get(name)
            try:
                results = estimator.train_or_load(X_train, y_train, model_path=model_path, force_retrain=force_retrain)
                training_results[name] = results
                if results.get('loaded'):
                    print(f"  {name}: Loaded pre-trained model from {model_path}")
                else:
                    print(f"  {name}: R² = {results['test_r2']:.3f}, MAE = {results['test_mae']:.3f}, Time = {results['training_time']:.2f}s")
            except Exception as e:
                print(f"  {name}: Error training/loading - {e}")
                training_results[name] = {'error': str(e)}
    
    return training_results


def evaluate_estimators(estimators, X_test, y_test, training_results):
    """
    Evaluate all estimators on test data.
    
    Parameters
    ----------
    estimators : dict
        Dictionary of estimators
    X_test : np.ndarray
        Test features
    y_test : np.ndarray
        Test targets
    training_results : dict
        Training results for ML estimators
        
    Returns
    -------
    dict
        Evaluation results
    """
    print("Evaluating estimators...")
    
    evaluation_results = {}
    
    for name, estimator in estimators.items():
        print(f"Evaluating {name}...")
        
        try:
            start_time = time.time()
            
            if name in training_results and 'error' not in training_results[name]:
                # ML estimator - use trained model
                predictions = []
                for i, data in enumerate(X_test):
                    result = estimator.estimate(data)
                    predictions.append(result['hurst_parameter'])
                predictions = np.array(predictions)
                evaluation_time = time.time() - start_time
                
            else:
                # Classical estimator
                predictions = []
                for i, data in enumerate(X_test):
                    result = estimator.estimate(data)
                    predictions.append(result['hurst_parameter'])
                predictions = np.array(predictions)
                evaluation_time = time.time() - start_time
            
            # Calculate metrics
            mae = np.mean(np.abs(predictions - y_test))
            mse = np.mean((predictions - y_test) ** 2)
            rmse = np.sqrt(mse)
            r2 = 1 - np.sum((predictions - y_test) ** 2) / np.sum((y_test - np.mean(y_test)) ** 2)
            
            evaluation_results[name] = {
                'mae': mae,
                'mse': mse,
                'rmse': rmse,
                'r2': r2,
                'evaluation_time': evaluation_time,
                'predictions': predictions
            }
            
            print(f"  {name}: R² = {r2:.3f}, MAE = {mae:.3f}, Time = {evaluation_time:.3f}s")
            
        except Exception as e:
            print(f"  {name}: Error evaluating - {e}")
            evaluation_results[name] = {'error': str(e)}
    
    return evaluation_results


def create_comparison_plots(evaluation_results, X_test, y_test, save_dir):
    """
    Create comprehensive comparison plots and save results.
    
    Parameters
    ----------
    evaluation_results : dict
        Evaluation results
    X_test : np.ndarray
        Test features
    y_test : np.ndarray
        Test targets
    save_dir : str
        Directory to save results
    """
    print("Creating comprehensive comparison plots...")
    
    # Create results DataFrame
    results_data = []
    for name, results in evaluation_results.items():
        if 'error' not in results:
            estimator_type = 'ML' if name in ['Random Forest', 'Gradient Boosting', 'SVR (RBF)'] else 'Classical'
            results_data.append({
                'Estimator': name,
                'Type': estimator_type,
                'MAE': results['mae'],
                'MSE': results['mse'],
                'RMSE': results['rmse'],
                'R²': results['r2'],
                'Evaluation Time (s)': results['evaluation_time']
            })
    
    results_df = pd.DataFrame(results_data)
    
    # Save results
    results_df.to_csv(f"{save_dir}/comprehensive_results.csv", index=False)
    print(f"Results saved to {save_dir}/comprehensive_results.csv")
    
    # Create ML vs Classical comparison plots
    create_ml_vs_classical_plots(results_df, evaluation_results, y_test, save_dir)
    
    # Create detailed performance plots
    create_detailed_performance_plots(results_df, save_dir)
    
    # Create accuracy analysis plots
    create_accuracy_analysis_plots(evaluation_results, y_test, save_dir)
    
    # Print comprehensive summary
    print_comprehensive_summary(results_df)
    
    return results_df


def create_ml_vs_classical_plots(results_df, evaluation_results, y_test, save_dir):
    """Create ML vs Classical comparison plots."""
    print("Creating ML vs Classical comparison plots...")
    
    # Set up the plot style
    plt.style.use('default')
    sns.set_palette("husl")
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Machine Learning vs Classical Estimators Comparison', fontsize=16, fontweight='bold')
    
    # 1. Accuracy Comparison (R² Score)
    ax1 = axes[0, 0]
    r2_data = results_df.sort_values('R²', ascending=True)
    colors = ['#FF6B35' if x == 'ML' else '#1E88E5' for x in r2_data['Type']]
    bars = ax1.barh(r2_data['Estimator'], r2_data['R²'], color=colors)
    ax1.set_xlabel('R² Score')
    ax1.set_title('Accuracy Comparison (R²)', fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.axvline(x=0.8, color='red', linestyle='--', alpha=0.5, label='Good Performance (0.8)')
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax1.text(width + 0.01, bar.get_y() + bar.get_height()/2, 
                f'{width:.3f}', ha='left', va='center', fontsize=9)
    
    # 2. Precision Comparison (MAE)
    ax2 = axes[0, 1]
    mae_data = results_df.sort_values('MAE', ascending=False)
    colors = ['#FF6B35' if x == 'ML' else '#1E88E5' for x in mae_data['Type']]
    bars = ax2.barh(mae_data['Estimator'], mae_data['MAE'], color=colors)
    ax2.set_xlabel('Mean Absolute Error')
    ax2.set_title('Precision Comparison (MAE)', fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.axvline(x=0.1, color='red', linestyle='--', alpha=0.5, label='Excellent (<0.1)')
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax2.text(width + 0.005, bar.get_y() + bar.get_height()/2, 
                f'{width:.3f}', ha='left', va='center', fontsize=9)
    
    # 3. Efficiency Comparison (Evaluation Time)
    ax3 = axes[0, 2]
    time_data = results_df.sort_values('Evaluation Time (s)', ascending=True)
    colors = ['#FF6B35' if x == 'ML' else '#1E88E5' for x in time_data['Type']]
    bars = ax3.barh(time_data['Estimator'], time_data['Evaluation Time (s)'], color=colors)
    ax3.set_xlabel('Evaluation Time (seconds)')
    ax3.set_title('Efficiency Comparison', fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax3.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
                f'{width:.2f}s', ha='left', va='center', fontsize=9)
    
    # 4. ML vs Classical Box Plot Comparison (Accuracy)
    ax4 = axes[1, 0]
    ml_r2 = results_df[results_df['Type'] == 'ML']['R²'].values
    classical_r2 = results_df[results_df['Type'] == 'Classical']['R²'].values
    
    box_data = [classical_r2, ml_r2]
    bp = ax4.boxplot(box_data, labels=['Classical', 'ML'], patch_artist=True)
    bp['boxes'][0].set_facecolor('#1E88E5')
    bp['boxes'][1].set_facecolor('#FF6B35')
    
    ax4.set_ylabel('R² Score')
    ax4.set_title('Accuracy Distribution', fontweight='bold')
    ax4.grid(True, alpha=0.3)
    
    # Add mean markers
    ax4.scatter([1, 2], [np.mean(classical_r2), np.mean(ml_r2)], 
               color='red', marker='D', s=50, label='Mean')
    ax4.legend()
    
    # 5. ML vs Classical Box Plot Comparison (Precision)
    ax5 = axes[1, 1]
    ml_mae = results_df[results_df['Type'] == 'ML']['MAE'].values
    classical_mae = results_df[results_df['Type'] == 'Classical']['MAE'].values
    
    box_data = [classical_mae, ml_mae]
    bp = ax5.boxplot(box_data, labels=['Classical', 'ML'], patch_artist=True)
    bp['boxes'][0].set_facecolor('#1E88E5')
    bp['boxes'][1].set_facecolor('#FF6B35')
    
    ax5.set_ylabel('MAE')
    ax5.set_title('Precision Distribution', fontweight='bold')
    ax5.grid(True, alpha=0.3)
    
    # Add mean markers
    ax5.scatter([1, 2], [np.mean(classical_mae), np.mean(ml_mae)], 
               color='red', marker='D', s=50, label='Mean')
    ax5.legend()
    
    # 6. Performance vs Efficiency Scatter Plot
    ax6 = axes[1, 2]
    ml_data = results_df[results_df['Type'] == 'ML']
    classical_data = results_df[results_df['Type'] == 'Classical']
    
    # Plot ML estimators
    ax6.scatter(ml_data['Evaluation Time (s)'], ml_data['R²'], 
               color='#FF6B35', s=100, alpha=0.7, label='ML', marker='o')
    
    # Plot Classical estimators
    ax6.scatter(classical_data['Evaluation Time (s)'], classical_data['R²'], 
               color='#1E88E5', s=100, alpha=0.7, label='Classical', marker='s')
    
    # Add estimator labels
    for _, row in results_df.iterrows():
        ax6.annotate(row['Estimator'], 
                    (row['Evaluation Time (s)'], row['R²']),
                    xytext=(5, 5), textcoords='offset points',
                    fontsize=8, alpha=0.8)
    
    ax6.set_xlabel('Evaluation Time (seconds)')
    ax6.set_ylabel('R² Score')
    ax6.set_title('Performance vs Efficiency', fontweight='bold')
    ax6.grid(True, alpha=0.3)
    ax6.legend()
    
    # Add performance regions
    ax6.axhline(y=0.8, color='red', linestyle='--', alpha=0.3, label='Good Performance')
    ax6.axvline(x=5, color='green', linestyle='--', alpha=0.3, label='Fast (<5s)')
    
    plt.tight_layout()
    plt.savefig(f"{save_dir}/ml_vs_classical_comparison.png", dpi=300, bbox_inches='tight')
    print(f"ML vs Classical comparison plot saved to {save_dir}/ml_vs_classical_comparison.png")


def create_detailed_performance_plots(results_df, save_dir):
    """Create detailed performance analysis plots."""
    print("Creating detailed performance plots...")
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Detailed Performance Analysis', fontsize=16, fontweight='bold')
    
    # 1. Performance Radar Chart
    ax1 = axes[0, 0]
    
    # Calculate normalized metrics for radar chart
    ml_data = results_df[results_df['Type'] == 'ML']
    classical_data = results_df[results_df['Type'] == 'Classical']
    
    # Normalize metrics (0-1 scale, higher is better)
    max_r2 = results_df['R²'].max()
    min_mae = results_df['MAE'].min()
    max_mae = results_df['MAE'].max()
    min_time = results_df['Evaluation Time (s)'].min()
    max_time = results_df['Evaluation Time (s)'].max()
    
    ml_metrics = [
        ml_data['R²'].mean() / max_r2,  # Accuracy (normalized)
        1 - (ml_data['MAE'].mean() - min_mae) / (max_mae - min_mae),  # Precision (inverted)
        1 - (ml_data['Evaluation Time (s)'].mean() - min_time) / (max_time - min_time),  # Speed (inverted)
    ]
    
    classical_metrics = [
        classical_data['R²'].mean() / max_r2,
        1 - (classical_data['MAE'].mean() - min_mae) / (max_mae - min_mae),
        1 - (classical_data['Evaluation Time (s)'].mean() - min_time) / (max_time - min_time),
    ]
    
    categories = ['Accuracy\n(R²)', 'Precision\n(Low MAE)', 'Speed\n(Fast Time)']
    
    # Create bar chart instead of radar (simpler)
    x = np.arange(len(categories))
    width = 0.35
    
    ax1.bar(x - width/2, ml_metrics, width, label='ML', color='#FF6B35', alpha=0.7)
    ax1.bar(x + width/2, classical_metrics, width, label='Classical', color='#1E88E5', alpha=0.7)
    
    ax1.set_xlabel('Performance Dimensions')
    ax1.set_ylabel('Normalized Score (0-1)')
    ax1.set_title('Average Performance Comparison', fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(categories)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for i, v in enumerate(ml_metrics):
        ax1.text(i - width/2, v + 0.01, f'{v:.3f}', ha='center', va='bottom', fontsize=9)
    for i, v in enumerate(classical_metrics):
        ax1.text(i + width/2, v + 0.01, f'{v:.3f}', ha='center', va='bottom', fontsize=9)
    
    # 2. Performance Ranking
    ax2 = axes[0, 1]
    
    # Create overall performance score
    results_df['Performance Score'] = (
        results_df['R²'] * 0.5 +  # 50% weight on accuracy
        (1 - (results_df['MAE'] - results_df['MAE'].min()) / (results_df['MAE'].max() - results_df['MAE'].min())) * 0.3 +  # 30% on precision
        (1 - (results_df['Evaluation Time (s)'] - results_df['Evaluation Time (s)'].min()) / (results_df['Evaluation Time (s)'].max() - results_df['Evaluation Time (s)'].min())) * 0.2  # 20% on speed
    )
    
    ranking_data = results_df.sort_values('Performance Score', ascending=True)
    colors = ['#FF6B35' if x == 'ML' else '#1E88E5' for x in ranking_data['Type']]
    
    bars = ax2.barh(ranking_data['Estimator'], ranking_data['Performance Score'], color=colors)
    ax2.set_xlabel('Overall Performance Score')
    ax2.set_title('Overall Performance Ranking', fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax2.text(width + 0.01, bar.get_y() + bar.get_height()/2, 
                f'{width:.3f}', ha='left', va='center', fontsize=9)
    
    # 3. Correlation Analysis
    ax3 = axes[1, 0]
    
    correlation_data = results_df[['R²', 'MAE', 'Evaluation Time (s)']].corr()
    im = ax3.imshow(correlation_data, cmap='RdBu_r', vmin=-1, vmax=1)
    
    # Add correlation values
    for i in range(len(correlation_data.columns)):
        for j in range(len(correlation_data.columns)):
            text = ax3.text(j, i, f'{correlation_data.iloc[i, j]:.2f}',
                           ha="center", va="center", color="black", fontweight='bold')
    
    ax3.set_xticks(range(len(correlation_data.columns)))
    ax3.set_yticks(range(len(correlation_data.columns)))
    ax3.set_xticklabels(correlation_data.columns, rotation=45)
    ax3.set_yticklabels(correlation_data.columns)
    ax3.set_title('Performance Metrics Correlation', fontweight='bold')
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax3)
    cbar.set_label('Correlation Coefficient')
    
    # 4. Best in Class Analysis
    ax4 = axes[1, 1]
    
    # Find best performers in each category
    best_accuracy = results_df.loc[results_df['R²'].idxmax()]
    best_precision = results_df.loc[results_df['MAE'].idxmin()]
    best_speed = results_df.loc[results_df['Evaluation Time (s)'].idxmin()]
    best_overall = results_df.loc[results_df['Performance Score'].idxmax()]
    
    categories = ['Best\nAccuracy', 'Best\nPrecision', 'Best\nSpeed', 'Best\nOverall']
    estimators = [best_accuracy['Estimator'], best_precision['Estimator'], 
                 best_speed['Estimator'], best_overall['Estimator']]
    types = [best_accuracy['Type'], best_precision['Type'], 
            best_speed['Type'], best_overall['Type']]
    
    colors = ['#FF6B35' if t == 'ML' else '#1E88E5' for t in types]
    
    bars = ax4.bar(categories, [1, 1, 1, 1], color=colors, alpha=0.7)
    
    # Add estimator names on bars
    for i, (bar, estimator) in enumerate(zip(bars, estimators)):
        ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height()/2, 
                estimator, ha='center', va='center', fontweight='bold', 
                rotation=90 if len(estimator) > 10 else 0, fontsize=10)
    
    ax4.set_ylabel('Best Performer')
    ax4.set_title('Best in Class Analysis', fontweight='bold')
    ax4.set_ylim(0, 1.2)
    
    # Remove y-axis ticks
    ax4.set_yticks([])
    
    plt.tight_layout()
    plt.savefig(f"{save_dir}/detailed_performance_analysis.png", dpi=300, bbox_inches='tight')
    print(f"Detailed performance analysis plot saved to {save_dir}/detailed_performance_analysis.png")


def create_accuracy_analysis_plots(evaluation_results, y_test, save_dir):
    """Create accuracy analysis plots."""
    print("Creating accuracy analysis plots...")
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Accuracy Analysis: Predictions vs True Values', fontsize=16, fontweight='bold')
    
    # Separate ML and Classical estimators
    ml_estimators = ['Random Forest', 'Gradient Boosting', 'SVR (RBF)']
    classical_estimators = [name for name in evaluation_results.keys() 
                          if name not in ml_estimators and 'error' not in evaluation_results[name]]
    
    # 1. ML Estimators Predictions
    ax1 = axes[0, 0]
    colors = ['#FF6B35', '#FF8C42', '#FFA552']
    
    for i, name in enumerate(ml_estimators):
        if name in evaluation_results and 'error' not in evaluation_results[name]:
            predictions = evaluation_results[name]['predictions']
            ax1.scatter(y_test, predictions, alpha=0.6, label=name, 
                       color=colors[i % len(colors)], s=30)
    
    # Perfect prediction line
    ax1.plot([0, 1], [0, 1], 'k--', alpha=0.5, linewidth=2, label='Perfect Prediction')
    
    ax1.set_xlabel('True Hurst Parameter')
    ax1.set_ylabel('Predicted Hurst Parameter')
    ax1.set_title('ML Estimators Accuracy', fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    
    # 2. Classical Estimators Predictions
    ax2 = axes[0, 1]
    colors = ['#1E88E5', '#1976D2', '#1565C0', '#0D47A1', '#0277BD', '#0288D1']
    
    for i, name in enumerate(classical_estimators[:6]):  # Limit to 6 for visibility
        if name in evaluation_results and 'error' not in evaluation_results[name]:
            predictions = evaluation_results[name]['predictions']
            ax2.scatter(y_test, predictions, alpha=0.6, label=name, 
                       color=colors[i % len(colors)], s=30)
    
    # Perfect prediction line
    ax2.plot([0, 1], [0, 1], 'k--', alpha=0.5, linewidth=2, label='Perfect Prediction')
    
    ax2.set_xlabel('True Hurst Parameter')
    ax2.set_ylabel('Predicted Hurst Parameter')
    ax2.set_title('Classical Estimators Accuracy', fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    
    # 3. Error Distribution by Hurst Parameter Range
    ax3 = axes[1, 0]
    
    # Define Hurst ranges
    hurst_ranges = [(0.1, 0.3), (0.3, 0.5), (0.5, 0.7), (0.7, 0.9)]
    range_labels = ['0.1-0.3\n(Anti-persistent)', '0.3-0.5\n(Short Memory)', 
                   '0.5-0.7\n(Long Memory)', '0.7-0.9\n(Persistent)']
    
    ml_errors_by_range = []
    classical_errors_by_range = []
    
    for h_min, h_max in hurst_ranges:
        mask = (y_test >= h_min) & (y_test < h_max)
        
        # ML errors
        ml_errors = []
        for name in ml_estimators:
            if name in evaluation_results and 'error' not in evaluation_results[name]:
                predictions = evaluation_results[name]['predictions']
                errors = np.abs(predictions[mask] - y_test[mask])
                ml_errors.extend(errors)
        
        # Classical errors
        classical_errors = []
        for name in classical_estimators:
            if name in evaluation_results and 'error' not in evaluation_results[name]:
                predictions = evaluation_results[name]['predictions']
                errors = np.abs(predictions[mask] - y_test[mask])
                classical_errors.extend(errors)
        
        ml_errors_by_range.append(ml_errors)
        classical_errors_by_range.append(classical_errors)
    
    # Create box plots
    positions_ml = [1, 3, 5, 7]
    positions_classical = [1.5, 3.5, 5.5, 7.5]
    
    bp1 = ax3.boxplot(ml_errors_by_range, positions=positions_ml, 
                     widths=0.4, patch_artist=True, 
                     boxprops=dict(facecolor='#FF6B35', alpha=0.7),
                     medianprops=dict(color='red', linewidth=2))
    
    bp2 = ax3.boxplot(classical_errors_by_range, positions=positions_classical, 
                     widths=0.4, patch_artist=True,
                     boxprops=dict(facecolor='#1E88E5', alpha=0.7),
                     medianprops=dict(color='blue', linewidth=2))
    
    ax3.set_xlabel('Hurst Parameter Range')
    ax3.set_ylabel('Absolute Error')
    ax3.set_title('Error Distribution by Hurst Range', fontweight='bold')
    ax3.set_xticks([1.25, 3.25, 5.25, 7.25])
    ax3.set_xticklabels(range_labels)
    ax3.grid(True, alpha=0.3)
    
    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor='#FF6B35', alpha=0.7, label='ML'),
                      Patch(facecolor='#1E88E5', alpha=0.7, label='Classical')]
    ax3.legend(handles=legend_elements)
    
    # 4. Performance Summary Statistics
    ax4 = axes[1, 1]
    ax4.axis('off')
    
    # Calculate summary statistics
    ml_results = []
    classical_results = []
    
    for name in ml_estimators:
        if name in evaluation_results and 'error' not in evaluation_results[name]:
            ml_results.append(evaluation_results[name])
    
    for name in classical_estimators:
        if name in evaluation_results and 'error' not in evaluation_results[name]:
            classical_results.append(evaluation_results[name])
    
    if ml_results and classical_results:
        ml_r2_mean = np.mean([r['r2'] for r in ml_results])
        ml_mae_mean = np.mean([r['mae'] for r in ml_results])
        ml_time_mean = np.mean([r['evaluation_time'] for r in ml_results])
        
        classical_r2_mean = np.mean([r['r2'] for r in classical_results])
        classical_mae_mean = np.mean([r['mae'] for r in classical_results])
        classical_time_mean = np.mean([r['evaluation_time'] for r in classical_results])
        
        summary_text = f"""
        PERFORMANCE SUMMARY
        
        Machine Learning Estimators:
        • Average R²: {ml_r2_mean:.3f}
        • Average MAE: {ml_mae_mean:.3f}
        • Average Time: {ml_time_mean:.2f}s
        • Count: {len(ml_results)}
        
        Classical Estimators:
        • Average R²: {classical_r2_mean:.3f}
        • Average MAE: {classical_mae_mean:.3f}
        • Average Time: {classical_time_mean:.2f}s
        • Count: {len(classical_results)}
        
        COMPARISON:
        • R² Advantage: {"ML" if ml_r2_mean > classical_r2_mean else "Classical"} 
          (+{abs(ml_r2_mean - classical_r2_mean):.3f})
        • MAE Advantage: {"ML" if ml_mae_mean < classical_mae_mean else "Classical"}
          (-{abs(ml_mae_mean - classical_mae_mean):.3f})
        • Speed Advantage: {"ML" if ml_time_mean < classical_time_mean else "Classical"}
          (-{abs(ml_time_mean - classical_time_mean):.2f}s)
        """
        
        ax4.text(0.05, 0.95, summary_text, transform=ax4.transAxes, 
                fontsize=11, verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(f"{save_dir}/accuracy_analysis.png", dpi=300, bbox_inches='tight')
    print(f"Accuracy analysis plot saved to {save_dir}/accuracy_analysis.png")


def print_comprehensive_summary(results_df):
    """Print comprehensive summary with detailed analysis."""
    ml_results = results_df[results_df['Type'] == 'ML']
    classical_results = results_df[results_df['Type'] == 'Classical']
    
    print("\n" + "="*80)
    print("COMPREHENSIVE ML vs CLASSICAL BENCHMARKING SUMMARY")
    print("="*80)
    
    print("\n🏆 TOP PERFORMERS BY CATEGORY:")
    print("-" * 40)
    
    print(f"🎯 BEST ACCURACY (R²):")
    best_r2 = results_df.loc[results_df['R²'].idxmax()]
    print(f"   {best_r2['Estimator']} ({best_r2['Type']}): R² = {best_r2['R²']:.3f}")
    
    print(f"🎯 BEST PRECISION (MAE):")
    best_mae = results_df.loc[results_df['MAE'].idxmin()]
    print(f"   {best_mae['Estimator']} ({best_mae['Type']}): MAE = {best_mae['MAE']:.3f}")
    
    print(f"⚡ FASTEST ESTIMATOR:")
    fastest = results_df.loc[results_df['Evaluation Time (s)'].idxmin()]
    print(f"   {fastest['Estimator']} ({fastest['Type']}): {fastest['Evaluation Time (s)']:.3f}s")
    
    print(f"\n📊 MACHINE LEARNING vs CLASSICAL COMPARISON:")
    print("-" * 50)
    
    if not ml_results.empty and not classical_results.empty:
        ml_r2_mean = ml_results['R²'].mean()
        classical_r2_mean = classical_results['R²'].mean()
        ml_mae_mean = ml_results['MAE'].mean()
        classical_mae_mean = classical_results['MAE'].mean()
        ml_time_mean = ml_results['Evaluation Time (s)'].mean()
        classical_time_mean = classical_results['Evaluation Time (s)'].mean()
        
        print(f"📈 ACCURACY (R² Score):")
        print(f"   ML Average:        {ml_r2_mean:.3f}")
        print(f"   Classical Average: {classical_r2_mean:.3f}")
        print(f"   Winner: {'🤖 ML' if ml_r2_mean > classical_r2_mean else '📚 Classical'} "
              f"(+{abs(ml_r2_mean - classical_r2_mean):.3f})")
        
        print(f"\n🎯 PRECISION (MAE):")
        print(f"   ML Average:        {ml_mae_mean:.3f}")
        print(f"   Classical Average: {classical_mae_mean:.3f}")
        print(f"   Winner: {'🤖 ML' if ml_mae_mean < classical_mae_mean else '📚 Classical'} "
              f"(-{abs(ml_mae_mean - classical_mae_mean):.3f})")
        
        print(f"\n⚡ EFFICIENCY (Evaluation Time):")
        print(f"   ML Average:        {ml_time_mean:.3f}s")
        print(f"   Classical Average: {classical_time_mean:.3f}s")
        print(f"   Winner: {'🤖 ML' if ml_time_mean < classical_time_mean else '📚 Classical'} "
              f"(-{abs(ml_time_mean - classical_time_mean):.3f}s)")
        
        # Overall assessment
        ml_wins = sum([
            ml_r2_mean > classical_r2_mean,  # Accuracy
            ml_mae_mean < classical_mae_mean,  # Precision
            ml_time_mean < classical_time_mean   # Speed
        ])
        
        print(f"\n🏆 OVERALL WINNER: {'🤖 MACHINE LEARNING' if ml_wins >= 2 else '📚 CLASSICAL'}")
        print(f"   Wins: {'ML' if ml_wins >= 2 else 'Classical'} ({ml_wins}/3 categories)")
    
    print(f"\n📋 DETAILED RANKINGS:")
    print("-" * 30)
    
    print("By R² Score (Accuracy):")
    top_r2 = results_df.nlargest(5, 'R²')
    for i, (_, row) in enumerate(top_r2.iterrows(), 1):
        icon = "🤖" if row['Type'] == 'ML' else "📚"
        print(f"   {i}. {icon} {row['Estimator']}: R² = {row['R²']:.3f}")
    
    print("\nBy MAE (Precision):")
    top_mae = results_df.nsmallest(5, 'MAE')
    for i, (_, row) in enumerate(top_mae.iterrows(), 1):
        icon = "🤖" if row['Type'] == 'ML' else "📚"
        print(f"   {i}. {icon} {row['Estimator']}: MAE = {row['MAE']:.3f}")
    
    print("\nBy Speed (Evaluation Time):")
    top_speed = results_df.nsmallest(5, 'Evaluation Time (s)')
    for i, (_, row) in enumerate(top_speed.iterrows(), 1):
        icon = "🤖" if row['Type'] == 'ML' else "📚"
        print(f"   {i}. {icon} {row['Estimator']}: {row['Evaluation Time (s)']:.3f}s")
    
    print("\n" + "="*80)


def main():
    parser = argparse.ArgumentParser(description="Comprehensive ML vs Classical Estimators Benchmark")
    parser.add_argument("--force-retrain", action="store_true", help="Force retraining ML models, ignoring cached checkpoints")
    parser.add_argument("--model-dir", type=str, default="saved_models", help="Directory to save/load ML model checkpoints")
    args = parser.parse_args()
    """Main benchmarking function."""
    print("="*60)
    print("COMPREHENSIVE ML VS CLASSICAL ESTIMATORS BENCHMARKING")
    print("="*60)
    
    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_dir = f"results/comprehensive_benchmark_{timestamp}"
    Path(save_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate training data for ML estimators
    X_train, y_train = generate_training_data(n_samples=500, data_length=1024)
    
    # Generate test data
    X_test, y_test, model_info = generate_test_data(n_samples=200, data_length=1024)
    
    print(f"Training set size: {len(X_train)}")
    print(f"Test set size: {len(X_test)}")
    
    # Create estimators
    estimators = create_estimators()
    
    # Train or load ML estimators (train-once, apply-many)
    training_results = train_ml_estimators(
        estimators,
        X_train,
        y_train,
        model_dir=args.model_dir,
        force_retrain=args.force_retrain,
    )
    
    # Evaluate all estimators
    evaluation_results = evaluate_estimators(estimators, X_test, y_test, training_results)
    
    # Create comparison plots and save results
    results_df = create_comparison_plots(evaluation_results, X_test, y_test, save_dir)
    
    print(f"\nComprehensive benchmarking completed! Results saved to {save_dir}/")
    
    return results_df


if __name__ == "__main__":
    results = main()
