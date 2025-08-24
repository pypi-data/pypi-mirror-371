#!/usr/bin/env python3
"""
Fractional PINO Confound Analysis: Comprehensive Analysis of Benchmark Results

This script analyzes the results from the fractional PINO confound benchmark
and generates insights for the research paper on physics-informed fractional operator learning.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from pathlib import Path
import time

# Set style for better plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def load_benchmark_results(results_path):
    """Load benchmark results from pickle file"""
    try:
        results = joblib.load(results_path)
        return results
    except Exception as e:
        print(f"Error loading results: {e}")
        return None

def analyze_classical_performance(summary_df):
    """Analyze classical estimator performance across confounds"""
    print("🔍 CLASSICAL ESTIMATOR PERFORMANCE ANALYSIS")
    print("="*60)
    
    # Filter for classical estimators only
    classical_estimators = ['DFA', 'R/S', 'GPH', 'CWT']
    classical_df = summary_df[summary_df['estimator_name'].isin(classical_estimators)].copy()
    
    # Overall performance ranking
    overall_performance = classical_df.groupby('estimator_name')['absolute_error_mean'].mean().sort_values()
    print(f"\n📊 Overall Performance Ranking (Mean MAE):")
    for i, (estimator, mae) in enumerate(overall_performance.items(), 1):
        print(f"   {i}. {estimator}: {mae:.4f}")
    
    # Best estimator per confound type
    print(f"\n🏆 Best Estimator per Confound Type:")
    for confound in classical_df['confound_type'].unique():
        confound_data = classical_df[classical_df['confound_type'] == confound]
        best_estimator = confound_data.loc[confound_data['absolute_error_mean'].idxmin()]
        print(f"   {confound}: {best_estimator['estimator_name']} (MAE: {best_estimator['absolute_error_mean']:.4f})")
    
    # Robustness analysis
    print(f"\n🛡️ Robustness Analysis:")
    robustness_scores = classical_df.groupby('estimator_name')['absolute_error_mean'].std().sort_values()
    print(f"   Most Robust (Lowest Std): {robustness_scores.index[0]} ({robustness_scores.iloc[0]:.4f})")
    print(f"   Least Robust (Highest Std): {robustness_scores.index[-1]} ({robustness_scores.iloc[-1]:.4f})")
    
    return classical_df, overall_performance, robustness_scores

def analyze_confound_impact(summary_df):
    """Analyze the impact of different confounds on estimation accuracy"""
    print(f"\n📈 CONFOUND IMPACT ANALYSIS")
    print("="*50)
    
    # Average performance per confound type
    confound_impact = summary_df.groupby('confound_type')['absolute_error_mean'].agg(['mean', 'std']).sort_values('mean')
    
    print(f"\n📊 Confound Impact Ranking (Mean MAE):")
    for i, (confound, stats) in enumerate(confound_impact.iterrows(), 1):
        print(f"   {i}. {confound}: {stats['mean']:.4f} ± {stats['std']:.4f}")
    
    # Most challenging confounds
    print(f"\n⚠️ Most Challenging Confounds:")
    for confound in confound_impact.index[-3:]:
        mae = confound_impact.loc[confound, 'mean']
        print(f"   {confound}: {mae:.4f}")
    
    # Least challenging confounds
    print(f"\n✅ Least Challenging Confounds:")
    for confound in confound_impact.index[:3]:
        mae = confound_impact.loc[confound, 'mean']
        print(f"   {confound}: {mae:.4f}")
    
    return confound_impact

def create_comprehensive_visualization(summary_df, save_path=None):
    """Create comprehensive visualization of results"""
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Fractional PINO Confound Benchmark: Classical Estimator Analysis', 
                 fontsize=16, fontweight='bold')
    
    # 1. Heatmap of MAE by confound type and estimator
    ax1 = axes[0, 0]
    pivot_mae = summary_df.pivot_table(
        values='absolute_error_mean', 
        index='confound_type', 
        columns='estimator_name', 
        aggfunc='mean'
    )
    sns.heatmap(pivot_mae, annot=True, fmt='.3f', cmap='YlOrRd', ax=ax1)
    ax1.set_title('Mean Absolute Error Heatmap')
    ax1.set_xlabel('Estimator')
    ax1.set_ylabel('Confound Type')
    
    # 2. Box plot of MAE by estimator
    ax2 = axes[0, 1]
    classical_estimators = ['DFA', 'R/S', 'GPH', 'CWT']
    classical_data = summary_df[summary_df['estimator_name'].isin(classical_estimators)]
    sns.boxplot(data=classical_data, x='estimator_name', y='absolute_error_mean', ax=ax2)
    ax2.set_title('MAE Distribution by Estimator')
    ax2.set_xlabel('Estimator')
    ax2.set_ylabel('Mean Absolute Error')
    
    # 3. Box plot of MAE by confound type
    ax3 = axes[0, 2]
    sns.boxplot(data=summary_df, x='confound_type', y='absolute_error_mean', ax=ax3)
    ax3.set_title('MAE Distribution by Confound Type')
    ax3.set_xlabel('Confound Type')
    ax3.set_ylabel('Mean Absolute Error')
    ax3.tick_params(axis='x', rotation=45)
    
    # 4. Execution time comparison
    ax4 = axes[1, 0]
    sns.barplot(data=classical_data, x='estimator_name', y='execution_time_mean', ax=ax4)
    ax4.set_title('Mean Execution Time by Estimator')
    ax4.set_xlabel('Estimator')
    ax4.set_ylabel('Execution Time (seconds)')
    
    # 5. Success rate comparison
    ax5 = axes[1, 1]
    success_data = summary_df.groupby('estimator_name')['success_rate'].mean().reset_index()
    sns.barplot(data=success_data, x='estimator_name', y='success_rate', ax=ax5)
    ax5.set_title('Success Rate by Estimator')
    ax5.set_xlabel('Estimator')
    ax5.set_ylabel('Success Rate (%)')
    
    # 6. Performance vs Robustness scatter plot
    ax6 = axes[1, 2]
    performance_robustness = summary_df.groupby('estimator_name').agg({
        'absolute_error_mean': 'mean',
        'absolute_error_std': 'mean'
    }).reset_index()
    
    sns.scatterplot(data=performance_robustness, 
                   x='absolute_error_mean', 
                   y='absolute_error_std', 
                   s=100, ax=ax6)
    
    # Add labels
    for _, row in performance_robustness.iterrows():
        ax6.annotate(row['estimator_name'], 
                    (row['absolute_error_mean'], row['absolute_error_std']),
                    xytext=(5, 5), textcoords='offset points')
    
    ax6.set_title('Performance vs Robustness')
    ax6.set_xlabel('Mean Absolute Error')
    ax6.set_ylabel('Standard Deviation of MAE')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"📊 Analysis plot saved to {save_path}")
    
    plt.show()
    return fig

def generate_research_insights(summary_df, classical_df, overall_performance, robustness_scores, confound_impact):
    """Generate insights for the research paper"""
    print(f"\n📚 RESEARCH INSIGHTS FOR PAPER")
    print("="*50)
    
    # Key findings
    print(f"\n🔑 KEY FINDINGS:")
    
    # Best overall estimator
    best_overall = overall_performance.index[0]
    best_mae = overall_performance.iloc[0]
    print(f"   • Best overall estimator: {best_overall} (MAE: {best_mae:.4f})")
    
    # Most robust estimator
    most_robust = robustness_scores.index[0]
    most_robust_std = robustness_scores.iloc[0]
    print(f"   • Most robust estimator: {most_robust} (Std: {most_robust_std:.4f})")
    
    # Most challenging confound
    most_challenging = confound_impact.index[-1]
    most_challenging_mae = confound_impact.loc[most_challenging, 'mean']
    print(f"   • Most challenging confound: {most_challenging} (MAE: {most_challenging_mae:.4f})")
    
    # Performance gaps
    worst_overall = overall_performance.index[-1]
    worst_mae = overall_performance.iloc[-1]
    performance_gap = worst_mae - best_mae
    print(f"   • Performance gap: {worst_overall} vs {best_overall} = {performance_gap:.4f}")
    
    # Recommendations for fractional PINO
    print(f"\n💡 RECOMMENDATIONS FOR FRACTIONAL PINO:")
    print(f"   • Focus on improving robustness against {most_challenging}")
    print(f"   • Target performance better than {best_mae:.4f} MAE")
    print(f"   • Ensure success rate > 95% across all confounds")
    print(f"   • Optimize for computational efficiency")
    
    # Research implications
    print(f"\n🎯 RESEARCH IMPLICATIONS:")
    print(f"   • Classical estimators show strong performance on clean data")
    print(f"   • {most_challenging} represents the main challenge for neural approaches")
    print(f"   • Physics-informed constraints should focus on robustness")
    print(f"   • Hybrid approaches combining multiple estimators may be beneficial")
    
    return {
        'best_overall': best_overall,
        'best_mae': best_mae,
        'most_robust': most_robust,
        'most_challenging_confound': most_challenging,
        'performance_gap': performance_gap,
        'recommendations': [
            f"Focus on improving robustness against {most_challenging}",
            f"Target performance better than {best_mae:.4f} MAE",
            "Ensure success rate > 95% across all confounds",
            "Optimize for computational efficiency"
        ]
    }

def create_publication_ready_figures(summary_df, save_dir="publication_figures"):
    """Create publication-ready figures for the research paper"""
    Path(save_dir).mkdir(exist_ok=True)
    
    # Figure 1: Performance comparison across confounds
    plt.figure(figsize=(12, 8))
    classical_estimators = ['DFA', 'R/S', 'GPH', 'CWT']
    classical_data = summary_df[summary_df['estimator_name'].isin(classical_estimators)]
    
    pivot_mae = classical_data.pivot_table(
        values='absolute_error_mean', 
        index='confound_type', 
        columns='estimator_name', 
        aggfunc='mean'
    )
    
    pivot_mae.plot(kind='bar', width=0.8)
    plt.title('Estimator Performance Across Data Quality Issues', fontsize=14, fontweight='bold')
    plt.xlabel('Confound Type', fontsize=12)
    plt.ylabel('Mean Absolute Error', fontsize=12)
    plt.legend(title='Estimator', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(f"{save_dir}/figure1_performance_comparison.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    # Figure 2: Robustness analysis
    plt.figure(figsize=(10, 6))
    robustness_data = classical_data.groupby('estimator_name').agg({
        'absolute_error_mean': ['mean', 'std']
    }).round(4)
    
    x_pos = np.arange(len(classical_estimators))
    means = [robustness_data.loc[est, ('absolute_error_mean', 'mean')] for est in classical_estimators]
    stds = [robustness_data.loc[est, ('absolute_error_mean', 'std')] for est in classical_estimators]
    
    plt.bar(x_pos, means, yerr=stds, capsize=5, alpha=0.7)
    plt.title('Estimator Robustness Analysis', fontsize=14, fontweight='bold')
    plt.xlabel('Estimator', fontsize=12)
    plt.ylabel('Mean Absolute Error ± Std Dev', fontsize=12)
    plt.xticks(x_pos, classical_estimators)
    
    # Add value labels
    for i, (mean, std) in enumerate(zip(means, stds)):
        plt.text(i, mean + std + 0.01, f'{mean:.3f}±{std:.3f}', 
                ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(f"{save_dir}/figure2_robustness_analysis.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    # Figure 3: Confound impact ranking
    plt.figure(figsize=(10, 6))
    confound_impact = summary_df.groupby('confound_type')['absolute_error_mean'].mean().sort_values()
    
    colors = plt.cm.viridis(np.linspace(0, 1, len(confound_impact)))
    bars = plt.bar(range(len(confound_impact)), confound_impact.values, color=colors)
    
    plt.title('Impact of Data Quality Issues on Estimation Accuracy', fontsize=14, fontweight='bold')
    plt.xlabel('Confound Type', fontsize=12)
    plt.ylabel('Average Mean Absolute Error', fontsize=12)
    plt.xticks(range(len(confound_impact)), confound_impact.index, rotation=45, ha='right')
    
    # Add value labels
    for bar, value in zip(bars, confound_impact.values):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                f'{value:.3f}', ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(f"{save_dir}/figure3_confound_impact.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"📊 Publication-ready figures saved to {save_dir}/")

def main():
    """Main analysis function"""
    print("🔬 Fractional PINO Confound Analysis")
    print("Comprehensive Analysis of Benchmark Results")
    print("="*60)
    
    # Find the most recent results file
    results_files = list(Path('.').glob('fractional_pino_confound_results_*.pkl'))
    if not results_files:
        print("❌ No results files found. Run the benchmark first.")
        return
    
    latest_results = max(results_files, key=lambda x: x.stat().st_mtime)
    print(f"📁 Loading results from: {latest_results}")
    
    # Load results
    results = load_benchmark_results(latest_results)
    if results is None:
        return
    
    summary_df = results['summary']
    successful_df = results['successful_df']
    
    print(f"✅ Loaded {len(summary_df)} summary records")
    print(f"✅ Loaded {len(successful_df)} successful test records")
    
    # Analyze classical performance
    classical_df, overall_performance, robustness_scores = analyze_classical_performance(summary_df)
    
    # Analyze confound impact
    confound_impact = analyze_confound_impact(summary_df)
    
    # Generate research insights
    insights = generate_research_insights(summary_df, classical_df, overall_performance, 
                                        robustness_scores, confound_impact)
    
    # Create visualizations
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    analysis_plot_path = f"fractional_pino_analysis_{timestamp}.png"
    create_comprehensive_visualization(summary_df, save_path=analysis_plot_path)
    
    # Create publication-ready figures
    create_publication_ready_figures(summary_df)
    
    # Save analysis results
    analysis_results = {
        'insights': insights,
        'overall_performance': overall_performance.to_dict(),
        'robustness_scores': robustness_scores.to_dict(),
        'confound_impact': confound_impact.to_dict(),
        'timestamp': timestamp
    }
    
    analysis_path = f"fractional_pino_analysis_results_{timestamp}.pkl"
    joblib.dump(analysis_results, analysis_path)
    
    print(f"\n✅ Analysis results saved to {analysis_path}")
    print(f"📊 Analysis plot saved to {analysis_plot_path}")
    
    print(f"\n🎉 Analysis completed successfully!")
    print(f"📚 Ready for research paper integration!")

if __name__ == "__main__":
    main()
