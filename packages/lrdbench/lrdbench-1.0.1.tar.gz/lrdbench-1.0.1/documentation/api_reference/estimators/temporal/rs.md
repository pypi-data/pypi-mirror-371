# R/S (Rescaled Range) Analysis Estimator

## Overview

The `RSEstimator` implements the classic Rescaled Range (R/S) analysis method for estimating the Hurst parameter of a time series. This method is one of the most widely used techniques for detecting long-range dependence in time series data.

## Mathematical Foundation

The R/S method is based on the relationship between the rescaled range statistic and the time window size. For a time series with long-range dependence, the expected value of the R/S statistic follows a power law:

```
E[R/S(n)] ~ n^H
```

where:
- `R` is the range of the cumulative deviations
- `S` is the standard deviation of the original series
- `n` is the window size
- `H` is the Hurst parameter

### Algorithm

1. **Window Division**: Divide the time series into non-overlapping windows of size `n`
2. **R/S Calculation**: For each window:
   - Calculate the mean: `μ = (1/n) * Σ(x_i)`
   - Compute deviations: `d_i = x_i - μ`
   - Calculate cumulative deviations: `D_i = Σ(d_j) for j=1 to i`
   - Find the range: `R = max(D_i) - min(D_i)`
   - Calculate standard deviation: `S = sqrt((1/(n-1)) * Σ(d_i²))`
   - Compute R/S statistic: `R/S = R / S`
3. **Averaging**: Average R/S values across all windows of the same size
4. **Power Law Fitting**: Fit the relationship `log(R/S) = H * log(n) + c` using linear regression

## Constructor

```python
RSEstimator(min_window_size=10, max_window_size=None, window_sizes=None, overlap=False)
```

### Parameters

- **min_window_size** (int, default=10): Minimum window size for R/S calculation
- **max_window_size** (int, optional): Maximum window size. If None, uses `n/4` where `n` is data length
- **window_sizes** (List[int], optional): Specific window sizes to use. If provided, overrides min/max settings
- **overlap** (bool, default=False): Whether to use overlapping windows (not currently implemented)

## Methods

### estimate(data)

Estimates the Hurst parameter using R/S analysis.

**Parameters:**
- `data` (np.ndarray): Input time series data

**Returns:**
- `Dict[str, Any]`: Dictionary containing:
  - `hurst_parameter`: Estimated Hurst parameter
  - `window_sizes`: List of window sizes used
  - `rs_values`: List of average R/S values for each window size
  - `r_squared`: R-squared value of the linear fit
  - `std_error`: Standard error of the Hurst parameter estimate
  - `confidence_interval`: 95% confidence interval for H
  - `p_value`: P-value of the linear regression
  - `intercept`: Intercept of the linear fit
  - `slope`: Slope of the linear fit (equals H)

### get_confidence_intervals(confidence_level=0.95)

Returns confidence intervals for the estimated parameters.

**Parameters:**
- `confidence_level` (float): Confidence level (default: 0.95)

**Returns:**
- `Dict[str, Tuple[float, float]]`: Confidence intervals

### get_estimation_quality()

Returns quality metrics for the estimation.

**Returns:**
- `Dict[str, Any]`: Quality metrics including R-squared, p-value, standard error, and number of windows

### plot_scaling(save_path=None)

Plots the R/S scaling relationship.

**Parameters:**
- `save_path` (str, optional): Path to save the plot

## Usage Examples

### Basic Usage

```python
import numpy as np
from analysis.temporal.rs import RSEstimator

# Generate sample data (fBm-like)
np.random.seed(42)
data = np.cumsum(np.random.normal(0, 1, 1000))

# Create estimator
estimator = RSEstimator()

# Estimate Hurst parameter
results = estimator.estimate(data)

print(f"Hurst parameter: {results['hurst_parameter']:.3f}")
print(f"R-squared: {results['r_squared']:.3f}")
print(f"Confidence interval: {results['confidence_interval']}")
```

### Custom Window Sizes

```python
# Use specific window sizes
window_sizes = [10, 20, 40, 80, 160]
estimator = RSEstimator(window_sizes=window_sizes)

results = estimator.estimate(data)
print(f"Window sizes used: {results['window_sizes']}")
```

### Quality Assessment

```python
# Get quality metrics
quality = estimator.get_estimation_quality()
print(f"R-squared: {quality['r_squared']:.3f}")
print(f"P-value: {quality['p_value']:.3e}")
print(f"Standard error: {quality['std_error']:.3f}")
print(f"Number of windows: {quality['n_windows']}")
```

### Visualization

```python
# Plot the scaling relationship
estimator.plot_scaling(save_path="rs_scaling.png")
```

## Parameter Selection Guidelines

### Window Size Selection

- **Minimum window size**: Should be at least 4, typically 10-20 for reliable estimation
- **Maximum window size**: Should not exceed `n/4` to ensure sufficient windows
- **Number of windows**: Aim for at least 3-5 different window sizes
- **Window size progression**: Geometric progression (e.g., 10, 20, 40, 80) works well

### Data Requirements

- **Minimum length**: At least 20 data points (preferably 100+)
- **Stationarity**: Method assumes stationary increments
- **No trends**: Remove trends before analysis for better results

## Performance Considerations

### Computational Complexity

- **Time complexity**: O(n * k) where n is data length and k is number of window sizes
- **Space complexity**: O(n) for storing cumulative deviations
- **Memory usage**: Moderate, scales linearly with data size

### Optimization Tips

- Use geometric progression for window sizes to reduce computation
- For very long series, consider subsampling or using larger minimum window sizes
- The method is embarrassingly parallel for different window sizes

## Validation and Limitations

### Validation

The estimator includes several validation checks:
- Parameter validation (window sizes, data length)
- Statistical validation (R-squared, p-value)
- Confidence interval calculation

### Limitations

1. **Sensitivity to trends**: The method is sensitive to non-stationary trends
2. **Finite sample effects**: Results may be biased for short series
3. **Window size dependence**: Results can vary with window size selection
4. **Assumption of normality**: Assumes Gaussian increments (though robust to violations)

### Comparison with Other Methods

- **vs DFA**: R/S is more sensitive to trends but computationally simpler
- **vs Spectral methods**: R/S works well with non-stationary data
- **vs Wavelet methods**: R/S is less computationally intensive but less robust

## References

1. Hurst, H. E. (1951). Long-term storage capacity of reservoirs. *Transactions of the American Society of Civil Engineers*, 116, 770-808.

2. Mandelbrot, B. B., & Wallis, J. R. (1969). Robustness of the rescaled range R/S in the measurement of noncyclic long run statistical dependence. *Water Resources Research*, 5(5), 967-988.

3. Peters, E. E. (1994). *Fractal market analysis: applying chaos theory to investment and economics*. John Wiley & Sons.

4. Beran, J. (1994). *Statistics for long-memory processes*. Chapman & Hall/CRC.

## Implementation Notes

The implementation follows the standard R/S methodology with several enhancements:

- **Robust window size selection**: Automatic generation of appropriate window sizes
- **Statistical validation**: Comprehensive quality metrics and confidence intervals
- **Visualization**: Built-in plotting capabilities for result interpretation
- **Error handling**: Robust error checking for edge cases

The estimator is designed to be both user-friendly for basic applications and flexible enough for advanced research use cases.
