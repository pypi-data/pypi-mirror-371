# Neural fSDE Models

## Overview

The neural fSDE (fractional Stochastic Differential Equation) models implement neural network-based fractional stochastic differential equations based on the work by Hayashi & Nakagawa (2022, 2024). This system provides a hybrid approach with both JAX and PyTorch implementations for maximum flexibility and performance.

## Key Features

- **Hybrid Framework Support**: JAX (high-performance) + PyTorch (compatibility)
- **Multiple Numerical Schemes**: Euler-Maruyama, Milstein, Heun
- **Efficient fBm Generation**: Cholesky, Circulant, JAX-optimized methods
- **Automatic Framework Selection**: Factory pattern with performance benchmarking
- **Latent Fractional Networks**: Advanced latent space modeling
- **GPU Acceleration**: JAX-based high-performance computation

## Core Components

### BaseNeuralFSDE

Base class for all neural fSDE models.

```python
from models.data_models.neural_fsde import BaseNeuralFSDE
```

**Key Methods:**
- `simulate(n_samples, dt, scheme, seed)`: Generate time series
- `get_parameters()`: Get model parameters
- `get_model_info()`: Get model information

### FractionalBrownianMotionGenerator

Efficient fBm generation with multiple algorithms.

```python
from models.data_models.neural_fsde import FractionalBrownianMotionGenerator
```

**Constructor:**
```python
FractionalBrownianMotionGenerator(
    method: str = 'auto',  # 'cholesky', 'circulant', 'jax', 'auto'
    seed: Optional[int] = None
)
```

**Methods:**
- `generate_path(n_steps, hurst, dt, method)`: Generate fBm path
- `generate_increments(n_steps, hurst, dt, method)`: Generate fBm increments

### Numerical Solvers

Multiple SDE solvers for different numerical schemes.

```python
from models.data_models.neural_fsde import (
    SDESolver,
    JAXSDESolver,
    AdaptiveSDESolver,
    solve_sde
)
```

**Available Solvers:**
- `SDESolver`: Base solver with multiple schemes
- `JAXSDESolver`: JAX-optimized solver
- `AdaptiveSDESolver`: Adaptive step-size solver

## Factory System

### NeuralFSDEFactory

Automatic framework selection and model creation.

```python
from models.data_models.neural_fsde import (
    NeuralFSDEFactory,
    get_factory,
    create_fsde_net,
    create_latent_fsde_net,
    benchmark_frameworks
)
```

**Factory Methods:**
- `create_fsde_net()`: Create standard fSDE network
- `create_latent_fsde_net()`: Create latent fractional network
- `benchmark_frameworks()`: Compare framework performance
- `get_framework_info()`: Get available frameworks

## Model Types

### Standard fSDE Networks

```python
# Create with automatic framework selection
model = create_fsde_net(
    state_dim=1,
    hidden_dim=32,
    num_layers=3,
    hurst_parameter=0.7
)

# Simulate time series
trajectory = model.simulate(n_samples=1000, dt=0.01)
```

### Latent Fractional Networks

```python
# Create latent network
model = create_latent_fsde_net(
    obs_dim=1,
    latent_dim=16,
    hidden_dim=64,
    num_layers=4,
    hurst_parameter=0.6
)

# Simulate with latent dynamics
trajectory = model.simulate(n_samples=1000, dt=0.01)
```

## Framework-Specific Implementations

### JAX Implementation

```python
from models.data_models.neural_fsde import (
    JAXfSDENet,
    JAXLatentFractionalNet,
    JAXMLP,
    create_jax_fsde_net,
    create_jax_latent_fsde_net
)

# High-performance JAX model
model = JAXfSDENet(
    state_dim=1,
    hidden_dim=32,
    hurst_parameter=0.7
)
```

### PyTorch Implementation

```python
from models.data_models.neural_fsde import (
    TorchfSDENet,
    TorchLatentFractionalNet,
    TorchMLP,
    create_torch_fsde_net,
    create_torch_latent_fsde_net
)

# PyTorch model for compatibility
model = TorchfSDENet(
    state_dim=1,
    hidden_dim=32,
    hurst_parameter=0.7
)
```

