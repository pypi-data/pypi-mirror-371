#!/usr/bin/env python3
"""
Confounded Data Benchmark: Test Estimator Robustness Against Data Quality Issues

This script systematically tests all available estimators against various classes of 
confounded data to assess their robustness and identify which estimators are most 
susceptible to realistic data quality issues.
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import time
import psutil
import warnings
from pathlib import Path
from typing import Dict, List, Tuple, Any
import traceback
from scipy import signal, stats

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Import data models
from models.data_models.fbm.fbm_model import FractionalBrownianMotion
from models.data_models.fgn.fgn_model import FractionalGaussianNoise

# Import all available estimators
try:
    from analysis.temporal.dfa.dfa_estimator import DFAEstimator
    DFA_AVAILABLE = True
except ImportError:
    DFA_AVAILABLE = False

try:
    from analysis.temporal.rs.rs_estimator import RSEstimator
    RS_AVAILABLE = True
except ImportError:
    RS_AVAILABLE = False

try:
    from analysis.temporal.higuchi.higuchi_estimator import HiguchiEstimator
    HIGUCHI_AVAILABLE = True
except ImportError:
    HIGUCHI_AVAILABLE = False

try:
    from analysis.temporal.dma.dma_estimator import DMAEstimator
    DMA_AVAILABLE = True
except ImportError:
    DMA_AVAILABLE = False

try:
    from analysis.spectral.periodogram.periodogram_estimator import PeriodogramEstimator
    PERIODOGRAM_AVAILABLE = True
except ImportError:
    PERIODOGRAM_AVAILABLE = False

try:
    from analysis.spectral.whittle.whittle_estimator import WhittleEstimator
    WHITTLE_AVAILABLE = True
except ImportError:
    WHITTLE_AVAILABLE = False

try:
    from analysis.spectral.gph.gph_estimator import GPHEstimator
    GPH_AVAILABLE = True
except ImportError:
    GPH_AVAILABLE = False

try:
    from analysis.wavelet.log_variance.wavelet_log_variance_estimator import WaveletLogVarianceEstimator
    WAVELET_LOG_VAR_AVAILABLE = True
except ImportError:
    WAVELET_LOG_VAR_AVAILABLE = False

try:
    from analysis.wavelet.variance.wavelet_variance_estimator import WaveletVarianceEstimator
    WAVELET_VAR_AVAILABLE = True
except ImportError:
    WAVELET_VAR_AVAILABLE = False

try:
    from analysis.wavelet.whittle.wavelet_whittle_estimator import WaveletWhittleEstimator
    WAVELET_WHITTLE_AVAILABLE = True
except ImportError:
    WAVELET_WHITTLE_AVAILABLE = False

try:
    from analysis.wavelet.cwt.cwt_estimator import CWTEstimator
    CWT_AVAILABLE = True
except ImportError:
    CWT_AVAILABLE = False

try:
    from analysis.multifractal.mfdfa.mfdfa_estimator import MFDFAEstimator
    MFDFA_AVAILABLE = True
except ImportError:
    MFDFA_AVAILABLE = False

# Set plotting style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class ConfoundedDataBenchmark:
    """Benchmark for testing estimator robustness against confounded data."""
    
    def __init__(self, data_length: int = 2048, n_trials: int = 5):
        self.data_length = data_length
        self.n_trials = n_trials
        self.results = {}
        
        # Initialize all available estimators
        self.estimators = self._initialize_estimators()
        
        # Test parameters for different Hurst values
        self.test_hurst_values = [0.3, 0.5, 0.7]
        
        # Confound types and their parameters
        self.confound_types = {
            'clean': {'description': 'Clean data (no confounds)', 'params': {}},
            'noise': {'description': 'Additive white noise', 'params': {'noise_level': [0.1, 0.3, 0.5]}},
            'outliers': {'description': 'Random outliers', 'params': {'outlier_ratio': [0.01, 0.05, 0.1]}},
            'trends': {'description': 'Linear/quadratic trends', 'params': {'trend_strength': [0.1, 0.3, 0.5]}},
            'seasonality': {'description': 'Seasonal patterns', 'params': {'seasonal_strength': [0.1, 0.3, 0.5]}},
            'missing_data': {'description': 'Random missing data', 'params': {'missing_ratio': [0.05, 0.1, 0.2]}},
            'smoothing': {'description': 'Moving average smoothing', 'params': {'window_size': [3, 7, 15]}},
            'heteroscedasticity': {'description': 'Varying variance', 'params': {'variance_factor': [2, 5, 10]}},
            'nonstationarity': {'description': 'Non-stationary segments', 'params': {'segment_length': [256, 512, 1024]}}
        }
        
        print(f"Initialized {len(self.estimators)} estimators")
        print("Available estimators:")
        for name, info in self.estimators.items():
            print(f"  - {name} ({info['category']})")
        
        print(f"\nConfound types: {len(self.confound_types)}")
        for confound_name, confound_info in self.confound_types.items():
            print(f"  - {confound_name}: {confound_info['description']}")
    
    def _initialize_estimators(self) -> Dict[str, Any]:
        """Initialize all available estimators with robust parameters."""
        estimators = {}
        
        # Temporal estimators
        if DFA_AVAILABLE:
            estimators['DFA'] = {
                'class': DFAEstimator,
                'params': {'min_box_size': 10, 'max_box_size': 100},
                'category': 'temporal'
            }
        
        if RS_AVAILABLE:
            estimators['R/S'] = {
                'class': RSEstimator,
                'params': {'min_window_size': 10, 'max_window_size': 100},
                'category': 'temporal'
            }
        
        if HIGUCHI_AVAILABLE:
            estimators['Higuchi'] = {
                'class': HiguchiEstimator,
                'params': {'min_k': 2, 'max_k': 20},
                'category': 'temporal'
            }
        
        if DMA_AVAILABLE:
            estimators['DMA'] = {
                'class': DMAEstimator,
                'params': {'min_window_size': 4, 'max_window_size': 50},
                'category': 'temporal'
            }
        
        # Spectral estimators
        if PERIODOGRAM_AVAILABLE:
            estimators['Periodogram'] = {
                'class': PeriodogramEstimator,
                'params': {'min_freq_ratio': 0.01, 'max_freq_ratio': 0.1},
                'category': 'spectral'
            }
        
        if WHITTLE_AVAILABLE:
            estimators['Whittle'] = {
                'class': WhittleEstimator,
                'params': {'min_freq_ratio': 0.01, 'max_freq_ratio': 0.1},
                'category': 'spectral'
            }
        
        if GPH_AVAILABLE:
            estimators['GPH'] = {
                'class': GPHEstimator,
                'params': {'min_freq_ratio': 0.01, 'max_freq_ratio': 0.1},
                'category': 'spectral'
            }
        
        # Wavelet estimators
        if WAVELET_LOG_VAR_AVAILABLE:
            estimators['Wavelet Log Variance'] = {
                'class': WaveletLogVarianceEstimator,
                'params': {'scales': list(range(2, 9))},
                'category': 'wavelet'
            }
        
        if WAVELET_VAR_AVAILABLE:
            estimators['Wavelet Variance'] = {
                'class': WaveletVarianceEstimator,
                'params': {'scales': list(range(2, 9))},
                'category': 'wavelet'
            }
        
        if WAVELET_WHITTLE_AVAILABLE:
            estimators['Wavelet Whittle'] = {
                'class': WaveletWhittleEstimator,
                'params': {'scales': list(range(2, 9))},
                'category': 'wavelet'
            }
        
        if CWT_AVAILABLE:
            estimators['CWT'] = {
                'class': CWTEstimator,
                'params': {'scales': np.logspace(1, 2, 8)},
                'category': 'wavelet'
            }
        
        # Multifractal estimators
        if MFDFA_AVAILABLE:
            estimators['MFDFA'] = {
                'class': MFDFAEstimator,
                'params': {'min_box_size': 10, 'max_box_size': 100, 'q_values': [-2, -1, 0, 1, 2]},
                'category': 'multifractal'
            }
        
        return estimators
    
    def apply_confound(self, data: np.ndarray, confound_type: str, confound_params: Dict) -> np.ndarray:
        """Apply a specific confound to the data."""
        confounded_data = data.copy()
        
        if confound_type == 'clean':
            return confounded_data
        
        elif confound_type == 'noise':
            noise_level = confound_params['noise_level']
            noise = np.random.normal(0, noise_level, len(data))
            confounded_data += noise
        
        elif confound_type == 'outliers':
            outlier_ratio = confound_params['outlier_ratio']
            n_outliers = int(len(data) * outlier_ratio)
            outlier_indices = np.random.choice(len(data), n_outliers, replace=False)
            outlier_magnitude = 3 * np.std(data)
            confounded_data[outlier_indices] += np.random.choice([-1, 1], n_outliers) * outlier_magnitude
        
        elif confound_type == 'trends':
            trend_strength = confound_params['trend_strength']
            # Linear trend
            linear_trend = np.linspace(0, trend_strength, len(data))
            # Quadratic trend
            quadratic_trend = trend_strength * (np.linspace(-1, 1, len(data)) ** 2)
            confounded_data += linear_trend + quadratic_trend
        
        elif confound_type == 'seasonality':
            seasonal_strength = confound_params['seasonal_strength']
            # Multiple seasonal components
            t = np.arange(len(data))
            seasonal1 = seasonal_strength * np.sin(2 * np.pi * t / 50)  # Short period
            seasonal2 = seasonal_strength * 0.5 * np.sin(2 * np.pi * t / 100)  # Medium period
            confounded_data += seasonal1 + seasonal2
        
        elif confound_type == 'missing_data':
            missing_ratio = confound_params['missing_ratio']
            n_missing = int(len(data) * missing_ratio)
            missing_indices = np.random.choice(len(data), n_missing, replace=False)
            confounded_data[missing_indices] = np.nan
        
        elif confound_type == 'smoothing':
            window_size = confound_params['window_size']
            if window_size > 1:
                confounded_data = signal.convolve(data, np.ones(window_size)/window_size, mode='same')
        
        elif confound_type == 'heteroscedasticity':
            variance_factor = confound_params['variance_factor']
            # Create varying variance pattern
            variance_pattern = 1 + variance_factor * np.sin(np.linspace(0, 4*np.pi, len(data)))
            confounded_data *= np.sqrt(variance_pattern)
        
        elif confound_type == 'nonstationarity':
            segment_length = confound_params['segment_length']
            n_segments = len(data) // segment_length
            
            for i in range(n_segments):
                start_idx = i * segment_length
                end_idx = start_idx + segment_length
                
                # Add different mean to each segment
                segment_mean = np.random.normal(0, 0.5)
                confounded_data[start_idx:end_idx] += segment_mean
        
        return confounded_data
    
    def test_single_estimator(self, estimator_name: str, estimator_info: Dict, 
                             data: np.ndarray, true_hurst: float) -> Dict[str, Any]:
        """Test a single estimator and return detailed results."""
        try:
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            # Create estimator instance
            estimator = estimator_info['class'](**estimator_info['params'])
            
            # Run estimation
            results = estimator.estimate(data)
            
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            # Extract estimated Hurst parameter
            estimated_hurst = results.get('hurst_parameter', None)
            if estimated_hurst is None:
                for key in ['H', 'hurst', 'fractal_dimension']:
                    if key in results:
                        estimated_hurst = results[key]
                        break
            
            execution_time = end_time - start_time
            memory_usage = end_memory - start_memory
            
            # Calculate accuracy metrics
            if estimated_hurst is not None and true_hurst is not None:
                absolute_error = abs(estimated_hurst - true_hurst)
                relative_error = absolute_error / true_hurst if true_hurst != 0 else float('inf')
                squared_error = (estimated_hurst - true_hurst) ** 2
            else:
                absolute_error = relative_error = squared_error = float('inf')
            
            result = {
                'estimator_name': estimator_name,
                'estimated_hurst': estimated_hurst,
                'true_hurst': true_hurst,
                'execution_time': execution_time,
                'memory_usage': memory_usage,
                'absolute_error': absolute_error,
                'relative_error': relative_error,
                'squared_error': squared_error,
                'success': True,
                'raw_results': results
            }
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            return {
                'estimator_name': estimator_name,
                'estimated_hurst': None,
                'true_hurst': true_hurst,
                'execution_time': 0,
                'memory_usage': 0,
                'absolute_error': float('inf'),
                'relative_error': float('inf'),
                'squared_error': float('inf'),
                'success': False,
                'error': error_msg,
                'raw_results': {}
            }
    
    def run_confound_benchmark(self) -> None:
        """Run the complete confound benchmark."""
        print("=== CONFOUNDED DATA BENCHMARK ===")
        print(f"Data length: {self.data_length}")
        print(f"Number of trials: {self.n_trials}")
        print(f"Estimators: {len(self.estimators)}")
        print(f"Confound types: {len(self.confound_types)}")
        
        all_results = []
        
        # Test each confound type
        for confound_name, confound_info in self.confound_types.items():
            print(f"\n{'='*80}")
            print(f"TESTING CONFOUND: {confound_name.upper()}")
            print(f"Description: {confound_info['description']}")
            print(f"{'='*80}")
            
            confound_results = []
            
            # Get confound parameters
            if confound_name == 'clean':
                # Test clean data
                for hurst_value in self.test_hurst_values:
                    for trial in range(self.n_trials):
                        print(f"  Hurst {hurst_value}, Trial {trial + 1}:")
                        
                        # Generate clean fBm data
                        np.random.seed(trial)
                        generator = FractionalBrownianMotion(H=hurst_value, sigma=1.0)
                        data = generator.generate(self.data_length, seed=trial)
                        
                        # Test all estimators
                        for estimator_name, estimator_info in self.estimators.items():
                            result = self.test_single_estimator(
                                estimator_name, estimator_info, data, hurst_value
                            )
                            
                            result.update({
                                'confound_type': confound_name,
                                'confound_params': {},
                                'hurst_value': hurst_value,
                                'trial': trial,
                                'data_length': self.data_length
                            })
                            
                            confound_results.append(result)
                            
                            if result['success']:
                                print(f"    {estimator_name}: ✓ H_est={result['estimated_hurst']:.3f}, error={result['absolute_error']:.3f}")
                            else:
                                print(f"    {estimator_name}: ✗ Failed: {result.get('error', 'Unknown error')}")
            
            else:
                # Test with confound parameters
                param_name = list(confound_info['params'].keys())[0]
                param_values = confound_info['params'][param_name]
                
                for param_value in param_values:
                    for hurst_value in self.test_hurst_values:
                        for trial in range(self.n_trials):
                            print(f"  {param_name}={param_value}, Hurst {hurst_value}, Trial {trial + 1}:")
                            
                            # Generate clean fBm data
                            np.random.seed(trial)
                            generator = FractionalBrownianMotion(H=hurst_value, sigma=1.0)
                            clean_data = generator.generate(self.data_length, seed=trial)
                            
                            # Apply confound
                            confound_params = {param_name: param_value}
                            confounded_data = self.apply_confound(clean_data, confound_name, confound_params)
                            
                            # Handle missing data by interpolation
                            if confound_name == 'missing_data':
                                confounded_data = pd.Series(confounded_data).interpolate().values
                            
                            # Test all estimators
                            for estimator_name, estimator_info in self.estimators.items():
                                result = self.test_single_estimator(
                                    estimator_name, estimator_info, confounded_data, hurst_value
                                )
                                
                                result.update({
                                    'confound_type': confound_name,
                                    'confound_params': confound_params,
                                    'hurst_value': hurst_value,
                                    'trial': trial,
                                    'data_length': self.data_length
                                })
                                
                                confound_results.append(result)
                                
                                if result['success']:
                                    print(f"    {estimator_name}: ✓ H_est={result['estimated_hurst']:.3f}, error={result['absolute_error']:.3f}")
                                else:
                                    print(f"    {estimator_name}: ✗ Failed: {result.get('error', 'Unknown error')}")
            
            # Store results for this confound
            self.results[confound_name] = confound_results
            all_results.extend(confound_results)
            
            # Show summary for this confound
            self._analyze_confound_results(confound_name, confound_results)
        
        # Create overall leaderboard
        self._create_overall_leaderboard(all_results)
        
        # Save results
        self.save_results(all_results)
    
    def _analyze_confound_results(self, confound_name: str, results: List[Dict]) -> None:
        """Analyze results for a specific confound type."""
        print(f"\n  📊 RESULTS SUMMARY FOR {confound_name.upper()}")
        print(f"  {'-'*60}")
        
        df = pd.DataFrame(results)
        
        # Group by estimator
        for estimator_name in df['estimator_name'].unique():
            estimator_data = df[df['estimator_name'] == estimator_name]
            successful = estimator_data[estimator_data['success'] == True]
            failed = estimator_data[estimator_data['success'] == False]
            
            print(f"    {estimator_name}:")
            
            if len(successful) > 0:
                success_rate = len(successful) / len(estimator_data) * 100
                mean_error = successful['absolute_error'].mean()
                mean_time = successful['execution_time'].mean()
                
                print(f"      ✓ Success: {success_rate:.1f}% ({len(successful)}/{len(estimator_data)})")
                print(f"      ✓ Mean Error: {mean_error:.3f}")
                print(f"      ✓ Mean Time: {mean_time:.3f}s")
            else:
                print(f"      ✗ Failed: 0% ({len(failed)}/{len(estimator_data)})")
                
                if len(failed) > 0:
                    errors = failed['error'].unique()
                    print(f"      ✗ Errors: {', '.join(errors[:3])}")
    
    def _create_overall_leaderboard(self, all_results: List[Dict]) -> None:
        """Create overall leaderboard across all confounds."""
        print(f"\n{'='*80}")
        print("🏆 OVERALL ESTIMATOR QUALITY LEADERBOARD")
        print("Ranked by: 1) Accuracy (MAE), 2) Success Rate, 3) Speed, 4) Robustness")
        print(f"{'='*80}")
        
        df = pd.DataFrame(all_results)
        
        # Calculate robustness scores for each estimator
        leaderboard = []
        
        # Debug: Show actual success rates
        print("\n🔍 DEBUG: Actual Success Rates by Confound Type:")
        print("-" * 80)
        for confound_type in df['confound_type'].unique():
            confound_data = df[df['confound_type'] == confound_type]
            print(f"\n{confound_type.upper()}:")
            for estimator_name in confound_data['estimator_name'].unique():
                estimator_data = confound_data[confound_data['estimator_name'] == estimator_name]
                success_rate = estimator_data['success'].mean() * 100
                print(f"  {estimator_name}: {success_rate:.1f}% ({estimator_data['success'].sum()}/{len(estimator_data)})")
        
        print("\n" + "="*80)
        
        for estimator_name in df['estimator_name'].unique():
            estimator_data = df[df['estimator_name'] == estimator_name]
            
            # Overall success rate
            overall_success_rate = estimator_data['success'].mean() * 100
            
            # Success rate by confound type
            confound_success_rates = {}
            for confound_type in df['confound_type'].unique():
                confound_data = estimator_data[estimator_data['confound_type'] == confound_type]
                if len(confound_data) > 0:
                    confound_success_rates[confound_type] = confound_data['success'].mean() * 100
                else:
                    confound_success_rates[confound_type] = 0.0
            
            # Average error for successful runs
            successful = estimator_data[estimator_data['success'] == True]
            if len(successful) > 0:
                avg_error = successful['absolute_error'].mean()
                avg_time = successful['execution_time'].mean()
            else:
                avg_error = float('inf')
                avg_time = 0.0
            
            # Calculate quality metrics for ranking
            # 1. Accuracy (MAE) - lower is better, normalize to 0-100 scale
            if avg_error != float('inf'):
                # Normalize MAE: 0 error = 100 points, 1.0 error = 0 points
                accuracy_score = max(0, 100 - (avg_error * 100))
            else:
                accuracy_score = 0
            
            # 2. Success rate (0-100 scale)
            success_score = overall_success_rate
            
            # 3. Execution time - faster is better, normalize to 0-100 scale
            # Assume reasonable range: 0.001s = 100 points, 1.0s = 0 points
            if avg_time > 0:
                time_score = max(0, 100 - (avg_time * 100))
            else:
                time_score = 0
            
            # 4. Robustness bonus for handling common confounds well
            common_confound_success = np.mean([confound_success_rates.get(ct, 0) for ct in ['noise', 'outliers', 'trends']])
            robustness_bonus = common_confound_success * 0.1
            
            # Overall quality score prioritizing accuracy, then success, then speed
            quality_score = (0.5 * accuracy_score + 0.3 * success_score + 0.15 * time_score + 0.05 * robustness_bonus)
            
            # Get category from estimator initialization
            category = self.estimators[estimator_name]['category']
            
            leaderboard.append({
                'estimator': estimator_name,
                'category': category,
                'avg_error': avg_error,
                'overall_success_rate': overall_success_rate,
                'avg_time': avg_time,
                'clean_success_rate': confound_success_rates.get('clean', 0),
                'noise_success_rate': confound_success_rates.get('noise', 0),
                'outliers_success_rate': confound_success_rates.get('outliers', 0),
                'trends_success_rate': confound_success_rates.get('trends', 0),
                'accuracy_score': accuracy_score,
                'success_score': success_score,
                'time_score': time_score,
                'robustness_bonus': robustness_bonus,
                'quality_score': quality_score
            })
        
        # Sort by quality score (accuracy first, then success, then speed)
        leaderboard.sort(key=lambda x: x['quality_score'], reverse=True)
        
        # Display leaderboard with metrics in priority order
        print(f"{'Rank':<4} {'Estimator':<25} {'Category':<12} {'MAE':<8} {'Success':<8} {'Time(s)':<8} {'Quality':<10}")
        print("-" * 80)
        
        for rank, entry in enumerate(leaderboard, 1):
            mae_str = f"{entry['avg_error']:.3f}" if entry['avg_error'] != float('inf') else "∞"
            success_str = f"{entry['overall_success_rate']:.1f}%"
            time_str = f"{entry['avg_time']:.3f}" if entry['avg_time'] > 0 else "0.000"
            
            print(f"{rank:<4} {entry['estimator']:<25} {entry['category']:<12} "
                  f"{mae_str:<8} {success_str:<8} {time_str:<8} {entry['quality_score']:<9.1f}")
        
        # Show best and worst performers
        if leaderboard:
            best_performer = leaderboard[0]
            worst_performer = leaderboard[-1]
            
            print(f"\n🥇 BEST PERFORMER: {best_performer['estimator']} ({best_performer['category']})")
            print(f"   Quality Score: {best_performer['quality_score']:.1f}")
            print(f"   MAE: {best_performer['avg_error']:.3f}" if best_performer['avg_error'] != float('inf') else "   MAE: ∞")
            print(f"   Success Rate: {best_performer['overall_success_rate']:.1f}%")
            print(f"   Execution Time: {best_performer['avg_time']:.3f}s")
            
            print(f"\n⚠️  WORST PERFORMER: {worst_performer['estimator']} ({worst_performer['category']})")
            print(f"   Quality Score: {worst_performer['quality_score']:.1f}")
            print(f"   MAE: {worst_performer['avg_error']:.3f}" if worst_performer['avg_error'] != float('inf') else "   MAE: ∞")
            print(f"   Success Rate: {worst_performer['overall_success_rate']:.1f}%")
            print(f"   Execution Time: {worst_performer['avg_time']:.3f}s")
        
        # Store leaderboard
        self.leaderboard = leaderboard
    
    def save_results(self, all_results: List[Dict]) -> None:
        """Save confound benchmark results."""
        Path('confound_results').mkdir(exist_ok=True)
        
        # Save detailed results
        df = pd.DataFrame(all_results)
        df.to_csv('confound_results/confound_benchmark_results.csv', index=False)
        print(f"\nDetailed results saved to: confound_results/confound_benchmark_results.csv")
        
        # Save leaderboard
        if hasattr(self, 'leaderboard'):
            leaderboard_df = pd.DataFrame(self.leaderboard)
            leaderboard_df.to_csv('confound_results/quality_leaderboard.csv', index=False)
            print(f"Quality leaderboard saved to: confound_results/quality_leaderboard.csv")
        
        # Create summary by confound type
        summary_by_confound = {}
        for confound_type in df['confound_type'].unique():
            confound_data = df[df['confound_type'] == confound_type]
            
            confound_summary = {}
            for estimator_name in confound_data['estimator_name'].unique():
                estimator_data = confound_data[confound_data['estimator_name'] == estimator_name]
                successful = estimator_data[estimator_data['success'] == True]
                
                if len(successful) > 0:
                    confound_summary[estimator_name] = {
                        'success_rate': len(successful) / len(estimator_data),
                        'mean_error': successful['absolute_error'].mean(),
                        'mean_time': successful['execution_time'].mean()
                    }
                else:
                    confound_summary[estimator_name] = {
                        'success_rate': 0.0,
                        'mean_error': float('inf'),
                        'mean_time': 0.0
                    }
            
            summary_by_confound[confound_type] = confound_summary
        
        # Save confound-specific summaries
        for confound_type, summary in summary_by_confound.items():
            summary_df = pd.DataFrame(summary).T
            summary_df.to_csv(f'confound_results/{confound_type}_summary.csv')
            print(f"{confound_type.capitalize()} summary saved to: confound_results/{confound_type}_summary.csv")

def main():
    """Main function to run the confounded data benchmark."""
    print("=== CONFOUNDED DATA BENCHMARK: ESTIMATOR ROBUSTNESS TESTING ===")
    
    benchmark = ConfoundedDataBenchmark(data_length=2048, n_trials=5)
    
    try:
        benchmark.run_confound_benchmark()
        
    except Exception as e:
        print(f"Error during confound benchmark: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
