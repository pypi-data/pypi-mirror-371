## Fractional Gaussian Noise (fGn)

**Class**: `models.data_models.fgn.fgn_model.FractionalGaussianNoise`

### Overview
Fractional Gaussian Noise (fGn) is the stationary increment process of fractional Brownian motion (fBm). It is fully characterized by the Hurst parameter H ∈ (0, 1) and variance σ², and exhibits long-range dependence for H > 0.5.

### Constructor
```
FractionalGaussianNoise(H: float, sigma: float = 1.0, method: str = "circulant")
```

- **H**: Hurst parameter (0 < H < 1)
- **sigma**: Standard deviation (> 0)
- **method**: "circulant" (default) or "cholesky"

### Methods
- `generate(n: int, seed: Optional[int] = None) -> np.ndarray`: Generate length-n fGn sample
- `get_theoretical_properties() -> Dict[str, Any]`: Returns theoretical properties

### Notes
- Circulant embedding is efficient for large n and typically stable
- Cholesky is exact but O(n²) memory/time and used for validation or small n

### Example
```python
from models.data_models.fgn.fgn_model import FractionalGaussianNoise

fgn = FractionalGaussianNoise(H=0.7, sigma=1.0)
x = fgn.generate(n=4096, seed=123)
```



