# Component Discovery Summary

Generated on: 2025-08-22 16:18:06

## Data Generators

### ARFIMAModel
- **Type**: stochastic
- **Module**: `models.data_models.arfima.arfima_model`
- **File**: `models\data_models\arfima\arfima_model.py`
- **Description**: Autoregressive Fractionally Integrated Moving Average (ARFIMA) model.

ARFIMA(p,d,q) process combines autoregressive (AR), fractionally integrated (FI),
and moving average (MA) components. The fractional integration parameter d
controls long-range dependence.

Parameters
----------
d : float
    Fractional integration parameter (-0.5 < d < 0.5)
ar_params : List[float], optional
    Autoregressive parameters (default: [])
ma_params : List[float], optional
    Moving average parameters (default: [])
sigma : float, optional
    Standard deviation of innovations (default: 1.0)
method : str, optional
    Generation method (default: 'spectral')
- **Parameters**: ['d', 'ar_params', 'ma_params', 'sigma', 'method']

### BaseModel
- **Type**: stochastic
- **Module**: `models.data_models.mrw.mrw_model`
- **File**: `models\data_models\mrw\mrw_model.py`
- **Description**: Abstract base class for all stochastic models.

This class defines the interface that all stochastic models must implement,
including methods for parameter validation, data generation, and model
information retrieval.
- **Parameters**: []

### FractionalBrownianMotion
- **Type**: stochastic
- **Module**: `models.data_models.fbm.fbm_model`
- **File**: `models\data_models\fbm\fbm_model.py`
- **Description**: Fractional Brownian Motion (fBm) model.

Fractional Brownian motion is a self-similar Gaussian process with
stationary increments. It is characterized by the Hurst parameter H,
where 0 < H < 1.

Parameters
----------
H : float
    Hurst parameter (0 < H < 1)
    - H = 0.5: Standard Brownian motion
    - H > 0.5: Persistent (long-range dependence)
    - H < 0.5: Anti-persistent
sigma : float, optional
    Standard deviation of the process (default: 1.0)
method : str, optional
    Method for generating fBm:
    - 'davies_harte': Davies-Harte method (default)
    - 'cholesky': Cholesky decomposition method
    - 'circulant': Circulant embedding method
- **Parameters**: ['H', 'sigma', 'method']

### FractionalGaussianNoise
- **Type**: stochastic
- **Module**: `models.data_models.fgn.fgn_model`
- **File**: `models\data_models\fgn\fgn_model.py`
- **Description**: Fractional Gaussian Noise (fGn) generator.

fGn is the stationary increment process of fractional Brownian motion (fBm).
This class generates fGn directly using the circulant embedding approach on
the autocovariance function of fGn.
- **Parameters**: ['H', 'sigma', 'method']

### MultifractalRandomWalk
- **Type**: stochastic
- **Module**: `models.data_models.mrw.mrw_model`
- **File**: `models\data_models\mrw\mrw_model.py`
- **Description**: Multifractal Random Walk (MRW) model.

MRW is a multifractal process that exhibits scale-invariant properties
and is characterized by a log-normal volatility cascade. It is defined
by the Hurst parameter H and the intermittency parameter λ.

Parameters
----------
H : float
    Hurst parameter (0 < H < 1)
lambda_param : float
    Intermittency parameter (λ > 0)
sigma : float, optional
    Base volatility (default: 1.0)
method : str, optional
    Generation method (default: 'cascade')
- **Parameters**: ['H', 'lambda_param', 'sigma', 'method']

## Estimators

### BaseMLEstimator
- **Category**: other
- **Module**: `analysis.machine_learning.transformer_estimator`
- **File**: `analysis\machine_learning\transformer_estimator.py`
- **Description**: Abstract base class for all machine learning-based estimators.

This class defines the interface that all ML estimators must implement,
including methods for feature extraction, model training, prediction,
and performance evaluation.
- **Parameters**: []

### CNNEstimator
- **Category**: other
- **Module**: `analysis.machine_learning.cnn_estimator`
- **File**: `analysis\machine_learning\cnn_estimator.py`
- **Description**: Convolutional Neural Network estimator for Hurst parameter estimation.

This estimator uses CNN to learn the mapping from time series data
to Hurst parameters. Currently a placeholder for future implementation.
- **Parameters**: []

