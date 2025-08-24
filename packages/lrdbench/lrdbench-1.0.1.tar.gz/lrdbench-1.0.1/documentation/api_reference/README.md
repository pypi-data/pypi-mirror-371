# API Reference

This section provides comprehensive API documentation for all components of the Synthetic Data Generation and Analysis Project.

## Models

### Base Classes
- [BaseModel](models/base_model.md) - Abstract base class for all stochastic models

### Stochastic Models
- [Fractional Brownian Motion (fBm)](models/fbm.md) - Self-similar Gaussian process
- [Fractional Gaussian Noise (fGn)](models/fgn.md) - Stationary increments of fBm
- [ARFIMA](models/arfima.md) - AutoRegressive Fractionally Integrated Moving Average
- [Multifractal Random Walk (MRW)](models/mrw.md) - Non-Gaussian multifractal process
- [Neural fSDE](models/neural_fsde.md) - Neural network-based fractional SDEs

## Estimators

### Base Classes
- [BaseEstimator](estimators/base_estimator.md) - Abstract base class for all estimators

### Temporal Estimators
- [DFA (Detrended Fluctuation Analysis)](estimators/temporal/dfa.md)
- [R/S Analysis](estimators/temporal/rs.md)
- [Higuchi Method](estimators/temporal/higuchi.md)
- [DMA (Detrending Moving Average)](estimators/temporal/dma.md)

### Spectral Estimators
- [Periodogram](estimators/spectral/periodogram.md)
- [Whittle Estimator](estimators/spectral/whittle.md)
- [GPH (Geweke-Porter-Hudak)](estimators/spectral/gph.md)

### Wavelet Estimators
- [Wavelet Log Variance](estimators/wavelet/log_variance.md)
- [Wavelet Variance](estimators/wavelet/variance.md)
- [Wavelet Whittle](estimators/wavelet/whittle.md)
- [Continuous Wavelet Transform (CWT)](estimators/wavelet/cwt.md)

### Multifractal Estimators
- [MFDFA](estimators/multifractal/mfdfa.md)
- [Wavelet Leaders](estimators/multifractal/wavelet_leaders.md)

### High-Performance Estimators
- [JAX Optimized](estimators/high_performance/jax.md)
- [Numba Optimized](estimators/high_performance/numba.md)

## Utilities

### Data Generation
- [Synthetic Data Generators](utilities/data_generation.md)
- [Parameter Validation](utilities/validation.md)

### Analysis Tools
- [Visualization Utilities](utilities/visualization.md)
- [Statistical Analysis](utilities/statistics.md)

### Performance Tools
- [Benchmarking](utilities/benchmarking.md)
- [Profiling](utilities/profiling.md)

## Complete API Reference

For a comprehensive index of all classes with their exact callable attributes and methods, see:

**[Complete API Reference](COMPLETE_API_REFERENCE.md)**

This document provides detailed information about:
- All class constructors with exact parameters
- All methods with signatures and return types
- All properties and their types
- Usage patterns and examples
- Error handling specifications

## API Design Principles

### Consistent Interface
All models and estimators follow a consistent interface pattern:

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

### Parameter Validation
All classes include comprehensive parameter validation with informative error messages.

### Documentation Standards
- Complete docstrings with parameter descriptions
- Type hints for all functions
- Examples for all major methods
- Mathematical formulas where appropriate
- References to relevant literature
