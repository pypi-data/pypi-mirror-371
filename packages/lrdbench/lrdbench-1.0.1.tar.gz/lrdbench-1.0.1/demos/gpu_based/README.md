# GPU-Based Demos

This directory contains demonstration scripts that leverage GPU acceleration for high-performance computation. These demos showcase the JAX-optimized implementations of estimators and are designed to take advantage of GPU resources for faster computation on large datasets.

## Available Demos

### 1. **JAX Performance Demo** (`jax_performance_demo.py`)
- **Purpose**: Demonstrates JAX-optimized estimator performance
- **Features**: 
  - GPU-accelerated computation using JAX
  - Performance comparison with CPU implementations
  - Memory usage optimization
  - Batch processing capabilities
- **Usage**: `python jax_performance_demo.py [--device cpu/gpu] [--batch-size 100] [--no-plot]`

### 2. **High Performance Comparison Demo** (`high_performance_comparison_demo.py`)
- **Purpose**: Comprehensive comparison of CPU vs GPU performance
- **Features**:
  - Side-by-side comparison of all 13 estimators
  - JAX vs Numba vs Original implementations
  - Scaling analysis across different data sizes
  - Memory and time complexity profiling
- **Usage**: `python high_performance_comparison_demo.py [--sizes 1000,5000,10000] [--save-dir DIR]`

## GPU Requirements

### Hardware Requirements
- **NVIDIA GPU**: CUDA-compatible GPU with compute capability 7.0+
- **Memory**: At least 4GB GPU memory (8GB+ recommended for large datasets)
- **Driver**: Latest NVIDIA drivers

### Software Requirements
- **CUDA Toolkit**: 11.0 or later
- **cuDNN**: Compatible version for your CUDA installation
- **JAX**: GPU-enabled version
- **Python**: 3.8+

## Installation

```bash
# Install JAX with GPU support
pip install --upgrade "jax[cuda]" -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html

# Or for CPU-only JAX (fallback)
pip install --upgrade jax jaxlib

# Additional requirements
pip install numpy scipy matplotlib seaborn pandas
```

## Running the Demos

```bash
# Run JAX performance demo
cd demos/gpu_based
python jax_performance_demo.py --device gpu --batch-size 1000

# Run comprehensive performance comparison
python high_performance_comparison_demo.py --sizes 1000,5000,10000,20000

# CPU fallback (if GPU not available)
python jax_performance_demo.py --device cpu
```

## Performance Characteristics

### GPU Acceleration Benefits
- **Speedup**: 10-100x faster for large datasets
- **Batch Processing**: Efficient parallel computation
- **Memory Efficiency**: Optimized GPU memory usage
- **Scalability**: Better performance scaling with data size

### When to Use GPU Demos
- **Large datasets**: >10,000 data points
- **Batch processing**: Multiple time series analysis
- **Performance testing**: Benchmarking and optimization
- **Research**: High-throughput analysis

### When to Use CPU Demos
- **Small datasets**: <1,000 data points
- **Development**: Testing and debugging
- **Limited resources**: No GPU available
- **Real-time analysis**: Low-latency requirements

## Common Features

All GPU-based demos include:
- **Device selection**: Automatic GPU detection with CPU fallback
- **Memory management**: Efficient GPU memory allocation
- **Batch processing**: Parallel computation capabilities
- **Progress monitoring**: Real-time performance metrics
- **Error handling**: Graceful fallback to CPU if GPU unavailable

## Performance Tips

### GPU Optimization
1. **Batch size**: Use larger batch sizes for better GPU utilization
2. **Memory**: Monitor GPU memory usage to avoid OOM errors
3. **Data transfer**: Minimize CPU-GPU data transfers
4. **Compilation**: JAX JIT compilation for optimal performance

### Troubleshooting
- **GPU not detected**: Check CUDA installation and JAX GPU support
- **Memory errors**: Reduce batch size or data size
- **Performance issues**: Ensure latest drivers and JAX version
- **Compatibility**: Verify CUDA and cuDNN versions

## Output

GPU demos generate:
- **Performance metrics**: Speedup ratios and timing information
- **Memory usage**: GPU and CPU memory consumption
- **Scalability plots**: Performance vs data size relationships
- **Comparison reports**: Detailed performance analysis

## Example Performance Results

Typical speedup ratios (GPU vs CPU):
- **Small datasets (1K points)**: 2-5x speedup
- **Medium datasets (10K points)**: 10-20x speedup  
- **Large datasets (100K+ points)**: 50-100x speedup

*Note: Actual performance depends on hardware, data characteristics, and implementation details.*
