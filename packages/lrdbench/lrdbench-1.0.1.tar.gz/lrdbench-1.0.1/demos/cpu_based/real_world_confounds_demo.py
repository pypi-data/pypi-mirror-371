"""
Real-World Confounds Demo

This script demonstrates the complex time series library and contamination models,
showing how to generate realistic time series with various types of confounds
and test estimator robustness against these contaminations.

Features:
1. Complex time series generation with multiple contaminations
2. Estimator robustness testing against confounds
3. Statistical analysis of contaminated data
4. Visualization of contamination effects
5. Performance comparison across different estimators
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Any, Optional
import sys
import os
import argparse
from dataclasses import dataclass
import pandas as pd

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.contamination.complex_time_series_library import (
    ComplexTimeSeriesLibrary, ComplexTimeSeriesType, ComplexTimeSeriesConfig
)
from models.contamination.contamination_models import (
    ContaminationModel, ContaminationType
)
from models.data_models.fbm.fbm_model import FractionalBrownianMotion
from models.data_models.fgn.fgn_model import FractionalGaussianNoise
from models.data_models.arfima.arfima_model import ARFIMAModel
from models.data_models.mrw.mrw_model import MultifractalRandomWalk

# Import estimators
from analysis.temporal.dfa.dfa_estimator import DFAEstimator
from analysis.temporal.rs.rs_estimator import RSEstimator
from analysis.temporal.higuchi.higuchi_estimator import HiguchiEstimator
from analysis.temporal.dma.dma_estimator import DMAEstimator
from analysis.spectral.periodogram.periodogram_estimator import PeriodogramEstimator
from analysis.spectral.whittle.whittle_estimator import WhittleEstimator
from analysis.spectral.gph.gph_estimator import GPHEstimator
from analysis.wavelet.variance.wavelet_variance_estimator import WaveletVarianceEstimator
from analysis.wavelet.log_variance.wavelet_log_variance_estimator import WaveletLogVarianceEstimator
from analysis.wavelet.whittle.wavelet_whittle_estimator import WaveletWhittleEstimator
from analysis.wavelet.cwt.cwt_estimator import CWTEstimator
from analysis.multifractal.mfdfa.mfdfa_estimator import MFDFAEstimator
from analysis.multifractal.wavelet_leaders.multifractal_wavelet_leaders_estimator import MultifractalWaveletLeadersEstimator


@dataclass
class EstimatorConfig:
    """Configuration for estimator testing."""
    
    # Temporal estimators
    dfa_min_window: int = 10
    dfa_max_window: int = 100
    rs_min_window: int = 10
    rs_max_window: int = 100
    higuchi_min_k: int = 2
    higuchi_max_k: int = 20
    dma_min_window: int = 10
    dma_max_window: int = 100
    
    # Spectral estimators
    periodogram_min_freq: float = 0.01
    periodogram_max_freq: float = 0.1
    whittle_min_freq: float = 0.01
    whittle_max_freq: float = 0.1
    gph_min_freq: float = 0.01
    gph_max_freq: float = 0.1
    
    # Wavelet estimators
    wavelet_min_scale: int = 2
    wavelet_max_scale: int = 8
    cwt_min_scale: float = 1.0
    cwt_max_scale: float = 64.0
    
    # Multifractal estimators
    mfdfa_min_window: int = 10
    mfdfa_max_window: int = 100
    q_values: List[float] = None
    
    def __post_init__(self):
        if self.q_values is None:
            self.q_values = [-5, -3, -1, 0, 1, 3, 5]


class RealWorldConfoundsDemo:
    """
    Demo class for showcasing real-world confounds and contamination models.
    """
    
    def __init__(self, config: Optional[ComplexTimeSeriesConfig] = None,
                 estimator_config: Optional[EstimatorConfig] = None):
        """
        Initialize the real-world confounds demo.
        
        Parameters
        ----------
        config : ComplexTimeSeriesConfig, optional
            Configuration for complex time series generation
        estimator_config : EstimatorConfig, optional
            Configuration for estimators
        """
        self.config = config or ComplexTimeSeriesConfig()
        self.estimator_config = estimator_config or EstimatorConfig()
        
        # Initialize complex time series library
        self.library = ComplexTimeSeriesLibrary(self.config)
        
        # Initialize estimators
        self.estimators = self._initialize_estimators()
        
        # Results storage
        self.results = {}
        
    def _initialize_estimators(self) -> Dict[str, Any]:
        """Initialize all estimators for testing."""
        estimators = {}
        
        # Temporal estimators
        estimators['DFA'] = DFAEstimator(
            min_box_size=self.estimator_config.dfa_min_window,
            max_box_size=self.estimator_config.dfa_max_window
        )
        estimators['R/S'] = RSEstimator(
            min_window_size=self.estimator_config.rs_min_window,
            max_window_size=self.estimator_config.rs_max_window
        )
        estimators['Higuchi'] = HiguchiEstimator(
            min_k=self.estimator_config.higuchi_min_k,
            max_k=self.estimator_config.higuchi_max_k
        )
        estimators['DMA'] = DMAEstimator(
            min_window_size=self.estimator_config.dma_min_window,
            max_window_size=self.estimator_config.dma_max_window
        )
        
        # Spectral estimators
        estimators['Periodogram'] = PeriodogramEstimator(
            min_freq_ratio=self.estimator_config.periodogram_min_freq,
            max_freq_ratio=self.estimator_config.periodogram_max_freq
        )
        estimators['Whittle'] = WhittleEstimator(
            min_freq_ratio=self.estimator_config.whittle_min_freq,
            max_freq_ratio=self.estimator_config.whittle_max_freq
        )
        estimators['GPH'] = GPHEstimator(
            min_freq_ratio=self.estimator_config.gph_min_freq,
            max_freq_ratio=self.estimator_config.gph_max_freq
        )
        
        # Wavelet estimators
        scales = list(range(self.estimator_config.wavelet_min_scale, self.estimator_config.wavelet_max_scale + 1))
        estimators['Wavelet Variance'] = WaveletVarianceEstimator(scales=scales)
        estimators['Wavelet Log Variance'] = WaveletLogVarianceEstimator(scales=scales)
        estimators['Wavelet Whittle'] = WaveletWhittleEstimator(scales=scales)
        cwt_scales = np.logspace(np.log10(self.estimator_config.cwt_min_scale), 
                                np.log10(self.estimator_config.cwt_max_scale), 20)
        estimators['CWT'] = CWTEstimator(scales=cwt_scales)
        
        # Multifractal estimators
        estimators['MFDFA'] = MFDFAEstimator(
            min_box_size=self.estimator_config.mfdfa_min_window,
            max_box_size=self.estimator_config.mfdfa_max_window,
            q_values=self.estimator_config.q_values
        )
        estimators['Wavelet Leaders'] = MultifractalWaveletLeadersEstimator(
            min_scale=self.estimator_config.wavelet_min_scale,
            max_scale=self.estimator_config.wavelet_max_scale,
            q_values=self.estimator_config.q_values
        )
        
        return estimators
    
    def generate_clean_data(self, n_samples: int = 1000) -> Dict[str, np.ndarray]:
        """Generate clean data from different models."""
        print("Generating clean data...")
        
        # Generate data from different models
        fbm = FractionalBrownianMotion(hurst_parameter=0.7)
        fgn = FractionalGaussianNoise(hurst_parameter=0.7)
        arfima = ARFIMAModel(d=0.3)
        mrw = MultifractalRandomWalk(hurst_parameter=0.7, lambda_squared=0.1)
        
        clean_data = {
            'fBm': fbm.simulate(n_samples),
            'fGn': fgn.simulate(n_samples),
            'ARFIMA': arfima.simulate(n_samples),
            'MRW': mrw.simulate(n_samples)
        }
        
        return clean_data
    
    def generate_contaminated_data(self, clean_data: Dict[str, np.ndarray]) -> Dict[str, Dict[str, np.ndarray]]:
        """Generate contaminated versions of clean data."""
        print("Generating contaminated data...")
        
        contaminated_data = {}
        
        # Get all complex time series types
        series_types = list(ComplexTimeSeriesType)
        
        for model_name, clean_series in clean_data.items():
            contaminated_data[model_name] = {}
            
            # Add clean version
            contaminated_data[model_name]['clean'] = clean_series
            
            # Generate contaminated versions
            for series_type in series_types:
                try:
                    contaminated_series = self.library.generate_complex_time_series(
                        series_type, clean_series
                    )
                    contaminated_data[model_name][series_type.value] = contaminated_series
                except Exception as e:
                    print(f"Warning: Could not generate {series_type.value} for {model_name}: {e}")
                    continue
        
        return contaminated_data
    
    def test_estimator_robustness(self, data: Dict[str, Dict[str, np.ndarray]]) -> Dict[str, Dict[str, Dict[str, float]]]:
        """Test estimator robustness against different contaminations."""
        print("Testing estimator robustness...")
        
        results = {}
        
        for model_name, model_data in data.items():
            results[model_name] = {}
            
            for contamination_type, series in model_data.items():
                results[model_name][contamination_type] = {}
                
                for estimator_name, estimator in self.estimators.items():
                    try:
                        # Estimate Hurst parameter
                        estimation_result = estimator.estimate(series)
                        results[model_name][contamination_type][estimator_name] = estimation_result.hurst_parameter
                    except Exception as e:
                        print(f"Warning: {estimator_name} failed for {model_name} - {contamination_type}: {e}")
                        results[model_name][contamination_type][estimator_name] = np.nan
        
        return results
    
    def analyze_results(self, results: Dict[str, Dict[str, Dict[str, float]]]) -> pd.DataFrame:
        """Analyze and summarize the results."""
        print("Analyzing results...")
        
        # Convert results to DataFrame
        rows = []
        for model_name, model_results in results.items():
            for contamination_type, contamination_results in model_results.items():
                for estimator_name, hurst_value in contamination_results.items():
                    rows.append({
                        'Model': model_name,
                        'Contamination': contamination_type,
                        'Estimator': estimator_name,
                        'Hurst_Parameter': hurst_value
                    })
        
        df = pd.DataFrame(rows)
        
        # Calculate statistics
        stats = df.groupby(['Model', 'Contamination'])['Hurst_Parameter'].agg([
            'mean', 'std', 'min', 'max', 'count'
        ]).reset_index()
        
        return df, stats
    
    def plot_results(self, df: pd.DataFrame, save_dir: Optional[str] = None) -> None:
        """Plot the results of the robustness testing."""
        print("Creating plots...")
        
        # Set up plotting style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Estimator Robustness to Real-World Confounds', fontsize=16, fontweight='bold')
        
        # 1. Box plot of Hurst parameter estimates by contamination type
        ax1 = axes[0, 0]
        contamination_order = ['clean', 'heavy_tailed_trending', 'noisy_seasonal', 
                              'long_memory_level_shifts', 'multifractal_measurement_errors']
        
        plot_data = df[df['Contamination'].isin(contamination_order)]
        sns.boxplot(data=plot_data, x='Contamination', y='Hurst_Parameter', ax=ax1)
        ax1.set_title('Hurst Parameter Estimates by Contamination Type')
        ax1.set_xlabel('Contamination Type')
        ax1.set_ylabel('Hurst Parameter')
        ax1.tick_params(axis='x', rotation=45)
        
        # 2. Heatmap of estimator performance
        ax2 = axes[0, 1]
        pivot_data = df.pivot_table(
            values='Hurst_Parameter', 
            index='Estimator', 
            columns='Contamination', 
            aggfunc='mean'
        )
        sns.heatmap(pivot_data, annot=True, fmt='.3f', cmap='RdYlBu_r', ax=ax2)
        ax2.set_title('Mean Hurst Parameter Estimates (Heatmap)')
        
        # 3. Estimator comparison for clean data
        ax3 = axes[1, 0]
        clean_data = df[df['Contamination'] == 'clean']
        sns.barplot(data=clean_data, x='Estimator', y='Hurst_Parameter', ax=ax3)
        ax3.set_title('Estimator Performance on Clean Data')
        ax3.set_xlabel('Estimator')
        ax3.set_ylabel('Hurst Parameter')
        ax3.tick_params(axis='x', rotation=45)
        
        # 4. Robustness comparison (std of estimates across contaminations)
        ax4 = axes[1, 1]
        robustness_data = df.groupby('Estimator')['Hurst_Parameter'].std().reset_index()
        robustness_data = robustness_data.sort_values('Hurst_Parameter', ascending=True)
        sns.barplot(data=robustness_data, x='Estimator', y='Hurst_Parameter', ax=ax4)
        ax4.set_title('Estimator Robustness (Lower is Better)')
        ax4.set_xlabel('Estimator')
        ax4.set_ylabel('Standard Deviation of Hurst Parameter')
        ax4.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        if save_dir:
            plt.savefig(os.path.join(save_dir, 'robustness_analysis.png'), 
                       dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def create_detailed_report(self, df: pd.DataFrame, stats: pd.DataFrame, 
                              save_dir: Optional[str] = None) -> None:
        """Create a detailed report of the analysis."""
        print("Creating detailed report...")
        
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("REAL-WORLD CONFOUNDS ROBUSTNESS ANALYSIS REPORT")
        report_lines.append("=" * 80)
        report_lines.append("")
        
        # Summary statistics
        report_lines.append("SUMMARY STATISTICS:")
        report_lines.append("-" * 40)
        report_lines.append(f"Total number of tests: {len(df)}")
        report_lines.append(f"Number of models: {df['Model'].nunique()}")
        report_lines.append(f"Number of contamination types: {df['Contamination'].nunique()}")
        report_lines.append(f"Number of estimators: {df['Estimator'].nunique()}")
        report_lines.append("")
        
        # Best performing estimators
        report_lines.append("BEST PERFORMING ESTIMATORS (by robustness):")
        report_lines.append("-" * 50)
        robustness_scores = df.groupby('Estimator')['Hurst_Parameter'].std().sort_values()
        for i, (estimator, score) in enumerate(robustness_scores.head(5).items()):
            report_lines.append(f"{i+1}. {estimator}: {score:.4f}")
        report_lines.append("")
        
        # Most challenging contaminations
        report_lines.append("MOST CHALLENGING CONTAMINATIONS:")
        report_lines.append("-" * 40)
        contamination_scores = df.groupby('Contamination')['Hurst_Parameter'].std().sort_values(ascending=False)
        for i, (contamination, score) in enumerate(contamination_scores.head(5).items()):
            report_lines.append(f"{i+1}. {contamination}: {score:.4f}")
        report_lines.append("")
        
        # Model-specific analysis
        report_lines.append("MODEL-SPECIFIC ANALYSIS:")
        report_lines.append("-" * 30)
        for model in df['Model'].unique():
            model_data = df[df['Model'] == model]
            clean_hurst = model_data[model_data['Contamination'] == 'clean']['Hurst_Parameter'].mean()
            report_lines.append(f"\n{model}:")
            report_lines.append(f"  Clean data Hurst parameter: {clean_hurst:.3f}")
            
            # Best estimator for this model
            model_robustness = model_data.groupby('Estimator')['Hurst_Parameter'].std().sort_values()
            best_estimator = model_robustness.index[0]
            report_lines.append(f"  Most robust estimator: {best_estimator}")
        
        # Save report
        if save_dir:
            report_path = os.path.join(save_dir, 'robustness_report.txt')
            with open(report_path, 'w') as f:
                f.write('\n'.join(report_lines))
        
        # Print report
        print('\n'.join(report_lines))
    
    def run_full_demo(self, n_samples: int = 1000, save_dir: Optional[str] = None) -> None:
        """Run the complete real-world confounds demonstration."""
        print("=" * 80)
        print("REAL-WORLD CONFOUNDS DEMO")
        print("=" * 80)
        
        # Create save directory if specified
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)
        
        # Generate data
        clean_data = self.generate_clean_data(n_samples)
        contaminated_data = self.generate_contaminated_data(clean_data)
        
        # Test robustness
        results = self.test_estimator_robustness(contaminated_data)
        
        # Analyze results
        df, stats = self.analyze_results(results)
        
        # Create visualizations
        self.plot_results(df, save_dir)
        
        # Create detailed report
        self.create_detailed_report(df, stats, save_dir)
        
        # Save results to CSV
        if save_dir:
            df.to_csv(os.path.join(save_dir, 'robustness_results.csv'), index=False)
            stats.to_csv(os.path.join(save_dir, 'robustness_stats.csv'), index=False)
        
        print("\n" + "=" * 80)
        print("DEMO COMPLETE")
        print("=" * 80)
        if save_dir:
            print(f"\nResults saved to: {save_dir}")


def main():
    """Main function to run the real-world confounds demo."""
    parser = argparse.ArgumentParser(description='Real-World Confounds Demo')
    parser.add_argument('--n-samples', type=int, default=1000,
                       help='Number of samples to generate')
    parser.add_argument('--save-dir', type=str, default='results/confounds_analysis',
                       help='Directory to save results')
    parser.add_argument('--no-plot', action='store_true',
                       help='Disable plotting')
    
    args = parser.parse_args()
    
    # Create demo instance
    demo = RealWorldConfoundsDemo()
    
    # Run the demonstration
    demo.run_full_demo(n_samples=args.n_samples, save_dir=args.save_dir)


if __name__ == "__main__":
    main()
