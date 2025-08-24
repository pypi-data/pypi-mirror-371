"""
Parameter Estimation Demo

This script demonstrates various parameter estimation techniques for stochastic models:
- Temporal estimators: DFA, R/S, Higuchi, DMA
- Spectral estimators: Periodogram, Whittle, GPH
- Comparison of estimation accuracy
- Parameter recovery analysis
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Any, Optional
import sys
import os
import argparse
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import models and estimators
try:
    from models.data_models.fbm.fbm_model import FractionalBrownianMotion
    from models.data_models.fgn.fgn_model import FractionalGaussianNoise
    from models.data_models.arfima.arfima_model import ARFIMAModel
    from models.data_models.mrw.mrw_model import MultifractalRandomWalk
    
    # Import temporal estimators
    from analysis.temporal.dfa.dfa_estimator import DFAEstimator
    from analysis.temporal.rs.rs_estimator import RSEstimator
    from analysis.temporal.higuchi.higuchi_estimator import HiguchiEstimator
    from analysis.temporal.dma.dma_estimator import DMAEstimator
    # Import spectral estimators
    from analysis.spectral.periodogram.periodogram_estimator import PeriodogramEstimator
    from analysis.spectral.whittle.whittle_estimator import WhittleEstimator
    from analysis.spectral.gph.gph_estimator import GPHEstimator
    # Import wavelet estimators
    from analysis.wavelet.variance.wavelet_variance_estimator import WaveletVarianceEstimator
    from analysis.wavelet.log_variance.wavelet_log_variance_estimator import WaveletLogVarianceEstimator
    from analysis.wavelet.whittle.wavelet_whittle_estimator import WaveletWhittleEstimator
    from analysis.wavelet.cwt.cwt_estimator import CWTEstimator
    # Import multifractal estimators
    from analysis.multifractal.mfdfa.mfdfa_estimator import MFDFAEstimator
    from analysis.multifractal.wavelet_leaders.multifractal_wavelet_leaders_estimator import MultifractalWaveletLeadersEstimator
    
    ESTIMATORS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some estimators not available: {e}")
    ESTIMATORS_AVAILABLE = False

# Set up plotting style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class ParameterEstimationDemo:
    """Demonstration of parameter estimation techniques."""
    
    def __init__(self, n_samples: int = 2000, seed: int = 42,
                 show_plots: bool = True, save_plots: bool = False,
                 save_dir: Optional[str] = None):
        """
        Initialize the parameter estimation demo.
        
        Parameters
        ----------
        n_samples : int
            Number of samples to generate for estimation
        seed : int
            Random seed for reproducibility
        show_plots : bool
            Whether to display plots interactively
        save_plots : bool
            Whether to save plots to disk (location controlled by save_dir)
        save_dir : Optional[str]
            Directory to save plots when save_plots is True. Defaults to 'results/plots'.
        """
        self.n_samples = n_samples
        self.seed = seed
        np.random.seed(seed)
        self.show_plots = show_plots
        self.save_plots = save_plots
        self.save_dir = save_dir or os.path.join('results', 'plots')
        if self.save_plots:
            os.makedirs(self.save_dir, exist_ok=True)
        
        # True parameter values for testing
        self.true_params = {
            'fBm': {'H': 0.7, 'sigma': 1.0},
            'fGn': {'H': 0.6, 'sigma': 1.0},
            'ARFIMA': {'d': 0.3, 'ar_params': [0.5], 'ma_params': [0.3], 'sigma': 1.0},
            'MRW': {'H': 0.7, 'lambda_param': 0.3, 'sigma': 1.0}
        }
        
        self.generated_data = {}
        self.estimation_results = {}
        
    def _get_true_parameter(self, model_name: str) -> float:
        """
        Get the appropriate true parameter for comparison based on model type.
        
        Parameters
        ----------
        model_name : str
            Name of the model
            
        Returns
        -------
        float
            True parameter value for comparison
        """
        if model_name == 'ARFIMA':
            return self.true_params[model_name]['d']  # ARFIMA uses 'd' parameter
        else:
            return self.true_params[model_name]['H']  # fBm, fGn, MRW use 'H' parameter
        
    def generate_test_data(self) -> Dict[str, np.ndarray]:
        """
        Generate test data with known parameters.
        
        Returns
        -------
        dict
            Dictionary containing generated time series
        """
        print("Generating test data with known parameters...")
        
        for model_name, true_params in self.true_params.items():
            try:
                print(f"  Generating {model_name} data...")
                
                if model_name == 'fBm':
                    model = FractionalBrownianMotion(**true_params)
                elif model_name == 'fGn':
                    model = FractionalGaussianNoise(**true_params)
                elif model_name == 'ARFIMA':
                    model = ARFIMAModel(**true_params)
                elif model_name == 'MRW':
                    model = MultifractalRandomWalk(**true_params)
                else:
                    continue
                    
                data = model.generate(self.n_samples, seed=self.seed)
                self.generated_data[model_name] = data
                
                print(f"    ✓ Generated {len(data)} samples")
                print(f"    True parameters: {true_params}")
                
            except Exception as e:
                print(f"    ✗ Error generating {model_name}: {e}")
                continue
                
        return self.generated_data
    
    def run_temporal_estimators(self) -> Dict[str, Dict[str, Any]]:
        """
        Run temporal estimators on the generated data.
        
        Returns
        -------
        dict
            Dictionary containing estimation results
        """
        if not ESTIMATORS_AVAILABLE:
            print("Estimators not available. Please ensure all estimator implementations are complete.")
            return {}
            
        if not self.generated_data:
            print("No data available. Run generate_test_data() first.")
            return {}
            
        print("\nRunning temporal estimators...")
        
        temporal_estimators = {
            'DFA': DFAEstimator(),
            'R/S': RSEstimator(),
            'Higuchi': HiguchiEstimator(),
            'DMA': DMAEstimator()
        }
        
        results = {}
        
        for model_name, data in self.generated_data.items():
            print(f"  Estimating parameters for {model_name}...")
            results[model_name] = {}
            
            for est_name, estimator in temporal_estimators.items():
                try:
                    print(f"    Running {est_name}...")
                    output = estimator.estimate(data)
                    # Normalize to H
                    if isinstance(output, dict):
                        if 'hurst_parameter' in output:
                            estimated_H = float(output['hurst_parameter'])
                        elif 'fractal_dimension' in output:
                            estimated_H = float(2 - output['fractal_dimension'])
                        else:
                            raise ValueError("Estimator output missing 'hurst_parameter' or 'fractal_dimension'")
                    else:
                        estimated_H = float(output)

                    true_param = self._get_true_parameter(model_name)
                    entry = {
                        'H_estimated': estimated_H,
                        'H_true': true_param,
                        'error': abs(estimated_H - true_param)
                    }
                    results[model_name][est_name] = entry
                    print(f"      ✓ {est_name}: H = {estimated_H:.4f} (error: {entry['error']:.4f})")

                except Exception as e:
                    print(f"      ✗ Error with {est_name}: {e}")
                    results[model_name][est_name] = {'error': str(e)}
                    
        self.estimation_results['temporal'] = results
        return results
    
    def run_spectral_estimators(self) -> Dict[str, Dict[str, Any]]:
        """
        Run spectral estimators on the generated data.
        
        Returns
        -------
        dict
            Dictionary containing estimation results
        """
        if not ESTIMATORS_AVAILABLE:
            print("Estimators not available. Please ensure all estimator implementations are complete.")
            return {}
            
        if not self.generated_data:
            print("No data available. Run generate_test_data() first.")
            return {}
            
        print("\nRunning spectral estimators...")
        
        spectral_estimators = {
            'Periodogram': PeriodogramEstimator(),
            'Whittle': WhittleEstimator(),
            'GPH': GPHEstimator()
        }
        
        results = {}
        
        for model_name, data in self.generated_data.items():
            print(f"  Estimating parameters for {model_name}...")
            results[model_name] = {}
            
            for est_name, estimator in spectral_estimators.items():
                try:
                    print(f"    Running {est_name}...")
                    output = estimator.estimate(data)
                    if isinstance(output, dict):
                        if 'hurst_parameter' in output:
                            estimated_H = float(output['hurst_parameter'])
                        else:
                            raise ValueError("Estimator output missing 'hurst_parameter'")
                    else:
                        estimated_H = float(output)

                    true_param = self._get_true_parameter(model_name)
                    entry = {
                        'H_estimated': estimated_H,
                        'H_true': true_param,
                        'error': abs(estimated_H - true_param)
                    }
                    results[model_name][est_name] = entry
                    print(f"      ✓ {est_name}: H = {estimated_H:.4f} (error: {entry['error']:.4f})")

                except Exception as e:
                    print(f"      ✗ Error with {est_name}: {e}")
                    results[model_name][est_name] = {'error': str(e)}
                    
        self.estimation_results['spectral'] = results
        return results
    
    def run_wavelet_estimators(self) -> Dict[str, Dict[str, Any]]:
        """
        Run wavelet estimators on the generated data.
        
        Returns
        -------
        dict
            Dictionary containing estimation results
        """
        if not ESTIMATORS_AVAILABLE:
            print("Estimators not available. Please ensure all estimator implementations are complete.")
            return {}
            
        if not self.generated_data:
            print("No data available. Run generate_test_data() first.")
            return {}
            
        print("\nRunning wavelet estimators...")
        
        wavelet_estimators = {
            'Wavelet Variance': WaveletVarianceEstimator(),
            'Wavelet Log Variance': WaveletLogVarianceEstimator(),
            'Wavelet Whittle': WaveletWhittleEstimator(),
            'CWT': CWTEstimator()
        }
        
        results = {}
        
        for model_name, data in self.generated_data.items():
            print(f"  Estimating parameters for {model_name}...")
            results[model_name] = {}
            
            for est_name, estimator in wavelet_estimators.items():
                try:
                    print(f"    Running {est_name}...")
                    
                    # Wavelet estimators typically estimate Hurst parameter
                    estimated_H = estimator.estimate(data)
                    true_param = self._get_true_parameter(model_name)
                    results[model_name][est_name] = {
                        'H_estimated': estimated_H,
                        'H_true': true_param,
                        'error': abs(estimated_H - true_param)
                    }
                    
                    print(f"      ✓ {est_name}: H = {estimated_H:.4f} (error: {results[model_name][est_name]['error']:.4f})")
                    
                except Exception as e:
                    print(f"      ✗ Error with {est_name}: {e}")
                    results[model_name][est_name] = {'error': str(e)}
                    
        self.estimation_results['wavelet'] = results
        return results
    
    def run_multifractal_estimators(self) -> Dict[str, Dict[str, Any]]:
        """
        Run multifractal estimators on the generated data.
        
        Returns
        -------
        dict
            Dictionary containing estimation results
        """
        if not ESTIMATORS_AVAILABLE:
            print("Estimators not available. Please ensure all estimator implementations are complete.")
            return {}
            
        if not self.generated_data:
            print("No data available. Run generate_test_data() first.")
            return {}
            
        print("\nRunning multifractal estimators...")
        
        multifractal_estimators = {
            'MFDFA': MFDFAEstimator(),
            'Wavelet Leaders': MultifractalWaveletLeadersEstimator()
        }
        
        results = {}
        
        for model_name, data in self.generated_data.items():
            print(f"  Estimating parameters for {model_name}...")
            results[model_name] = {}
            
            for est_name, estimator in multifractal_estimators.items():
                try:
                    print(f"    Running {est_name}...")
                    
                    # Multifractal estimators estimate Hurst parameter
                    output = estimator.estimate(data)
                    if isinstance(output, dict):
                        if 'hurst_parameter' in output:
                            estimated_H = float(output['hurst_parameter'])
                        else:
                            raise ValueError("Estimator output missing 'hurst_parameter'")
                    else:
                        estimated_H = float(output)
                    
                    true_param = self._get_true_parameter(model_name)
                    results[model_name][est_name] = {
                        'H_estimated': estimated_H,
                        'H_true': true_param,
                        'error': abs(estimated_H - true_param)
                    }
                    
                    print(f"      ✓ {est_name}: H = {estimated_H:.4f} (error: {results[model_name][est_name]['error']:.4f})")
                    
                except Exception as e:
                    print(f"      ✗ Error with {est_name}: {e}")
                    results[model_name][est_name] = {'error': str(e)}
                    
        self.estimation_results['multifractal'] = results
        return results
    
    def plot_estimation_results(self, figsize: Tuple[int, int] = (20, 14),
                                save_path: Optional[str] = None) -> None:
        """Plot estimation results comparison."""
        if not self.estimation_results:
            print("No estimation results to plot. Run estimation methods first.")
            return
            
        fig, axes = plt.subplots(2, 3, figsize=(24, 16))
        axes = axes.flatten()
        
        # Plot temporal estimators
        if 'temporal' in self.estimation_results:
            ax1 = axes[0]
            self._plot_estimator_comparison(
                self.estimation_results['temporal'], 
                ax1, 
                'Temporal Estimators'
            )
        
        # Plot spectral estimators
        if 'spectral' in self.estimation_results:
            ax2 = axes[1]
            self._plot_estimator_comparison(
                self.estimation_results['spectral'], 
                ax2, 
                'Spectral Estimators'
            )
        
        # Plot wavelet estimators
        if 'wavelet' in self.estimation_results:
            ax3 = axes[2]
            self._plot_estimator_comparison(
                self.estimation_results['wavelet'], 
                ax3, 
                'Wavelet Estimators'
            )
        
        # Plot multifractal estimators
        if 'multifractal' in self.estimation_results:
            ax4 = axes[3]
            self._plot_estimator_comparison(
                self.estimation_results['multifractal'], 
                ax4, 
                'Multifractal Estimators'
            )
        
        # Plot error comparison
        ax5 = axes[4]
        self._plot_error_comparison(ax5)
        
        # Plot true vs estimated
        ax6 = axes[5]
        self._plot_true_vs_estimated(ax6)
        
        plt.tight_layout()
        if save_path:
            try:
                fig.savefig(save_path, dpi=300, bbox_inches='tight')
                print(f"Saved comparison figure to {save_path}")
            except Exception as e:
                print(f"Warning: failed to save figure to {save_path}: {e}")
        if self.show_plots:
            plt.show()
        else:
            plt.close(fig)
    
    def _plot_estimator_comparison(self, results: Dict, ax: plt.Axes, title: str) -> None:
        """Plot comparison of estimators for a given category."""
        models = list(results.keys())
        estimators = list(results[models[0]].keys()) if models else []
        
        x = np.arange(len(estimators))
        width = 0.35
        
        for i, model in enumerate(models):
            values = []
            for est in estimators:
                if 'H_estimated' in results[model][est]:
                    values.append(results[model][est]['H_estimated'])
                else:
                    values.append(np.nan)
            
            ax.bar(x + i * width, values, width, label=model, alpha=0.8)
        
        ax.set_xlabel('Estimator', fontsize=10)
        ax.set_ylabel('Estimated H', fontsize=10)
        ax.set_title(title, fontsize=12)
        ax.set_xticks(x + width / 2)
        ax.set_xticklabels(estimators, rotation=45, ha='right', fontsize=8)
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='both', which='major', labelsize=8)
    
    def _plot_error_comparison(self, ax: plt.Axes) -> None:
        """Plot estimation errors comparison with color-based grouping."""
        # Group errors by estimator type and calculate mean errors
        estimator_errors = {}
        estimator_colors = {
            'DFA': '#1f77b4',      # Blue
            'R/S': '#ff7f0e',      # Orange
            'Higuchi': '#2ca02c',   # Green
            'DMA': '#d62728',      # Red
            'Periodogram': '#9467bd', # Purple
            'Whittle': '#8c564b',   # Brown
            'GPH': '#e377c2',      # Pink
            'Wavelet Variance': '#7f7f7f', # Gray
            'Wavelet Log Variance': '#bcbd22', # Olive
            'Wavelet Whittle': '#17becf', # Cyan
            'CWT': '#ff9896',      # Light red
            'MFDFA': '#9467bd',    # Purple
            'Wavelet Leaders': '#8c564b'  # Brown
        }
        
        # Collect errors by estimator type
        for category, results in self.estimation_results.items():
            for model, estimators in results.items():
                for est_name, est_result in estimators.items():
                    if 'error' in est_result and isinstance(est_result['error'], (int, float)):
                        if est_name not in estimator_errors:
                            estimator_errors[est_name] = []
                        estimator_errors[est_name].append(est_result['error'])
        
        if estimator_errors:
            # Calculate mean errors for each estimator
            estimators = list(estimator_errors.keys())
            mean_errors = [np.mean(estimator_errors[est]) for est in estimators]
            std_errors = [np.std(estimator_errors[est]) for est in estimators]
            
            # Create color list
            colors = [estimator_colors.get(est, '#1f77b4') for est in estimators]
            
            # Create bar plot
            bars = ax.bar(range(len(estimators)), mean_errors, 
                         yerr=std_errors, capsize=5, alpha=0.8, color=colors)
            
            # Customize plot
            ax.set_xlabel('Estimator Type', fontsize=12)
            ax.set_ylabel('Mean Absolute Error', fontsize=12)
            ax.set_title('Estimation Errors by Method', fontsize=14)
            ax.set_xticks(range(len(estimators)))
            ax.set_xticklabels(estimators, rotation=45, ha='right', fontsize=10)
            ax.grid(True, alpha=0.3, axis='y')
            ax.tick_params(axis='both', which='major', labelsize=9)
            
            # Add value labels on bars
            for i, (bar, mean_err) in enumerate(zip(bars, mean_errors)):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                       f'{mean_err:.3f}', ha='center', va='bottom', fontsize=8)
            
            # Add legend for color coding
            legend_elements = []
            for est, color in estimator_colors.items():
                if est in estimators:
                    legend_elements.append(plt.Rectangle((0,0),1,1, facecolor=color, alpha=0.8, label=est))
            
            # Create a separate legend
            ax.legend(handles=legend_elements, loc='upper right', fontsize=8, 
                     bbox_to_anchor=(1.15, 1.0))
    
    def _plot_true_vs_estimated(self, ax: plt.Axes) -> None:
        """Plot true vs estimated parameter values with color coding."""
        # Color scheme for different estimator categories
        category_colors = {
            'temporal': '#1f77b4',    # Blue
            'spectral': '#ff7f0e',    # Orange  
            'wavelet': '#2ca02c',     # Green
            'multifractal': '#d62728' # Red
        }
        
        # Collect data by category
        category_data = {}
        for category, results in self.estimation_results.items():
            category_data[category] = {'true': [], 'estimated': [], 'estimators': []}
            for model, estimators in results.items():
                true_param = self._get_true_parameter(model)
                for est_name, est_result in estimators.items():
                    if 'H_estimated' in est_result:
                        category_data[category]['true'].append(true_param)
                        category_data[category]['estimated'].append(est_result['H_estimated'])
                        category_data[category]['estimators'].append(est_name)
        
        # Plot each category with different colors
        legend_elements = []
        for category, data in category_data.items():
            if data['true']:
                color = category_colors.get(category, '#1f77b4')
                ax.scatter(data['true'], data['estimated'], 
                          alpha=0.7, s=80, color=color, label=category.title())
                legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', 
                                                markerfacecolor=color, markersize=8, label=category.title()))
        
        # Add perfect estimation line
        ax.plot([0, 1], [0, 1], 'r--', alpha=0.8, linewidth=2, label='Perfect Estimation')
        
        # Customize plot
        ax.set_xlabel('True H', fontsize=12)
        ax.set_ylabel('Estimated H', fontsize=12)
        ax.set_title('True vs Estimated Parameters', fontsize=14)
        ax.legend(fontsize=10, loc='lower left')
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='both', which='major', labelsize=9)
        
        # Set axis limits
        ax.set_xlim(0.5, 0.9)
        ax.set_ylim(0.0, 0.9)
    
    def print_summary(self) -> None:
        """Print summary of estimation results."""
        if not self.estimation_results:
            print("No estimation results to summarize.")
            return
            
        print("\n" + "="*60)
        print("ESTIMATION SUMMARY")
        print("="*60)
        
        for category, results in self.estimation_results.items():
            print(f"\n{category.upper()} ESTIMATORS:")
            print("-" * 40)
            
            for model, estimators in results.items():
                print(f"\n{model}:")
                for est_name, est_result in estimators.items():
                    if 'H_estimated' in est_result:
                        print(f"  {est_name}:")
                        print(f"    True H: {est_result['H_true']:.4f}")
                        print(f"    Estimated H: {est_result['H_estimated']:.4f}")
                        print(f"    Error: {est_result['error']:.4f}")
                    else:
                        print(f"  {est_name}: Error - {est_result.get('error', 'Unknown')}")
    
    def run_full_demo(self) -> None:
        """Run the complete parameter estimation demonstration."""
        print("="*60)
        print("PARAMETER ESTIMATION DEMO")
        print("="*60)
        
        # Generate test data
        self.generate_test_data()
        
        if not self.generated_data:
            print("No data was generated. Demo cannot continue.")
            return
        
        # Run temporal estimators
        self.run_temporal_estimators()
        
        # Run spectral estimators
        self.run_spectral_estimators()
        
        # Run wavelet estimators
        self.run_wavelet_estimators()
        
        # Run multifractal estimators
        self.run_multifractal_estimators()
        
        # Plot results
        # Plot results (save and/or show depending on flags)
        print("\nGenerating estimation comparison plots...")
        save_path = None
        if self.save_plots:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_path = os.path.join(self.save_dir, f'estimation_comparison_{timestamp}.png')
        self.plot_estimation_results(save_path=save_path)
        
        # Print summary
        self.print_summary()
        
        print("\n" + "="*60)
        print("DEMO COMPLETE")
        print("="*60)


def main():
    """Main function to run the parameter estimation demo."""
    parser = argparse.ArgumentParser(description='Parameter Estimation Demo')
    parser.add_argument('--n-samples', type=int, default=2000, help='Number of samples to generate')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    parser.add_argument('--no-plot', action='store_true', help='Do not display plots (CI-friendly)')
    parser.add_argument('--save-plots', action='store_true', help='Save plots to disk')
    parser.add_argument('--save-dir', type=str, default=None, help="Directory to save plots (default results/plots)")
    args = parser.parse_args()

    # Create demo instance
    demo = ParameterEstimationDemo(
        n_samples=args.n_samples,
        seed=args.seed,
        show_plots=not args.no_plot,
        save_plots=args.save_plots,
        save_dir=args.save_dir,
    )
    
    # Run the full demonstration
    demo.run_full_demo()


if __name__ == "__main__":
    main()
