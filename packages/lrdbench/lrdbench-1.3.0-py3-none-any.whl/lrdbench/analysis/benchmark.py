#!/usr/bin/env python3
"""
Comprehensive Benchmark Module for LRDBench
A unified interface for running all types of benchmarks and analyses
"""

import numpy as np
import time
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import json
from datetime import datetime

# Import estimators
from .temporal.rs.rs_estimator import RSEstimator
from .temporal.dfa.dfa_estimator import DFAEstimator
from .temporal.dma.dma_estimator import DMAEstimator
from .temporal.higuchi.higuchi_estimator import HiguchiEstimator
from .spectral.gph.gph_estimator import GPHEstimator
from .spectral.whittle.whittle_estimator import WhittleEstimator
from .spectral.periodogram.periodogram_estimator import PeriodogramEstimator
from .wavelet.cwt.cwt_estimator import CWTEstimator
from .wavelet.variance.wavelet_variance_estimator import WaveletVarianceEstimator
from .wavelet.log_variance.wavelet_log_variance_estimator import WaveletLogVarianceEstimator
from .wavelet.whittle.wavelet_whittle_estimator import WaveletWhittleEstimator
from .multifractal.mfdfa.mfdfa_estimator import MFDFAEstimator
from .multifractal.wavelet_leaders.multifractal_wavelet_leaders_estimator import MultifractalWaveletLeadersEstimator

# Import data models
from models.data_models.fbm.fbm_model import FractionalBrownianMotion as FBMModel
from models.data_models.fgn.fgn_model import FractionalGaussianNoise as FGNModel
from models.data_models.arfima.arfima_model import ARFIMAModel
from models.data_models.mrw.mrw_model import MultifractalRandomWalk as MRWModel

# Import contamination models
# Simple contamination classes for benchmarking
class AdditiveGaussianNoise:
    def __init__(self, noise_level=0.1, std=0.1):
        self.noise_level = noise_level
        self.std = std
    
    def apply(self, data):
        noise = np.random.normal(0, self.std * self.noise_level, len(data))
        return data + noise

class MultiplicativeNoise:
    def __init__(self, noise_level=0.05, std=0.05):
        self.noise_level = noise_level
        self.std = std
    
    def apply(self, data):
        noise = np.random.normal(1, self.std * self.noise_level, len(data))
        return data * noise

class OutlierContamination:
    def __init__(self, outlier_fraction=0.1, outlier_magnitude=3.0):
        self.outlier_fraction = outlier_fraction
        self.outlier_magnitude = outlier_magnitude
    
    def apply(self, data):
        contaminated = data.copy()
        n_outliers = int(len(data) * self.outlier_fraction)
        outlier_indices = np.random.choice(len(data), n_outliers, replace=False)
        contaminated[outlier_indices] += np.random.normal(0, self.outlier_magnitude, n_outliers)
        return contaminated

class TrendContamination:
    def __init__(self, trend_strength=0.1, trend_type='linear'):
        self.trend_strength = trend_strength
        self.trend_type = trend_type
    
    def apply(self, data):
        n = len(data)
        if self.trend_type == 'linear':
            trend = np.linspace(0, self.trend_strength, n)
        else:
            trend = np.zeros(n)
        return data + trend

class SeasonalContamination:
    def __init__(self, seasonal_strength=0.1, period=None):
        self.seasonal_strength = seasonal_strength
        self.period = period
    
    def apply(self, data):
        n = len(data)
        if self.period is None:
            self.period = n // 4
        t = np.arange(n)
        seasonal = self.seasonal_strength * np.sin(2 * np.pi * t / self.period)
        return data + seasonal

class MissingDataContamination:
    def __init__(self, missing_fraction=0.1, missing_pattern='random'):
        self.missing_fraction = missing_fraction
        self.missing_pattern = missing_pattern
    
    def apply(self, data):
        contaminated = data.copy()
        n_missing = int(len(data) * self.missing_fraction)
        if self.missing_pattern == 'random':
            missing_indices = np.random.choice(len(data), n_missing, replace=False)
            contaminated[missing_indices] = np.nan
        return contaminated

