# Wavelet Whittle Estimator

## Overview

The Wavelet Whittle Estimator is a spectral method that combines wavelet analysis with Whittle likelihood estimation to provide robust estimates of the Hurst parameter. This estimator is particularly effective for analyzing long-memory processes with complex spectral characteristics.

## Mathematical Background

The wavelet Whittle estimator maximizes the Whittle likelihood function in the wavelet domain:

$$\mathcal{L}(H) = -\frac{1}{2}\sum_{j=1}^{J} \left[ \log(S_j(H)) + \frac{I_j}{S_j(H)} \right]$$

where:
- $S_j(H)$ is the theoretical wavelet spectrum at scale $j$
- $I_j$ is the empirical wavelet periodogram at scale $j$
- $H$ is the Hurst parameter

The Hurst parameter is estimated by maximizing this likelihood function.

## Class Definition

```python
class WaveletWhittleEstimator(BaseEstimator)
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `wavelet` | str | 'db4' | Wavelet family to use |
| `min_scale` | int | 2 | Minimum wavelet scale |
| `max_scale` | int | 8 | Maximum wavelet scale |
| `confidence_level` | float | 0.95 | Confidence level for intervals |
| `optimization_method` | str | 'L-BFGS-B' | Optimization method |

## Methods

### `estimate(data: np.ndarray) -> EstimationResult`

Estimates the Hurst parameter using wavelet Whittle likelihood.

**Parameters:**
- `data`: Input time series data

**Returns:**
- `EstimationResult` object containing:
  - `hurst_parameter`: Estimated Hurst parameter
  - `confidence_intervals`: Confidence intervals
  - `scales`: Wavelet scales used
  - `likelihood_value`: Maximum likelihood value
  - `optimization_success`: Whether optimization converged

### `plot_scaling(data: np.ndarray, results: Optional[EstimationResult] = None, save_path: Optional[str] = None) -> None`

Plots the wavelet Whittle scaling relationship.

**Parameters:**
- `data`: Input time series data
- `results`: Optional estimation results
- `save_path`: Optional path to save the plot

## Example Usage

```python
import numpy as np
from analysis.wavelet.whittle.wavelet_whittle_estimator import WaveletWhittleEstimator

# Create estimator
estimator = WaveletWhittleEstimator(
    wavelet='db4',
    min_scale=2,
    max_scale=8,
    confidence_level=0.95,
    optimization_method='L-BFGS-B'
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

- **Time Complexity**: O(n log n) due to wavelet transform + optimization
- **Space Complexity**: O(n)
- **Accuracy**: Excellent for long-memory processes
- **Robustness**: Highly robust to noise and model misspecification

## Advantages

1. **Likelihood-Based**: Uses maximum likelihood estimation
2. **Asymptotic Efficiency**: Asymptotically efficient under Gaussian assumptions
3. **Model Flexibility**: Can incorporate complex spectral models
4. **Statistical Foundation**: Well-grounded in statistical theory

## Limitations

1. **Computational Cost**: More expensive due to optimization
2. **Convergence Issues**: May have convergence problems with some data
3. **Model Assumptions**: Relies on Gaussian assumptions
4. **Parameter Sensitivity**: Sensitive to initial parameter values

## References

1. Whittle, P. (1953). Estimation and information in stationary time series.
2. Abry, P., & Veitch, D. (1998). Wavelet analysis of long-range-dependent traffic.
3. Bardet, J. M., et al. (2000). Generators of long-range dependent processes.

## Related Estimators

- [Wavelet Variance Estimator](variance.md)
- [Wavelet Log Variance Estimator](log_variance.md)
- [Continuous Wavelet Transform Estimator](cwt.md)
