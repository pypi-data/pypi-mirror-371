# CPU-Based Demos

This directory contains demonstration scripts that are optimized for CPU-based computation and do not require GPU acceleration. These demos showcase the core functionality of the data modeling and generation project using standard Python libraries and CPU-optimized implementations.

## Available Demos

### 1. **Parameter Estimation Demo** (`parameter_estimation_demo.py`)
- **Purpose**: Demonstrates parameter estimation across all estimator categories
- **Features**: 
  - Tests all 13 estimators on different data models
  - Compares accuracy and performance
  - Generates comprehensive comparison plots
- **Usage**: `python parameter_estimation_demo.py [--no-plot] [--save-plots] [--save-dir DIR]`

### 2. **Estimator Benchmark** (`estimator_benchmark.py`)
- **Purpose**: Automated performance benchmarking of all estimators
- **Features**:
  - Performance testing across different data sizes
  - Memory usage analysis
  - Automated report generation
- **Usage**: `python estimator_benchmark.py [--sizes 1000,2000,5000] [--save-dir DIR]`

### 3. **ARFIMA Performance Demo** (`arfima_performance_demo.py`)
- **Purpose**: Showcases the optimized ARFIMA model implementation
- **Features**:
  - FFT-based fractional differencing performance
  - Comparison with traditional methods
  - Memory and time complexity analysis
- **Usage**: `python arfima_performance_demo.py [--no-plot] [--save-plots]`

### 4. **Plotting Configuration Demo** (`plotting_configuration_demo.py`)
- **Purpose**: Demonstrates the global plotting configuration system
- **Features**:
  - Multiple plotting themes (Default, Dark, Light, Scientific, Presentation)
  - Consistent styling across all plots
  - Export-ready formatting
- **Usage**: `python plotting_configuration_demo.py`

### 5. **Comprehensive Model Demo** (`comprehensive_model_demo.py`)
- **Purpose**: End-to-end demonstration of all data models
- **Features**:
  - All 4 data models (fBm, fGn, ARFIMA, MRW)
  - Parameter validation and testing
  - Theoretical property verification
- **Usage**: `python comprehensive_model_demo.py [--no-plot] [--save-plots]`

### 6. **Real-World Confounds Demo** (`real_world_confounds_demo.py`)
- **Purpose**: Tests estimator robustness against real-world contaminations
- **Features**:
  - Complex time series library with 10 contamination types
  - Robustness testing across all estimators
  - Statistical analysis of contaminated data
- **Usage**: `python real_world_confounds_demo.py [--n-samples 1000] [--save-dir DIR]`

## Common Features

All CPU-based demos include:
- **CI-friendly flags**: `--no-plot`, `--save-plots`, `--save-dir`
- **Comprehensive error handling**: Robust error handling and parameter validation
- **Documentation**: Detailed docstrings and usage examples
- **Performance optimization**: CPU-optimized implementations using NumPy, SciPy, and Numba

## Requirements

- Python 3.8+
- NumPy
- SciPy
- Matplotlib
- Seaborn
- Pandas
- Numba (for optimized implementations)

## Running the Demos

```bash
# Run all CPU-based demos
cd demos/cpu_based

# Basic parameter estimation demo
python parameter_estimation_demo.py

# Performance benchmarking
python estimator_benchmark.py --sizes 1000,2000,5000

# Real-world confounds testing
python real_world_confounds_demo.py --n-samples 2000

# Plotting configuration demo
python plotting_configuration_demo.py
```

## Output

All demos generate:
- **Console output**: Progress information and results
- **Plots**: Visualizations (unless `--no-plot` is used)
- **Saved files**: Results, plots, and reports (if `--save-dir` is specified)

## Performance Notes

- These demos are optimized for CPU computation
- Use Numba JIT compilation for performance-critical sections
- Memory usage is optimized for typical desktop/laptop systems
- All demos include progress indicators for long-running operations