### GradientBoostingEstimator
- **Category**: other
- **Module**: `analysis.machine_learning.gradient_boosting_estimator`
- **File**: `analysis\machine_learning\gradient_boosting_estimator.py`
- **Description**: Gradient Boosting estimator for Hurst parameter estimation.

This estimator uses gradient boosting to learn the mapping
from time series features to Hurst parameters.
- **Parameters**: []

### GRUEstimator
- **Category**: other
- **Module**: `analysis.machine_learning.gru_estimator`
- **File**: `analysis\machine_learning\gru_estimator.py`
- **Description**: GRU estimator for Hurst parameter estimation using PyTorch.
- **Parameters**: []

### LSTMEstimator
- **Category**: other
- **Module**: `analysis.machine_learning.lstm_estimator`
- **File**: `analysis\machine_learning\lstm_estimator.py`
- **Description**: LSTM estimator for Hurst parameter estimation using PyTorch.
- **Parameters**: []

### NeuralNetworkEstimator
- **Category**: other
- **Module**: `analysis.machine_learning.neural_network_estimator`
- **File**: `analysis\machine_learning\neural_network_estimator.py`
- **Description**: Neural Network estimator for Hurst parameter estimation.

This estimator uses a multi-layer perceptron (MLP) to learn the mapping
from time series features to Hurst parameters.
- **Parameters**: []

### RandomForestEstimator
- **Category**: other
- **Module**: `analysis.machine_learning.random_forest_estimator`
- **File**: `analysis\machine_learning\random_forest_estimator.py`
- **Description**: Random Forest estimator for Hurst parameter estimation.

This estimator uses an ensemble of decision trees to learn the mapping
from time series features to Hurst parameters.
- **Parameters**: []

### SVREstimator
- **Category**: other
- **Module**: `analysis.machine_learning.svr_estimator`
- **File**: `analysis\machine_learning\svr_estimator.py`
- **Description**: Support Vector Regression estimator for Hurst parameter estimation.

This estimator uses support vector regression to learn the mapping
from time series features to Hurst parameters.
- **Parameters**: []

### TransformerEstimator
- **Category**: other
- **Module**: `analysis.machine_learning.transformer_estimator`
- **File**: `analysis\machine_learning\transformer_estimator.py`
- **Description**: Transformer estimator for Hurst parameter estimation.

This estimator uses transformer architecture to learn the mapping from time series data
to Hurst parameters. Currently a placeholder for future implementation.
- **Parameters**: []

### BaseEstimator
- **Category**: other
- **Module**: `models.estimators.base_estimator`
- **File**: `models\estimators\base_estimator.py`
- **Description**: Abstract base class for all parameter estimators.

This class defines the interface that all estimators must implement,
including methods for parameter estimation, confidence intervals,
and result reporting.
- **Parameters**: []

### CWTEstimator
- **Category**: wavelet
- **Module**: `analysis.wavelet.cwt.cwt_estimator`
- **File**: `analysis\wavelet\cwt\cwt_estimator.py`
- **Description**: Continuous Wavelet Transform (CWT) Analysis estimator.

This estimator uses continuous wavelet transforms to analyze the scaling behavior
of time series data and estimate the Hurst parameter for fractional processes.

Attributes:
    wavelet (str): Wavelet type to use for continuous transform
    scales (np.ndarray): Array of scales for wavelet analysis
    confidence (float): Confidence level for confidence intervals
- **Parameters**: ['wavelet', 'scales', 'confidence']

### WaveletLogVarianceEstimator
- **Category**: wavelet
- **Module**: `analysis.wavelet.log_variance.wavelet_log_variance_estimator`
- **File**: `analysis\wavelet\log_variance\wavelet_log_variance_estimator.py`
- **Description**: Wavelet Log Variance Analysis estimator.

This estimator uses wavelet decomposition to analyze the log-transformed variance
of wavelet coefficients at different scales, which can be used to estimate the 
Hurst parameter for fractional processes with improved statistical properties.

Attributes:
    wavelet (str): Wavelet type to use for decomposition
    scales (List[int]): List of scales for wavelet analysis
    confidence (float): Confidence level for confidence intervals
- **Parameters**: ['wavelet', 'scales', 'confidence']

### WaveletVarianceEstimator
- **Category**: wavelet
- **Module**: `analysis.wavelet.variance.wavelet_variance_estimator`
- **File**: `analysis\wavelet\variance\wavelet_variance_estimator.py`
- **Description**: Wavelet Variance Analysis estimator.

