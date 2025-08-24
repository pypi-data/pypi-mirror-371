# DFAEstimator

## Class Definition

```python
class DFAEstimator(BaseEstimator):
    """
    Detrended Fluctuation Analysis (DFA) estimator.
    
    Estimates the Hurst parameter H using the DFA method, which is
    robust to non-stationarities and trends in the data.
    """
```

## Constructor

```python
def __init__(self, min_box_size: int = 8, max_box_size: int = 200, 
             box_sizes: Optional[List[int]] = None, overlap: bool = True,
             polynomial_order: int = 1, remove_mean: bool = True):
    """
    Initialize DFA estimator.
    
    Parameters
    ----------
    min_box_size : int, default=8
        Minimum box size for analysis
    max_box_size : int, default=200
        Maximum box size for analysis
    box_sizes : List[int], optional
        Custom list of box sizes (overrides min/max)
    overlap : bool, default=True
        Whether to use overlapping boxes
    polynomial_order : int, default=1
        Order of polynomial for detrending (1=linear, 2=quadratic, etc.)
    remove_mean : bool, default=True
        Whether to remove mean from data
        
    Raises
    ------
    ValueError
        If box sizes are invalid or polynomial order is negative
    """
```

## Methods

### estimate

```python
def estimate(self, data: np.ndarray) -> Dict[str, Any]:
    """
    Estimate Hurst parameter using DFA.
    
    Parameters
    ----------
    data : np.ndarray
        Time series data of shape (n,)
        
    Returns
    -------
    Dict[str, Any]
        Dictionary containing:
        - hurst_parameter: float - Estimated Hurst parameter
        - r_squared: float - R-squared of linear fit
        - intercept: float - Intercept of linear fit
        - slope: float - Slope of linear fit
        - box_sizes: np.ndarray - Box sizes used
        - fluctuations: np.ndarray - Fluctuation values
        - residuals: np.ndarray - Residuals from linear fit
        - estimation_quality: str - Quality assessment
        
    Raises
    ------
    ValueError
        If data is too short or invalid
    """
```

### get_confidence_intervals

```python
def get_confidence_intervals(self, confidence_level: float = 0.95, 
                           n_bootstrap: int = 1000) -> Dict[str, Tuple[float, float]]:
    """
    Get confidence intervals for estimated parameters.
    
    Parameters
    ----------
    confidence_level : float, default=0.95
        Confidence level (0 < level < 1)
    n_bootstrap : int, default=1000
        Number of bootstrap samples
        
    Returns
    -------
    Dict[str, Tuple[float, float]]
        Dictionary containing confidence intervals:
        - hurst_parameter: (lower, upper) - CI for Hurst parameter
        - slope: (lower, upper) - CI for slope
        - intercept: (lower, upper) - CI for intercept
        
    Raises
    ------
    ValueError
        If confidence level is invalid or no estimation results available
    """
```

### get_estimation_quality

```python
def get_estimation_quality(self) -> Dict[str, Any]:
    """
    Get quality metrics for the estimation.
    
    Returns
    -------
    Dict[str, Any]
        Dictionary containing quality metrics:
        - r_squared: float - R-squared of linear fit
        - mse: float - Mean squared error
        - mae: float - Mean absolute error
        - quality_score: float - Overall quality score (0-1)
        - quality_level: str - Quality assessment ('excellent', 'good', 'fair', 'poor')
        
    Raises
    ------
    ValueError
        If no estimation results available
    """
```

### plot_scaling

```python
def plot_scaling(self, figsize: Tuple[int, int] = (10, 6), 
                save_path: Optional[str] = None, show: bool = True) -> None:
    """
    Plot the scaling relationship (log-log plot).
    
    Parameters
    ----------
    figsize : Tuple[int, int], default=(10, 6)
        Figure size (width, height)
    save_path : str, optional
        Path to save the plot
    show : bool, default=True
        Whether to display the plot
        
    Raises
    ------
    ValueError
        If no estimation results available
    """
```

### set_parameters

```python
def set_parameters(self, **kwargs) -> None:
    """
    Set estimator parameters.
    
    Parameters
    ----------
    **kwargs : dict
        Parameters to set (min_box_size, max_box_size, box_sizes, 
                         overlap, polynomial_order, remove_mean)
        
    Raises
    ------
    ValueError
        If parameters are invalid
    """
```

### validate_parameters

```python
def validate_parameters(self) -> None:
    """
    Validate estimator parameters.
    
    Raises
    ------
    ValueError
        If parameters are invalid
    """
```

### get_parameters

```python
def get_parameters(self) -> Dict[str, Any]:
    """
    Get current estimator parameters.
    
    Returns
    -------
    Dict[str, Any]
        Dictionary containing current parameters
    """
```

### __str__

```python
def __str__(self) -> str:
    """
    String representation of the estimator.
    
    Returns
    -------
    str
        String representation
    """
```

### __repr__

```python
def __repr__(self) -> str:
    """
    Detailed string representation of the estimator.
    
    Returns
    -------
    str
        Detailed string representation
    """
```

## Properties

### min_box_size

```python
@property
def min_box_size(self) -> int:
    """
    Get minimum box size.
    
    Returns
    -------
    int
        Minimum box size
    """
```

### max_box_size

```python
@property
def max_box_size(self) -> int:
    """
    Get maximum box size.
    
    Returns
    -------
    int
        Maximum box size
    """
```

### box_sizes

```python
@property
def box_sizes(self) -> List[int]:
    """
    Get box sizes used for analysis.
    
    Returns
    -------
    List[int]
        List of box sizes
    """
```

### overlap

```python
@property
def overlap(self) -> bool:
    """
    Get overlap setting.
    
    Returns
    -------
    bool
        Whether overlapping boxes are used
    """
```

