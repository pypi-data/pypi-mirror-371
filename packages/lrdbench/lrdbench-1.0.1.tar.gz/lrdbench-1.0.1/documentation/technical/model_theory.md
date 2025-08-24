# Model Theory

This document provides the mathematical foundations and theoretical background for all stochastic models implemented in the project.

## Table of Contents

1. [Fractional Brownian Motion (fBm)](#fractional-brownian-motion-fbm)
2. [Fractional Gaussian Noise (fGn)](#fractional-gaussian-noise-fgn)
3. [ARFIMA Models](#arfima-models)
4. [Multifractal Random Walk (MRW)](#multifractal-random-walk-mrw)
5. [Model Relationships](#model-relationships)
6. [Mathematical Properties](#mathematical-properties)

## Fractional Brownian Motion (fBm)

### Definition

Fractional Brownian Motion is a self-similar Gaussian process with stationary increments. For a Hurst parameter H ∈ (0, 1), fBm is defined as a Gaussian process B_H(t) with:

1. **Zero mean**: E[B_H(t)] = 0
2. **Covariance function**: E[B_H(t)B_H(s)] = (σ²/2)(|t|^(2H) + |s|^(2H) - |t-s|^(2H))
3. **Self-similarity**: B_H(at) = a^H B_H(t) for all a > 0
4. **Stationary increments**: B_H(t) - B_H(s) has the same distribution as B_H(t-s)

### Mathematical Properties

#### Self-Similarity

The self-similarity property states that:

B_H(at) = a^H B_H(t)

This means that scaling the time axis by a factor a scales the process by a^H.

#### Variance Scaling

The variance of fBm scales as:

Var(B_H(t)) = σ²|t|^(2H)

#### Long-Range Dependence

For H > 0.5, fBm exhibits long-range dependence:

- **Persistent**: H > 0.5 (positive correlations)
- **Anti-persistent**: H < 0.5 (negative correlations)
- **Independent**: H = 0.5 (standard Brownian motion)

#### Autocorrelation Function

The autocorrelation function of fBm increments (fGn) is:

ρ(k) = (1/2)(|k+1|^(2H) - 2|k|^(2H) + |k-1|^(2H))

For large k, this behaves as:

ρ(k) ≈ H(2H-1)k^(2H-2)

#### Power Spectral Density

The power spectral density of fBm is:

S(f) = σ²|f|^(-2H-1)

### Generation Methods

#### Davies-Harte Method

The Davies-Harte method uses the spectral representation:

1. **Spectral Density**: S(f) = σ²(2 sin(πf/n))^(1-2H)
2. **Complex Noise**: Generate Z(f) ~ CN(0, 1)
3. **Filtering**: Y(f) = √S(f) Z(f)
4. **Inverse FFT**: B_H(t) = FFT^(-1)(Y(f))

#### Cholesky Decomposition

1. **Covariance Matrix**: C(i,j) = σ²/2(|i|^(2H) + |j|^(2H) - |i-j|^(2H))
2. **Cholesky Decomposition**: C = LL^T
3. **Generation**: B_H = LZ where Z ~ N(0, I)

#### Circulant Embedding

1. **Autocovariance**: γ(k) = σ²/2(|k+1|^(2H) - 2|k|^(2H) + |k-1|^(2H))
2. **Circulant Matrix**: Construct circulant matrix from γ(k)
3. **Eigenvalue Decomposition**: C = QΛQ^T
4. **Generation**: B_H = Q√ΛZ

## Fractional Gaussian Noise (fGn)

### Definition

Fractional Gaussian Noise is the increments of fBm:

X(t) = B_H(t+1) - B_H(t)

### Properties

#### Stationarity

fGn is a stationary process with:

- **Mean**: E[X(t)] = 0
- **Variance**: Var(X(t)) = σ²
- **Autocorrelation**: ρ(k) = (1/2)(|k+1|^(2H) - 2|k|^(2H) + |k-1|^(2H))

#### Long-Range Dependence

For H > 0.5, the autocorrelation function decays slowly:

ρ(k) ≈ H(2H-1)k^(2H-2) as k → ∞

#### Power Spectral Density

The power spectral density of fGn is:

S(f) = 4σ² sin²(πf)|f|^(-2H-1)

### Relationship to fBm

fGn and fBm are related through:

1. **fGn from fBm**: X(t) = B_H(t+1) - B_H(t)
2. **fBm from fGn**: B_H(t) = Σ_{k=1}^t X(k)

## ARFIMA Models

### Definition

ARFIMA(p,d,q) models combine ARMA processes with fractional differencing:

(1 - B)^d Φ(B)X_t = Θ(B)ε_t

where:
- d is the fractional differencing parameter
- Φ(B) is the AR polynomial of order p
- Θ(B) is the MA polynomial of order q
- ε_t is white noise

### Fractional Differencing

The fractional differencing operator (1 - B)^d is defined as:

(1 - B)^d = Σ_{k=0}^∞ (d choose k) (-B)^k

where (d choose k) = d(d-1)...(d-k+1)/k!

### Properties

#### Long-Range Dependence

For 0 < d < 0.5, ARFIMA processes exhibit long-range dependence with:

- **Autocorrelation**: ρ(k) ≈ Ck^(2d-1) as k → ∞
- **Power Spectrum**: S(f) ≈ C|f|^(-2d) as f → 0

#### Stationarity

ARFIMA processes are stationary for -0.5 < d < 0.5.

#### Invertibility

ARFIMA processes are invertible for d > -1.

### Parameter Estimation

#### Maximum Likelihood

The log-likelihood function is:

L(θ) = -(n/2)log(2π) - (1/2)log|Σ| - (1/2)X^T Σ^(-1) X

where Σ is the covariance matrix.

#### Whittle Estimation

The Whittle likelihood is:

L_W(θ) = -Σ_{j=1}^m [log S(f_j; θ) + I(f_j)/S(f_j; θ)]

where I(f_j) is the periodogram.

## Multifractal Random Walk (MRW)

### Definition

Multifractal Random Walk is a non-Gaussian multifractal process defined as:

X(t) = B_H(t) exp(ω(t))

where:
- B_H(t) is fBm with Hurst parameter H
- ω(t) is a Gaussian process with specific covariance structure

### Multifractal Properties

#### Multifractal Spectrum

The multifractal spectrum f(α) describes the distribution of Hölder exponents:

f(α) = dim{t : α(t) = α}

where α(t) is the local Hölder exponent.

#### Structure Functions

The q-th order structure function scales as:

S_q(τ) = E[|X(t+τ) - X(t)|^q] ≈ τ^ζ(q)

where ζ(q) is the scaling exponent function.

### Parameter Estimation

#### Multifractal Detrended Fluctuation Analysis (MFDFA)

1. **Profile**: Y(i) = Σ_{k=1}^i (X(k) - ⟨X⟩)
2. **Segmentation**: Divide into N_s = N/s segments
3. **Detrending**: Fit polynomial and calculate variance
4. **Scaling**: F_q(s) = [Σ_{ν=1}^N_s F²(ν,s)^(q/2)/N_s]^(1/q)
5. **Multifractal Spectrum**: f(α) = qα - τ(q)

## Model Relationships

### Hierarchical Structure

```
Stochastic Processes
├── Gaussian Processes
│   ├── Fractional Brownian Motion (fBm)
│   │   └── Fractional Gaussian Noise (fGn)
│   └── ARFIMA Models
└── Non-Gaussian Processes
    └── Multifractal Random Walk (MRW)
```

### Transformations

1. **fBm → fGn**: X(t) = B_H(t+1) - B_H(t)
2. **fGn → fBm**: B_H(t) = Σ_{k=1}^t X(k)
3. **ARFIMA → Long Memory**: d > 0 induces long-range dependence
4. **MRW → Multifractal**: Combines fBm with log-normal multipliers

### Parameter Relationships

| Model | Key Parameter | Range | Interpretation |
|-------|---------------|-------|----------------|
| fBm | H | (0, 1) | Hurst parameter |
| fGn | H | (0, 1) | Hurst parameter |
| ARFIMA | d | (-0.5, 0.5) | Fractional differencing |
| MRW | H, λ² | H ∈ (0, 1), λ² > 0 | Hurst + multifractal |

## Mathematical Properties

### Scaling Properties

#### Self-Similarity

- **fBm**: B_H(at) = a^H B_H(t)
- **fGn**: X(at) = a^(H-1) X(t)
- **ARFIMA**: No exact self-similarity
- **MRW**: Approximate self-similarity

#### Long-Range Dependence

- **fBm**: H > 0.5
- **fGn**: H > 0.5
- **ARFIMA**: d > 0
- **MRW**: H > 0.5

### Statistical Properties

#### Moments

| Model | Mean | Variance | Skewness | Kurtosis |
|-------|------|----------|----------|----------|
| fBm | 0 | σ²t^(2H) | 0 | 3 |
| fGn | 0 | σ² | 0 | 3 |
| ARFIMA | 0 | σ² | 0 | 3 |
| MRW | 0 | σ²t^(2H) | 0 | > 3 |

#### Autocorrelation

- **fBm**: Non-stationary
- **fGn**: ρ(k) ≈ H(2H-1)k^(2H-2)
- **ARFIMA**: ρ(k) ≈ Ck^(2d-1)
- **MRW**: Complex structure

### Computational Complexity

| Generation Method | Time Complexity | Space Complexity | Accuracy |
|-------------------|-----------------|------------------|----------|
| Davies-Harte | O(n log n) | O(n) | Good |
| Cholesky | O(n³) | O(n²) | Exact |
| Circulant | O(n log n) | O(n) | Good |
| ARFIMA | O(n²) | O(n) | Exact |
| MRW | O(n log n) | O(n) | Good |

## References

1. Mandelbrot, B. B., & Van Ness, J. W. (1968). Fractional Brownian motions, fractional noises and applications. *SIAM Review*, 10(4), 422-437.

2. Beran, J. (1994). *Statistics for Long-Memory Processes*. Chapman & Hall.

3. Granger, C. W., & Joyeux, R. (1980). An introduction to long-memory time series models and fractional differencing. *Journal of Time Series Analysis*, 1(1), 15-29.

4. Bacry, E., Delour, J., & Muzy, J. F. (2001). Multifractal random walk. *Physical Review E*, 64(2), 026103.

5. Davies, R. B., & Harte, D. S. (1987). Tests for Hurst effect. *Biometrika*, 74(1), 95-101.

6. Abry, P., & Veitch, D. (1998). Wavelet analysis of long-range-dependent traffic. *IEEE Transactions on Information Theory*, 44(1), 2-15.
