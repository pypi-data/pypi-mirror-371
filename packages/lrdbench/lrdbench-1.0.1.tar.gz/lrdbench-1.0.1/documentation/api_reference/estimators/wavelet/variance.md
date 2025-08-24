# Wavelet Variance Estimator

## Overview

The Wavelet Variance Estimator is a spectral method for estimating the Hurst parameter (H) of long-memory time series using wavelet analysis. This estimator is particularly effective for analyzing the scaling properties of time series in the wavelet domain.

## Mathematical Background

The wavelet variance estimator is based on the relationship between the wavelet coefficients and the Hurst parameter:

$$\log_2(\text{Var}(W_j)) = (2H - 1)j + C$$

where:
- $W_j$ are the wavelet coefficients at scale $j$
- $H$ is the Hurst parameter
- $C$ is a constant

The Hurst parameter is estimated by fitting a linear regression to the log-variance versus scale plot.

## Class Definition

```python
class WaveletVarianceEstimator(BaseEstimator)
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

Estimates the Hurst parameter using wavelet variance analysis.

**Parameters:**
- `data`: Input time series data

**Returns:**
- `EstimationResult` object containing:
  - `hurst_parameter`: Estimated Hurst parameter
  - `confidence_intervals`: Confidence intervals
  - `scales`: Wavelet scales used
  - `variances`: Wavelet variances at each scale
  - `r_squared`: R-squared value of the fit

### `plot_scaling(data: np.ndarray, results: Optional[EstimationResult] = None, save_path: Optional[str] = None) -> None`

Plots the wavelet variance scaling relationship.

**Parameters:**
- `data`: Input time series data
- `results`: Optional estimation results
- `save_path`: Optional path to save the plot

## Example Usage

```python
import numpy as np
from analysis.wavelet.variance.wavelet_variance_estimator import WaveletVarianceEstimator

# Create estimator
estimator = WaveletVarianceEstimator(
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
- **Accuracy**: Good for long-memory processes
- **Robustness**: Moderately robust to noise

## Advantages

1. **Spectral Resolution**: Provides good frequency resolution
2. **Noise Robustness**: Relatively robust to additive noise
3. **Scale Localization**: Captures scale-dependent properties
4. **Non-stationarity Handling**: Can handle some non-stationary processes

## Limitations

1. **Wavelet Choice**: Performance depends on wavelet selection
2. **Scale Range**: Requires careful selection of scale range
3. **Computational Cost**: More expensive than temporal methods
4. **Parameter Sensitivity**: Sensitive to scale range parameters

## References

1. Abry, P., & Veitch, D. (1998). Wavelet analysis of long-range-dependent traffic.
2. Flandrin, P. (1992). Wavelet analysis and synthesis of fractional Brownian motion.
3. Veitch, D., & Abry, P. (1999). A wavelet-based joint estimator of the parameters of long-range dependence.

## Related Estimators

- [Wavelet Log Variance Estimator](log_variance.md)
- [Wavelet Whittle Estimator](whittle.md)
- [Continuous Wavelet Transform Estimator](cwt.md)