This estimator uses wavelet decomposition to analyze the variance of wavelet
coefficients at different scales, which can be used to estimate the Hurst
parameter for fractional processes.

Attributes:
    wavelet (str): Wavelet type to use for decomposition
    scales (List[int]): List of scales for wavelet analysis
    confidence (float): Confidence level for confidence intervals
- **Parameters**: ['wavelet', 'scales', 'confidence']

### WaveletWhittleEstimator
- **Category**: wavelet
- **Module**: `analysis.wavelet.whittle.wavelet_whittle_estimator`
- **File**: `analysis\wavelet\whittle\wavelet_whittle_estimator.py`
- **Description**: Wavelet Whittle Analysis estimator.

This estimator combines wavelet decomposition with Whittle likelihood estimation
to provide robust estimation of the Hurst parameter for fractional processes.

Attributes:
    wavelet (str): Wavelet type to use for decomposition
    scales (List[int]): List of scales for wavelet analysis
    confidence (float): Confidence level for confidence intervals
- **Parameters**: ['wavelet', 'scales', 'confidence']

### DFAEstimator
- **Category**: temporal
- **Module**: `analysis.temporal.dfa.dfa_estimator`
- **File**: `analysis\temporal\dfa\dfa_estimator.py`
- **Description**: Detrended Fluctuation Analysis (DFA) estimator.

DFA is a method for quantifying long-range correlations in time series
that is robust to non-stationarities. It estimates the Hurst parameter
by analyzing the scaling behavior of detrended fluctuations.

Parameters
----------
min_box_size : int, optional
    Minimum box size for analysis (default: 4)
max_box_size : int, optional
    Maximum box size for analysis (default: None, will use n/4)
box_sizes : array-like, optional
    Specific box sizes to use (default: None)
polynomial_order : int, optional
    Order of polynomial for detrending (default: 1)
- **Parameters**: ['min_box_size', 'max_box_size', 'box_sizes', 'polynomial_order']

### DMAEstimator
- **Category**: temporal
- **Module**: `analysis.temporal.dma.dma_estimator`
- **File**: `analysis\temporal\dma\dma_estimator.py`
- **Description**: Detrended Moving Average (DMA) estimator for Hurst parameter.

The DMA method is a variant of DFA that uses a moving average instead
of polynomial fitting for detrending. It is computationally efficient
and robust to various types of non-stationarity.

The method works by:
1. Computing the cumulative sum of the time series
2. For each window size, calculating the moving average
3. Detrending by subtracting the moving average
4. Computing the fluctuation function
5. Fitting a power law relationship: F(n) ~ n^H

Parameters
----------
min_window_size : int, default=4
    Minimum window size for DMA calculation.
max_window_size : int, optional
    Maximum window size. If None, uses n/4 where n is data length.
window_sizes : List[int], optional
    Specific window sizes to use. If provided, overrides min/max.
overlap : bool, default=True
    Whether to use overlapping windows for moving average.
- **Parameters**: ['min_window_size', 'max_window_size', 'window_sizes', 'overlap']

### HiguchiEstimator
- **Category**: temporal
- **Module**: `analysis.temporal.higuchi.higuchi_estimator`
- **File**: `analysis\temporal\higuchi\higuchi_estimator.py`
- **Description**: Higuchi Method estimator for fractal dimension and Hurst parameter.

The Higuchi method is an efficient algorithm for estimating the fractal
dimension of a time series. It is based on the relationship between the
length of the curve and the time interval used to measure it.

The method works by:
1. Computing the curve length for different time intervals k
2. Fitting a power law relationship: L(k) ~ k^(-D)
3. The fractal dimension D is related to the Hurst parameter H by: H = 2 - D

Parameters
----------
min_k : int, default=2
    Minimum time interval for curve length calculation.
max_k : int, optional
    Maximum time interval. If None, uses n/4 where n is data length.
k_values : List[int], optional
    Specific k values to use. If provided, overrides min/max.
- **Parameters**: ['min_k', 'max_k', 'k_values']

### RSEstimator
- **Category**: temporal
- **Module**: `analysis.temporal.rs.rs_estimator`
- **File**: `analysis\temporal\rs\rs_estimator.py`
- **Description**: Rescaled Range (R/S) Analysis estimator.

The R/S method estimates the Hurst parameter by analyzing the scaling
behavior of the rescaled range statistic across different time scales.

