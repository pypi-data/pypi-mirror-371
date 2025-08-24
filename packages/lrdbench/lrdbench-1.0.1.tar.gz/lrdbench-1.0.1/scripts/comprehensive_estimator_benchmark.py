#!/usr/bin/env python3
"""
Comprehensive Estimator Benchmark: All 13 Estimators vs All Data Generators

This script performs a comprehensive benchmark of all available estimators
against all available data generators to create a performance leaderboard.
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

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Import data models
from models.data_models.arfima.arfima_model import ARFIMAModel
from models.data_models.mrw.mrw_model import BaseModel
from models.data_models.fbm.fbm_model import FractionalBrownianMotion
from models.data_models.fgn.fgn_model import FractionalGaussianNoise
from models.data_models.mrw.mrw_model import MultifractalRandomWalk

# Try to import neural components
try:
    from models.data_models.neural_fsde.base_neural_fsde import BaseModel
    BASEMODEL_AVAILABLE = True
except ImportError:
    BASEMODEL_AVAILABLE = False

try:
    from models.data_models.neural_fsde.torch_fsde_net import BaseNeuralFSDE
    BASENEURALFSDE_AVAILABLE = True
except ImportError:
    BASENEURALFSDE_AVAILABLE = False

try:
    from models.data_models.neural_fsde.jax_fsde_net import JAXLatentFractionalNet
    JAXLATENTFRACTIONALNET_AVAILABLE = True
except ImportError:
    JAXLATENTFRACTIONALNET_AVAILABLE = False

try:
    from models.data_models.neural_fsde.jax_fsde_net import JAXfSDENet
    JAXFSDENET_AVAILABLE = True
except ImportError:
    JAXFSDENET_AVAILABLE = False

try:
    from models.data_models.neural_fsde.hybrid_factory import NeuralFSDEFactory
    NEURALFSDEFACTORY_AVAILABLE = True
except ImportError:
    NEURALFSDEFACTORY_AVAILABLE = False

try:
    from models.data_models.neural_fsde.torch_fsde_net import TorchLatentFractionalNet
    TORCHLATENTFRACTIONALNET_AVAILABLE = True
except ImportError:
    TORCHLATENTFRACTIONALNET_AVAILABLE = False

try:
    from models.data_models.neural_fsde.torch_fsde_net import TorchfSDENet
    TORCHFSDENET_AVAILABLE = True
except ImportError:
    TORCHFSDENET_AVAILABLE = False

# Import all available estimators
try:
    from analysis.machine_learning.transformer_estimator import BaseMLEstimator
    BASEMLESTIMATOR_AVAILABLE = True
except ImportError:
    BASEMLESTIMATOR_AVAILABLE = False

try:
    from analysis.machine_learning.cnn_estimator import CNNEstimator
    CNNESTIMATOR_AVAILABLE = True
except ImportError:
    CNNESTIMATOR_AVAILABLE = False

try:
    from analysis.machine_learning.gradient_boosting_estimator import GradientBoostingEstimator
    GRADIENTBOOSTINGESTIMATOR_AVAILABLE = True
except ImportError:
    GRADIENTBOOSTINGESTIMATOR_AVAILABLE = False

try:
    from analysis.machine_learning.gru_estimator import GRUEstimator
    GRUESTIMATOR_AVAILABLE = True
except ImportError:
    GRUESTIMATOR_AVAILABLE = False

try:
    from analysis.machine_learning.lstm_estimator import LSTMEstimator
    LSTMESTIMATOR_AVAILABLE = True
except ImportError:
    LSTMESTIMATOR_AVAILABLE = False

try:
    from analysis.machine_learning.neural_network_estimator import NeuralNetworkEstimator
    NEURALNETWORKESTIMATOR_AVAILABLE = True
except ImportError:
    NEURALNETWORKESTIMATOR_AVAILABLE = False

try:
    from analysis.machine_learning.random_forest_estimator import RandomForestEstimator
    RANDOMFORESTESTIMATOR_AVAILABLE = True
except ImportError:
    RANDOMFORESTESTIMATOR_AVAILABLE = False

try:
    from analysis.machine_learning.svr_estimator import SVREstimator
    SVRESTIMATOR_AVAILABLE = True
except ImportError:
    SVRESTIMATOR_AVAILABLE = False

try:
    from analysis.machine_learning.transformer_estimator import TransformerEstimator
    TRANSFORMERESTIMATOR_AVAILABLE = True
except ImportError:
    TRANSFORMERESTIMATOR_AVAILABLE = False

try:
    from models.estimators.base_estimator import BaseEstimator
    BASEESTIMATOR_AVAILABLE = True
except ImportError:
    BASEESTIMATOR_AVAILABLE = False

try:
    from analysis.wavelet.cwt.cwt_estimator import CWTEstimator
    CWTESTIMATOR_AVAILABLE = True
except ImportError:
    CWTESTIMATOR_AVAILABLE = False

try:
    from analysis.wavelet.log_variance.wavelet_log_variance_estimator import WaveletLogVarianceEstimator
    WAVELETLOGVARIANCEESTIMATOR_AVAILABLE = True
except ImportError:
    WAVELETLOGVARIANCEESTIMATOR_AVAILABLE = False

try:
    from analysis.wavelet.variance.wavelet_variance_estimator import WaveletVarianceEstimator
    WAVELETVARIANCEESTIMATOR_AVAILABLE = True
except ImportError:
    WAVELETVARIANCEESTIMATOR_AVAILABLE = False

try:
    from analysis.wavelet.whittle.wavelet_whittle_estimator import WaveletWhittleEstimator
    WAVELETWHITTLEESTIMATOR_AVAILABLE = True
except ImportError:
    WAVELETWHITTLEESTIMATOR_AVAILABLE = False

try:
    from analysis.temporal.dfa.dfa_estimator import DFAEstimator
    DFAESTIMATOR_AVAILABLE = True
except ImportError:
    DFAESTIMATOR_AVAILABLE = False

try:
    from analysis.temporal.dma.dma_estimator import DMAEstimator
    DMAESTIMATOR_AVAILABLE = True
except ImportError:
    DMAESTIMATOR_AVAILABLE = False

try:
    from analysis.temporal.higuchi.higuchi_estimator import HiguchiEstimator
    HIGUCHIESTIMATOR_AVAILABLE = True
except ImportError:
    HIGUCHIESTIMATOR_AVAILABLE = False

try:
    from analysis.temporal.rs.rs_estimator import RSEstimator
    RSESTIMATOR_AVAILABLE = True
except ImportError:
    RSESTIMATOR_AVAILABLE = False

try:
    from analysis.spectral.gph.gph_estimator import GPHEstimator
    GPHESTIMATOR_AVAILABLE = True
except ImportError:
    GPHESTIMATOR_AVAILABLE = False

try:
    from analysis.spectral.periodogram.periodogram_estimator import PeriodogramEstimator
    PERIODOGRAMESTIMATOR_AVAILABLE = True
except ImportError:
    PERIODOGRAMESTIMATOR_AVAILABLE = False

try:
    from analysis.spectral.whittle.whittle_estimator import WhittleEstimator
    WHITTLEESTIMATOR_AVAILABLE = True
except ImportError:
    WHITTLEESTIMATOR_AVAILABLE = False

try:
    from analysis.multifractal.mfdfa.mfdfa_estimator import MFDFAEstimator
    MFDFAESTIMATOR_AVAILABLE = True
except ImportError:
    MFDFAESTIMATOR_AVAILABLE = False

try:
    from analysis.multifractal.wavelet_leaders.multifractal_wavelet_leaders_estimator import MultifractalWaveletLeadersEstimator
    MULTIFRACTALWAVELETLEADERSESTIMATOR_AVAILABLE = True
except ImportError:
    MULTIFRACTALWAVELETLEADERSESTIMATOR_AVAILABLE = False


    from models.estimators.base_estimator import BaseEstimator
    BASEESTIMATOR_AVAILABLE = True
except ImportError:
    BASEESTIMATOR_AVAILABLE = False

try:
    from analysis.wavelet.cwt.cwt_estimator import CWTEstimator
    CWTESTIMATOR_AVAILABLE = True
except ImportError:
    CWTESTIMATOR_AVAILABLE = False

try:
    from analysis.wavelet.log_variance.wavelet_log_variance_estimator import WaveletLogVarianceEstimator
    WAVELETLOGVARIANCEESTIMATOR_AVAILABLE = True
except ImportError:
    WAVELETLOGVARIANCEESTIMATOR_AVAILABLE = False

try:
    from analysis.wavelet.variance.wavelet_variance_estimator import WaveletVarianceEstimator
    WAVELETVARIANCEESTIMATOR_AVAILABLE = True
except ImportError:
    WAVELETVARIANCEESTIMATOR_AVAILABLE = False

try:
    from analysis.wavelet.whittle.wavelet_whittle_estimator import WaveletWhittleEstimator
    WAVELETWHITTLEESTIMATOR_AVAILABLE = True
except ImportError:
    WAVELETWHITTLEESTIMATOR_AVAILABLE = False

try:
    from analysis.temporal.dfa.dfa_estimator import DFAEstimator
    DFAESTIMATOR_AVAILABLE = True
except ImportError:
    DFAESTIMATOR_AVAILABLE = False

try:
    from analysis.temporal.dma.dma_estimator import DMAEstimator
    DMAESTIMATOR_AVAILABLE = True
except ImportError:
    DMAESTIMATOR_AVAILABLE = False

try:
    from analysis.temporal.higuchi.higuchi_estimator import HiguchiEstimator
    HIGUCHIESTIMATOR_AVAILABLE = True
except ImportError:
    HIGUCHIESTIMATOR_AVAILABLE = False

try:
    from analysis.temporal.rs.rs_estimator import RSEstimator
    RSESTIMATOR_AVAILABLE = True
except ImportError:
    RSESTIMATOR_AVAILABLE = False

try:
    from analysis.spectral.gph.gph_estimator import GPHEstimator
    GPHESTIMATOR_AVAILABLE = True
except ImportError:
    GPHESTIMATOR_AVAILABLE = False

try:
    from analysis.spectral.periodogram.periodogram_estimator import PeriodogramEstimator
    PERIODOGRAMESTIMATOR_AVAILABLE = True
except ImportError:
    PERIODOGRAMESTIMATOR_AVAILABLE = False

try:
    from analysis.spectral.whittle.whittle_estimator import WhittleEstimator
    WHITTLEESTIMATOR_AVAILABLE = True
except ImportError:
    WHITTLEESTIMATOR_AVAILABLE = False

try:
    from analysis.multifractal.mfdfa.mfdfa_estimator import MFDFAEstimator
    MFDFAESTIMATOR_AVAILABLE = True
except ImportError:
    MFDFAESTIMATOR_AVAILABLE = False

try:
    from analysis.multifractal.wavelet_leaders.multifractal_wavelet_leaders_estimator import MultifractalWaveletLeadersEstimator
    MULTIFRACTALWAVELETLEADERSESTIMATOR_AVAILABLE = True
except ImportError:
    MULTIFRACTALWAVELETLEADERSESTIMATOR_AVAILABLE = False


    from models.estimators.base_estimator import BaseEstimator
    BASEESTIMATOR_AVAILABLE = True
except ImportError:
    BASEESTIMATOR_AVAILABLE = False

try:
    from analysis.wavelet.cwt.cwt_estimator import CWTEstimator
    CWTESTIMATOR_AVAILABLE = True
except ImportError:
    CWTESTIMATOR_AVAILABLE = False

try:
    from analysis.wavelet.log_variance.wavelet_log_variance_estimator import WaveletLogVarianceEstimator
    WAVELETLOGVARIANCEESTIMATOR_AVAILABLE = True
except ImportError:
    WAVELETLOGVARIANCEESTIMATOR_AVAILABLE = False

try:
    from analysis.wavelet.variance.wavelet_variance_estimator import WaveletVarianceEstimator
    WAVELETVARIANCEESTIMATOR_AVAILABLE = True
except ImportError:
    WAVELETVARIANCEESTIMATOR_AVAILABLE = False

try:
    from analysis.wavelet.whittle.wavelet_whittle_estimator import WaveletWhittleEstimator
    WAVELETWHITTLEESTIMATOR_AVAILABLE = True
except ImportError:
    WAVELETWHITTLEESTIMATOR_AVAILABLE = False

try:
    from analysis.temporal.dfa.dfa_estimator import DFAEstimator
    DFAESTIMATOR_AVAILABLE = True
except ImportError:
    DFAESTIMATOR_AVAILABLE = False

try:
    from analysis.temporal.dma.dma_estimator import DMAEstimator
    DMAESTIMATOR_AVAILABLE = True
except ImportError:
    DMAESTIMATOR_AVAILABLE = False

try:
    from analysis.temporal.higuchi.higuchi_estimator import HiguchiEstimator
    HIGUCHIESTIMATOR_AVAILABLE = True
except ImportError:
    HIGUCHIESTIMATOR_AVAILABLE = False

try:
    from analysis.temporal.rs.rs_estimator import RSEstimator
    RSESTIMATOR_AVAILABLE = True
except ImportError:
    RSESTIMATOR_AVAILABLE = False

try:
    from analysis.spectral.gph.gph_estimator import GPHEstimator
    GPHESTIMATOR_AVAILABLE = True
except ImportError:
    GPHESTIMATOR_AVAILABLE = False

try:
    from analysis.spectral.periodogram.periodogram_estimator import PeriodogramEstimator
    PERIODOGRAMESTIMATOR_AVAILABLE = True
except ImportError:
    PERIODOGRAMESTIMATOR_AVAILABLE = False

try:
    from analysis.spectral.whittle.whittle_estimator import WhittleEstimator
    WHITTLEESTIMATOR_AVAILABLE = True
except ImportError:
    WHITTLEESTIMATOR_AVAILABLE = False

try:
    from analysis.multifractal.mfdfa.mfdfa_estimator import MFDFAEstimator
    MFDFAESTIMATOR_AVAILABLE = True
except ImportError:
    MFDFAESTIMATOR_AVAILABLE = False

try:
    from analysis.multifractal.wavelet_leaders.multifractal_wavelet_leaders_estimator import MultifractalWaveletLeadersEstimator
    MULTIFRACTALWAVELETLEADERSESTIMATOR_AVAILABLE = True
except ImportError:
    MULTIFRACTALWAVELETLEADERSESTIMATOR_AVAILABLE = False


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
    from analysis.wavelet.log_variance.log_variance_estimator import WaveletLogVarianceEstimator
    WAVELET_LOG_VAR_AVAILABLE = True
except ImportError:
    WAVELET_LOG_VAR_AVAILABLE = False

try:
    from analysis.wavelet.variance.variance_estimator import WaveletVarianceEstimator
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

try:
    from analysis.multifractal.wavelet_leaders.wavelet_leaders_estimator import WaveletLeadersEstimator
    WAVELET_LEADERS_AVAILABLE = True
except ImportError:
    WAVELET_LEADERS_AVAILABLE = False

# Set plotting style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class ComprehensiveEstimatorBenchmark:
    """Comprehensive benchmark for all estimators vs all data generators."""
    
    def __init__(self, data_length: int = 2048, n_trials: int = 5):
        self.data_length = data_length
        self.n_trials = n_trials
        self.results = {}
        self.performance_metrics = {}
        
        # Initialize data generators with correct parameters
        self.data_generators = self._initialize_data_generators()
        
        # Initialize all available estimators
        self.estimators = self._initialize_estimators()
        
        # Test parameters for different Hurst values
        self.test_hurst_values = [0.3, 0.5, 0.7, 0.9]
        
            """Initialize all available data generators with correct parameters."""
        print("Initializing data generators...")
        
        generators = {}
        
        # Traditional stochastic models
        generators['ARFIMAModel'] = {
            'class': ARFIMAModel,
            'params': {'d': value, 'sigma': 1.0, 'method': 'spectral'},
            'type': 'stochastic'
        }
        generators['BaseModel'] = {
            'class': BaseModel,
            'params': {},
            'type': 'stochastic'
        }
        generators['FractionalBrownianMotion'] = {
            'class': FractionalBrownianMotion,
            'params': {'H': value, 'sigma': 1.0, 'method': 'davies_harte'},
            'type': 'stochastic'
        }
        generators['FractionalGaussianNoise'] = {
            'class': FractionalGaussianNoise,
            'params': {'H': value, 'sigma': 1.0, 'method': 'circulant'},
            'type': 'stochastic'
        }
        generators['MultifractalRandomWalk'] = {
            'class': MultifractalRandomWalk,
            'params': {'H': value, 'lambda_param': value, 'sigma': 1.0, 'method': 'cascade'},
            'type': 'stochastic'
        }
        
        # Neural components (if available)
        if BASEMODEL_AVAILABLE:
            try:
                generators['BaseModel'] = {
                    'class': BaseModel,
                    'params': {},
                    'type': 'neural'
                }
            except Exception as e:
                print(f"Warning: BaseModel not available: {e}")
        if BASENEURALFSDE_AVAILABLE:
            try:
                generators['BaseNeuralFSDE'] = {
                    'class': BaseNeuralFSDE,
                    'params': {'state_dim': value, 'hidden_dim': value, 'hurst_parameter': 0.7, 'framework': 'auto'},
                    'type': 'neural'
                }
            except Exception as e:
                print(f"Warning: BaseNeuralFSDE not available: {e}")
        if JAXLATENTFRACTIONALNET_AVAILABLE:
            try:
                generators['JAXLatentFractionalNet'] = {
                    'class': JAXLatentFractionalNet,
                    'params': {'obs_dim': value, 'latent_dim': value, 'hidden_dim': value, 'num_layers': 3, 'hurst_parameter': 0.7, 'activation': 'relu'},
                    'type': 'neural'
                }
            except Exception as e:
                print(f"Warning: JAXLatentFractionalNet not available: {e}")
        if JAXFSDENET_AVAILABLE:
            try:
                generators['JAXfSDENet'] = {
                    'class': JAXfSDENet,
                    'params': {'state_dim': value, 'hidden_dim': value, 'num_layers': 3, 'hurst_parameter': 0.7, 'activation': 'relu'},
                    'type': 'neural'
                }
            except Exception as e:
                print(f"Warning: JAXfSDENet not available: {e}")
        if NEURALFSDEFACTORY_AVAILABLE:
            try:
                generators['NeuralFSDEFactory'] = {
                    'class': NeuralFSDEFactory,
                    'params': {'preferred_framework': 'auto'},
                    'type': 'neural'
                }
            except Exception as e:
                print(f"Warning: NeuralFSDEFactory not available: {e}")
        if TORCHLATENTFRACTIONALNET_AVAILABLE:
            try:
                generators['TorchLatentFractionalNet'] = {
                    'class': TorchLatentFractionalNet,
                    'params': {'obs_dim': value, 'latent_dim': value, 'hidden_dim': value, 'num_layers': 3, 'hurst_parameter': 0.7, 'activation': 'relu', 'dropout': 0.0},
                    'type': 'neural'
                }
            except Exception as e:
                print(f"Warning: TorchLatentFractionalNet not available: {e}")
        if TORCHFSDENET_AVAILABLE:
            try:
                generators['TorchfSDENet'] = {
                    'class': TorchfSDENet,
                    'params': {'state_dim': value, 'hidden_dim': value, 'num_layers': 3, 'hurst_parameter': 0.7, 'activation': 'relu', 'dropout': 0.0},
                    'type': 'neural'
                }
            except Exception as e:
                print(f"Warning: TorchfSDENet not available: {e}")
        
        print(f"  Initialized {len(generators)} data generators")
        return generators
    
            """Initialize all available estimators."""
        print("Initializing estimators...")
        
        estimators = {}
        
        # Group estimators by category
        # Other estimators
        if BASEESTIMATOR_AVAILABLE:
            estimators['BaseEstimator'] = {
                'class': BaseEstimator,
                'params': {},
                'category': 'other'
            }
        # Wavelet estimators
        if CWTESTIMATOR_AVAILABLE:
            estimators['CWTEstimator'] = {
                'class': CWTEstimator,
                'params': {'wavelet': 'cmor1.5-1.0', 'confidence': 0.95},
                'category': 'wavelet'
            }
        if WAVELETLOGVARIANCEESTIMATOR_AVAILABLE:
            estimators['WaveletLogVarianceEstimator'] = {
                'class': WaveletLogVarianceEstimator,
                'params': {'wavelet': 'db4', 'confidence': 0.95},
                'category': 'wavelet'
            }
        if WAVELETVARIANCEESTIMATOR_AVAILABLE:
            estimators['WaveletVarianceEstimator'] = {
                'class': WaveletVarianceEstimator,
                'params': {'wavelet': 'db4', 'confidence': 0.95},
                'category': 'wavelet'
            }
        if WAVELETWHITTLEESTIMATOR_AVAILABLE:
            estimators['WaveletWhittleEstimator'] = {
                'class': WaveletWhittleEstimator,
                'params': {'wavelet': 'db4', 'confidence': 0.95},
                'category': 'wavelet'
            }
        if MULTIFRACTALWAVELETLEADERSESTIMATOR_AVAILABLE:
            estimators['MultifractalWaveletLeadersEstimator'] = {
                'class': MultifractalWaveletLeadersEstimator,
                'params': {'wavelet': 'db4', 'min_scale': 2, 'max_scale': 32, 'num_scales': 10},
                'category': 'wavelet'
            }
        # Temporal estimators
        if DFAESTIMATOR_AVAILABLE:
            estimators['DFAEstimator'] = {
                'class': DFAEstimator,
                'params': {'min_box_size': 4, 'polynomial_order': 1},
                'category': 'temporal'
            }
        if DMAESTIMATOR_AVAILABLE:
            estimators['DMAEstimator'] = {
                'class': DMAEstimator,
                'params': {'min_window_size': 4, 'overlap': True},
                'category': 'temporal'
            }
        if HIGUCHIESTIMATOR_AVAILABLE:
            estimators['HiguchiEstimator'] = {
                'class': HiguchiEstimator,
                'params': {'min_k': 2},
                'category': 'temporal'
            }
        if RSESTIMATOR_AVAILABLE:
            estimators['RSEstimator'] = {
                'class': RSEstimator,
                'params': {'min_window_size': 10, 'overlap': False},
                'category': 'temporal'
            }
        # Spectral estimators
        if GPHESTIMATOR_AVAILABLE:
            estimators['GPHEstimator'] = {
                'class': GPHEstimator,
                'params': {'min_freq_ratio': 0.01, 'max_freq_ratio': 0.1, 'use_welch': True, 'window': 'hann', 'apply_bias_correction': True},
                'category': 'spectral'
            }
        if PERIODOGRAMESTIMATOR_AVAILABLE:
            estimators['PeriodogramEstimator'] = {
                'class': PeriodogramEstimator,
                'params': {'min_freq_ratio': 0.01, 'max_freq_ratio': 0.1, 'use_welch': True, 'window': 'hann', 'use_multitaper': False, 'n_tapers': 3},
                'category': 'spectral'
            }
        if WHITTLEESTIMATOR_AVAILABLE:
            estimators['WhittleEstimator'] = {
                'class': WhittleEstimator,
                'params': {'min_freq_ratio': 0.01, 'max_freq_ratio': 0.1, 'use_local_whittle': True, 'use_welch': True, 'window': 'hann'},
                'category': 'spectral'
            }
        # Multifractal estimators
        if MFDFAESTIMATOR_AVAILABLE:
            estimators['MFDFAEstimator'] = {
                'class': MFDFAEstimator,
                'params': {'min_scale': 8, 'max_scale': 50, 'num_scales': 15, 'order': 1},
                'category': 'multifractal'
            }
        
        print(f"  Initialized {len(estimators)} estimators")
        return estimators
    
    def generate_test_data(self, generator_name: str, generator_info: Dict, 
                          hurst_value: float, seed: int) -> Tuple[np.ndarray, float]:
        """Generate test data using the specified generator."""
        try:
            np.random.seed(seed)
            
            if generator_info['type'] == 'stochastic':
                if generator_name == 'fBm':
                    generator = generator_info['class'](H=hurst_value, **generator_info['params'])
                    data = generator.generate(self.data_length, seed=seed)
                    true_hurst = hurst_value
                elif generator_name == 'fGn':
                    generator = generator_info['class'](H=hurst_value, **generator_info['params'])
                    data = generator.generate(self.data_length, seed=seed)
                    true_hurst = hurst_value
                elif generator_name == 'ARFIMA':
                    # For ARFIMA, d parameter relates to Hurst: H = d + 0.5
                    d_value = hurst_value - 0.5
                    generator = generator_info['class'](d=d_value, **generator_info['params'])
                    data = generator.generate(self.data_length, seed=seed)
                    true_hurst = hurst_value
                elif generator_name == 'MRW':
                    # MRW uses H parameter directly
                    generator = generator_info['class'](H=hurst_value, **generator_info['params'])
                    data = generator.generate(self.data_length, seed=seed)
                    true_hurst = hurst_value
                else:
                    generator = generator_info['class'](**generator_info['params'])
                    data = generator.generate(self.data_length, seed=seed)
                    true_hurst = 0.5
                    
            elif generator_info['type'] == 'neural':
                params = generator_info['params'].copy()
                params['hurst_parameter'] = hurst_value
                generator = generator_info['class'](**params)
                data = generator.simulate(n_samples=self.data_length, dt=0.01)[:, 0]
                true_hurst = hurst_value
            else:
                raise ValueError(f"Unknown generator type: {generator_info['type']}")
                
            return data, true_hurst
            
        except Exception as e:
            print(f"Error generating data with {generator_name}: {e}")
            return None, None
    
    def run_estimator(self, estimator_name: str, estimator_info: Dict, 
                     data: np.ndarray, true_hurst: float) -> Dict[str, Any]:
        """Run a single estimator on the given data."""
        try:
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            estimator = estimator_info['class'](**estimator_info['params'])
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
            
            return {
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
            
        except Exception as e:
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
                'error': str(e),
                'raw_results': {}
            }
    
    def run_benchmark(self) -> None:
        """Run the comprehensive benchmark."""
        print(f"\n=== COMPREHENSIVE ESTIMATOR BENCHMARK ===")
        print(f"Data length: {self.data_length}")
        print(f"Number of trials: {self.n_trials}")
        print(f"Data generators: {len(self.data_generators)}")
        print(f"Estimators: {len(self.estimators)}")
        print(f"Total combinations: {len(self.data_generators) * len(self.estimators) * len(self.test_hurst_values) * self.n_trials}")
        
        all_results = []
        total_combinations = len(self.data_generators) * len(self.estimators) * len(self.test_hurst_values) * self.n_trials
        current_combination = 0
        
        for generator_name, generator_info in self.data_generators.items():
            print(f"\n--- Testing Data Generator: {generator_name} ---")
            
            for hurst_value in self.test_hurst_values:
                print(f"  Hurst parameter: {hurst_value}")
                
                for trial in range(self.n_trials):
                    data, true_hurst = self.generate_test_data(
                        generator_name, generator_info, hurst_value, trial
                    )
                    
                    if data is None:
                        print(f"    Warning: Failed to generate data for trial {trial}")
                        continue
                    
                    for estimator_name, estimator_info in self.estimators.items():
                        current_combination += 1
                        progress = (current_combination / total_combinations) * 100
                        
                        print(f"    [{progress:.1f}%] Testing {estimator_name}...", end=' ')
                        
                        result = self.run_estimator(
                            estimator_name, estimator_info, data, true_hurst
                        )
                        
                        result.update({
                            'generator_name': generator_name,
                            'generator_type': generator_info['type'],
                            'hurst_value': hurst_value,
                            'trial': trial,
                            'data_length': self.data_length
                        })
                        
                        all_results.append(result)
                        
                        if result['success']:
                            print(f"✓ H_est={result['estimated_hurst']:.3f}, "
                                  f"error={result['absolute_error']:.3f}, "
                                  f"time={result['execution_time']:.3f}s")
                        else:
                            print(f"✗ Failed: {result.get('error', 'Unknown error')}")
        
        self.results = all_results
        print(f"\n=== BENCHMARK COMPLETE ===")
        print(f"Total results: {len(all_results)}")
        
        self._analyze_results()
    
    def _analyze_results(self) -> None:
        """Analyze benchmark results and create performance leaderboard."""
        print("\n--- Analyzing Results ---")
        
        df = pd.DataFrame(self.results)
        summary_stats = {}
        
        for estimator_name in df['estimator_name'].unique():
            estimator_data = df[df['estimator_name'] == estimator_name]
            successful = estimator_data[estimator_data['success'] == True]
            
            if len(successful) > 0:
                summary_stats[estimator_name] = {
                    'total_trials': len(estimator_data),
                    'successful_trials': len(successful),
                    'success_rate': len(successful) / len(estimator_data),
                    'mean_absolute_error': successful['absolute_error'].mean(),
                    'std_absolute_error': successful['absolute_error'].std(),
                    'mean_relative_error': successful['relative_error'].mean(),
                    'std_relative_error': successful['relative_error'].std(),
                    'mean_execution_time': successful['execution_time'].mean(),
                    'std_execution_time': successful['execution_time'].std(),
                    'mean_memory_usage': successful['memory_usage'].mean(),
                    'std_memory_usage': successful['memory_usage'].std()
                }
            else:
                summary_stats[estimator_name] = {
                    'total_trials': len(estimator_data),
                    'successful_trials': 0,
                    'success_rate': 0.0,
                    'mean_absolute_error': float('inf'),
                    'std_absolute_error': float('inf'),
                    'mean_relative_error': float('inf'),
                    'std_relative_error': float('inf'),
                    'mean_execution_time': 0.0,
                    'std_execution_time': 0.0,
                    'mean_memory_usage': 0.0,
                    'std_memory_usage': 0.0
                }
        
        self.performance_metrics = summary_stats
        
        # Create performance leaderboard
        self._create_performance_leaderboard()
    
    def _create_performance_leaderboard(self) -> None:
        """Create and display performance leaderboard."""
        print("\n" + "="*100)
        print("🏆 PERFORMANCE LEADERBOARD 🏆")
        print("="*100)
        
        # Sort by success rate first, then by accuracy
        leaderboard = sorted(
            self.performance_metrics.items(),
            key=lambda x: (x[1]['success_rate'], -x[1]['mean_absolute_error']),
            reverse=True
        )
        
        print(f"{'Rank':<4} {'Estimator':<25} {'Success':<8} {'MAE':<8} {'MRE':<8} {'Time(s)':<8} {'Memory(MB)':<10}")
        print("-" * 100)
        
        for rank, (estimator_name, stats) in enumerate(leaderboard, 1):
            success_rate = stats['success_rate'] * 100
            mae = stats['mean_absolute_error']
            mre = stats['mean_relative_error'] * 100 if stats['mean_relative_error'] != float('inf') else float('inf')
            time = stats['mean_execution_time']
            memory = stats['mean_memory_usage']
            
            # Add emojis for top performers
            if rank == 1:
                rank_str = "🥇"
            elif rank == 2:
                rank_str = "🥈"
            elif rank == 3:
                rank_str = "🥉"
            else:
                rank_str = f"{rank:>2}."
            
            print(f"{rank_str:<4} {estimator_name:<25} {success_rate:>6.1f}% {mae:>7.3f} {mre:>7.1f}% {time:>7.3f} {memory:>9.2f}")
        
        print("-" * 100)
        
        # Show best performers in each category
        self._show_category_winners()
    
    def _show_category_winners(self) -> None:
        """Show best performers in each category."""
        print("\n🏅 CATEGORY WINNERS 🏅")
        print("-" * 50)
        
        categories = {}
        for estimator_name, stats in self.performance_metrics.items():
            for est_name, est_info in self.estimators.items():
                if est_name == estimator_name:
                    category = est_info['category']
                    if category not in categories:
                        categories[category] = []
                    categories[category].append((estimator_name, stats))
                    break
        
        for category, estimators in categories.items():
            if estimators:
                # Find best in category (highest success rate, lowest error)
                best = min(estimators, key=lambda x: (-x[1]['success_rate'], x[1]['mean_absolute_error']))
                print(f"{category.title()}: {best[0]} (Success: {best[1]['success_rate']*100:.1f}%, MAE: {best[1]['mean_absolute_error']:.3f})")
    
    def save_results(self, filename: str = 'comprehensive_benchmark_results.csv') -> None:
        """Save benchmark results to CSV file."""
        if not self.results:
            print("No results to save. Run benchmark first.")
            return
        
        Path('benchmark_results').mkdir(exist_ok=True)
        
        # Save detailed results
        df = pd.DataFrame(self.results)
        df.to_csv(f'benchmark_results/{filename}', index=False)
        print(f"Detailed results saved to: benchmark_results/{filename}")
        
        # Save performance summary
        summary_df = pd.DataFrame(self.performance_metrics).T
        summary_df.to_csv('benchmark_results/performance_summary.csv')
        print("Performance summary saved to: benchmark_results/performance_summary.csv")

def main():
    """Main function to run the comprehensive estimator benchmark."""
    print("=== COMPREHENSIVE ESTIMATOR BENCHMARK: ALL 13 ESTIMATORS vs ALL DATA GENERATORS ===\n")
    
    benchmark = ComprehensiveEstimatorBenchmark(data_length=2048, n_trials=5)
    
    try:
        benchmark.run_benchmark()
        benchmark.save_results()
        
        print("\n=== BENCHMARK COMPLETE ===")
        print("Results saved to 'benchmark_results/' directory")
        
    except Exception as e:
        print(f"Error during benchmark: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
