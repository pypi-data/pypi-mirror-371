# Complete API Reference

This document provides a comprehensive index of all classes in the DataExploratoryProject with their exact callable attributes and methods.

## Table of Contents

1. [Base Classes](#base-classes)
2. [Data Models](#data-models)
3. [Estimators](#estimators)
4. [Neural fSDE Components](#neural-fsde-components)
5. [High-Performance Optimizations](#high-performance-optimizations)

## Base Classes

### BaseModel
**File**: `models/data_models/base_model.py`

**Abstract Methods**:
- `generate(n: int, seed: Optional[int] = None) -> np.ndarray`
- `get_parameters() -> Dict[str, Any]`
- `get_theoretical_properties() -> Dict[str, Any]`

**Concrete Methods**:
- `set_parameters(**kwargs) -> None`
- `validate_parameters() -> None`
- `get_model_info() -> Dict[str, Any]`
- `__str__() -> str`
- `__repr__() -> str`

**Properties**:
- `model_name: str`
- `description: str`

### BaseEstimator
**File**: `models/estimators/base_estimator.py`

**Abstract Methods**:
- `estimate(data: np.ndarray) -> Dict[str, Any]`

**Concrete Methods**:
- `get_confidence_intervals(confidence_level: float = 0.95) -> Dict[str, Tuple[float, float]]`
- `get_estimation_quality() -> Dict[str, Any]`
- `set_parameters(**kwargs) -> None`
- `validate_parameters() -> None`
- `get_parameters() -> Dict[str, Any]`
- `__str__() -> str`
- `__repr__() -> str`

**Properties**:
- `estimator_name: str`
- `description: str`

## Data Models

### FractionalBrownianMotion
**File**: `models/data_models/fbm/fbm_model.py`

**Constructor**:
```python
def __init__(self, H: float = 0.5, sigma: float = 1.0, method: str = 'auto')
```

**Methods**:
- `generate(n: int, seed: Optional[int] = None) -> np.ndarray`
- `get_parameters() -> Dict[str, Any]`
- `get_theoretical_properties() -> Dict[str, Any]`
- `set_parameters(**kwargs) -> None`
- `validate_parameters() -> None`
- `get_increments(data: np.ndarray) -> np.ndarray`
- `get_cumulative_variance(t: Union[float, np.ndarray]) -> Union[float, np.ndarray]`
- `get_autocorrelation(lag: Union[int, np.ndarray]) -> Union[float, np.ndarray]`
- `get_spectral_density(frequency: Union[float, np.ndarray]) -> Union[float, np.ndarray]`
- `__str__() -> str`
- `__repr__() -> str`

**Properties**:
- `H: float`
- `sigma: float`
- `method: str`
- `model_name: str`
- `description: str`

### FractionalGaussianNoise
**File**: `models/data_models/fgn/fgn_model.py`

**Constructor**:
```python
def __init__(self, H: float = 0.5, sigma: float = 1.0, method: str = 'auto')
```

**Methods**:
- `generate(n: int, seed: Optional[int] = None) -> np.ndarray`
- `get_parameters() -> Dict[str, Any]`
- `get_theoretical_properties() -> Dict[str, Any]`
- `set_parameters(**kwargs) -> None`
- `validate_parameters() -> None`
- `get_cumulative_sum() -> np.ndarray`
- `get_autocorrelation(lag: Union[int, np.ndarray]) -> Union[float, np.ndarray]`
- `get_spectral_density(frequency: Union[float, np.ndarray]) -> Union[float, np.ndarray]`
- `__str__() -> str`
- `__repr__() -> str`

**Properties**:
- `H: float`
- `sigma: float`
- `method: str`
- `model_name: str`
- `description: str`

### ARFIMAModel
**File**: `models/data_models/arfima/arfima_model.py`

**Constructor**:
```python
def __init__(self, d: float = 0.3, ar_params: Optional[List[float]] = None, 
             ma_params: Optional[List[float]] = None, sigma: float = 1.0, 
             method: str = 'spectral')
```

**Methods**:
- `generate(n: int, seed: Optional[int] = None) -> np.ndarray`
- `get_parameters() -> Dict[str, Any]`
- `get_theoretical_properties() -> Dict[str, Any]`
- `set_parameters(**kwargs) -> None`
- `validate_parameters() -> None`
- `get_fractional_differencing(data: np.ndarray, d: float) -> np.ndarray`
- `get_spectral_density(frequency: Union[float, np.ndarray]) -> Union[float, np.ndarray]`
- `get_autocorrelation(lag: Union[int, np.ndarray]) -> Union[float, np.ndarray]`
- `__str__() -> str`
- `__repr__() -> str`

**Properties**:
- `d: float`
- `ar_params: Optional[List[float]]`
- `ma_params: Optional[List[float]]`
- `sigma: float`
- `method: str`
- `model_name: str`
- `description: str`

### MultifractalRandomWalk
**File**: `models/data_models/mrw/mrw_model.py`

**Constructor**:
```python
def __init__(self, H: float = 0.7, lambda_param: float = 0.5, sigma: float = 1.0, 
             method: str = 'cascade')
```

**Methods**:
- `generate(n: int, seed: Optional[int] = None) -> np.ndarray`
- `get_parameters() -> Dict[str, Any]`
- `get_theoretical_properties() -> Dict[str, Any]`
- `set_parameters(**kwargs) -> None`
- `validate_parameters() -> None`
- `get_multifractal_spectrum(q_values: np.ndarray) -> np.ndarray`
- `get_scaling_exponents(q_values: np.ndarray) -> np.ndarray`
- `get_singularity_spectrum() -> Dict[str, np.ndarray]`
- `__str__() -> str`
- `__repr__() -> str`

**Properties**:
- `H: float`
- `lambda_param: float`
- `sigma: float`
- `method: str`
- `model_name: str`
- `description: str`

## Neural fSDE Components

### BaseNeuralFSDE
**File**: `models/data_models/neural_fsde/base_neural_fsde.py`

**Abstract Methods**:
- `simulate(n_samples: int, dt: float = 0.01, scheme: str = 'euler', seed: Optional[int] = None) -> np.ndarray`
- `get_parameters() -> Dict[str, Any]`
- `get_model_info() -> Dict[str, Any]`

**Concrete Methods**:
- `set_parameters(**kwargs) -> None`
- `validate_parameters() -> None`
- `simulate_batch(n_samples: int, batch_size: int, dt: float = 0.01, scheme: str = 'euler', seed: Optional[int] = None) -> np.ndarray`
- `__str__() -> str`
- `__repr__() -> str`

**Properties**:
- `framework: str`
- `state_dim: int`
- `hidden_dim: int`
- `hurst_parameter: float`
- `model_name: str`
- `description: str`

### FractionalBrownianMotionGenerator
**File**: `models/data_models/neural_fsde/fractional_brownian_motion.py`

**Constructor**:
```python
def __init__(self, method: str = 'auto', seed: Optional[int] = None)
```

**Methods**:
- `generate_path(n_steps: int, hurst: float, dt: float = 1.0, method: Optional[str] = None) -> np.ndarray`
- `generate_increments(n_steps: int, hurst: float, dt: float = 1.0, method: Optional[str] = None) -> np.ndarray`
- `get_parameters() -> Dict[str, Any]`
- `set_parameters(**kwargs) -> None`
- `validate_parameters() -> None`
- `__str__() -> str`
- `__repr__() -> str`

**Properties**:
- `method: str`
- `seed: Optional[int]`

### NeuralFSDEFactory
**File**: `models/data_models/neural_fsde/hybrid_factory.py`

**Constructor**:
```python
def __init__(self, default_framework: str = 'auto')
```

**Methods**:
- `create_fsde_net(state_dim: int, hidden_dim: int, num_layers: int = 3, hurst_parameter: float = 0.7, framework: str = 'auto', **kwargs) -> BaseNeuralFSDE`
- `create_latent_fsde_net(obs_dim: int, latent_dim: int, hidden_dim: int, num_layers: int = 3, hurst_parameter: float = 0.7, framework: str = 'auto', **kwargs) -> BaseNeuralFSDE`
- `benchmark_frameworks(state_dim: int = 1, hidden_dim: int = 32, n_samples: int = 1000, n_runs: int = 5) -> Dict[str, Any]`
- `get_framework_info() -> Dict[str, Any]`
- `get_available_frameworks() -> List[str]`
- `get_recommended_framework() -> str`
- `__str__() -> str`
- `__repr__() -> str`

**Properties**:
- `default_framework: str`
- `available_frameworks: List[str]`

### SDESolver
**File**: `models/data_models/neural_fsde/numerical_solvers.py`

**Constructor**:
```python
def __init__(self, scheme: str = 'euler')
```

**Methods**:
- `solve(drift_func, diffusion_func, x0: np.ndarray, t_span: Tuple[float, float], n_steps: int, hurst: float, dt: float = 0.01, seed: Optional[int] = None) -> np.ndarray`
- `solve_euler(drift_func, diffusion_func, x0: np.ndarray, t_span: Tuple[float, float], n_steps: int, hurst: float, dt: float = 0.01, seed: Optional[int] = None) -> np.ndarray`
- `solve_milstein(drift_func, diffusion_func, x0: np.ndarray, t_span: Tuple[float, float], n_steps: int, hurst: float, dt: float = 0.01, seed: Optional[int] = None) -> np.ndarray`
- `solve_heun(drift_func, diffusion_func, x0: np.ndarray, t_span: Tuple[float, float], n_steps: int, hurst: float, dt: float = 0.01, seed: Optional[int] = None) -> np.ndarray`
- `get_parameters() -> Dict[str, Any]`
- `set_parameters(**kwargs) -> None`
- `validate_parameters() -> None`
- `__str__() -> str`
- `__repr__() -> str`

**Properties**:
- `scheme: str`
- `available_schemes: List[str]`

## Estimators

### Temporal Estimators

#### DFAEstimator
**File**: `analysis/temporal/dfa/dfa_estimator.py`

**Constructor**:
```python
def __init__(self, min_box_size: int = 8, max_box_size: int = 200, 
             box_sizes: Optional[List[int]] = None, overlap: bool = True,
             polynomial_order: int = 1, remove_mean: bool = True)
```

**Methods**:
- `estimate(data: np.ndarray) -> Dict[str, Any]`
- `get_confidence_intervals(confidence_level: float = 0.95, n_bootstrap: int = 1000) -> Dict[str, Tuple[float, float]]`
- `get_estimation_quality() -> Dict[str, Any]`
- `plot_scaling(figsize: Tuple[int, int] = (10, 6), save_path: Optional[str] = None, show: bool = True) -> None`
- `set_parameters(**kwargs) -> None`
- `validate_parameters() -> None`
- `get_parameters() -> Dict[str, Any]`
- `__str__() -> str`
- `__repr__() -> str`

**Properties**:
- `min_box_size: int`
- `max_box_size: int`
- `box_sizes: List[int]`
- `overlap: bool`
- `polynomial_order: int`
- `remove_mean: bool`
- `estimator_name: str`
- `description: str`

#### RSEstimator
**File**: `analysis/temporal/rs/rs_estimator.py`

**Constructor**:
```python
def __init__(self, min_window_size: int = 8, max_window_size: int = 200,
             window_sizes: Optional[List[int]] = None, overlap: bool = True)
```

**Methods**:
- `estimate(data: np.ndarray) -> Dict[str, Any]`
- `get_confidence_intervals(confidence_level: float = 0.95, n_bootstrap: int = 1000) -> Dict[str, Tuple[float, float]]`
- `get_estimation_quality() -> Dict[str, Any]`
- `plot_scaling(figsize: Tuple[int, int] = (10, 6), save_path: Optional[str] = None, show: bool = True) -> None`
- `set_parameters(**kwargs) -> None`
- `validate_parameters() -> None`
- `get_parameters() -> Dict[str, Any]`
- `__str__() -> str`
- `__repr__() -> str`

**Properties**:
- `min_window_size: int`
- `max_window_size: int`
- `window_sizes: List[int]`
- `overlap: bool`
- `estimator_name: str`
- `description: str`

#### HiguchiEstimator
**File**: `analysis/temporal/higuchi/higuchi_estimator.py`

**Constructor**:
```python
def __init__(self, min_k: int = 2, max_k: int = 50, k_values: Optional[List[int]] = None)
```

**Methods**:
- `estimate(data: np.ndarray) -> Dict[str, Any]`
- `get_confidence_intervals(confidence_level: float = 0.95, n_bootstrap: int = 1000) -> Dict[str, Tuple[float, float]]`
- `get_estimation_quality() -> Dict[str, Any]`
- `plot_scaling(figsize: Tuple[int, int] = (10, 6), save_path: Optional[str] = None, show: bool = True) -> None`
- `set_parameters(**kwargs) -> None`
- `validate_parameters() -> None`
- `get_parameters() -> Dict[str, Any]`
- `__str__() -> str`
- `__repr__() -> str`

**Properties**:
- `min_k: int`
- `max_k: int`
- `k_values: List[int]`
- `estimator_name: str`
- `description: str`

#### DMAEstimator
**File**: `analysis/temporal/dma/dma_estimator.py`

**Constructor**:
```python
def __init__(self, min_window_size: int = 8, max_window_size: int = 200,
             window_sizes: Optional[List[int]] = None, overlap: bool = True,
             polynomial_order: int = 1)
```

**Methods**:
- `estimate(data: np.ndarray) -> Dict[str, Any]`
- `get_confidence_intervals(confidence_level: float = 0.95, n_bootstrap: int = 1000) -> Dict[str, Tuple[float, float]]`
- `get_estimation_quality() -> Dict[str, Any]`
- `plot_scaling(figsize: Tuple[int, int] = (10, 6), save_path: Optional[str] = None, show: bool = True) -> None`
- `set_parameters(**kwargs) -> None`
- `validate_parameters() -> None`
- `get_parameters() -> Dict[str, Any]`
- `__str__() -> str`
- `__repr__() -> str`

**Properties**:
- `min_window_size: int`
- `max_window_size: int`
- `window_sizes: List[int]`
- `overlap: bool`
- `polynomial_order: int`
- `estimator_name: str`
- `description: str`

### Spectral Estimators

#### PeriodogramEstimator
**File**: `analysis/spectral/periodogram/periodogram_estimator.py`

**Constructor**:
```python
def __init__(self, min_freq_ratio: float = 0.01, max_freq_ratio: float = 0.1,
             use_welch: bool = True, window: str = 'hann', nperseg: Optional[int] = None,
             use_multitaper: bool = False, n_tapers: int = 3)
```

**Methods**:
- `estimate(data: np.ndarray) -> Dict[str, Any]`
- `get_confidence_intervals(confidence_level: float = 0.95, n_bootstrap: int = 1000) -> Dict[str, Tuple[float, float]]`
- `get_estimation_quality() -> Dict[str, Any]`
- `plot_spectrum(figsize: Tuple[int, int] = (10, 6), save_path: Optional[str] = None, show: bool = True) -> None`
- `set_parameters(**kwargs) -> None`
- `validate_parameters() -> None`
- `get_parameters() -> Dict[str, Any]`
- `__str__() -> str`
- `__repr__() -> str`

**Properties**:
- `min_freq_ratio: float`
- `max_freq_ratio: float`
- `use_welch: bool`
- `window: str`
- `nperseg: Optional[int]`
- `use_multitaper: bool`
- `n_tapers: int`
- `estimator_name: str`
- `description: str`

#### WhittleEstimator
**File**: `analysis/spectral/whittle/whittle_estimator.py`

**Constructor**:
```python
def __init__(self, min_freq_ratio: float = 0.01, max_freq_ratio: float = 0.1,
             use_welch: bool = True, window: str = 'hann', nperseg: Optional[int] = None,
             apply_bias_correction: bool = True)
```

**Methods**:
- `estimate(data: np.ndarray) -> Dict[str, Any]`
- `get_confidence_intervals(confidence_level: float = 0.95, n_bootstrap: int = 1000) -> Dict[str, Tuple[float, float]]`
- `get_estimation_quality() -> Dict[str, Any]`
- `plot_spectrum(figsize: Tuple[int, int] = (10, 6), save_path: Optional[str] = None, show: bool = True) -> None`
- `set_parameters(**kwargs) -> None`
- `validate_parameters() -> None`
- `get_parameters() -> Dict[str, Any]`
- `__str__() -> str`
- `__repr__() -> str`

**Properties**:
- `min_freq_ratio: float`
- `max_freq_ratio: float`
- `use_welch: bool`
- `window: str`
- `nperseg: Optional[int]`
- `apply_bias_correction: bool`
- `estimator_name: str`
- `description: str`

#### GPHEstimator
**File**: `analysis/spectral/gph/gph_estimator.py`

**Constructor**:
```python
def __init__(self, min_freq_ratio: float = 0.01, max_freq_ratio: float = 0.1,
             use_welch: bool = True, window: str = 'hann', nperseg: Optional[int] = None,
             apply_bias_correction: bool = True)
```

**Methods**:
- `estimate(data: np.ndarray) -> Dict[str, Any]`
- `get_confidence_intervals(confidence_level: float = 0.95, n_bootstrap: int = 1000) -> Dict[str, Tuple[float, float]]`
- `get_estimation_quality() -> Dict[str, Any]`
- `plot_spectrum(figsize: Tuple[int, int] = (10, 6), save_path: Optional[str] = None, show: bool = True) -> None`
- `set_parameters(**kwargs) -> None`
- `validate_parameters() -> None`
- `get_parameters() -> Dict[str, Any]`
- `__str__() -> str`
- `__repr__() -> str`

**Properties**:
- `min_freq_ratio: float`
- `max_freq_ratio: float`
- `use_welch: bool`
- `window: str`
- `nperseg: Optional[int]`
- `apply_bias_correction: bool`
- `estimator_name: str`
- `description: str`

### Wavelet Estimators

#### WaveletVarianceEstimator
**File**: `analysis/wavelet/variance/wavelet_variance_estimator.py`

**Constructor**:
```python
def __init__(self, wavelet: str = 'db4', scales: Optional[List[int]] = None,
             min_scale: int = 2, max_scale: int = 64)
```

**Methods**:
- `estimate(data: np.ndarray) -> Dict[str, Any]`
- `get_confidence_intervals(confidence_level: float = 0.95, n_bootstrap: int = 1000) -> Dict[str, Tuple[float, float]]`
- `get_estimation_quality() -> Dict[str, Any]`
- `plot_scaling(figsize: Tuple[int, int] = (10, 6), save_path: Optional[str] = None, show: bool = True) -> None`
- `set_parameters(**kwargs) -> None`
- `validate_parameters() -> None`
- `get_parameters() -> Dict[str, Any]`
- `__str__() -> str`
- `__repr__() -> str`

**Properties**:
- `wavelet: str`
- `scales: List[int]`
- `min_scale: int`
- `max_scale: int`
- `estimator_name: str`
- `description: str`

#### WaveletLogVarianceEstimator
**File**: `analysis/wavelet/log_variance/wavelet_log_variance_estimator.py`

**Constructor**:
```python
def __init__(self, wavelet: str = 'db4', scales: Optional[List[int]] = None,
             min_scale: int = 2, max_scale: int = 64)
```

**Methods**:
- `estimate(data: np.ndarray) -> Dict[str, Any]`
- `get_confidence_intervals(confidence_level: float = 0.95, n_bootstrap: int = 1000) -> Dict[str, Tuple[float, float]]`
- `get_estimation_quality() -> Dict[str, Any]`
- `plot_scaling(figsize: Tuple[int, int] = (10, 6), save_path: Optional[str] = None, show: bool = True) -> None`
- `set_parameters(**kwargs) -> None`
- `validate_parameters() -> None`
- `get_parameters() -> Dict[str, Any]`
- `__str__() -> str`
- `__repr__() -> str`

**Properties**:
- `wavelet: str`
- `scales: List[int]`
- `min_scale: int`
- `max_scale: int`
- `estimator_name: str`
- `description: str`

#### WaveletWhittleEstimator
**File**: `analysis/wavelet/whittle/wavelet_whittle_estimator.py`

**Constructor**:
```python
def __init__(self, wavelet: str = 'db4', scales: Optional[List[int]] = None,
             min_scale: int = 2, max_scale: int = 64, apply_bias_correction: bool = True)
```

**Methods**:
- `estimate(data: np.ndarray) -> Dict[str, Any]`
- `get_confidence_intervals(confidence_level: float = 0.95, n_bootstrap: int = 1000) -> Dict[str, Tuple[float, float]]`
- `get_estimation_quality() -> Dict[str, Any]`
- `plot_spectrum(figsize: Tuple[int, int] = (10, 6), save_path: Optional[str] = None, show: bool = True) -> None`
- `set_parameters(**kwargs) -> None`
- `validate_parameters() -> None`
- `get_parameters() -> Dict[str, Any]`
- `__str__() -> str`
- `__repr__() -> str`

**Properties**:
- `wavelet: str`
- `scales: List[int]`
- `min_scale: int`
- `max_scale: int`
- `apply_bias_correction: bool`
- `estimator_name: str`
- `description: str`

#### CWTEstimator
**File**: `analysis/wavelet/cwt/cwt_estimator.py`

**Constructor**:
```python
def __init__(self, wavelet: str = 'morlet', scales: Optional[List[float]] = None,
             min_scale: float = 1.0, max_scale: float = 64.0, n_scales: int = 50)
```

**Methods**:
- `estimate(data: np.ndarray) -> Dict[str, Any]`
- `get_confidence_intervals(confidence_level: float = 0.95, n_bootstrap: int = 1000) -> Dict[str, Tuple[float, float]]`
- `get_estimation_quality() -> Dict[str, Any]`
- `plot_scalogram(figsize: Tuple[int, int] = (12, 8), save_path: Optional[str] = None, show: bool = True) -> None`
- `set_parameters(**kwargs) -> None`
- `validate_parameters() -> None`
- `get_parameters() -> Dict[str, Any]`
- `__str__() -> str`
- `__repr__() -> str`

**Properties**:
- `wavelet: str`
- `scales: List[float]`
- `min_scale: float`
- `max_scale: float`
- `n_scales: int`
- `estimator_name: str`
- `description: str`

### Multifractal Estimators

#### MFDFAEstimator
**File**: `analysis/multifractal/mfdfa/mfdfa_estimator.py`

**Constructor**:
```python
def __init__(self, q_values: Optional[List[float]] = None, min_box_size: int = 8,
             max_box_size: int = 200, polynomial_order: int = 1)
```

**Methods**:
- `estimate(data: np.ndarray) -> Dict[str, Any]`
- `get_confidence_intervals(confidence_level: float = 0.95, n_bootstrap: int = 1000) -> Dict[str, Tuple[float, float]]`
- `get_estimation_quality() -> Dict[str, Any]`
- `plot_multifractal_spectrum(figsize: Tuple[int, int] = (10, 6), save_path: Optional[str] = None, show: bool = True) -> None`
- `set_parameters(**kwargs) -> None`
- `validate_parameters() -> None`
- `get_parameters() -> Dict[str, Any]`
- `__str__() -> str`
- `__repr__() -> str`

**Properties**:
- `q_values: List[float]`
- `min_box_size: int`
- `max_box_size: int`
- `polynomial_order: int`
- `estimator_name: str`
- `description: str`

#### MultifractalWaveletLeadersEstimator
**File**: `analysis/multifractal/wavelet_leaders/multifractal_wavelet_leaders_estimator.py`

**Constructor**:
```python
def __init__(self, wavelet: str = 'db4', q_values: Optional[List[float]] = None,
             min_scale: int = 2, max_scale: int = 64)
```

**Methods**:
- `estimate(data: np.ndarray) -> Dict[str, Any]`
- `get_confidence_intervals(confidence_level: float = 0.95, n_bootstrap: int = 1000) -> Dict[str, Tuple[float, float]]`
- `get_estimation_quality() -> Dict[str, Any]`
- `plot_multifractal_spectrum(figsize: Tuple[int, int] = (10, 6), save_path: Optional[str] = None, show: bool = True) -> None`
- `set_parameters(**kwargs) -> None`
- `validate_parameters() -> None`
- `get_parameters() -> Dict[str, Any]`
- `__str__() -> str`
- `__repr__() -> str`

**Properties**:
- `wavelet: str`
- `q_values: List[float]`
- `min_scale: int`
- `max_scale: int`
- `estimator_name: str`
- `description: str`

## High-Performance Optimizations

### JAX Optimized Estimators

All estimators have JAX-optimized versions in `analysis/high_performance/jax/`:

- `dfa_jax.py` - JAX-optimized DFA
- `rs_jax.py` - JAX-optimized R/S
- `higuchi_jax.py` - JAX-optimized Higuchi
- `dma_jax.py` - JAX-optimized DMA
- `periodogram_jax.py` - JAX-optimized Periodogram
- `whittle_jax.py` - JAX-optimized Whittle
- `gph_jax.py` - JAX-optimized GPH
- `wavelet_variance_jax.py` - JAX-optimized Wavelet Variance
- `wavelet_log_variance_jax.py` - JAX-optimized Wavelet Log Variance
- `wavelet_whittle_jax.py` - JAX-optimized Wavelet Whittle
- `cwt_jax.py` - JAX-optimized CWT
- `mfdfa_jax.py` - JAX-optimized MFDFA
- `multifractal_wavelet_leaders_jax.py` - JAX-optimized Multifractal Wavelet Leaders

### Numba Optimized Estimators

All estimators have Numba-optimized versions in `analysis/high_performance/numba/`:

- `dfa_numba.py` - Numba-optimized DFA
- `rs_numba.py` - Numba-optimized R/S
- `higuchi_numba.py` - Numba-optimized Higuchi
- `dma_numba.py` - Numba-optimized DMA
- `periodogram_numba.py` - Numba-optimized Periodogram
- `whittle_numba.py` - Numba-optimized Whittle
- `gph_numba.py` - Numba-optimized GPH
- `wavelet_variance_numba.py` - Numba-optimized Wavelet Variance
- `wavelet_log_variance_numba.py` - Numba-optimized Wavelet Log Variance
- `wavelet_whittle_numba.py` - Numba-optimized Wavelet Whittle
- `cwt_numba.py` - Numba-optimized CWT
- `mfdfa_numba.py` - Numba-optimized MFDFA
- `multifractal_wavelet_leaders_numba.py` - Numba-optimized Multifractal Wavelet Leaders

## Usage Patterns

### Common Interface Pattern

All classes follow a consistent interface pattern:

```python
# Models
model = ModelClass(parameters)
data = model.generate(n, seed=seed)
properties = model.get_theoretical_properties()

# Estimators
estimator = EstimatorClass(parameters)
results = estimator.estimate(data)
confidence_intervals = estimator.get_confidence_intervals()
quality = estimator.get_estimation_quality()
```

### Parameter Management

All classes support parameter management:

```python
# Get current parameters
params = obj.get_parameters()

# Update parameters
obj.set_parameters(new_param=value)

# Validate parameters
obj.validate_parameters()
```

### Error Handling

All classes include comprehensive error handling:

- Parameter validation with informative error messages
- Type checking for all inputs
- Range validation for numeric parameters
- Graceful handling of edge cases

### Documentation Standards

All classes include:

- Complete docstrings with parameter descriptions
- Type hints for all functions
- Examples for all major methods
- Mathematical formulas where appropriate
- References to relevant literature
