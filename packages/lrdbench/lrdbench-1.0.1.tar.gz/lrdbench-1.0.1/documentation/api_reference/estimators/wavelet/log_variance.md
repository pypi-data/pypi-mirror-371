# Wavelet Log Variance Estimator

## Overview

The Wavelet Log Variance Estimator is a spectral method for estimating the Hurst parameter (H) using the log-variance of wavelet coefficients. This estimator is particularly useful for analyzing long-memory processes and provides robust estimates even in the presence of noise.

## Mathematical Background

The wavelet log variance estimator is based on the relationship:

$$\log(\text{Var}(W_j)) = (2H - 1)\log(2^j) + C$$

where:
- $W_j$ are the wavelet coefficients at scale $j$
- $H$ is the Hurst parameter
- $C$ is a constant

The Hurst parameter is estimated by fitting a linear regression to the log-variance versus log-scale plot.

## Class Definition

```python
class WaveletLogVarianceEstimator(BaseEstimator)
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `wavelet` | str | 'db4' | Wavelet family to use |
| `min_scale` | int | 2 | Minimum wavelet scale |
| `max_scale` | int | 8 | Maximum wavelet scale |
| `confidence_level` | float | 0.95 | Confidence level for intervals |

## Methods

### `estimate(data: np.ndarray) -> EstimationResult`

Estimates the Hurst parameter using wavelet log variance analysis.

**Parameters:**
- `data`: Input time series data

**Returns:**
- `EstimationResult` object containing:
  - `hurst_parameter`: Estimated Hurst parameter
  - `confidence_intervals`: Confidence intervals
  - `scales`: Wavelet scales used
  - `log_variances`: Log variances at each scale
  - `r_squared`: R-squared value of the fit

### `plot_scaling(data: np.ndarray, results: Optional[EstimationResult] = None, save_path: Optional[str] = None) -> None`

Plots the wavelet log variance scaling relationship.

**Parameters:**
- `data`: Input time series data
- `results`: Optional estimation results
- `save_path`: Optional path to save the plot

## Example Usage

```python
import numpy as np
from analysis.wavelet.log_variance.wavelet_log_variance_estimator import WaveletLogVarianceEstimator

# Create estimator
estimator = WaveletLogVarianceEstimator(
    wavelet='db4',
    min_scale=2,
    max_scale=8,
    confidence_level=0.95
)

# Generate sample data
data = np.random.randn(1000)

# Estimate Hurst parameter
results = estimator.estimate(data)
print(f"Hurst parameter: {results.hurst_parameter:.3f}")
print(f"Confidence intervals: {results.confidence_intervals}")

# Plot results
estimator.plot_scaling(data, results)
```

## Performance Characteristics

- **Time Complexity**: O(n log n) due to wavelet transform
- **Space Complexity**: O(n)
- **Accuracy**: Excellent for long-memory processes
- **Robustness**: Highly robust to noise

## Advantages

1. **Log-Scale Relationship**: Natural log-scale relationship for long-memory processes
2. **Noise Robustness**: Very robust to additive noise
3. **Scale Invariance**: Captures scale-invariant properties
4. **Theoretical Foundation**: Well-grounded in wavelet theory

## Limitations

1. **Wavelet Choice**: Performance depends on wavelet selection
2. **Scale Range**: Requires careful selection of scale range
3. **Computational Cost**: More expensive than temporal methods
4. **Short Series**: May not work well with very short time series

## References

1. Abry, P., & Veitch, D. (1998). Wavelet analysis of long-range-dependent traffic.
2. Flandrin, P. (1992). Wavelet analysis and synthesis of fractional Brownian motion.
3. Veitch, D., & Abry, P. (1999). A wavelet-based joint estimator of the parameters of long-range dependence.

## Related Estimators

- [Wavelet Variance Estimator](variance.md)
- [Wavelet Whittle Estimator](whittle.md)
- [Continuous Wavelet Transform Estimator](cwt.md)
