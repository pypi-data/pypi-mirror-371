# DMA (Detrended Moving Average) Estimator

## Overview

The `DMAEstimator` implements the Detrended Moving Average (DMA) method for estimating the Hurst parameter of time series data. DMA is a variant of Detrended Fluctuation Analysis (DFA) that uses a moving average instead of polynomial fitting for detrending, making it computationally efficient and robust to various types of non-stationarity.

## Mathematical Foundation

The DMA method is based on the scaling behavior of the fluctuation function. For a time series with long-range dependence, the fluctuation function follows a power law:

\[ F(n) \sim n^H \]

where:
- \( F(n) \) is the fluctuation function at window size \( n \)
- \( H \) is the Hurst parameter
- \( n \) is the window size

The DMA algorithm works as follows:

1. **Cumulative Sum**: Compute the cumulative sum of the detrended time series:
   \[ Y(i) = \sum_{k=1}^{i} (x_k - \bar{x}) \]

2. **Moving Average**: For each window size \( n \), calculate the moving average:
   \[ \tilde{Y}_n(i) = \frac{1}{n} \sum_{j=i-n/2}^{i+n/2} Y(j) \]

3. **Detrending**: Subtract the moving average from the cumulative sum:
   \[ \epsilon_n(i) = Y(i) - \tilde{Y}_n(i) \]

4. **Fluctuation Function**: Calculate the root mean square of the detrended series:
   \[ F(n) = \sqrt{\frac{1}{N} \sum_{i=1}^{N} \epsilon_n^2(i)} \]

5. **Scaling Analysis**: Fit a power law relationship:
   \[ \log(F(n)) = H \log(n) + c \]

The Hurst parameter \( H \) is estimated as the slope of the linear regression.

## Constructor

```python
DMAEstimator(
    min_window_size: int = 4,
    max_window_size: int = None,
    window_sizes: List[int] = None,
    overlap: bool = True
)
```

### Parameters

- **min_window_size** (int, default=4): Minimum window size for DMA calculation. Must be at least 3.
- **max_window_size** (int, optional): Maximum window size. If None, uses n/4 where n is data length.
- **window_sizes** (List[int], optional): Specific window sizes to use. If provided, overrides min/max.
- **overlap** (bool, default=True): Whether to use overlapping windows for moving average calculation.

## Methods

### estimate(data: np.ndarray) -> Dict[str, Any]

Estimates the Hurst parameter using the DMA method.

#### Parameters

- **data** (np.ndarray): Input time series data. Must have length at least 10.

#### Returns

Dictionary containing estimation results:
- `hurst_parameter` (float): Estimated Hurst parameter
- `window_sizes` (List[int]): List of window sizes used
- `fluctuation_values` (List[float]): List of fluctuation values for each window size
- `r_squared` (float): R-squared value of the linear fit
- `std_error` (float): Standard error of the Hurst parameter estimate
- `confidence_interval` (Tuple[float, float]): 95% confidence interval for H
- `p_value` (float): P-value of the linear regression
- `intercept` (float): Intercept of the linear fit
- `slope` (float): Slope of the linear fit (equal to H)

### get_confidence_intervals(confidence_level: float = 0.95) -> Dict[str, Tuple[float, float]]

Calculates confidence intervals for the estimated parameters.

#### Parameters

- **confidence_level** (float, default=0.95): Confidence level for the intervals.

#### Returns

Dictionary containing confidence intervals:
- `hurst_parameter` (Tuple[float, float]): Confidence interval for H

### get_estimation_quality() -> Dict[str, Any]

Returns quality metrics for the estimation.

#### Returns

Dictionary containing quality metrics:
- `r_squared` (float): R-squared value of the linear fit
- `p_value` (float): P-value of the linear regression
- `std_error` (float): Standard error of the Hurst parameter estimate
- `n_windows` (int): Number of window sizes used

### plot_scaling(save_path: str = None) -> None

Plots the DMA scaling relationship.

#### Parameters

- **save_path** (str, optional): Path to save the plot. If None, displays the plot.

## Usage Examples

### Basic Usage

```python
import numpy as np
from analysis.temporal.dma.dma_estimator import DMAEstimator

# Generate test data (fBm-like)
np.random.seed(42)
data = np.cumsum(np.random.normal(0, 1, 1000))

# Create estimator
estimator = DMAEstimator(min_window_size=4, max_window_size=100)

# Estimate Hurst parameter
results = estimator.estimate(data)

print(f"Hurst parameter: {results['hurst_parameter']:.3f}")
print(f"R-squared: {results['r_squared']:.3f}")
print(f"Confidence interval: {results['confidence_interval']}")
```