# Import pre-trained ML models for production use
from models.pretrained_models.ml_pretrained import RandomForestPretrainedModel, SVREstimatorPretrainedModel, GradientBoostingPretrainedModel

# Import pre-trained neural models
from models.pretrained_models.cnn_pretrained import CNNPretrainedModel
from models.pretrained_models.transformer_pretrained import TransformerPretrainedModel


class ComprehensiveBenchmark:
    """
    Comprehensive benchmark class for testing all estimators and data models.
    """
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize the benchmark system.
        
        Parameters
        ----------
        output_dir : str, optional
            Directory to save benchmark results
        """
        self.output_dir = Path(output_dir) if output_dir else Path("benchmark_results")
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize all estimator categories
        self.all_estimators = self._initialize_all_estimators()
        
        # Initialize data models
        self.data_models = self._initialize_data_models()
        
        # Initialize contamination models
        self.contamination_models = self._initialize_contamination_models()
        
        # Results storage
        self.results = {}
        self.performance_metrics = {}
        
    def _initialize_all_estimators(self) -> Dict[str, Dict[str, Any]]:
        """Initialize all available estimators organized by category."""
        estimators = {
            'classical': {
                # Temporal estimators
                'R/S': RSEstimator(),
                'DFA': DFAEstimator(),
                'DMA': DMAEstimator(),
                'Higuchi': HiguchiEstimator(),
                
                # Spectral estimators
                'GPH': GPHEstimator(),
                'Whittle': WhittleEstimator(),
                'Periodogram': PeriodogramEstimator(),
                
                # Wavelet estimators - will be initialized with adaptive scales
                'CWT': CWTEstimator(),
                'WaveletVar': None,  # Will be initialized dynamically
                'WaveletLogVar': None,  # Will be initialized dynamically
                'WaveletWhittle': None,  # Will be initialized dynamically
                
                # Multifractal estimators
                'MFDFA': MFDFAEstimator(),
                'WaveletLeaders': MultifractalWaveletLeadersEstimator(),
            },
            'ML': {
                'RandomForest': RandomForestPretrainedModel(),  # Use pre-trained model for PyPI
                'GradientBoosting': GradientBoostingPretrainedModel(),  # Use pre-trained model for PyPI
                'SVR': SVREstimatorPretrainedModel(),  # Use pre-trained model for PyPI
            },
            'neural': {
                'CNN': CNNPretrainedModel(input_length=500),  # Use pre-trained model
                'Transformer': TransformerPretrainedModel(input_length=500),  # Use pre-trained model
            }
        }
        return estimators
    

    
    def _get_adaptive_wavelet_estimators(self, data_length: int) -> Dict[str, Any]:
        """Create wavelet estimators with scales adapted to data length."""
        # Calculate maximum safe scale: log2(data_length) - 1 (for safety margin)
        max_safe_scale = max(1, int(np.log2(data_length)) - 1)
        
        # Create scales that work with the data length
        # Use fewer, more meaningful scales for shorter data
        if data_length < 100:
            scales = [1, 2, 3]
        elif data_length < 500:
            scales = list(range(1, max_safe_scale + 1))
        else:
            # For longer data, use more scales but ensure they're safe
            scales = list(range(1, min(max_safe_scale + 1, 8)))
        
        return {
            'WaveletVar': WaveletVarianceEstimator(scales=scales),
            'WaveletLogVar': WaveletLogVarianceEstimator(scales=scales),
            'WaveletWhittle': WaveletWhittleEstimator(scales=scales),
        }
    
    def _initialize_data_models(self) -> Dict[str, Any]:
        """Initialize all available data models."""
        data_models = {
            'fBm': FBMModel,
            'fGn': FGNModel,
            'ARFIMAModel': ARFIMAModel,
            'MRW': MRWModel,
        }
        return data_models
    
    def _initialize_contamination_models(self) -> Dict[str, Any]:
        """Initialize all available contamination models."""
        contamination_models = {
            'additive_gaussian': AdditiveGaussianNoise,
            'multiplicative_noise': MultiplicativeNoise,
            'outliers': OutlierContamination,
            'trend': TrendContamination,
            'seasonal': SeasonalContamination,
            'missing_data': MissingDataContamination,
        }
        return contamination_models
    
    def get_estimators_by_type(self, benchmark_type: str = 'comprehensive', data_length: int = 1000) -> Dict[str, Any]:
        """
        Get estimators based on the specified benchmark type.
        
        Parameters
        ----------
        benchmark_type : str
            Type of benchmark to run:
            - 'comprehensive': All estimators (default)
            - 'classical': Only classical statistical estimators
            - 'ML': Only machine learning estimators (non-neural)
            - 'neural': Only neural network estimators
        data_length : int
            Length of data to be tested (used for adaptive wavelet estimators)
            
        Returns
        -------
        dict
            Dictionary of estimators for the specified type
        """
        if benchmark_type == 'comprehensive':
            # Combine all estimators
            all_est = {}
            for category in self.all_estimators.values():
                all_est.update(category)
            
            # Replace None wavelet estimators with adaptive ones
            adaptive_wavelets = self._get_adaptive_wavelet_estimators(data_length)
            for name, estimator in adaptive_wavelets.items():
                if name in all_est:
                    all_est[name] = estimator
            
            return all_est
        elif benchmark_type in self.all_estimators:
            estimators = self.all_estimators[benchmark_type].copy()
            
            # Replace None wavelet estimators with adaptive ones
            if benchmark_type == 'classical':
                adaptive_wavelets = self._get_adaptive_wavelet_estimators(data_length)
                for name, estimator in adaptive_wavelets.items():
                    if name in estimators:
                        estimators[name] = estimator
            
            return estimators
        else:
            raise ValueError(f"Unknown benchmark type: {benchmark_type}. "
                           f"Available types: {list(self.all_estimators.keys()) + ['comprehensive']}")
    
    def generate_test_data(self, model_name: str, data_length: int = 1000, **kwargs) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Generate test data using specified model.
        
        Parameters
        ----------
        model_name : str
            Name of the data model to use
        data_length : int
            Length of data to generate
        **kwargs : dict
            Additional parameters for the data model
            
        Returns
        -------
        tuple
            (data, parameters)
        """
        if model_name not in self.data_models:
            raise ValueError(f"Unknown data model: {model_name}")
        
        model_class = self.data_models[model_name]
        
        # Set default parameters if not provided
        if model_name == 'fBm':
            params = {'H': 0.7, 'sigma': 1.0, **kwargs}
        elif model_name == 'fGn':
            params = {'H': 0.7, 'sigma': 1.0, **kwargs}
        elif model_name == 'ARFIMAModel':
            params = {'d': 0.3, 'ar_params': [0.5], 'ma_params': [0.2], **kwargs}
        elif model_name == 'MRW':
            params = {'H': 0.7, 'lambda_param': 0.5, 'sigma': 1.0, **kwargs}
        
        model = model_class(**params)
        data = model.generate(data_length, seed=42)
        
        return data, params
    
    def apply_contamination(self, data: np.ndarray, contamination_type: str, 
                           contamination_level: float = 0.1, **kwargs) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Apply contamination to the data.
        
        Parameters
        ----------
        data : np.ndarray
            Original clean data
        contamination_type : str
            Type of contamination to apply
        contamination_level : float
            Level/intensity of contamination (0.0 to 1.0)
        **kwargs : dict
            Additional parameters for specific contamination types
            
        Returns
        -------
        tuple
            (contaminated_data, contamination_info)
        """
        if contamination_type not in self.contamination_models:
            raise ValueError(f"Unknown contamination type: {contamination_type}. "
                           f"Available types: {list(self.contamination_models.keys())}")
        
        contamination_class = self.contamination_models[contamination_type]
        
        # Set default parameters based on contamination type
        if contamination_type == 'additive_gaussian':
            default_params = {'noise_level': contamination_level, 'std': 0.1}
        elif contamination_type == 'multiplicative_noise':
            default_params = {'noise_level': contamination_level, 'std': 0.05}
        elif contamination_type == 'outliers':
            default_params = {'outlier_fraction': contamination_level, 'outlier_magnitude': 3.0}
        elif contamination_type == 'trend':
            default_params = {'trend_strength': contamination_level, 'trend_type': 'linear'}
        elif contamination_type == 'seasonal':
            default_params = {'seasonal_strength': contamination_level, 'period': len(data) // 4}
        elif contamination_type == 'missing_data':
            default_params = {'missing_fraction': contamination_level, 'missing_pattern': 'random'}
        else:
            default_params = {}
        
        # Update with provided kwargs
        contamination_params = {**default_params, **kwargs}
        
        # Apply contamination
        contamination_model = contamination_class(**contamination_params)
        contaminated_data = contamination_model.apply(data)
        
        contamination_info = {
            'type': contamination_type,
            'level': contamination_level,
            'parameters': contamination_params,
            'original_data_shape': data.shape,
            'contaminated_data_shape': contaminated_data.shape
        }
        
        return contaminated_data, contamination_info
    
    def run_single_estimator_test(self, estimator_name: str, data: np.ndarray, 
                                 true_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a single estimator test.
        
        Parameters
        ----------
        estimator_name : str
            Name of the estimator to test
        data : np.ndarray
            Test data
        true_params : dict
            True parameters of the data
            
        Returns
        -------
        dict
            Test results
        """
        # Get the estimator from the comprehensive list
        all_estimators = self.get_estimators_by_type('comprehensive')
        estimator = all_estimators[estimator_name]
        
        # Measure execution time
        start_time = time.time()
        
        try:
            result = estimator.estimate(data)
            execution_time = time.time() - start_time
            
            # Extract key metrics
            hurst_est = result.get('hurst_parameter', None)
            if hurst_est is not None:
                # Try different parameter names for different data models
                true_hurst = None
                if 'H' in true_params:
                    true_hurst = true_params['H']
                elif 'd' in true_params:
                    # For ARFIMA models, use d parameter directly
                    true_hurst = true_params['d']
                
                if true_hurst is not None:
                    error = abs(hurst_est - true_hurst)
                else:
                    # If we can't calculate error, still mark as successful but with no error metric
                    error = None
                
                # Update true_hurst in the result for consistency
                if true_hurst is not None:
                    true_params['H'] = true_hurst
            else:
                error = None
            
            test_result = {
                'estimator': estimator_name,
                'success': True,
                'execution_time': execution_time,
                'estimated_hurst': hurst_est,
                'true_hurst': true_params.get('H', None),
                'error': error,
                'r_squared': result.get('r_squared', None),
                'p_value': result.get('p_value', None),
                'intercept': result.get('intercept', None),
                'slope': result.get('slope', None),
                'std_error': result.get('std_error', None),
                'full_result': result
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            test_result = {
                'estimator': estimator_name,
                'success': False,
                'execution_time': execution_time,
                'error_message': str(e),
                'estimated_hurst': None,
                'true_hurst': true_params.get('H', None),
                'error': None,
                'r_squared': None,
                'p_value': None,
                'intercept': None,
                'slope': None,
                'std_error': None,
                'full_result': None
            }
        
        return test_result
    
    def run_comprehensive_benchmark(self, data_length: int = 1000, 
                                   benchmark_type: str = 'comprehensive',
                                   contamination_type: Optional[str] = None,
                                   contamination_level: float = 0.1,
                                   save_results: bool = True) -> Dict[str, Any]:
        """
        Run comprehensive benchmark across all estimators and data models.
        
        Parameters
        ----------
        data_length : int
            Length of test data to generate
        benchmark_type : str
            Type of benchmark to run:
            - 'comprehensive': All estimators (default)
            - 'classical': Only classical statistical estimators
            - 'ML': Only machine learning estimators (non-neural)
            - 'neural': Only neural network estimators
        contamination_type : str, optional
            Type of contamination to apply to the data
        contamination_level : float
            Level/intensity of contamination (0.0 to 1.0)
        save_results : bool
            Whether to save results to file
            
        Returns
        -------
        dict
            Comprehensive benchmark results
        """
        print("🚀 Starting LRDBench Benchmark")
        print("=" * 60)
        print(f"Benchmark Type: {benchmark_type.upper()}")
        if contamination_type:
            print(f"Contamination: {contamination_type} (level: {contamination_level})")
        print("=" * 60)
        
        # Get estimators based on benchmark type
        estimators = self.get_estimators_by_type(benchmark_type, data_length)
        print(f"Testing {len(estimators)} estimators...")
        
        all_results = {}
        total_tests = 0
        successful_tests = 0
        
        # Test with different data models
        for model_name in self.data_models:
            print(f"\n📊 Testing with {model_name} data model...")
            
            try:
                # Generate clean data
                data, params = self.generate_test_data(model_name, data_length=data_length)
                print(f"   Generated {len(data)} clean data points")
                
                # Apply contamination if specified
                if contamination_type:
                    data, contamination_info = self.apply_contamination(
                        data, contamination_type, contamination_level
                    )
                    print(f"   Applied {contamination_type} contamination (level: {contamination_level})")
                    params['contamination'] = contamination_info
                
                model_results = []
                
                # Test all estimators
                for estimator_name in estimators:
                    print(f"   🔍 Testing {estimator_name}...", end=" ")
                    
                    result = self.run_single_estimator_test(estimator_name, data, params)
                    model_results.append(result)
                    
                    if result['success']:
                        print("✅")
                        successful_tests += 1
                    else:
                        print(f"❌ ({result['error_message']})")
                    
                    total_tests += 1
                
                all_results[model_name] = {
                    'data_params': params,
                    'estimator_results': model_results
                }
                
            except Exception as e:
                print(f"   ❌ Error with {model_name}: {e}")
                all_results[model_name] = {
                    'data_params': None,
                    'estimator_results': [],
                    'error': str(e)
                }
        
        # Compile summary
        summary = {
            'timestamp': datetime.now().isoformat(),
            'benchmark_type': benchmark_type,
            'contamination_type': contamination_type,
            'contamination_level': contamination_level,
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'success_rate': successful_tests / total_tests if total_tests > 0 else 0,
            'data_models_tested': len(self.data_models),
            'estimators_tested': len(estimators),
            'results': all_results
        }
        
        # Save results if requested
        if save_results:
            self.save_results(summary)
        
        # Print summary
        self.print_summary(summary)
        
        return summary
    
    def run_classical_benchmark(self, data_length: int = 1000, 
                               contamination_type: Optional[str] = None,
                               contamination_level: float = 0.1,
                               save_results: bool = True) -> Dict[str, Any]:
        """Run benchmark with only classical statistical estimators."""
        return self.run_comprehensive_benchmark(
            data_length=data_length,
            benchmark_type='classical',
            contamination_type=contamination_type,
            contamination_level=contamination_level,
            save_results=save_results
        )
    
    def run_ml_benchmark(self, data_length: int = 1000, 
                         contamination_type: Optional[str] = None,
                         contamination_level: float = 0.1,
                         save_results: bool = True) -> Dict[str, Any]:
        """Run benchmark with only machine learning estimators (non-neural)."""
        return self.run_comprehensive_benchmark(
            data_length=data_length,
            benchmark_type='ML',
            contamination_type=contamination_type,
            contamination_level=contamination_level,
            save_results=save_results
        )
    
    def run_neural_benchmark(self, data_length: int = 1000, 
                            contamination_type: Optional[str] = None,
                            contamination_level: float = 0.1,
                            save_results: bool = True) -> Dict[str, Any]:
        """Run benchmark with only neural network estimators."""
        return self.run_comprehensive_benchmark(
            data_length=data_length,
            benchmark_type='neural',
            contamination_type=contamination_type,
            contamination_level=contamination_level,
            save_results=save_results
        )
    
    def save_results(self, results: Dict[str, Any]) -> None:
        """Save benchmark results to files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed results as JSON
        json_file = self.output_dir / f"comprehensive_benchmark_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Save summary as CSV
        csv_data = []
        for model_name, model_data in results['results'].items():
            if 'estimator_results' in model_data:
                for est_result in model_data['estimator_results']:
                    csv_data.append({
                        'data_model': model_name,
                        'estimator': est_result['estimator'],
                        'success': est_result['success'],
                        'execution_time': est_result['execution_time'],
                        'estimated_hurst': est_result['estimated_hurst'],
                        'true_hurst': est_result['true_hurst'],
                        'error': est_result['error'],
                        'r_squared': est_result['r_squared'],
                        'p_value': est_result['p_value'],
                        'intercept': est_result['intercept'],
                        'slope': est_result['slope'],
                        'std_error': est_result['std_error']
                    })
        
        if csv_data:
            df = pd.DataFrame(csv_data)
            csv_file = self.output_dir / f"benchmark_summary_{timestamp}.csv"
            df.to_csv(csv_file, index=False)
            print(f"\n💾 Results saved to:")
            print(f"   JSON: {json_file}")
            print(f"   CSV: {csv_file}")
    
    def print_summary(self, summary: Dict[str, Any]) -> None:
        """Print benchmark summary."""
        print("\n" + "=" * 60)
        print("📊 BENCHMARK SUMMARY")
        print("=" * 60)
        print(f"Benchmark Type: {summary.get('benchmark_type', 'Unknown').upper()}")
        if summary.get('contamination_type'):
            print(f"Contamination: {summary['contamination_type']} (level: {summary['contamination_level']})")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Successful: {summary['successful_tests']}")
        print(f"Success Rate: {summary['success_rate']:.1%}")
        print(f"Data Models: {summary['data_models_tested']}")
        print(f"Estimators: {summary['estimators_tested']}")
        
        # Show top performers (aggregated by estimator across all data models)
        print("\n🏆 TOP PERFORMING ESTIMATORS (Average across all data models):")
        
        # Aggregate results by estimator
        estimator_performance = {}
        
        for model_name, model_data in summary['results'].items():
            if 'estimator_results' in model_data:
                for est_result in model_data['estimator_results']:
                    if est_result['success'] and est_result['error'] is not None:
                        estimator_name = est_result['estimator']
                        
                        if estimator_name not in estimator_performance:
                            estimator_performance[estimator_name] = {
                                'errors': [],
                                'execution_times': [],
                                'data_models': []
                            }
                        
                        estimator_performance[estimator_name]['errors'].append(est_result['error'])
                        estimator_performance[estimator_name]['execution_times'].append(est_result['execution_time'])
                        estimator_performance[estimator_name]['data_models'].append(model_name)
        
        if estimator_performance:
            # Calculate average performance for each estimator
            aggregated_performance = []
            for estimator_name, perf_data in estimator_performance.items():
                avg_error = np.mean(perf_data['errors'])
                avg_time = np.mean(perf_data['execution_times'])
                data_models_tested = len(perf_data['data_models'])
                
                aggregated_performance.append({
                    'estimator': estimator_name,
                    'avg_error': avg_error,
                    'avg_time': avg_time,
                    'data_models_tested': data_models_tested,
                    'min_error': min(perf_data['errors']),
                    'max_error': max(perf_data['errors'])
                })
            
            # Sort by average error (lower is better)
            aggregated_performance.sort(key=lambda x: x['avg_error'])
            
            for i, perf in enumerate(aggregated_performance[:5]):
                print(f"   {i+1}. {perf['estimator']}")
                print(f"      Avg Error: {perf['avg_error']:.4f} (Range: {perf['min_error']:.4f}-{perf['max_error']:.4f})")
                print(f"      Avg Time: {perf['avg_time']:.3f}s | Data Models: {perf['data_models_tested']}")
                
                # Show estimated H values for this estimator across data models
                estimator_name = perf['estimator']
                print(f"      Estimated H values:")
                for model_name, model_data in summary['results'].items():
                    if 'estimator_results' in model_data:
                        for est_result in model_data['estimator_results']:
                            if est_result['estimator'] == estimator_name and est_result['success']:
                                true_h = est_result['true_hurst']
                                est_h = est_result['estimated_hurst']
                                if est_h is not None:
                                    print(f"        {model_name}: H_est={est_h:.4f}, H_true={true_h:.4f}")
                print()
        
        # Show detailed breakdown by data model
        print("\n📊 DETAILED PERFORMANCE BY DATA MODEL:")
        for model_name, model_data in summary['results'].items():
            if 'estimator_results' in model_data and model_data['estimator_results']:
                print(f"\n   {model_name}:")
                successful_results = [r for r in model_data['estimator_results'] if r['success'] and r['error'] is not None]
                if successful_results:
                    # Sort by error for this data model
                    successful_results.sort(key=lambda x: x['error'])
                    for i, result in enumerate(successful_results[:3]):  # Top 3 for each model
                        print(f"     {i+1}. {result['estimator']}: Error {result['error']:.4f}, Time {result['execution_time']:.3f}s")
                else:
                    print("     No successful estimators")
        
        print("\n🎯 Benchmark completed successfully!")


def main():
    """
    Main function for running comprehensive benchmarks.
    This serves as the entry point for the lrdbench command.
    """
    print("🚀 LRDBench - Comprehensive Benchmark System")
    print("=" * 50)
    
    # Initialize benchmark system
    benchmark = ComprehensiveBenchmark()
    
    # Run comprehensive benchmark (default)
    print("\n📊 Running COMPREHENSIVE benchmark (all estimators)...")
    results = benchmark.run_comprehensive_benchmark(
        data_length=1000,
        benchmark_type='comprehensive',
        save_results=True
    )
    
    print(f"\n✅ Benchmark completed with {results['success_rate']:.1%} success rate!")
    print("\n💡 Available benchmark types:")
    print("   - 'comprehensive': All estimators (default)")
    print("   - 'classical': Only classical statistical estimators")
    print("   - 'ML': Only machine learning estimators (non-neural)")
    print("   - 'neural': Only neural network estimators")
    print("\n💡 Available contamination types:")
    print("   - 'additive_gaussian': Add Gaussian noise")
    print("   - 'multiplicative_noise': Multiplicative noise")
    print("   - 'outliers': Add outliers")
    print("   - 'trend': Add trend")
    print("   - 'seasonal': Add seasonal patterns")
    print("   - 'missing_data': Remove data points")
    print("\n   Use the ComprehensiveBenchmark class in your own code:")
    print("   from analysis.benchmark import ComprehensiveBenchmark")
    print("   benchmark = ComprehensiveBenchmark()")
    print("   results = benchmark.run_comprehensive_benchmark(")
    print("       benchmark_type='classical',  # or 'ML', 'neural'")
    print("       contamination_type='additive_gaussian',  # optional")
    print("       contamination_level=0.2  # 0.0 to 1.0")
    print("   )")


if __name__ == "__main__":
    main()
