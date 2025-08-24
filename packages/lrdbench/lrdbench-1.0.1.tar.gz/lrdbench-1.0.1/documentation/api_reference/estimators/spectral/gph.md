# GPH (Geweke-Porter-Hudak) Estimator

## Overview

The `GPHEstimator` implements the Geweke-Porter-Hudak (GPH) log-periodogram regression estimator for fractional differencing parameter d and Hurst parameter. This method regresses the log-periodogram on a specific regressor function derived from the theoretical spectrum of fractional noise.

## Mathematical Foundation

The GPH estimator is based on the relationship between the periodogram I(ω) and the theoretical spectrum of fractional noise. For fractional Gaussian noise, the regression model is:

```
log(I(ω_j)) = c - d * log(4 sin²(ω_j/2)) + ε_j
```

where:
- ω_j are the Fourier frequencies
- d is the fractional differencing parameter
- c is a constant
- ε_j are regression errors

The estimator uses only the lowest m frequencies, where m = floor(n^α) with α ∈ (0.5, 0.8).

## Constructor

```python
GPHEstimator(
    alpha: float = 0.6
)
```

### Parameters

- **alpha** (`float`): Exponent for determining the number of frequencies to use. Must be in (0.5, 0.8). Default: 0.6

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
- `r_squared` (`float`): R-squared value of the regression
- `log_regressor` (`np.ndarray`): Log of the regressor values
- `log_periodogram` (`np.ndarray`): Log of the periodogram values
- `slope` (`float`): Slope of the regression (=-d)
- `intercept` (`float`): Intercept of the regression
- `m` (`int`): Number of frequencies used in the regression

### get_confidence_intervals(confidence_level=0.95)

Computes confidence intervals for the estimated parameters.

**Parameters:**
- `confidence_level` (`float`): Confidence level (default: 0.95)

**Returns:**
- `Dict[str, Tuple[float, float]]`: Dictionary with confidence intervals for both d and H

### get_estimation_quality()

Returns quality metrics for the estimation.

**Returns:**
- `Dict[str, Any]`: Dictionary with quality metrics (R-squared)

### plot_scaling(save_path=None)

Creates visualization of the GPH regression.

**Parameters:**
- `save_path` (`str`, optional): Path to save the plot

## Usage Examples

### Basic Usage

```python
import numpy as np
from analysis.spectral.gph import GPHEstimator
from models.data_models.fgn import FractionalGaussianNoise

# Generate test data
fgn = FractionalGaussianNoise(H=0.55)
data = fgn.generate(2048)

# Create estimator
estimator = GPHEstimator(alpha=0.6)

# Estimate parameters
result = estimator.estimate(data)
print(f"Estimated d: {result['d']:.3f}")
print(f"Estimated H: {result['hurst_parameter']:.3f}")
print(f"R-squared: {result['r_squared']:.3f}")
print(f"Frequencies used: {result['m']}")

# Get confidence intervals
ci = estimator.get_confidence_intervals()
print(f"95% CI for d: {ci['d']}")
print(f"95% CI for H: {ci['hurst_parameter']}")

# Plot results
estimator.plot_scaling()
```

### Alpha Parameter Sensitivity

```python
# Test different alpha values
for alpha in [0.55, 0.6, 0.7]:
    estimator = GPHEstimator(alpha=alpha)
    result = estimator.estimate(data)
    print(f"alpha={alpha}: d={result['d']:.3f}, H={result['hurst_parameter']:.3f}, m={result['m']}")
```

### Quality Assessment

```python
estimator = GPHEstimator(alpha=0.6)
result = estimator.estimate(data)

# Check quality metrics
quality = estimator.get_estimation_quality()
print(f"R-squared: {quality['r_squared']:.3f}")

if quality['r_squared'] > 0.8:
    print("Good fit quality")
elif quality['r_squared'] > 0.6:
    print("Moderate fit quality")
else:
    print("Poor fit quality - consider different parameters")
```

## Performance Considerations

- **Data length**: Requires at least 16 samples, but longer series (≥1024) provide better estimates
- **Alpha selection**: Controls bias-variance tradeoff in frequency selection
- **Frequency count**: Number of frequencies used is m = floor(n^α)
- **Regressor**: Uses log(4 sin²(ω/2)) as the regressor variable

## Validation

The estimator includes robust validation:
- Checks for sufficient data length
- Filters out non-positive periodogram values
- Ensures minimum number of frequencies for regression
- Validates alpha parameter range

## Limitations

- Assumes the theoretical spectrum model is correct
- Sensitive to the choice of α parameter
- May be affected by high-frequency noise
- Requires sufficient low-frequency content

## Advantages

- Simple linear regression approach
- Computationally efficient
- Provides both d and H estimates
- Includes quality metrics (R-squared)
- Well-established theoretical foundation

## Parameter Selection Guidelines

### Alpha (α) Selection

- **α = 0.5**: Uses more frequencies, higher variance, lower bias
- **α = 0.6**: Balanced choice (default)
- **α = 0.7**: Uses fewer frequencies, lower variance, higher bias

### Data Length Requirements

- **Minimum**: 16 samples
- **Recommended**: ≥1024 samples for reliable estimates
- **Optimal**: ≥4096 samples for high precision

## References

1. Geweke, J., & Porter-Hudak, S. (1983). The estimation and application of long memory time series models.
2. Robinson, P. M. (1995). Log-periodogram regression of time series with long range dependence.
3. Beran, J. (1994). Statistics for Long-Memory Processes.
4. Hurvich, C. M., & Ray, B. K. (1995). Estimation of the memory parameter for the log-periodogram regression.
