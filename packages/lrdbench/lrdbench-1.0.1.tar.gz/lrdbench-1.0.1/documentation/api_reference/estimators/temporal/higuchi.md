# Higuchi Estimator

## Overview

The Higuchi Estimator is a temporal method for estimating the fractal dimension of time series data. It is based on the relationship between the curve length and the step size, providing a robust estimate of the fractal dimension which can be related to the Hurst parameter.

## Mathematical Background

The Higuchi method calculates the curve length $L(k)$ for different step sizes $k$:

$$L(k) = \frac{N-1}{k^2} \sum_{i=1}^{N-m} \left| x_{i+mk} - x_{i+(m-1)k} \right|$$

where:
- $N$ is the length of the time series
- $k$ is the step size
- $m$ is the starting point index
- $x_i$ are the time series values

The fractal dimension $D$ is estimated from the relationship:

$$\log(L(k)) = -D \log(k) + C$$

where $C$ is a constant. The Hurst parameter is related to the fractal dimension by $H = 2 - D$.

## Class Definition

```python
class HiguchiEstimator(BaseEstimator)
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `min_k` | int | 2 | Minimum step size |
| `max_k` | int | 20 | Maximum step size |
| `confidence_level` | float | 0.95 | Confidence level for intervals |

## Methods

### `estimate(data: np.ndarray) -> EstimationResult`

Estimates the Hurst parameter using the Higuchi method.

**Parameters:**
- `data`: Input time series data

**Returns:**
- `EstimationResult` object containing:
  - `hurst_parameter`: Estimated Hurst parameter
  - `confidence_intervals`: Confidence intervals
  - `fractal_dimension`: Estimated fractal dimension
  - `k_values`: Step sizes used
  - `curve_lengths`: Curve lengths at each step size
  - `r_squared`: R-squared value of the fit

### `plot_scaling(data: np.ndarray, results: Optional[EstimationResult] = None, save_path: Optional[str] = None) -> None`

Plots the Higuchi scaling relationship.

**Parameters:**
- `data`: Input time series data
- `results`: Optional estimation results
- `save_path`: Optional path to save the plot

## Example Usage

```python
import numpy as np
from analysis.temporal.higuchi.higuchi_estimator import HiguchiEstimator

# Create estimator
estimator = HiguchiEstimator(
    min_k=2,
    max_k=20,
    confidence_level=0.95
)

# Generate sample data
data = np.random.randn(1000)

# Estimate Hurst parameter
results = estimator.estimate(data)
print(f"Hurst parameter: {results.hurst_parameter:.3f}")
print(f"Fractal dimension: {results.fractal_dimension:.3f}")

# Plot results
estimator.plot_scaling(data, results)
```

## Performance Characteristics

- **Time Complexity**: O(n × max_k)
- **Space Complexity**: O(max_k)
- **Accuracy**: Good for fractal processes
- **Robustness**: Moderately robust to noise

## Advantages

1. **Fractal Dimension**: Directly estimates fractal dimension
2. **Simplicity**: Simple and computationally efficient
3. **Non-parametric**: No assumptions about underlying process
4. **Curve Length**: Based on intuitive curve length concept

## Limitations

1. **Step Size Sensitivity**: Sensitive to step size range selection
2. **Short Series**: May not work well with very short time series
3. **Noise Sensitivity**: Can be affected by high-frequency noise
4. **Linear Assumption**: Assumes linear relationship in log-log plot

## References

1. Higuchi, T. (1988). Approach to an irregular time series on the basis of the fractal theory.
2. Higuchi, T. (1990). Relationship between the fractal dimension and the power law index for a time series.
3. Spasic, S., et al. (2005). Fractal analysis of rat brain activity after injury.

## Related Estimators

- [DFA Estimator](dfa.md)
- [R/S Estimator](rs.md)
- [DMA Estimator](dma.md)
