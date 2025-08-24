# MFDFA (Multifractal Detrended Fluctuation Analysis) Estimator

## Overview

The MFDFA (Multifractal Detrended Fluctuation Analysis) Estimator is a powerful method for analyzing multifractal properties in time series data. It extends the traditional DFA method to capture the multifractal spectrum, providing insights into the scaling behavior across different moments of the fluctuation function.

## Mathematical Background

MFDFA is based on the generalized Hurst exponent $h(q)$ which varies with the moment order $q$:

$$F_q(s) \sim s^{h(q)}$$

where:
- $F_q(s)$ is the $q$-th order fluctuation function at scale $s$
- $h(q)$ is the generalized Hurst exponent
- $q$ is the moment order

The multifractal spectrum $f(\alpha)$ is obtained through the Legendre transform:

$$\alpha = h(q) + qh'(q)$$
$$f(\alpha) = q[\alpha - h(q)] + 1$$

where $\alpha$ is the Hölder exponent and $f(\alpha)$ is the fractal dimension.

## Class Definition

```python
class MFDFAEstimator(BaseEstimator)
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `min_window_size` | int | 10 | Minimum window size |
| `max_window_size` | int | 100 | Maximum window size |
| `num_windows` | int | 20 | Number of window sizes |
| `q_values` | List[float] | [-5, -3, -1, 0, 1, 3, 5] | Moment orders |
| `polynomial_order` | int | 2 | Order of polynomial detrending |
| `confidence_level` | float | 0.95 | Confidence level for intervals |

## Methods

### `estimate(data: np.ndarray) -> EstimationResult`

Estimates the multifractal spectrum using MFDFA.

**Parameters:**
- `data`: Input time series data

**Returns:**
- `EstimationResult` object containing:
  - `hurst_parameter`: Average Hurst parameter (h(2))
  - `confidence_intervals`: Confidence intervals
  - `generalized_hurst`: Generalized Hurst exponents h(q)
  - `multifractal_spectrum`: Multifractal spectrum f(α)
  - `holder_exponents`: Hölder exponents α
  - `q_values`: Moment orders used
  - `window_sizes`: Window sizes used

### `plot_scaling(data: np.ndarray, results: Optional[EstimationResult] = None, save_path: Optional[str] = None) -> None`

Plots the MFDFA scaling relationships and multifractal spectrum.

**Parameters:**
- `data`: Input time series data
- `results`: Optional estimation results
- `save_path`: Optional path to save the plot

## Example Usage

```python
import numpy as np
from analysis.multifractal.mfdfa.mfdfa_estimator import MFDFAEstimator

# Create estimator
estimator = MFDFAEstimator(
    min_window_size=10,
    max_window_size=100,
    num_windows=20,
    q_values=[-5, -3, -1, 0, 1, 3, 5],
    polynomial_order=2,
    confidence_level=0.95
)

# Generate sample data
data = np.random.randn(1000)

# Estimate multifractal properties
results = estimator.estimate(data)
print(f"Average Hurst parameter: {results.hurst_parameter:.3f}")
print(f"Generalized Hurst exponents: {results.generalized_hurst}")

# Plot results
estimator.plot_scaling(data, results)
```

## Performance Characteristics

- **Time Complexity**: O(n × num_windows × len(q_values))
- **Space Complexity**: O(n × num_windows)
- **Accuracy**: Excellent for multifractal processes
- **Robustness**: Good robustness to trends and non-stationarity

## Advantages

1. **Multifractal Analysis**: Captures the full multifractal spectrum
2. **Trend Robustness**: Robust to polynomial trends
3. **Scale Invariance**: Analyzes scaling across multiple scales
4. **Comprehensive Information**: Provides detailed multifractal characteristics

## Limitations

1. **Computational Cost**: Expensive due to multiple moment orders
2. **Parameter Sensitivity**: Sensitive to window size selection
3. **Data Requirements**: Requires sufficient data for reliable estimates
4. **Interpretation Complexity**: Results require careful interpretation

## References

1. Kantelhardt, J. W., et al. (2002). Multifractal detrended fluctuation analysis of nonstationary time series.
2. Ihlen, E. A. F. (2012). Introduction to multifractal detrended fluctuation analysis in Matlab.
3. Kantelhardt, J. W., et al. (2001). Detecting long-range correlations with detrended fluctuation analysis.

## Related Estimators

- [Multifractal Wavelet Leaders Estimator](wavelet_leaders.md)
- [DFA Estimator](../temporal/dfa.md)
- [DMA Estimator](../temporal/dma.md)
