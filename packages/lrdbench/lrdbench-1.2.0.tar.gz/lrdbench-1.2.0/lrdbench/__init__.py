"""
LRDBench: Comprehensive Framework for Long-Range Dependence Estimation

A comprehensive repository for exploring synthetic data generation techniques 
and estimation methods for various stochastic processes, with a focus on 
long-range dependence estimation and machine learning approaches.

Author: Davian R. Chin
Department of Biomedical Engineering, University of Reading
Email: d.r.chin@pgr.reading.ac.uk
"""

__version__ = "1.2.0"
__author__ = "Davian R. Chin"
__email__ = "d.r.chin@pgr.reading.ac.uk"

# Import main components for easy access
from .analysis.benchmark import ComprehensiveBenchmark

# Import key estimators for convenience
from .analysis.temporal.rs.rs_estimator import RSEstimator
from .analysis.temporal.dfa.dfa_estimator import DFAEstimator
from .analysis.temporal.dma.dma_estimator import DMAEstimator
from .analysis.temporal.higuchi.higuchi_estimator import HiguchiEstimator

from .analysis.spectral.gph.gph_estimator import GPHEstimator
from .analysis.spectral.whittle.whittle_estimator import WhittleEstimator
from .analysis.spectral.periodogram.periodogram_estimator import PeriodogramEstimator

from .analysis.wavelet.cwt.cwt_estimator import CWTEstimator
from .analysis.wavelet.variance.wavelet_variance_estimator import WaveletVarianceEstimator
from .analysis.wavelet.log_variance.wavelet_log_variance_estimator import WaveletLogVarianceEstimator
from .analysis.wavelet.whittle.wavelet_whittle_estimator import WaveletWhittleEstimator

from .analysis.multifractal.mfdfa.mfdfa_estimator import MFDFAEstimator
from .analysis.multifractal.wavelet_leaders.multifractal_wavelet_leaders_estimator import MultifractalWaveletLeadersEstimator

from .analysis.machine_learning.random_forest_estimator import RandomForestEstimator
from .analysis.machine_learning.gradient_boosting_estimator import GradientBoostingEstimator
from .analysis.machine_learning.svr_estimator import SVREstimator

from .analysis.machine_learning.cnn_estimator import CNNEstimator
from .analysis.machine_learning.transformer_estimator import TransformerEstimator

# Import data models
from .models.data_models.fbm.fbm_model import FractionalBrownianMotion
from .models.data_models.fgn.fgn_model import FractionalGaussianNoise
from .models.data_models.arfima.arfima_model import ARFIMAModel
from .models.data_models.mrw.mrw_model import MultifractalRandomWalk

# Import pre-trained models
from .models.pretrained_models.cnn_pretrained import CNNPretrainedModel
from .models.pretrained_models.transformer_pretrained import TransformerPretrainedModel
from .models.pretrained_models.ml_pretrained import (
    RandomForestPretrainedModel, 
    SVREstimatorPretrainedModel, 
    GradientBoostingPretrainedModel
)

__all__ = [
    # Main benchmark class
    'ComprehensiveBenchmark',
    
    # Classical estimators
    'RSEstimator', 'DFAEstimator', 'DMAEstimator', 'HiguchiEstimator',
    'GPHEstimator', 'WhittleEstimator', 'PeriodogramEstimator',
    'CWTEstimator', 'WaveletVarianceEstimator', 'WaveletLogVarianceEstimator', 'WaveletWhittleEstimator',
    'MFDFAEstimator', 'MultifractalWaveletLeadersEstimator',
    
    # ML estimators
    'RandomForestEstimator', 'GradientBoostingEstimator', 'SVREstimator',
    
    # Neural estimators
    'CNNEstimator', 'TransformerEstimator',
    
    # Data models
    'FractionalBrownianMotion', 'FractionalGaussianNoise', 'ARFIMAModel', 'MultifractalRandomWalk',
    
    # Pre-trained models
    'CNNPretrainedModel', 'TransformerPretrainedModel',
    'RandomForestPretrainedModel', 'SVREstimatorPretrainedModel', 'GradientBoostingPretrainedModel',
]