### Custom Window Sizes

```python
# Use specific window sizes
window_sizes = [4, 8, 16, 32, 64, 128]
estimator = DMAEstimator(window_sizes=window_sizes)

results = estimator.estimate(data)
print(f"Window sizes used: {results['window_sizes']}")
```

### Different Overlap Settings

```python
# Compare overlapping vs non-overlapping windows
estimator_overlap = DMAEstimator(overlap=True)
estimator_no_overlap = DMAEstimator(overlap=False)

results_overlap = estimator_overlap.estimate(data)
results_no_overlap = estimator_no_overlap.estimate(data)

print(f"H (overlap): {results_overlap['hurst_parameter']:.3f}")
print(f"H (no overlap): {results_no_overlap['hurst_parameter']:.3f}")
```

### Quality Assessment

```python
# Get quality metrics
quality = estimator.get_estimation_quality()
print(f"R-squared: {quality['r_squared']:.3f}")
print(f"P-value: {quality['p_value']:.3e}")
print(f"Standard error: {quality['std_error']:.3f}")
print(f"Number of windows: {quality['n_windows']}")

# Get confidence intervals
ci = estimator.get_confidence_intervals(confidence_level=0.90)
print(f"90% CI for H: {ci['hurst_parameter']}")
```

### Visualization

```python
# Plot the scaling relationship
estimator.plot_scaling()

# Save the plot
estimator.plot_scaling(save_path="dma_scaling.png")
```

## Parameter Selection Guidelines

### Window Size Selection

- **Minimum window size**: Should be at least 3, typically 4-10
- **Maximum window size**: Should not exceed n/4 to ensure sufficient data points
- **Number of windows**: At least 3-5 windows for reliable estimation
- **Window spacing**: Geometric progression (e.g., powers of 2) is often effective

### Overlap Parameter

- **overlap=True** (default): Uses overlapping windows, more computationally intensive but potentially more accurate
- **overlap=False**: Uses non-overlapping windows, faster computation but may be less accurate

### Data Requirements

- **Minimum length**: At least 10 data points
- **Recommended length**: 1000+ data points for reliable estimation
- **Data type**: Should be stationary or detrended before analysis

## Performance Considerations

### Computational Complexity

- **Time complexity**: O(n × m) where n is data length and m is number of window sizes
- **Space complexity**: O(n) for storing cumulative sums and moving averages
- **Overlap impact**: Using overlap=True increases computation time by approximately 2-3x

### Memory Usage

- **Cumulative sum**: Requires O(n) additional memory
- **Moving averages**: Requires O(n) additional memory
- **Total memory**: Approximately 3n additional memory usage

## Validation and Limitations

### Validation

The estimator includes several validation checks:
- Parameter validation (window sizes, data length)
- Numerical stability checks
- Quality metrics (R-squared, p-value)

### Limitations

1. **Assumes power law scaling**: May not work well for data with complex scaling behavior
2. **Window size sensitivity**: Results can be sensitive to window size selection
3. **Non-stationarity**: While robust to some non-stationarity, may fail with strong trends
4. **Finite size effects**: Limited accuracy for very short time series

### Comparison with Other Methods

- **vs DFA**: DMA is computationally faster but may be less accurate for polynomial trends
- **vs R/S**: DMA is more robust to non-stationarity
- **vs Higuchi**: DMA provides direct Hurst parameter estimation

## References

1. Gu, G. F., & Zhou, W. X. (2010). Detrended moving average algorithm for multifractals. Physical Review E, 82(1), 011136.

2. Alessio, E., Carbone, A., Castelli, G., & Frappietro, V. (2002). Second-order moving average and scaling of stochastic time series. The European Physical Journal B-Condensed Matter and Complex Systems, 27(2), 197-200.

3. Carbone, A., Castelli, G., & Stanley, H. E. (2004). Time-dependent Hurst exponent in financial time series. Physica A: Statistical Mechanics and its Applications, 344(1-2), 267-271.

## Implementation Notes

### Algorithm Details

The implementation uses two approaches for moving average calculation:

1. **Overlapping windows**: For each point, calculate the average of surrounding points within the window
2. **Non-overlapping windows**: Divide the data into non-overlapping segments and calculate averages

### Numerical Stability

- Uses log-log regression for better numerical stability
- Includes checks for zero or negative fluctuation values
- Handles edge cases in moving average calculation

### Error Handling

- Validates input parameters before processing
- Provides informative error messages for invalid inputs
- Gracefully handles numerical issues during computation
