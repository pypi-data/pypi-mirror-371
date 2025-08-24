# FractionalBrownianMotion

## Class Definition

```python
class FractionalBrownianMotion(BaseModel):
    """
    Fractional Brownian Motion (fBm) model.
    
    A self-similar Gaussian process with long-range dependence,
    characterized by the Hurst parameter H.
    """
```

## Constructor

```python
def __init__(self, H: float = 0.5, sigma: float = 1.0, method: str = 'auto'):
    """
    Initialize Fractional Brownian Motion model.
    
    Parameters
    ----------
    H : float, default=0.5
        Hurst parameter (0 < H < 1)
        - H = 0.5: Standard Brownian motion
        - H > 0.5: Persistent (long-range dependent)
        - H < 0.5: Anti-persistent
    sigma : float, default=1.0
        Scale parameter (standard deviation)
    method : str, default='auto'
        Generation method:
        - 'cholesky': Cholesky decomposition (O(n²), stable)
        - 'circulant': Circulant matrix embedding (O(n log n))
        - 'jax': JAX-optimized generation (GPU acceleration)
        - 'auto': Automatic method selection
        
    Raises
    ------
    ValueError
        If H is not in (0, 1) or sigma is not positive
    """
```

## Methods

### generate

```python
def generate(self, n: int, seed: Optional[int] = None) -> np.ndarray:
    """
    Generate fractional Brownian motion time series.
    
    Parameters
    ----------
    n : int
        Number of samples to generate
    seed : int, optional
        Random seed for reproducibility
        
    Returns
    -------
    np.ndarray
        fBm time series of shape (n,)
        
    Raises
    ------
    ValueError
        If n is not positive
    """
```

### get_parameters

```python
def get_parameters(self) -> Dict[str, Any]:
    """
    Get model parameters.
    
    Returns
    -------
    Dict[str, Any]
        Dictionary containing:
        - H: float - Hurst parameter
        - sigma: float - Scale parameter
        - method: str - Generation method
    """
```

### get_theoretical_properties

```python
def get_theoretical_properties(self) -> Dict[str, Any]:
    """
    Get theoretical properties of fBm.
    
    Returns
    -------
    Dict[str, Any]
        Dictionary containing:
        - variance: float - Variance at time t=1
        - autocorrelation: function - Theoretical autocorrelation
        - spectral_density: function - Power spectral density
        - self_similarity: bool - Self-similarity property
        - long_range_dependence: bool - Long-range dependence
    """
```

### set_parameters

```python
def set_parameters(self, **kwargs) -> None:
    """
    Set model parameters.
    
    Parameters
    ----------
    **kwargs : dict
        Parameters to set (H, sigma, method)
        
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
    Validate model parameters.
    
    Raises
    ------
    ValueError
        If H is not in (0, 1) or sigma is not positive
    """
```

### get_increments

```python
def get_increments(self, data: np.ndarray) -> np.ndarray:
    """
    Get increments of the fBm process.
    
    Parameters
    ----------
    data : np.ndarray
        fBm time series
        
    Returns
    -------
    np.ndarray
        Increments (differences) of shape (n-1,)
    """
```

### get_cumulative_variance

```python
def get_cumulative_variance(self, t: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """
    Get cumulative variance at time t.
    
    Parameters
    ----------
    t : float or np.ndarray
        Time point(s)
        
    Returns
    -------
    float or np.ndarray
        Cumulative variance at time t
    """
```

### get_autocorrelation

```python
def get_autocorrelation(self, lag: Union[int, np.ndarray]) -> Union[float, np.ndarray]:
    """
    Get theoretical autocorrelation function.
    
    Parameters
    ----------
    lag : int or np.ndarray
        Lag(s) for autocorrelation
        
    Returns
    -------
    float or np.ndarray
        Autocorrelation values
    """
```

### get_spectral_density

```python
def get_spectral_density(self, frequency: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """
    Get theoretical power spectral density.
    
    Parameters
    ----------
    frequency : float or np.ndarray
        Frequency(ies)
        
    Returns
    -------
    float or np.ndarray
        Power spectral density values
    """
```

### __str__

```python
def __str__(self) -> str:
    """
    String representation of the model.
    
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
    Detailed string representation of the model.
    
    Returns
    -------
    str
        Detailed string representation
    """
```

## Properties

### H

```python
@property
def H(self) -> float:
    """
    Get Hurst parameter.
    
    Returns
    -------
    float
        Hurst parameter
    """
```

### sigma

```python
@property
def sigma(self) -> float:
    """
    Get scale parameter.
    
    Returns
    -------
    float
        Scale parameter
    """
```

### method