## Usage Examples

### Basic Usage

```python
import sys
sys.path.insert(0, '.')

from models.data_models.neural_fsde import (
    create_fsde_net,
    benchmark_frameworks
)

# Create model with automatic framework selection
model = create_fsde_net(
    state_dim=1,
    hidden_dim=32,
    num_layers=3,
    hurst_parameter=0.7
)

print(f"Created {model.framework} model: {model}")

# Simulate time series
trajectory = model.simulate(n_samples=1000, dt=0.01)
print(f"Generated trajectory shape: {trajectory.shape}")

# Get framework information
from models.data_models.neural_fsde import get_factory
factory = get_factory()
info = factory.get_framework_info()
print(f"Available frameworks: {info['available_frameworks']}")
print(f"Recommended framework: {info['recommended_framework']}")
```

### Framework Benchmarking

```python
# Benchmark available frameworks
results = benchmark_frameworks(
    state_dim=1,
    hidden_dim=32,
    n_samples=1000,
    n_runs=5
)

print("Benchmark Results:")
for framework, result in results['frameworks'].items():
    if result['status'] == 'success':
        print(f"{framework}: {result['samples_per_second']:.1f} samples/sec")
```

### Advanced Features

```python
# Test different numerical schemes
model = create_fsde_net(state_dim=1, hidden_dim=32, hurst_parameter=0.7)

schemes = ['euler', 'milstein', 'heun']
for scheme in schemes:
    trajectory = model.simulate(n_samples=100, dt=0.01, scheme=scheme)
    print(f"{scheme} scheme: shape {trajectory.shape}")

# Get model parameters
params = model.get_parameters()
print(f"Model parameters: {params}")
```

### fBm Generation

```python
from models.data_models.neural_fsde import (
    FractionalBrownianMotionGenerator,
    generate_fbm_path,
    generate_fbm_increments
)

# Using generator class
fbm_gen = FractionalBrownianMotionGenerator(method='cholesky')
path = fbm_gen.generate_path(n_steps=1000, hurst=0.7, dt=0.01)

# Using convenience functions
path2 = generate_fbm_path(hurst=0.6, n_steps=500, dt=0.01)
increments = generate_fbm_increments(hurst=0.5, n_steps=1000, dt=0.01)
```

## Performance Considerations

### Framework Selection

- **JAX**: Best for GPU environments and large-scale computation
- **PyTorch**: Best for development, debugging, and CPU environments
- **Auto**: Automatically selects best available framework

### Numerical Schemes

- **Euler**: Fastest, good for most applications
- **Milstein**: More accurate, slightly slower
- **Heun**: Most accurate, slowest

### fBm Generation Methods

- **Cholesky**: O(n²) but numerically stable
- **Circulant**: O(n log n) for large sequences
- **JAX**: GPU-accelerated generation

## Validation

The neural fSDE system includes comprehensive validation:

- **Framework Detection**: Automatic detection of available frameworks
- **Parameter Validation**: Checks for valid parameter ranges
- **Performance Benchmarking**: Framework comparison and optimization
- **Comprehensive Testing**: All 8 test categories passing (100% success rate)

## Limitations

- Requires JAX or PyTorch installation
- GPU acceleration requires compatible hardware
- Large models may require significant memory
- Training pipelines not included (inference only)

## References

1. Hayashi, K., & Nakagawa, K. (2022). fSDE-Net: Generating Time Series Data with Long-term Memory.
2. Nakagawa, K., & Hayashi, K. (2024). Lf-Net: Generating Fractional Time-Series with Latent Fractional-Net.
3. Kloeden, P. E., & Platen, E. (1992). Numerical Solution of Stochastic Differential Equations.
4. Mandelbrot, B. B., & Van Ness, J. W. (1968). Fractional Brownian motions, fractional noises and applications.
