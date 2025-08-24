# Continuous Wavelet Transform (CWT) Estimator

## Overview

The Continuous Wavelet Transform (CWT) Estimator is a spectral method that uses the continuous wavelet transform to estimate the Hurst parameter of long-memory time series. This estimator provides excellent time-frequency resolution and is particularly useful for analyzing non-stationary processes.

## Mathematical Background

The CWT estimator is based on the relationship between the wavelet coefficients and the Hurst parameter:

$$|W(a, b)|^2 \propto a^{2H-1}$$

where:
- $W(a, b)$ are the continuous wavelet coefficients
- $a$ is the scale parameter
- $b$ is the translation parameter
- $H$ is the Hurst parameter

The Hurst parameter is estimated by analyzing the scaling behavior of the wavelet coefficients across different scales.

## Class Definition

```python
class CWTEstimator(BaseEstimator)
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `wavelet` | str | 'morlet' | Wavelet family to use |
| `min_scale` | float | 1.0 | Minimum wavelet scale |
| `max_scale` | float | 64.0 | Maximum wavelet scale |
| `num_scales` | int | 64 | Number of scales to use |
| `confidence_level` | float | 0.95 | Confidence level for intervals |

## Methods

### `estimate(data: np.ndarray) -> EstimationResult`

Estimates the Hurst parameter using continuous wavelet transform analysis.

**Parameters:**
- `data`: Input time series data

**Returns:**
- `EstimationResult` object containing:
  - `hurst_parameter`: Estimated Hurst parameter
  - `confidence_intervals`: Confidence intervals
  - `scales`: Wavelet scales used
  - `power_spectrum`: Wavelet power spectrum
  - `r_squared`: R-squared value of the fit

### `plot_scaling(data: np.ndarray, results: Optional[EstimationResult] = None, save_path: Optional[str] = None) -> None`

Plots the CWT scaling relationship and wavelet power spectrum.

**Parameters:**
- `data`: Input time series data
- `results`: Optional estimation results
- `save_path`: Optional path to save the plot

## Example Usage

```python
import numpy as np
from analysis.wavelet.cwt.cwt_estimator import CWTEstimator

# Create estimator
estimator = CWTEstimator(
    wavelet='morlet',
    min_scale=1.0,
    max_scale=64.0,
    num_scales=64,
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

- **Time Complexity**: O(n log n) due to continuous wavelet transform
- **Space Complexity**: O(n × num_scales)
- **Accuracy**: Excellent for non-stationary processes
- **Robustness**: Good robustness to noise

## Advantages

1. **Time-Frequency Resolution**: Excellent time-frequency localization
2. **Non-stationarity Handling**: Can handle non-stationary processes
3. **Scale Continuity**: Continuous scale representation
4. **Visualization**: Provides rich visual information

## Limitations

1. **Computational Cost**: More expensive than discrete wavelet methods
2. **Memory Usage**: Higher memory requirements
3. **Parameter Sensitivity**: Sensitive to scale range selection
4. **Wavelet Choice**: Performance depends on wavelet selection

## References

1. Torrence, C., & Compo, G. P. (1998). A practical guide to wavelet analysis.
2. Flandrin, P. (1992). Wavelet analysis and synthesis of fractional Brownian motion.
3. Abry, P., & Veitch, D. (1998). Wavelet analysis of long-range-dependent traffic.

## Related Estimators

- [Wavelet Variance Estimator](variance.md)
- [Wavelet Log Variance Estimator](log_variance.md)
- [Wavelet Whittle Estimator](whittle.md)