```python
@property
def method(self) -> str:
    """
    Get generation method.
    
    Returns
    -------
    str
        Generation method
    """
```

### model_name

```python
@property
def model_name(self) -> str:
    """
    Get model name.
    
    Returns
    -------
    str
        Model name: "FractionalBrownianMotion"
    """
```

### description

```python
@property
def description(self) -> str:
    """
    Get model description.
    
    Returns
    -------
    str
        Model description
    """
```

## Usage Examples

### Basic Usage

```python
from models.data_models.fbm.fbm_model import FractionalBrownianMotion
import numpy as np

# Create fBm model
fbm = FractionalBrownianMotion(H=0.7, sigma=1.0)

# Generate time series
data = fbm.generate(n=1000, seed=42)

# Get parameters
params = fbm.get_parameters()
print(f"H: {params['H']}, sigma: {params['sigma']}")

# Get theoretical properties
properties = fbm.get_theoretical_properties()
print(f"Variance: {properties['variance']}")
```

### Different Hurst Parameters

```python
# Persistent fBm (H > 0.5)
fbm_persistent = FractionalBrownianMotion(H=0.8)
data_persistent = fbm_persistent.generate(1000, seed=42)

# Anti-persistent fBm (H < 0.5)
fbm_anti = FractionalBrownianMotion(H=0.3)
data_anti = fbm_anti.generate(1000, seed=42)

# Standard Brownian motion (H = 0.5)
fbm_standard = FractionalBrownianMotion(H=0.5)
data_standard = fbm_standard.generate(1000, seed=42)
```

### Different Generation Methods

```python
# Cholesky method (stable, slower)
fbm_chol = FractionalBrownianMotion(H=0.7, method='cholesky')
data_chol = fbm_chol.generate(1000, seed=42)

# Circulant method (faster, large n)
fbm_circ = FractionalBrownianMotion(H=0.7, method='circulant')
data_circ = fbm_circ.generate(10000, seed=42)

# JAX method (GPU acceleration)
fbm_jax = FractionalBrownianMotion(H=0.7, method='jax')
data_jax = fbm_jax.generate(1000, seed=42)
```

### Theoretical Properties

```python
# Get autocorrelation
lags = np.arange(1, 11)
autocorr = fbm.get_autocorrelation(lags)

# Get spectral density
freqs = np.linspace(0.01, 0.5, 100)
psd = fbm.get_spectral_density(freqs)

# Get cumulative variance
times = np.linspace(0, 10, 100)
variance = fbm.get_cumulative_variance(times)
```

### Parameter Updates

```python
# Update parameters
fbm.set_parameters(H=0.6, sigma=2.0)

# Validate parameters
try:
    fbm.set_parameters(H=1.5)  # Invalid H
except ValueError as e:
    print(f"Error: {e}")
```

## Mathematical Properties

### Self-Similarity
For any a > 0, the process satisfies:
```
B_H(at) = a^H B_H(t)
```

### Variance
The variance at time t is:
```
Var[B_H(t)] = σ² t^(2H)
```

### Autocorrelation
For s < t, the autocorrelation is:
```
E[B_H(s)B_H(t)] = (σ²/2) [s^(2H) + t^(2H) - |t-s|^(2H)]
```

### Spectral Density
The power spectral density is:
```
S(f) ∝ |f|^(-2H-1)
```

## Performance Considerations

### Method Selection
- **Cholesky**: Best for small n (< 1000), numerically stable
- **Circulant**: Best for large n (> 1000), O(n log n) complexity
- **JAX**: Best for GPU environments, parallel processing
- **Auto**: Automatically selects best method based on n

### Memory Usage
- **Cholesky**: O(n²) memory
- **Circulant**: O(n) memory
- **JAX**: O(n) memory, GPU memory if available

### Computational Complexity
- **Cholesky**: O(n³) time
- **Circulant**: O(n log n) time
- **JAX**: O(n log n) time, parallel execution

## Error Handling

The FractionalBrownianMotion class includes comprehensive error handling:

- **Parameter Validation**: H must be in (0, 1), sigma must be positive
- **Method Validation**: Method must be one of ['cholesky', 'circulant', 'jax', 'auto']
- **Input Validation**: n must be positive integer
- **Type Checking**: All parameters checked for correct types
- **Informative Errors**: Clear error messages for debugging

## References

1. Mandelbrot, B. B., & Van Ness, J. W. (1968). Fractional Brownian motions, fractional noises and applications.
2. Beran, J. (1994). Statistics for Long-Memory Processes.
3. Samorodnitsky, G., & Taqqu, M. S. (1994). Stable Non-Gaussian Random Processes.
