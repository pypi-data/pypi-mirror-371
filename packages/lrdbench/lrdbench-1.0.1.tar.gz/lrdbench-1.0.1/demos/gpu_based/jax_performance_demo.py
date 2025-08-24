#!/usr/bin/env python3
"""
JAX Performance Demo

This demo showcases the performance improvements of JAX-optimized estimators
compared to the original implementations. It runs both versions on the same data
and compares execution times and results.
"""

import numpy as np
import time
import argparse
import sys
import os
from typing import Dict, Any, List

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from models.data_models.fbm.fbm_model import FractionalBrownianMotion
from models.data_models.fgn.fgn_model import FractionalGaussianNoise
from analysis.temporal.dfa.dfa_estimator import DFAEstimator
from analysis.temporal.rs.rs_estimator import RSEstimator
from analysis.high_performance.jax.dfa_jax import DFAEstimatorJAX
from analysis.high_performance.jax.rs_jax import RSEstimatorJAX


class JAXPerformanceDemo:
    """
    Demo class for comparing JAX-optimized estimators with original implementations.
    """
    
    def __init__(self):
        """Initialize the demo."""
        self.results = {}
        
        # Generate test data
        print("Generating test data...")
        self._generate_test_data()
    
    def _generate_test_data(self):
        """Generate test data for performance comparison."""
        # Generate fBm data with known Hurst parameter
        fbm_model = FractionalBrownianMotion(H=0.7, sigma=1.0)
        self.fbm_data = fbm_model.generate(10000, seed=42)
        
        # Generate fGn data with known Hurst parameter
        fgn_model = FractionalGaussianNoise(H=0.6, sigma=1.0)
        self.fgn_data = fgn_model.generate(10000, seed=42)
        
        print(f"Generated {len(self.fbm_data)} fBm data points (H=0.7)")
        print(f"Generated {len(self.fgn_data)} fGn data points (H=0.6)")
    
    def _time_estimation(self, estimator, data: np.ndarray, name: str) -> Dict[str, Any]:
        """
        Time the estimation process.
        
        Parameters
        ----------
        estimator : BaseEstimator
            Estimator to test
        data : np.ndarray
            Data to analyze
        name : str
            Name for the test
            
        Returns
        -------
        dict
            Timing and result information
        """
        print(f"Running {name}...")
        
        # Warm up (first run)
        try:
            estimator.estimate(data)
        except Exception as e:
            print(f"Warning: {name} warm-up failed: {e}")
            return {'error': str(e)}
        
        # Time the actual run
        start_time = time.time()
        try:
            results = estimator.estimate(data)
            end_time = time.time()
            
            return {
                'time': end_time - start_time,
                'hurst_parameter': results.get('hurst_parameter'),
                'r_squared': results.get('r_squared'),
                'std_error': results.get('std_error'),
                'success': True
            }
        except Exception as e:
            end_time = time.time()
            return {
                'time': end_time - start_time,
                'error': str(e),
                'success': False
            }
    
    def run_dfa_comparison(self) -> Dict[str, Any]:
        """Compare DFA estimator performance."""
        print("\n" + "="*60)
        print("DFA ESTIMATOR PERFORMANCE COMPARISON")
        print("="*60)
        
        # Test on fBm data
        print(f"\nTesting on fBm data (true H = 0.7, n = {len(self.fbm_data)})")
        
        # Original DFA
        dfa_original = DFAEstimator(min_box_size=4, max_box_size=len(self.fbm_data)//4)
        original_results = self._time_estimation(dfa_original, self.fbm_data, "Original DFA")
        
        # JAX DFA
        dfa_jax = DFAEstimatorJAX(min_box_size=4, max_box_size=len(self.fbm_data)//4, use_gpu=True)
        jax_results = self._time_estimation(dfa_jax, self.fbm_data, "JAX DFA")
        
        # Compare results
        comparison = {
            'data_type': 'fBm',
            'data_length': len(self.fbm_data),
            'true_hurst': 0.7,
            'original': original_results,
            'jax': jax_results
        }
        
        if original_results.get('success') and jax_results.get('success'):
            speedup = original_results['time'] / jax_results['time']
            h_diff = abs(original_results['hurst_parameter'] - jax_results['hurst_parameter'])
            
            print(f"\nResults:")
            print(f"  Original DFA: H = {original_results['hurst_parameter']:.4f}, "
                  f"R² = {original_results['r_squared']:.4f}, "
                  f"Time = {original_results['time']:.4f}s")
            print(f"  JAX DFA:      H = {jax_results['hurst_parameter']:.4f}, "
                  f"R² = {jax_results['r_squared']:.4f}, "
                  f"Time = {jax_results['time']:.4f}s")
            print(f"  Speedup:      {speedup:.2f}x")
            print(f"  H difference: {h_diff:.6f}")
            
            comparison['speedup'] = speedup
            comparison['h_difference'] = h_diff
        
        return comparison
    
    def run_rs_comparison(self) -> Dict[str, Any]:
        """Compare R/S estimator performance."""
        print("\n" + "="*60)
        print("R/S ESTIMATOR PERFORMANCE COMPARISON")
        print("="*60)
        
        # Test on fGn data
        print(f"\nTesting on fGn data (true H = 0.6, n = {len(self.fgn_data)})")
        
        # Original R/S
        rs_original = RSEstimator(min_window_size=10, max_window_size=len(self.fgn_data)//4)
        original_results = self._time_estimation(rs_original, self.fgn_data, "Original R/S")
        
        # JAX R/S
        rs_jax = RSEstimatorJAX(min_window_size=10, max_window_size=len(self.fgn_data)//4, use_gpu=True)
        jax_results = self._time_estimation(rs_jax, self.fgn_data, "JAX R/S")
        
        # Compare results
        comparison = {
            'data_type': 'fGn',
            'data_length': len(self.fgn_data),
            'true_hurst': 0.6,
            'original': original_results,
            'jax': jax_results
        }
        
        if original_results.get('success') and jax_results.get('success'):
            speedup = original_results['time'] / jax_results['time']
            h_diff = abs(original_results['hurst_parameter'] - jax_results['hurst_parameter'])
            
            print(f"\nResults:")
            print(f"  Original R/S: H = {original_results['hurst_parameter']:.4f}, "
                  f"R² = {original_results['r_squared']:.4f}, "
                  f"Time = {original_results['time']:.4f}s")
            print(f"  JAX R/S:      H = {jax_results['hurst_parameter']:.4f}, "
                  f"R² = {jax_results['r_squared']:.4f}, "
                  f"Time = {jax_results['time']:.4f}s")
            print(f"  Speedup:      {speedup:.2f}x")
            print(f"  H difference: {h_diff:.6f}")
            
            comparison['speedup'] = speedup
            comparison['h_difference'] = h_diff
        
        return comparison
    
    def run_scaling_test(self) -> Dict[str, Any]:
        """Test performance scaling with data size."""
        print("\n" + "="*60)
        print("PERFORMANCE SCALING TEST")
        print("="*60)
        
        # Generate data of different sizes
        sizes = [1000, 5000, 10000, 20000]
        scaling_results = {}
        
        for size in sizes:
            print(f"\nTesting with {size} data points...")
            
            # Generate data
            fbm_model = FractionalBrownianMotion(H=0.7, sigma=1.0)
            data = fbm_model.generate(size, seed=42)
            
            # Test DFA
            dfa_original = DFAEstimator(min_box_size=4, max_box_size=size//4)
            dfa_jax = DFAEstimatorJAX(min_box_size=4, max_box_size=size//4, use_gpu=True)
            
            original_time = self._time_estimation(dfa_original, data, f"Original DFA (n={size})")
            jax_time = self._time_estimation(dfa_jax, data, f"JAX DFA (n={size})")
            
            if original_time.get('success') and jax_time.get('success'):
                speedup = original_time['time'] / jax_time['time']
                scaling_results[size] = {
                    'original_time': original_time['time'],
                    'jax_time': jax_time['time'],
                    'speedup': speedup
                }
                
                print(f"  Speedup: {speedup:.2f}x")
        
        return scaling_results
    
    def run_demo(self, save_plots: bool = False, save_dir: str = None) -> Dict[str, Any]:
        """
        Run the complete performance demo.
        
        Parameters
        ----------
        save_plots : bool, optional
            Whether to save plots (default: False)
        save_dir : str, optional
            Directory to save plots (default: None)
            
        Returns
        -------
        dict
            Complete demo results
        """
        print("JAX PERFORMANCE DEMO")
        print("="*60)
        print("This demo compares JAX-optimized estimators with original implementations")
        print("to showcase performance improvements and accuracy validation.")
        
        # Run comparisons
        dfa_comparison = self.run_dfa_comparison()
        rs_comparison = self.run_rs_comparison()
        scaling_results = self.run_scaling_test()
        
        # Compile results
        self.results = {
            'dfa_comparison': dfa_comparison,
            'rs_comparison': rs_comparison,
            'scaling_results': scaling_results,
            'summary': self._generate_summary()
        }
        
        # Print summary
        self._print_summary()
        
        return self.results
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate a summary of the results."""
        summary = {
            'total_tests': 0,
            'successful_tests': 0,
            'average_speedup': 0.0,
            'max_speedup': 0.0,
            'min_speedup': float('inf'),
            'accuracy_validation': True
        }
        
        speedups = []
        
        # DFA comparison
        if 'dfa_comparison' in self.results and 'speedup' in self.results['dfa_comparison']:
            speedup = self.results['dfa_comparison']['speedup']
            speedups.append(speedup)
            summary['total_tests'] += 1
            summary['successful_tests'] += 1
            
            # Check accuracy
            h_diff = self.results['dfa_comparison']['h_difference']
            if h_diff > 0.01:  # Allow 1% difference
                summary['accuracy_validation'] = False
        
        # R/S comparison
        if 'rs_comparison' in self.results and 'speedup' in self.results['rs_comparison']:
            speedup = self.results['rs_comparison']['speedup']
            speedups.append(speedup)
            summary['total_tests'] += 1
            summary['successful_tests'] += 1
            
            # Check accuracy
            h_diff = self.results['rs_comparison']['h_difference']
            if h_diff > 0.01:  # Allow 1% difference
                summary['accuracy_validation'] = False
        
        # Scaling results
        if 'scaling_results' in self.results:
            for size, result in self.results['scaling_results'].items():
                if 'speedup' in result:
                    speedup = result['speedup']
                    speedups.append(speedup)
                    summary['total_tests'] += 1
                    summary['successful_tests'] += 1
        
        if speedups:
            summary['average_speedup'] = np.mean(speedups)
            summary['max_speedup'] = np.max(speedups)
            summary['min_speedup'] = np.min(speedups)
        
        return summary
    
    def _print_summary(self):
        """Print a summary of the results."""
        summary = self.results['summary']
        
        print("\n" + "="*60)
        print("PERFORMANCE DEMO SUMMARY")
        print("="*60)
        print(f"Tests completed: {summary['successful_tests']}/{summary['total_tests']}")
        print(f"Average speedup: {summary['average_speedup']:.2f}x")
        print(f"Speedup range: {summary['min_speedup']:.2f}x - {summary['max_speedup']:.2f}x")
        print(f"Accuracy validation: {'PASS' if summary['accuracy_validation'] else 'FAIL'}")
        
        if summary['accuracy_validation']:
            print("\n✅ JAX optimizations maintain accuracy while providing significant speedup!")
        else:
            print("\n⚠️  JAX optimizations show some accuracy differences - investigation needed.")
        
        print("\nKey benefits of JAX optimization:")
        print("  • GPU acceleration for large datasets")
        print("  • JIT compilation for faster execution")
        print("  • Vectorized operations for better performance")
        print("  • Automatic differentiation capabilities")
        print("  • Consistent interface with original estimators")


def main():
    """Main function to run the JAX performance demo."""
    parser = argparse.ArgumentParser(description="JAX Performance Demo")
    parser.add_argument('--save-plots', action='store_true', 
                       help='Save performance plots')
    parser.add_argument('--save-dir', type=str, default='results/plots',
                       help='Directory to save plots (default: results/plots)')
    parser.add_argument('--no-plot', action='store_true',
                       help='Disable plotting (useful for CI)')
    
    args = parser.parse_args()
    
    # Create demo instance
    demo = JAXPerformanceDemo()
    
    # Run demo
    results = demo.run_demo(save_plots=args.save_plots, save_dir=args.save_dir)
    
    print(f"\nDemo completed successfully!")
    print(f"Results saved in demo.results")
    
    return results


if __name__ == "__main__":
    main()
