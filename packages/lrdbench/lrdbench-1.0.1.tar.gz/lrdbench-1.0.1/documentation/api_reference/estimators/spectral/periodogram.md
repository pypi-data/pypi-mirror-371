# Periodogram Estimator

## Overview

The `PeriodogramEstimator` estimates the Hurst parameter from the low-frequency slope of the power spectral density (periodogram). This method is based on the fact that long-memory processes exhibit power-law scaling in their spectral density.

## Mathematical Foundation

For a long-memory process with Hurst parameter H, the power spectral density follows:

```
S(f) ∝ f^(-β)
```

where:
- For fractional Gaussian noise (fGn): β = 2H - 1
- For fractional Brownian motion (fBm): β = 2H + 1

The estimator computes the periodogram and fits a linear relationship in log-log space:

```
log(S(f)) = -β * log(f) + c
```

## Constructor

```python
PeriodogramEstimator(
    window: Optional[str] = "hann",
    detrend: bool = True,
    min_freq_ratio: float = 0.01, max_freq_ratio: float = 0.1,
    assume: str = "fGn"
)
```

### Parameters

- **window** (`str`, optional): Windowing function for periodogram computation. Default: "hann"
- **detrend** (`bool`): Whether to remove the mean from the data. Default: True
- **min_freq_ratio** (`float`): Minimum frequency ratio (relative to Nyquist) for fitting. Must be in (0, 0.5). Default: 0.01
- **max_freq_ratio** (`float`): Maximum frequency ratio (relative to Nyquist) for fitting. Must be in (0, 0.5). Default: 0.1
- **assume** (`str`): Assumed process type. Options: "fGn" or "fBm". Default: "fGn"

## Methods

### estimate(data)

Estimates the Hurst parameter from time series data.

**Parameters:**
- `data` (`np.ndarray`): Input time series data (must have at least 8 samples)

**Returns:**
- `Dict[str, Any]`: Dictionary containing estimation results

**Results dictionary includes:**
- `hurst_parameter` (`float`): Estimated Hurst parameter
- `beta` (`float`): Estimated spectral slope β
- `intercept` (`float`): Intercept of the log-log fit
- `r_squared` (`float`): R-squared value of the linear fit
- `m` (`int`): Number of frequency bins used
- `log_freq` (`np.ndarray`): Log frequencies used for fitting
- `log_psd` (`np.ndarray`): Log periodogram values used for fitting

### get_confidence_intervals(confidence_level=0.95)

Computes confidence intervals for the estimated parameters.

**Parameters:**
- `confidence_level` (`float`): Confidence level (default: 0.95)

**Returns:**
- `Dict[str, Tuple[float, float]]`: Dictionary with confidence intervals

### get_estimation_quality()

Returns quality metrics for the estimation.

**Returns:**
- `Dict[str, Any]`: Dictionary with quality metrics (R-squared)

### plot_scaling(save_path=None)

Creates visualization of the scaling relationship.

**Parameters:**
- `save_path` (`str`, optional): Path to save the plot

## Usage Examples

### Basic Usage

```python
import numpy as np
from analysis.spectral.periodogram import PeriodogramEstimator
from models.data_models.fgn import FractionalGaussianNoise

# Generate test data
fgn = FractionalGaussianNoise(H=0.7)
data = fgn.generate(2048)

# Create estimator
estimator = PeriodogramEstimator(min_freq_ratio=0.01, max_freq_ratio=0.1, assume="fGn")

# Estimate Hurst parameter
result = estimator.estimate(data)
print(f"Estimated H: {result['hurst_parameter']:.3f}")
print(f"R-squared: {result['r_squared']:.3f}")

# Get confidence intervals
ci = estimator.get_confidence_intervals()
print(f"95% CI: {ci['hurst_parameter']}")

# Plot results
estimator.plot_scaling()
```

### Parameter Sensitivity

```python
# Test different low-frequency fractions
for frac in [0.05, 0.1, 0.2]:
    estimator = PeriodogramEstimator(min_freq_ratio=frac*0.1, max_freq_ratio=frac)
    result = estimator.estimate(data)
    print(f"frac={frac}: H={result['hurst_parameter']:.3f}")
```

### Process Type Comparison

```python
# Compare fGn vs fBm assumptions
for assume in ["fGn", "fBm"]:
    estimator = PeriodogramEstimator(assume=assume)
    result = estimator.estimate(data)
    print(f"{assume}: H={result['hurst_parameter']:.3f}")
```

## Performance Considerations

- **Data length**: Requires at least 8 samples, but longer series (≥1024) provide better estimates
- **Frequency selection**: `min_freq_ratio` and `max_freq_ratio` control bias-variance tradeoff
- **Windowing**: Hann window reduces spectral leakage but may affect scaling
- **Detrending**: Removing the mean is generally recommended for stationary processes

## Validation

The estimator includes robust validation:
- Checks for sufficient data length
- Filters out non-positive PSD values
- Ensures minimum number of frequency bins for fitting
- Validates parameter ranges

## Limitations

- Assumes power-law scaling in the low-frequency region
- Sensitive to the choice of `min_freq_ratio` and `max_freq_ratio`
- May be affected by spectral leakage and windowing artifacts
- Requires stationary data (use detrending for non-stationary series)

## References

1. Beran, J. (1994). Statistics for Long-Memory Processes.
2. Geweke, J., & Porter-Hudak, S. (1983). The estimation and application of long memory time series models.
3. Robinson, P. M. (1995). Log-periodogram regression of time series with long range dependence.