### polynomial_order

```python
@property
def polynomial_order(self) -> int:
    """
    Get polynomial order for detrending.
    
    Returns
    -------
    int
        Polynomial order
    """
```

### remove_mean

```python
@property
def remove_mean(self) -> bool:
    """
    Get mean removal setting.
    
    Returns
    -------
    bool
        Whether mean is removed from data
    """
```

### estimator_name

```python
@property
def estimator_name(self) -> str:
    """
    Get estimator name.
    
    Returns
    -------
    str
        Estimator name: "DFA"
    """
```

### description

```python
@property
def description(self) -> str:
    """
    Get estimator description.
    
    Returns
    -------
    str
        Estimator description
    """
```

## Usage Examples

### Basic Usage

```python
from analysis.temporal.dfa.dfa_estimator import DFAEstimator
import numpy as np

# Create DFA estimator
dfa = DFAEstimator(min_box_size=8, max_box_size=200)

# Generate test data (fBm with H=0.7)
from models.data_models.fbm.fbm_model import FractionalBrownianMotion
fbm = FractionalBrownianMotion(H=0.7)
data = fbm.generate(1000, seed=42)

# Estimate Hurst parameter
results = dfa.estimate(data)

print(f"Estimated H: {results['hurst_parameter']:.3f}")
print(f"R-squared: {results['r_squared']:.3f}")
print(f"Quality: {results['estimation_quality']}")
```

### Custom Parameters

```python
# Custom box sizes
box_sizes = [8, 16, 32, 64, 128, 256]
dfa = DFAEstimator(box_sizes=box_sizes, polynomial_order=2)

# Quadratic detrending
dfa_quad = DFAEstimator(polynomial_order=2)

# No overlap
dfa_no_overlap = DFAEstimator(overlap=False)

# Don't remove mean
dfa_no_mean = DFAEstimator(remove_mean=False)
```

### Confidence Intervals

```python
# Get confidence intervals
ci = dfa.get_confidence_intervals(confidence_level=0.95, n_bootstrap=1000)

print(f"95% CI for H: [{ci['hurst_parameter'][0]:.3f}, {ci['hurst_parameter'][1]:.3f}]")
print(f"95% CI for slope: [{ci['slope'][0]:.3f}, {ci['slope'][1]:.3f}]")
```

### Quality Assessment

```python
# Get quality metrics
quality = dfa.get_estimation_quality()

print(f"R-squared: {quality['r_squared']:.3f}")
print(f"MSE: {quality['mse']:.6f}")
print(f"Quality score: {quality['quality_score']:.3f}")
print(f"Quality level: {quality['quality_level']}")
```

### Visualization

```python
# Plot scaling relationship
dfa.plot_scaling(figsize=(12, 8), save_path='dfa_scaling.png')

# Plot without saving
dfa.plot_scaling(show=True, save_path=None)
```

### Parameter Updates

```python
# Update parameters
dfa.set_parameters(min_box_size=16, max_box_size=500, polynomial_order=2)

# Get current parameters
params = dfa.get_parameters()
print(f"Current parameters: {params}")
```

## Algorithm Details

### DFA Algorithm

1. **Integration**: Convert time series to cumulative sum
2. **Segmentation**: Divide into non-overlapping or overlapping segments
3. **Detrending**: Fit polynomial to each segment and remove trend
4. **Fluctuation Calculation**: Calculate RMS fluctuation for each box size
5. **Scaling Analysis**: Fit linear model to log(fluctuation) vs log(box_size)
6. **Hurst Estimation**: H = slope of linear fit

### Mathematical Formulation

For a time series x(t), the DFA algorithm computes:

1. **Integrated series**: y(t) = Σᵢ₌₁ᵗ x(i)
2. **Segments**: Divide y(t) into Nₛ segments of length s
3. **Detrending**: Fit polynomial pᵥ(t) to each segment ν
4. **Fluctuation**: F²(s) = (1/Nₛ) Σᵥ₌₁ᴺˢ (1/s) Σᵢ₌₁ˢ [yᵥ(i) - pᵥ(i)]²
5. **Scaling**: F(s) ∝ sᴴ

### Quality Assessment

The estimator provides several quality metrics:

- **R-squared**: Goodness of linear fit (0-1)
- **MSE**: Mean squared error of residuals
- **MAE**: Mean absolute error of residuals
- **Quality Score**: Overall assessment (0-1)
- **Quality Level**: Categorical assessment

## Performance Considerations

### Computational Complexity
- **Time**: O(n log n) for FFT-based operations
- **Space**: O(n) for storing integrated series and fluctuations

### Memory Usage
- **Integrated series**: O(n)
- **Fluctuation values**: O(log n)
- **Bootstrap samples**: O(n_bootstrap × log n)

### Optimization Tips
- Use appropriate box sizes for data length
- Consider polynomial order based on expected trends
- Use bootstrap for confidence intervals only when needed
- Enable overlap for better statistical power

## Error Handling

The DFAEstimator class includes comprehensive error handling:

- **Parameter Validation**: Box sizes must be positive and ordered
- **Data Validation**: Data must be numeric and non-empty
- **Length Requirements**: Data must be long enough for analysis
- **Bootstrap Validation**: Bootstrap parameters must be valid
- **Informative Errors**: Clear error messages for debugging

## References

1. Peng, C. K., et al. (1994). Mosaic organization of DNA nucleotides.
2. Kantelhardt, J. W., et al. (2001). Detecting long-range correlations with detrended fluctuation analysis.
3. Hu, K., et al. (2001). Effect of trends on detrended fluctuation analysis.
4. Bryce, R. M., & Sprague, K. B. (2012). Revisiting detrended fluctuation analysis.