Parameters
----------
min_scale : int, optional
    Minimum scale (window size) to use (default: 10)
max_scale : int, optional
    Maximum scale (window size) to use (default: None, uses n/4)
num_scales : int, optional
    Number of scales to use (default: 20)
- **Parameters**: ['min_window_size', 'max_window_size', 'window_sizes', 'overlap']

### GPHEstimator
- **Category**: spectral
- **Module**: `analysis.spectral.gph.gph_estimator`
- **File**: `analysis\spectral\gph\gph_estimator.py`
- **Description**: Geweke-Porter-Hudak (GPH) Hurst parameter estimator.

This estimator uses log-periodogram regression with the regressor
log(4*sin^2(ω/2)) to estimate the fractional differencing parameter d,
then converts to Hurst parameter as H = d + 0.5.

Parameters
----------
min_freq_ratio : float, optional (default=0.01)
    Minimum frequency ratio (relative to Nyquist) for fitting.
max_freq_ratio : float, optional (default=0.1)
    Maximum frequency ratio (relative to Nyquist) for fitting.
use_welch : bool, optional (default=True)
    Whether to use Welch's method for PSD estimation.
window : str, optional (default='hann')
    Window function for Welch's method.
nperseg : int, optional (default=None)
    Length of each segment for Welch's method. If None, uses n/8.
apply_bias_correction : bool, optional (default=True)
    Whether to apply bias correction for finite sample effects.
- **Parameters**: ['min_freq_ratio', 'max_freq_ratio', 'use_welch', 'window', 'nperseg', 'apply_bias_correction']

### PeriodogramEstimator
- **Category**: spectral
- **Module**: `analysis.spectral.periodogram.periodogram_estimator`
- **File**: `analysis\spectral\periodogram\periodogram_estimator.py`
- **Description**: Periodogram-based Hurst parameter estimator.

This estimator computes the power spectral density (PSD) of the time series
and fits a power law to the low-frequency portion to estimate the Hurst
parameter. The relationship is: PSD(f) ~ f^(-beta) where beta = 2H - 1.

Parameters
----------
min_freq_ratio : float, optional (default=0.01)
    Minimum frequency ratio (relative to Nyquist) for fitting.
max_freq_ratio : float, optional (default=0.1)
    Maximum frequency ratio (relative to Nyquist) for fitting.
use_welch : bool, optional (default=True)
    Whether to use Welch's method for PSD estimation.
window : str, optional (default='hann')
    Window function for Welch's method.
nperseg : int, optional (default=None)
    Length of each segment for Welch's method. If None, uses n/8.
use_multitaper : bool, optional (default=False)
    Whether to use multi-taper method for PSD estimation.
n_tapers : int, optional (default=3)
    Number of tapers for multi-taper method.
- **Parameters**: ['min_freq_ratio', 'max_freq_ratio', 'use_welch', 'window', 'nperseg', 'use_multitaper', 'n_tapers']

### WhittleEstimator
- **Category**: spectral
- **Module**: `analysis.spectral.whittle.whittle_estimator`
- **File**: `analysis\spectral\whittle\whittle_estimator.py`
- **Description**: Whittle-based Hurst parameter estimator.

This estimator uses maximum likelihood estimation in the frequency domain
to estimate the Hurst parameter. It can use either the standard Whittle
likelihood or the local Whittle variant.

Parameters
----------
min_freq_ratio : float, optional (default=0.01)
    Minimum frequency ratio (relative to Nyquist) for fitting.
max_freq_ratio : float, optional (default=0.1)
    Maximum frequency ratio (relative to Nyquist) for fitting.
use_local_whittle : bool, optional (default=True)
    Whether to use local Whittle estimation (more robust).
use_welch : bool, optional (default=True)
    Whether to use Welch's method for PSD estimation.
window : str, optional (default='hann')
    Window function for Welch's method.
nperseg : int, optional (default=None)
    Length of each segment for Welch's method. If None, uses n/8.
- **Parameters**: ['min_freq_ratio', 'max_freq_ratio', 'use_local_whittle', 'use_welch', 'window', 'nperseg']

### MFDFAEstimator
- **Category**: multifractal
- **Module**: `analysis.multifractal.mfdfa.mfdfa_estimator`
- **File**: `analysis\multifractal\mfdfa\mfdfa_estimator.py`
- **Description**: Multifractal Detrended Fluctuation Analysis (MFDFA) estimator.

