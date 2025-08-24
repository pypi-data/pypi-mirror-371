# Multifractal Wavelet Leaders Estimator

## Overview

The Multifractal Wavelet Leaders Estimator is a wavelet-based method for analyzing multifractal properties in time series data. It uses wavelet leaders to capture the local Hölder regularity and construct the multifractal spectrum, providing robust estimates of multifractal characteristics.

## Mathematical Background

The wavelet leaders method is based on the wavelet coefficients $d_x(j,k)$ and the wavelet leaders $L_x(j,k)$:

$$L_x(j,k) = \sup_{\lambda' \subset 3\lambda_{j,k}} |d_x(\lambda')|$$

where:
- $\lambda_{j,k}$ is the dyadic interval at scale $j$ and position $k$
- $3\lambda_{j,k}$ is the union of $\lambda_{j,k}$ and its two neighbors
- $d_x(\lambda')$ are the wavelet coefficients

The multifractal formalism relates the structure function $S(q,j)$ to the scaling exponents $\zeta(q)$:

$$S(q,j) = \frac{1}{n_j} \sum_{k=1}^{n_j} |L_x(j,k)|^q \sim 2^{j\zeta(q)}$$

The multifractal spectrum $f(\alpha)$ is obtained through the Legendre transform.

## Class Definition

```python
class MultifractalWaveletLeadersEstimator(BaseEstimator)
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `wavelet` | str | 'db4' | Wavelet family to use |
| `min_scale` | int | 2 | Minimum wavelet scale |
| `max_scale` | int | 8 | Maximum wavelet scale |
| `q_values` | List[float] | [-5, -3, -1, 0, 1, 3, 5] | Moment orders |
| `confidence_level` | float | 0.95 | Confidence level for intervals |

## Methods

### `estimate(data: np.ndarray) -> EstimationResult`

Estimates the multifractal spectrum using wavelet leaders.

**Parameters:**
- `data`: Input time series data

**Returns:**
- `EstimationResult` object containing:
  - `hurst_parameter`: Average Hurst parameter (ζ(2)/2)
  - `confidence_intervals`: Confidence intervals
  - `scaling_exponents`: Scaling exponents ζ(q)
  - `multifractal_spectrum`: Multifractal spectrum f(α)
  - `holder_exponents`: Hölder exponents α
  - `q_values`: Moment orders used
  - `scales`: Wavelet scales used

### `plot_scaling(data: np.ndarray, results: Optional[EstimationResult] = None, save_path: Optional[str] = None) -> None`

Plots the wavelet leaders scaling relationships and multifractal spectrum.

**Parameters:**
- `data`: Input time series data
- `results`: Optional estimation results
- `save_path`: Optional path to save the plot

## Example Usage

```python
import numpy as np
from analysis.multifractal.wavelet_leaders.multifractal_wavelet_leaders_estimator import MultifractalWaveletLeadersEstimator

# Create estimator
estimator = MultifractalWaveletLeadersEstimator(
    wavelet='db4',
    min_scale=2,
    max_scale=8,
    q_values=[-5, -3, -1, 0, 1, 3, 5],
    confidence_level=0.95
)

# Generate sample data
data = np.random.randn(1000)

# Estimate multifractal properties
results = estimator.estimate(data)
print(f"Average Hurst parameter: {results.hurst_parameter:.3f}")
print(f"Scaling exponents: {results.scaling_exponents}")

# Plot results
estimator.plot_scaling(data, results)
```

## Performance Characteristics

- **Time Complexity**: O(n log n × len(q_values))
- **Space Complexity**: O(n × num_scales)
- **Accuracy**: Excellent for multifractal processes
- **Robustness**: Highly robust to noise and trends

## Advantages

1. **Wavelet-Based**: Leverages wavelet analysis advantages
2. **Local Regularity**: Captures local Hölder regularity
3. **Robustness**: Highly robust to noise and trends
4. **Theoretical Foundation**: Well-grounded in wavelet theory

## Limitations

1. **Computational Cost**: Expensive due to wavelet transform and multiple moments
2. **Parameter Sensitivity**: Sensitive to scale range selection
3. **Data Requirements**: Requires sufficient data for reliable estimates
4. **Wavelet Choice**: Performance depends on wavelet selection

## References

1. Jaffard, S., et al. (2006). Wavelet leaders in multifractal analysis.
2. Wendt, H., et al. (2007). Wavelet leaders and bootstrap for multifractal analysis of images.
3. Wendt, H., & Abry, P. (2007). Bootstrap for multifractal analysis.

## Related Estimators

- [MFDFA Estimator](mfdfa.md)
- [Wavelet Variance Estimator](../wavelet/variance.md)
- [Wavelet Log Variance Estimator](../wavelet/log_variance.md)
