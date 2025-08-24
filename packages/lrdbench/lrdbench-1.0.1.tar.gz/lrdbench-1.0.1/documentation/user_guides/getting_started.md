# Getting Started Guide

Welcome to the Synthetic Data Generation and Analysis Project! This guide will help you get up and running quickly.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Basic Concepts](#basic-concepts)
4. [First Examples](#first-examples)
5. [Next Steps](#next-steps)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd DataExploratoryProject
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Unix/MacOS:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Verify Installation

```python
import numpy as np
import matplotlib.pyplot as plt
from models.data_models.fbm import FractionalBrownianMotion
from analysis.temporal.dfa import DFAEstimator

print("Installation successful!")
```

## Quick Start

### Generate Your First Synthetic Data

```python
# Import the fBm model
from models.data_models.fbm import FractionalBrownianMotion

# Create a model with Hurst parameter H = 0.7
fbm = FractionalBrownianMotion(H=0.7, sigma=1.0)

# Generate 1000 data points
data = fbm.generate(n=1000, seed=42)

# Plot the data
import matplotlib.pyplot as plt
plt.figure(figsize=(12, 4))
plt.plot(data)
plt.title('Fractional Brownian Motion (H = 0.7)')
plt.xlabel('Time')
plt.ylabel('Value')
plt.grid(True, alpha=0.3)
plt.show()
```

### Estimate Parameters from Data

```python
# Import the DFA estimator
from analysis.temporal.dfa import DFAEstimator

# Create estimator
dfa = DFAEstimator(min_box_size=8, max_box_size=200)

# Estimate Hurst parameter
results = dfa.estimate(data)

print(f"Estimated Hurst parameter: {results['hurst_parameter']:.3f}")
print(f"R-squared: {results['r_squared']:.3f}")

# Plot the scaling relationship
dfa.plot_scaling()
```

## Basic Concepts

### Stochastic Models

The project implements four main stochastic models:

1. **Fractional Brownian Motion (fBm)**
   - Self-similar Gaussian process
   - Characterized by Hurst parameter H
   - Exhibits long-range dependence

2. **Fractional Gaussian Noise (fGn)**
   - Increments of fBm
   - Stationary process
   - Related to fBm through differencing

3. **ARFIMA (AutoRegressive Fractionally Integrated Moving Average)**
   - Long-memory time series model
   - Combines ARMA with fractional differencing
   - Useful for modeling persistent time series

4. **Multifractal Random Walk (MRW)**
   - Non-Gaussian multifractal process
   - Exhibits scale-invariant properties
   - Characterized by multifractal spectrum

### Estimators

The project provides various estimators for characterizing time series:

#### Temporal Estimators
- **DFA**: Detrended Fluctuation Analysis
- **R/S**: Rescaled Range Analysis
- **Higuchi**: Higuchi's fractal dimension method
- **DMA**: Detrending Moving Average

#### Spectral Estimators
- **Periodogram**: Power spectral density estimation
- **Whittle**: Maximum likelihood estimation
- **GPH**: Geweke-Porter-Hudak estimator

#### Wavelet Estimators
- **Wavelet Log Variance**: Log-variance of wavelet coefficients
- **Wavelet Variance**: Variance of wavelet coefficients
- **Wavelet Whittle**: Whittle estimation using wavelets
- **CWT**: Continuous Wavelet Transform

#### Multifractal Estimators
- **MFDFA**: Multifractal Detrended Fluctuation Analysis
- **Wavelet Leaders**: Multifractal analysis using wavelet leaders

## First Examples

### Example 1: Comparing Different Hurst Parameters

```python
import numpy as np
import matplotlib.pyplot as plt
from models.data_models.fbm import FractionalBrownianMotion

# Generate fBm with different Hurst parameters
hurst_values = [0.3, 0.5, 0.7, 0.9]
n = 1000

fig, axes = plt.subplots(2, 2, figsize=(12, 8))
axes = axes.flatten()

for i, H in enumerate(hurst_values):
    fbm = FractionalBrownianMotion(H=H, sigma=1.0)
    data = fbm.generate(n, seed=42)
    
    axes[i].plot(data)
    axes[i].set_title(f'fBm with H = {H}')
    axes[i].set_xlabel('Time')
    axes[i].set_ylabel('Value')
    axes[i].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
```

### Example 2: Parameter Estimation and Validation

```python
from analysis.temporal.dfa import DFAEstimator

# Generate synthetic data with known Hurst parameter
true_H = 0.7
fbm = FractionalBrownianMotion(H=true_H, sigma=1.0)
data = fbm.generate(2000, seed=42)

# Estimate Hurst parameter using DFA
dfa = DFAEstimator(min_box_size=8, max_box_size=500)
results = dfa.estimate(data)

# Compare true vs estimated
estimated_H = results['hurst_parameter']
error = abs(estimated_H - true_H)

print(f"True Hurst parameter: {true_H}")
print(f"Estimated Hurst parameter: {estimated_H:.3f}")
print(f"Absolute error: {error:.3f}")
print(f"Relative error: {error/true_H*100:.1f}%")
print(f"R-squared: {results['r_squared']:.3f}")

# Get confidence intervals
ci = dfa.get_confidence_intervals(confidence_level=0.95)
lower, upper = ci['hurst_parameter']
print(f"95% Confidence Interval: [{lower:.3f}, {upper:.3f}]")
```

### Example 3: Comprehensive Analysis

```python
import numpy as np
import matplotlib.pyplot as plt
from models.data_models.fbm import FractionalBrownianMotion
from analysis.temporal.dfa import DFAEstimator

# Set up parameters
hurst_values = [0.3, 0.5, 0.7, 0.9]
n = 2000
n_trials = 10

# Results storage
results_summary = {}

for H_true in hurst_values:
    print(f"\nAnalyzing fBm with H = {H_true}")
    
    estimated_H_values = []
    
    for trial in range(n_trials):
        # Generate data
        fbm = FractionalBrownianMotion(H=H_true, sigma=1.0)
        data = fbm.generate(n, seed=42 + trial)
        
        # Estimate Hurst parameter
        dfa = DFAEstimator(min_box_size=8, max_box_size=n//8)
        dfa_results = dfa.estimate(data)
        
        estimated_H_values.append(dfa_results['hurst_parameter'])
    
    # Calculate statistics
    mean_H = np.mean(estimated_H_values)
    std_H = np.std(estimated_H_values)
    bias = mean_H - H_true
    
    results_summary[H_true] = {
        'mean': mean_H,
        'std': std_H,
        'bias': bias,
        'relative_error': abs(bias)/H_true*100
    }
    
    print(f"  True H: {H_true:.3f}")
    print(f"  Estimated H (mean ± std): {mean_H:.3f} ± {std_H:.3f}")
    print(f"  Bias: {bias:.3f}")
    print(f"  Relative error: {abs(bias)/H_true*100:.1f}%")

# Create summary plot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Plot 1: Estimation accuracy
true_Hs = list(results_summary.keys())
estimated_Hs = [results_summary[H]['mean'] for H in true_Hs]

ax1.scatter(true_Hs, estimated_Hs, s=100, alpha=0.7)
ax1.plot([0, 1], [0, 1], 'r--', alpha=0.7, label='Perfect estimation')
ax1.set_xlabel('True Hurst Parameter')
ax1.set_ylabel('Estimated Hurst Parameter')
ax1.set_title('Estimation Accuracy')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Plot 2: Relative errors
relative_errors = [results_summary[H]['relative_error'] for H in true_Hs]

ax2.bar(range(len(true_Hs)), relative_errors, alpha=0.7)
ax2.set_xlabel('Hurst Parameter')
ax2.set_ylabel('Relative Error (%)')
ax2.set_title('Estimation Errors')
ax2.set_xticks(range(len(true_Hs)))
ax2.set_xticklabels([f'{H:.1f}' for H in true_Hs])
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
```

## Next Steps

### 1. Explore the Models

- [fBm Model Tutorial](tutorials/fbm_tutorial.md)
- [ARFIMA Model Tutorial](tutorials/arfima_tutorial.md)
- [fGn Model Tutorial](tutorials/fgn_tutorial.md)
- [MRW Model Tutorial](tutorials/mrw_tutorial.md)

### 2. Learn About Estimators

- [DFA Tutorial](tutorials/dfa_tutorial.md)
- [R/S Analysis Tutorial](tutorials/rs_tutorial.md)
- [Wavelet Methods Tutorial](tutorials/wavelet_tutorial.md)
- [Multifractal Analysis Tutorial](tutorials/multifractal_tutorial.md)

### 3. Advanced Topics

- [Performance Optimization](advanced/performance.md)
- [High-Performance Computing](advanced/hpc.md)
- [Validation and Testing](advanced/validation.md)
- [Research Applications](advanced/applications.md)

### 4. API Reference

- [Complete API Documentation](../api_reference/README.md)
- [Model Classes](../api_reference/models/README.md)
- [Estimator Classes](../api_reference/estimators/README.md)

### 5. Examples and Use Cases

- [Financial Time Series](examples/financial.md)
- [Physiological Signals](examples/physiological.md)
- [Network Traffic](examples/network.md)
- [Climate Data](examples/climate.md)

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Make sure you're in the correct directory
   cd DataExploratoryProject
   
   # Activate virtual environment
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Unix/MacOS
   ```

2. **Missing Dependencies**
   ```bash
   # Reinstall requirements
   pip install -r requirements.txt
   ```

3. **Memory Issues**
   ```python
   # For large datasets, use smaller parameters
   dfa = DFAEstimator(min_box_size=16, max_box_size=100)
   ```

### Getting Help

- Check the [API Reference](../api_reference/README.md) for detailed documentation
- Review the [Examples](examples/README.md) for usage patterns
- Consult the [Technical Documentation](../technical/README.md) for implementation details

## Contributing

We welcome contributions! Please see the [Contributing Guide](../../CONTRIBUTING.md) for details on:

- Code style and standards
- Testing requirements
- Documentation guidelines
- Pull request process

## License

This project is licensed under the MIT License. See the [LICENSE](../../LICENSE) file for details.