MFDFA extends DFA to analyze multifractal properties by computing
fluctuation functions for different moments q.
- **Parameters**: ['q_values', 'scales', 'min_scale', 'max_scale', 'num_scales', 'order']

### MultifractalWaveletLeadersEstimator
- **Category**: wavelet
- **Module**: `analysis.multifractal.wavelet_leaders.multifractal_wavelet_leaders_estimator`
- **File**: `analysis\multifractal\wavelet_leaders\multifractal_wavelet_leaders_estimator.py`
- **Description**: Multifractal Wavelet Leaders estimator.

This estimator uses wavelet leaders to analyze multifractal properties
of time series data, providing robust estimates of the multifractal spectrum.
- **Parameters**: ['wavelet', 'scales', 'min_scale', 'max_scale', 'num_scales', 'q_values']

## Neural Components

### BaseModel
- **Type**: neural
- **Module**: `models.data_models.neural_fsde.base_neural_fsde`
- **File**: `models\data_models\neural_fsde\base_neural_fsde.py`
- **Description**: Abstract base class for all stochastic models.

This class defines the interface that all stochastic models must implement,
including methods for parameter validation, data generation, and model
information retrieval.
- **Parameters**: []

### BaseNeuralFSDE
- **Type**: neural
- **Module**: `models.data_models.neural_fsde.torch_fsde_net`
- **File**: `models\data_models\neural_fsde\torch_fsde_net.py`
- **Description**: Base class for neural fractional stochastic differential equations.

This class provides a unified interface for neural fSDEs implemented
in either JAX (for high performance) or PyTorch (for compatibility).
- **Parameters**: ['state_dim', 'hidden_dim', 'hurst_parameter', 'framework']

### JAXLatentFractionalNet
- **Type**: neural
- **Module**: `models.data_models.neural_fsde.jax_fsde_net`
- **File**: `models\data_models\neural_fsde\jax_fsde_net.py`
- **Description**: JAX-based Latent Fractional Net (Lf-Net) implementation.

This extends the basic fSDE-Net with latent space processing for
complex temporal dependencies.
- **Parameters**: ['obs_dim', 'latent_dim', 'hidden_dim', 'num_layers', 'hurst_parameter', 'activation', 'key']

### JAXfSDENet
- **Type**: neural
- **Module**: `models.data_models.neural_fsde.jax_fsde_net`
- **File**: `models\data_models\neural_fsde\jax_fsde_net.py`
- **Description**: JAX-based neural fractional stochastic differential equation network.

This implementation leverages JAX's JIT compilation and GPU acceleration
for high-performance neural fSDE computation.
- **Parameters**: ['state_dim', 'hidden_dim', 'num_layers', 'hurst_parameter', 'activation', 'key']

### NeuralFSDEFactory
- **Type**: neural
- **Module**: `models.data_models.neural_fsde.hybrid_factory`
- **File**: `models\data_models\neural_fsde\hybrid_factory.py`
- **Description**: Factory for creating neural fSDE models with automatic framework selection.

This factory automatically chooses the best available framework:
- JAX: High performance, GPU acceleration
- PyTorch: Compatibility, debugging, CPU/GPU support
- Fallback: Error if neither is available
- **Parameters**: ['preferred_framework']

### TorchLatentFractionalNet
- **Type**: neural
- **Module**: `models.data_models.neural_fsde.torch_fsde_net`
- **File**: `models\data_models\neural_fsde\torch_fsde_net.py`
- **Description**: PyTorch-based Latent Fractional Net (Lf-Net) implementation.

This extends the basic fSDE-Net with latent space processing for
complex temporal dependencies.
- **Parameters**: ['obs_dim', 'latent_dim', 'hidden_dim', 'num_layers', 'hurst_parameter', 'activation', 'dropout']

### TorchfSDENet
- **Type**: neural
- **Module**: `models.data_models.neural_fsde.torch_fsde_net`
- **File**: `models\data_models\neural_fsde\torch_fsde_net.py`
- **Description**: PyTorch-based neural fractional stochastic differential equation network.

This implementation provides compatibility and debugging capabilities
while maintaining the same interface as the JAX version.
- **Parameters**: ['state_dim', 'hidden_dim', 'num_layers', 'hurst_parameter', 'activation', 'dropout']

