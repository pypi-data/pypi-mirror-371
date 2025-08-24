# Multifractal Random Walk (MRW)

**Class**: `models.data_models.mrw.mrw_model.MultifractalRandomWalk`

## Overview

The Multifractal Random Walk (MRW) is a multifractal process that exhibits scale-invariant properties and is characterized by a log-normal volatility cascade. It combines long-range dependence (through the Hurst parameter H) with multifractal scaling (through the intermittency parameter λ).

## Mathematical Foundation

The MRW process is defined as:

```
X(t) = ∫₀ᵗ σ(s) dB_H(s)
```

where:
- `B_H(s)` is fractional Brownian motion with Hurst parameter H
- `σ(s) = σ₀ exp(ω(s))` is the volatility process
- `ω(s)` is a log-normal volatility cascade with parameter λ

The volatility cascade follows:
```
ω(s) = ∑ᵢ ωᵢ(s)
```

where each `ωᵢ(s)` is Gaussian noise at scale `2⁻ⁱ`.

## Constructor

```python
MultifractalRandomWalk(H: float, lambda_param: float, sigma: float = 1.0, method: str = 'cascade')
```

### Parameters

- **H**: Hurst parameter (0 < H < 1)
  - H = 0.5: Standard random walk
  - H > 0.5: Persistent (long-range dependence)
  - H < 0.5: Anti-persistent

- **lambda_param**: Intermittency parameter (λ > 0)
  - Controls the strength of multifractal scaling
  - Larger values lead to more pronounced volatility clustering

- **sigma**: Base volatility (default: 1.0)
  - Standard deviation of the base process

- **method**: Generation method
  - 'cascade': Volatility cascade method (default)
  - 'direct': Direct generation method

## Methods

### `generate(n: int, seed: Optional[int] = None) -> np.ndarray`

Generate a multifractal random walk time series.

**Parameters:**
- `n`: Length of the time series
- `seed`: Random seed for reproducibility

**Returns:**
- `np.ndarray`: Generated MRW time series

### `get_theoretical_properties() -> Dict[str, Any]`

Get theoretical properties of the MRW process.

**Returns:**
- Dictionary containing:
  - `hurst_parameter`: H
  - `intermittency_parameter`: λ
  - `base_volatility`: σ₀
  - `multifractal`: True
  - `scale_invariant`: True
  - `long_range_dependence`: H > 0.5
  - `volatility_clustering`: True

### `get_increments(mrw: np.ndarray) -> np.ndarray`

Get the increments of the MRW process.

**Parameters:**
- `mrw`: MRW time series

**Returns:**
- `np.ndarray`: Increments (differences)

## Generation Methods

### Cascade Method

1. Generate log-normal volatility cascade `ω(s)`
2. Generate fractional Brownian motion `B_H(s)`
3. Combine: `X(t) = B_H(t) × exp(ω(t))`

### Direct Method

1. Generate volatility cascade `ω(s)`
2. Generate Gaussian noise `ε(t)`
3. Form increments: `ΔX(t) = ε(t) × exp(ω(t)) × σ₀`
4. Cumulate: `X(t) = ∑ᵢ₌₁ᵗ ΔX(i)`

## Usage Examples

### Basic Usage

```python
from models.data_models.mrw.mrw_model import MultifractalRandomWalk

# Create MRW model
mrw = MultifractalRandomWalk(H=0.7, lambda_param=0.3, sigma=1.0)

# Generate time series
data = mrw.generate(n=4096, seed=123)

# Get theoretical properties
props = mrw.get_theoretical_properties()
print(f"Hurst parameter: {props['hurst_parameter']}")
print(f"Intermittency: {props['intermittency_parameter']}")
```

### Different Methods

```python
# Cascade method (default)
mrw_cascade = MultifractalRandomWalk(H=0.7, lambda_param=0.3, method='cascade')
data1 = mrw_cascade.generate(n=1024, seed=42)

# Direct method
mrw_direct = MultifractalRandomWalk(H=0.7, lambda_param=0.3, method='direct')
data2 = mrw_direct.generate(n=1024, seed=42)
```

### Parameter Analysis

```python
import numpy as np
import matplotlib.pyplot as plt

# Generate MRW with different parameters
H_values = [0.3, 0.5, 0.7]
lambda_values = [0.1, 0.3, 0.5]

fig, axes = plt.subplots(3, 3, figsize=(12, 10))

for i, H in enumerate(H_values):
    for j, lambda_param in enumerate(lambda_values):
        mrw = MultifractalRandomWalk(H=H, lambda_param=lambda_param)
        data = mrw.generate(n=512, seed=42)
        
        axes[i, j].plot(data)
        axes[i, j].set_title(f'H={H}, λ={lambda_param}')
        axes[i, j].grid(True)

plt.tight_layout()
plt.show()
```

## Theoretical Properties

### Scaling Behavior

The MRW exhibits multifractal scaling:
```
E[|X(t+τ) - X(t)|^q] ∝ τ^ζ(q)
```

where `ζ(q)` is the multifractal spectrum:
```
ζ(q) = qH - λ²q(q-1)/2
```

### Long-Range Dependence

For H > 0.5, the process exhibits long-range dependence:
```
ρ(τ) ∝ τ^(2H-2) for large τ
```

### Volatility Clustering

The squared increments show clustering:
```
E[|ΔX(t)|²|ΔX(t-τ)|²] > E[|ΔX(t)|²]E[|ΔX(t-τ)|²]
```

## Performance Considerations

- **Cascade method**: More computationally intensive but theoretically sound
- **Direct method**: Faster but may not capture all multifractal properties
- **Memory usage**: O(n) for both methods
- **Time complexity**: O(n log n) for cascade, O(n) for direct

## Validation

The implementation includes comprehensive tests covering:
- Parameter validation
- Reproducibility
- Theoretical properties
- Different generation methods
- Increment calculation

## References

1. Bacry, E., Delour, J., & Muzy, J. F. (2001). Multifractal random walk. Physical Review E, 64(2), 026103.
2. Muzy, J. F., Bacry, E., & Arneodo, A. (1991). Wavelets and multifractal formalism for singular signals: Application to turbulence data. Physical Review Letters, 67(25), 3515.
3. Calvet, L. E., & Fisher, A. J. (2002). Multifractality in asset returns: Theory and evidence. The Review of Economics and Statistics, 84(3), 381-406.
