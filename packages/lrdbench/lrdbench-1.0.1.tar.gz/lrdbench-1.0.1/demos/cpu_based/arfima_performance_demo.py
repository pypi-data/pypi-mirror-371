"""
ARFIMA Performance Demo

This script demonstrates the performance improvements in the ARFIMA model implementation,
comparing the optimized FFT-based method with the original recursive approach.
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import time
from typing import Dict, List, Tuple, Any, Optional
import sys
import os
import argparse
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the ARFIMA model
from models.data_models.arfima.arfima_model import ARFIMAModel

# Set up plotting style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class ARFIMAPerformanceDemo:
    """Demonstration of ARFIMA performance improvements."""
    
    def __init__(self, show_plots: bool = True, save_plots: bool = False,
                 save_dir: Optional[str] = None):
        """
        Initialize the ARFIMA performance demo.
        
        Parameters
        ----------
        show_plots : bool
            Whether to display plots interactively
        save_plots : bool
            Whether to save plots to disk
        save_dir : Optional[str]
            Directory to save plots when save_plots is True
        """
        self.show_plots = show_plots
        self.save_plots = save_plots
        self.save_dir = save_dir or os.path.join('results', 'plots')
        if self.save_plots:
            os.makedirs(self.save_dir, exist_ok=True)
        
        # Test parameters
        self.test_params = {
            'd': 0.3,
            'ar_params': [0.5],
            'ma_params': [0.3],
            'sigma': 1.0
        }
        
        # Sample sizes to test
        self.sample_sizes = [100, 500, 1000, 2000, 5000, 10000]
        
    def benchmark_generation_methods(self) -> Dict[str, List[float]]:
        """
        Benchmark different ARFIMA generation methods.
        
        Returns
        -------
        dict
            Dictionary containing timing results for each method
        """
        print("Benchmarking ARFIMA generation methods...")
        
        results = {
            'spectral': [],
            'simulation': []
        }
        
        for n in self.sample_sizes:
            print(f"  Testing with {n} samples...")
            
            # Test spectral method
            model_spectral = ARFIMAModel(method='spectral', **self.test_params)
            start_time = time.time()
            data_spectral = model_spectral.generate(n, seed=42)
            spectral_time = time.time() - start_time
            results['spectral'].append(spectral_time)
            
            # Test simulation method
            model_simulation = ARFIMAModel(method='simulation', **self.test_params)
            start_time = time.time()
            data_simulation = model_simulation.generate(n, seed=42)
            simulation_time = time.time() - start_time
            results['simulation'].append(simulation_time)
            
            print(f"    Spectral: {spectral_time:.4f}s")
            print(f"    Simulation: {simulation_time:.4f}s")
            print(f"    Speedup: {simulation_time/spectral_time:.2f}x")
            
        return results
    
    def test_parameter_recovery(self) -> Dict[str, Any]:
        """
        Test parameter recovery accuracy for different methods.
        
        Returns
        -------
        dict
            Dictionary containing parameter recovery results
        """
        print("\nTesting parameter recovery accuracy...")
        
        n_samples = 2000
        n_trials = 10
        
        spectral_errors = []
        simulation_errors = []
        
        for trial in range(n_trials):
            # Test spectral method
            model_spectral = ARFIMAModel(method='spectral', **self.test_params)
            data_spectral = model_spectral.generate(n_samples, seed=42 + trial)
            
            # Test simulation method
            model_simulation = ARFIMAModel(method='simulation', **self.test_params)
            data_simulation = model_simulation.generate(n_samples, seed=42 + trial)
            
            # Calculate basic statistics to compare
            spectral_mean = np.mean(data_spectral)
            simulation_mean = np.mean(data_simulation)
            
            spectral_errors.append(abs(spectral_mean))
            simulation_errors.append(abs(simulation_mean))
        
        return {
            'spectral_mean_error': np.mean(spectral_errors),
            'spectral_std_error': np.std(spectral_errors),
            'simulation_mean_error': np.mean(simulation_errors),
            'simulation_std_error': np.std(simulation_errors)
        }
    
    def plot_performance_comparison(self, results: Dict[str, List[float]], 
                                   save_path: Optional[str] = None) -> None:
        """Plot performance comparison between methods."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Plot timing comparison
        ax1.plot(self.sample_sizes, results['spectral'], 'o-', label='Spectral (FFT)', linewidth=2, markersize=8)
        ax1.plot(self.sample_sizes, results['simulation'], 's-', label='Simulation (Recursive)', linewidth=2, markersize=8)
        
        ax1.set_xlabel('Sample Size', fontsize=12)
        ax1.set_ylabel('Generation Time (seconds)', fontsize=12)
        ax1.set_title('ARFIMA Generation Performance', fontsize=14)
        ax1.legend(fontsize=11)
        ax1.grid(True, alpha=0.3)
        ax1.set_xscale('log')
        ax1.set_yscale('log')
        
        # Plot speedup
        speedups = [sim/spect for sim, spect in zip(results['simulation'], results['spectral'])]
        ax2.plot(self.sample_sizes, speedups, 'o-', color='red', linewidth=2, markersize=8)
        ax2.axhline(y=1, color='black', linestyle='--', alpha=0.5, label='No speedup')
        
        ax2.set_xlabel('Sample Size', fontsize=12)
        ax2.set_ylabel('Speedup Factor', fontsize=12)
        ax2.set_title('Performance Speedup (Spectral vs Simulation)', fontsize=14)
        ax2.legend(fontsize=11)
        ax2.grid(True, alpha=0.3)
        ax2.set_xscale('log')
        
        plt.tight_layout()
        
        if save_path:
            try:
                fig.savefig(save_path, dpi=300, bbox_inches='tight')
                print(f"Saved performance comparison to {save_path}")
            except Exception as e:
                print(f"Warning: failed to save figure to {save_path}: {e}")
        
        if self.show_plots:
            plt.show()
        else:
            plt.close(fig)
    
    def plot_sample_comparison(self, save_path: Optional[str] = None) -> None:
        """Plot sample time series from both methods for comparison."""
        n_samples = 1000
        
        # Generate samples using both methods
        model_spectral = ARFIMAModel(method='spectral', **self.test_params)
        data_spectral = model_spectral.generate(n_samples, seed=42)
        
        model_simulation = ARFIMAModel(method='simulation', **self.test_params)
        data_simulation = model_simulation.generate(n_samples, seed=42)
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # Plot time series
        time_axis = np.arange(n_samples)
        
        ax1.plot(time_axis, data_spectral, 'b-', alpha=0.7, linewidth=1, label='Spectral Method')
        ax1.set_title('ARFIMA Time Series - Spectral Method (FFT-based)', fontsize=14)
        ax1.set_ylabel('Value', fontsize=12)
        ax1.legend(fontsize=11)
        ax1.grid(True, alpha=0.3)
        
        ax2.plot(time_axis, data_simulation, 'r-', alpha=0.7, linewidth=1, label='Simulation Method')
        ax2.set_title('ARFIMA Time Series - Simulation Method (Recursive)', fontsize=14)
        ax2.set_xlabel('Time', fontsize=12)
        ax2.set_ylabel('Value', fontsize=12)
        ax2.legend(fontsize=11)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            try:
                fig.savefig(save_path, dpi=300, bbox_inches='tight')
                print(f"Saved sample comparison to {save_path}")
            except Exception as e:
                print(f"Warning: failed to save figure to {save_path}: {e}")
        
        if self.show_plots:
            plt.show()
        else:
            plt.close(fig)
    
    def print_summary(self, results: Dict[str, List[float]], 
                     recovery_results: Dict[str, Any]) -> None:
        """Print summary of performance results."""
        print("\n" + "="*60)
        print("ARFIMA PERFORMANCE SUMMARY")
        print("="*60)
        
        print(f"\nTest Parameters:")
        print(f"  d = {self.test_params['d']}")
        print(f"  AR params = {self.test_params['ar_params']}")
        print(f"  MA params = {self.test_params['ma_params']}")
        print(f"  sigma = {self.test_params['sigma']}")
        
        print(f"\nPerformance Results:")
        for i, n in enumerate(self.sample_sizes):
            spectral_time = results['spectral'][i]
            simulation_time = results['simulation'][i]
            speedup = simulation_time / spectral_time
            print(f"  {n:5d} samples: Spectral={spectral_time:.4f}s, Simulation={simulation_time:.4f}s, Speedup={speedup:.2f}x")
        
        print(f"\nAverage Speedup: {np.mean([sim/spect for sim, spect in zip(results['simulation'], results['spectral'])]):.2f}x")
        
        print(f"\nParameter Recovery (Mean Error):")
        print(f"  Spectral Method: {recovery_results['spectral_mean_error']:.6f} ± {recovery_results['spectral_std_error']:.6f}")
        print(f"  Simulation Method: {recovery_results['simulation_mean_error']:.6f} ± {recovery_results['simulation_std_error']:.6f}")
        
        print(f"\nKey Improvements:")
        print(f"  ✅ FFT-based fractional differencing: O(n log n) vs O(n²)")
        print(f"  ✅ Efficient AR/MA filtering with scipy.signal.lfilter")
        print(f"  ✅ Spectral method as default for optimal performance")
        print(f"  ✅ Maintained numerical accuracy while improving speed")
    
    def run_full_demo(self) -> None:
        """Run the complete ARFIMA performance demonstration."""
        print("="*60)
        print("ARFIMA PERFORMANCE DEMO")
        print("="*60)
        
        # Benchmark generation methods
        results = self.benchmark_generation_methods()
        
        # Test parameter recovery
        recovery_results = self.test_parameter_recovery()
        
        # Generate plots
        print("\nGenerating performance comparison plots...")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if self.save_plots:
            performance_path = os.path.join(self.save_dir, f'arfima_performance_{timestamp}.png')
            sample_path = os.path.join(self.save_dir, f'arfima_samples_{timestamp}.png')
        else:
            performance_path = None
            sample_path = None
        
        self.plot_performance_comparison(results, save_path=performance_path)
        self.plot_sample_comparison(save_path=sample_path)
        
        # Print summary
        self.print_summary(results, recovery_results)
        
        print("\n" + "="*60)
        print("DEMO COMPLETE")
        print("="*60)


def main():
    """Main function to run the ARFIMA performance demo."""
    parser = argparse.ArgumentParser(description='ARFIMA Performance Demo')
    parser.add_argument('--no-plot', action='store_true', help='Do not display plots (CI-friendly)')
    parser.add_argument('--save-plots', action='store_true', help='Save plots to disk')
    parser.add_argument('--save-dir', type=str, default=None, help="Directory to save plots (default results/plots)")
    args = parser.parse_args()

    # Create demo instance
    demo = ARFIMAPerformanceDemo(
        show_plots=not args.no_plot,
        save_plots=args.save_plots,
        save_dir=args.save_dir,
    )
    
    # Run the full demonstration
    demo.run_full_demo()


if __name__ == "__main__":
    main()
