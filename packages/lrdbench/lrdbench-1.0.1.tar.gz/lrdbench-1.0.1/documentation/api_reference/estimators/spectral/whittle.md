# Whittle Estimator

## Overview

The `WhittleEstimator` implements an approximate Whittle likelihood estimator for fractional Gaussian noise. It estimates the fractional differencing parameter d by minimizing the Whittle likelihood using the periodogram and the theoretical spectrum of fractional noise.

## Mathematical Foundation

The Whittle likelihood for a time series with spectral density f(ω) and periodogram I(ω) is:

```
L(d) = -∑[log(f(ω_j; d)) + I(ω_j)/f(ω_j; d)]
```

For fractional Gaussian noise, the spectral density is:

```
f_d(ω) ∝ |2 sin(ω/2)|^(-2d)
```

The estimator minimizes this likelihood with respect to d, then computes H = d + 0.5.

## Constructor

```python
WhittleEstimator(
    assume: str = "fGn",
    freq_cutoff_frac: float = 0.0
)
```

### Parameters

- **assume** (`str`): Assumed process type. Currently only "fGn" is supported. Default: "fGn"
- **freq_cutoff_frac** (`float`): Fraction of highest frequencies to exclude. Must be in [0, 0.5). Default: 0.0

## Methods

### estimate(data)

Estimates the fractional differencing parameter d and Hurst parameter from time series data.

**Parameters:**
- `data` (`np.ndarray`): Input time series data (must have at least 16 samples)

**Returns:**
- `Dict[str, Any]`: Dictionary containing estimation results

**Results dictionary includes:**
- `d` (`float`): Estimated fractional differencing parameter
- `hurst_parameter` (`float`): Estimated Hurst parameter (d + 0.5)
- `objective_value` (`float`): Value of the minimized objective function
- `converged` (`bool`): Whether the optimization converged
- `r_squared` (`float`): R-squared value of the model fit
- `log_model_spec` (`np.ndarray`): Log of the fitted model spectrum
- `log_periodogram` (`np.ndarray`): Log of the periodogram values
- `slope` (`float`): Slope of the log-log fit
- `intercept` (`float`): Intercept of the log-log fit

### get_confidence_intervals(confidence_level=0.95)

Computes confidence intervals for the estimated parameters.

**Parameters:**
- `confidence_level` (`float`): Confidence level (default: 0.95)

**Returns:**
- `Dict[str, Tuple[float, float]]`: Dictionary with confidence intervals for both d and H

### get_estimation_quality()

Returns quality metrics for the estimation.

**Returns:**
- `Dict[str, Any]`: Dictionary with quality metrics (R-squared, convergence status)

### plot_scaling(save_path=None)

Creates visualization of the Whittle fit.

**Parameters:**
- `save_path` (`str`, optional): Path to save the plot

## Usage Examples

### Basic Usage

```python
import numpy as np
from analysis.spectral.whittle import WhittleEstimator
from models.data_models.fgn import FractionalGaussianNoise

# Generate test data
fgn = FractionalGaussianNoise(H=0.6)
data = fgn.generate(2048)

# Create estimator
estimator = WhittleEstimator(assume="fGn")

# Estimate parameters
result = estimator.estimate(data)
print(f"Estimated d: {result['d']:.3f}")
print(f"Estimated H: {result['hurst_parameter']:.3f}")
print(f"Converged: {result['converged']}")
print(f"R-squared: {result['r_squared']:.3f}")

# Get confidence intervals
ci = estimator.get_confidence_intervals()
print(f"95% CI for d: {ci['d']}")
print(f"95% CI for H: {ci['hurst_parameter']}")

# Plot results
estimator.plot_scaling()
```

### Frequency Cutoff Analysis

```python
# Test different frequency cutoffs
for cutoff in [0.0, 0.1, 0.2]:
    estimator = WhittleEstimator(freq_cutoff_frac=cutoff)
    result = estimator.estimate(data)
    print(f"cutoff={cutoff}: d={result['d']:.3f}, H={result['hurst_parameter']:.3f}")
```

### Quality Assessment

```python
estimator = WhittleEstimator()
result = estimator.estimate(data)

# Check convergence and quality
quality = estimator.get_estimation_quality()
if quality['converged']:
    print(f"Estimation converged successfully")
    print(f"R-squared: {quality['r_squared']:.3f}")
else:
    print("Warning: Estimation did not converge")
```

## Performance Considerations

- **Data length**: Requires at least 16 samples, but longer series (≥1024) provide better estimates
- **Optimization**: Uses bounded optimization with d ∈ [-0.49, 0.49]
- **Frequency cutoff**: Can exclude high frequencies to reduce noise effects
- **Convergence**: Check the `converged` flag to ensure reliable estimates

## Validation

The estimator includes robust validation:
- Checks for sufficient data length
- Filters out non-positive periodogram values
- Ensures minimum number of frequency bins
- Validates parameter ranges and optimization bounds

## Limitations

- Currently only supports fractional Gaussian noise (fGn)
- Requires optimization convergence for reliable estimates
- May be sensitive to high-frequency noise
- Assumes the theoretical spectrum model is correct

## Advantages

- Based on maximum likelihood principles
- Provides both d and H estimates
- Includes convergence diagnostics
- Can exclude high-frequency noise via cutoff

## References

1. Whittle, P. (1953). Estimation and information in stationary time series.
2. Fox, R., & Taqqu, M. S. (1986). Large-sample properties of parameter estimates for strongly dependent stationary Gaussian time series.
3. Beran, J. (1994). Statistics for Long-Memory Processes.
