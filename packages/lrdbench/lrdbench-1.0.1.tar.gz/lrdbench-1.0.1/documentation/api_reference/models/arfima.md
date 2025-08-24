# Autoregressive Fractionally Integrated Moving Average (ARFIMA)

**Class**: `models.data_models.arfima.arfima_model.ARFIMAModel`

## Overview

The Autoregressive Fractionally Integrated Moving Average (ARFIMA) model is a generalization of the ARIMA model that allows for fractional differencing. It combines autoregressive (AR), fractionally integrated (FI), and moving average (MA) components to model time series with long-range dependence.

## Mathematical Foundation

The ARFIMA(p,d,q) process is defined by:

```
(1 - L)^d Φ(L)(X_t - μ) = Θ(L)ε_t
```

where:
- `L` is the lag operator: `LX_t = X_{t-1}`
- `d` is the fractional integration parameter (-0.5 < d < 0.5)
- `Φ(L) = 1 - φ₁L - φ₂L² - ... - φₚLᵖ` is the AR polynomial
- `Θ(L) = 1 + θ₁L + θ₂L² + ... + θ_qL^q` is the MA polynomial
- `ε_t` are i.i.d. innovations with variance σ²

The fractional differencing operator `(1-L)^d` is defined as:

```
(1-L)^d = 1 - dL - d(d-1)/2! L² - d(d-1)(d-2)/3! L³ - ...
```

## Constructor

```python
ARFIMAModel(d: float, ar_params: Optional[List[float]] = None, 
           ma_params: Optional[List[float]] = None, sigma: float = 1.0,
           method: str = 'simulation')
```

### Parameters

- **d**: Fractional integration parameter (-0.5 < d < 0.5)
  - d = 0: No fractional integration (ARMA process)
  - d > 0: Long-range dependence
  - d < 0: Anti-persistence

- **ar_params**: List of autoregressive parameters
  - Must satisfy stationarity conditions
  - Default: [] (no AR component)

- **ma_params**: List of moving average parameters
  - Must satisfy invertibility conditions
  - Default: [] (no MA component)

- **sigma**: Standard deviation of innovations (default: 1.0)

- **method**: Generation method
  - 'simulation': Time domain simulation (default)
  - 'spectral': Frequency domain generation

## Methods

### `generate(n: int, seed: Optional[int] = None) -> np.ndarray`

Generate an ARFIMA time series.

**Parameters:**
- `n`: Length of the time series
- `seed`: Random seed for reproducibility

**Returns:**
- `np.ndarray`: Generated ARFIMA time series

### `get_theoretical_properties() -> Dict[str, Any]`

Get theoretical properties of the ARFIMA process.

**Returns:**
- Dictionary containing:
  - `fractional_integration`: d
  - `ar_order`: Order of AR component
  - `ma_order`: Order of MA component
  - `innovation_variance`: σ²
  - `long_range_dependence`: d > 0
  - `stationary`: True
  - `invertible`: True
  - `autocorrelation_decay`: 'power_law' if d > 0, 'exponential' otherwise

### `get_increments(arfima: np.ndarray) -> np.ndarray`

Get the increments of the ARFIMA process.

**Parameters:**
- `arfima`: ARFIMA time series

**Returns:**
- `np.ndarray`: Increments (differences)

## Generation Methods

### Simulation Method

1. Generate white noise innovations
2. Apply MA filter (if MA parameters provided)
3. Apply fractional differencing operator `(1-L)^d`
4. Apply AR filter (if AR parameters provided)

### Spectral Method

1. Compute spectral density of ARFIMA process
2. Generate complex Gaussian noise
3. Apply spectral filter
4. Inverse FFT to get time series

## Usage Examples

### Basic Usage

```python
from models.data_models.arfima.arfima_model import ARFIMAModel

# Create ARFIMA(1,0.3,1) model
arfima = ARFIMAModel(d=0.3, ar_params=[0.5], ma_params=[0.3])

# Generate time series
data = arfima.generate(n=4096, seed=123)

# Get theoretical properties
props = arfima.get_theoretical_properties()
print(f"Fractional integration: {props['fractional_integration']}")
print(f"AR order: {props['ar_order']}")
print(f"MA order: {props['ma_order']}")
```

### Pure Fractional Integration

```python
# ARFIMA(0,d,0) - pure fractional integration
model = ARFIMAModel(d=0.3)
data = model.generate(n=1024, seed=42)
```

### Different Methods

```python
# Simulation method (default)
model1 = ARFIMAModel(d=0.3, ar_params=[0.5], method='simulation')
data1 = model1.generate(n=512, seed=123)

# Spectral method
model2 = ARFIMAModel(d=0.3, ar_params=[0.5], method='spectral')
data2 = model2.generate(n=512, seed=123)
```

### Parameter Analysis

```python
import numpy as np
import matplotlib.pyplot as plt

# Generate ARFIMA with different d values
d_values = [-0.3, 0.0, 0.3]
fig, axes = plt.subplots(3, 1, figsize=(12, 8))

for i, d in enumerate(d_values):
    model = ARFIMAModel(d=d, ar_params=[0.5], ma_params=[0.3])
    data = model.generate(n=512, seed=42)
    
    axes[i].plot(data)
    axes[i].set_title(f'ARFIMA(1,{d},1)')
    axes[i].grid(True)

plt.tight_layout()
plt.show()
```

## Theoretical Properties

### Long-Range Dependence

For d > 0, the autocorrelation function decays as:
```
ρ(k) ∝ k^(2d-1) for large k
```

### Spectral Density

The spectral density has the form:
```
f(ω) = σ² |1 - e^(-iω)|^(-2d) |Θ(e^(-iω))|² / |Φ(e^(-iω))|²
```

### Variance Scaling

The variance of partial sums scales as:
```
Var(∑ᵢ₌₁ⁿ Xᵢ) ∝ n^(1+2d) for large n
```

## Parameter Constraints

### Stationarity Conditions

AR parameters must satisfy:
```
|z| > 1 for all roots z of Φ(z) = 0
```

### Invertibility Conditions

MA parameters must satisfy:
```
|z| > 1 for all roots z of Θ(z) = 0
```

### Fractional Integration

The parameter d must satisfy:
```
-0.5 < d < 0.5
```

## Performance Considerations

- **Simulation method**: More accurate for small to medium sample sizes
- **Spectral method**: More efficient for large sample sizes
- **Memory usage**: O(n) for both methods
- **Time complexity**: O(n²) for simulation, O(n log n) for spectral

## Validation

The implementation includes comprehensive tests covering:
- Parameter validation (stationarity, invertibility)
- Reproducibility
- Theoretical properties
- Different generation methods
- Fractional differencing accuracy

## References

1. Granger, C. W., & Joyeux, R. (1980). An introduction to long-memory time series models and fractional differencing. Journal of time series analysis, 1(1), 15-29.
2. Hosking, J. R. (1981). Fractional differencing. Biometrika, 68(1), 165-176.
3. Sowell, F. (1992). Maximum likelihood estimation of stationary univariate fractionally integrated time series models. Journal of econometrics, 53(1-3), 165-188.
4. Beran, J. (1994). Statistics for long-memory processes. CRC press.
