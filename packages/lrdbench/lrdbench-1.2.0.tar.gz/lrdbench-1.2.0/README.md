# 🚀 **LRDBench: Comprehensive Framework for Long-Range Dependence Estimation**

A comprehensive repository for exploring synthetic data generation techniques and estimation methods for various stochastic processes, with a focus on **long-range dependence estimation** and **machine learning approaches**.

## 🎯 **Project Overview**

This project focuses on implementing and analyzing five key stochastic models:
- **ARFIMA** (AutoRegressive Fractionally Integrated Moving Average)
- **fBm** (Fractional Brownian Motion)
- **fGn** (Fractional Gaussian Noise)
- **MRW** (Multifractal Random Walk)
- **Neural fSDE** (Neural network-based fractional SDEs)

## 🏆 **Project Status**

🎉 **PROJECT COMPLETE - 100%** 🎉

All major components have been successfully implemented and tested:

- ✅ **Data Models**: 5/5 models fully implemented and optimized
- ✅ **Estimators**: 18/18 estimators with comprehensive testing
- ✅ **High-Performance**: Sub-100ms estimation times with robust algorithms
- ✅ **Neural fSDE**: Components present with optional JAX/PyTorch dependencies
- ✅ **Auto-Discovery**: Intelligent component discovery and integration system
- ✅ **PyPI Ready**: Complete packaging configuration for distribution
- ✅ **Demos**: Comprehensive demonstration scripts and examples
- ✅ **Production Ready**: All models come pre-trained and ready to use

## 🏗️ **Project Structure**

### **📁 Root Level (Essential Files)**
```
DataExploratoryProject/
├── README.md                           # Main project documentation
├── requirements.txt                    # Dependencies
├── setup.py                          # PyPI packaging configuration
├── pyproject.toml                     # Modern Python packaging
├── MANIFEST.in                        # Package inclusion rules
├── LICENSE                            # MIT License
├── .gitignore                         # Git ignore rules
├── auto_discovery_system.py           # Component discovery system
├── component_registry.json            # Component registry
├── models/                            # Data model implementations (5 generators)
├── analysis/                          # Estimator implementations (18 estimators)
├── setup/                             # Setup and configuration files
├── scripts/                           # Main Python scripts
├── config/                            # Configuration files
├── assets/                            # Images and media files
├── documentation/                     # Documentation
├── demos/                             # Demo scripts
├── tests/                             # Test files
└── confound_results/                  # Quality leaderboard and benchmark results
```

### **📁 Organized Folders**

#### **🔧 setup/ - Setup & Configuration**
- Git Bash setup guides and configuration
- PowerShell profiles and terminal settings
- Git hooks and automation scripts
- Project cleanup documentation

#### **🐍 scripts/ - Main Python Scripts**
- Comprehensive benchmarking scripts
- Machine learning estimator analysis and training
- Confound analysis and robustness testing
- Machine learning vs classical comparison

#### **⚙️ config/ - Configuration & Registry**
- Component registry and discovery metadata
- Git configuration and project settings
- Auto-discovery system configuration

#### **🖼️ assets/ - Images & Media**
- Research visualizations and diagrams
- Neural fSDE framework analysis
- Machine learning estimator performance results
- Publication-quality figures

---

## 🚀 **Quick Start**

### **1. Installation**

#### **From PyPI (Recommended)**
```bash
pip install lrdbench
```

#### **From Source**
```bash
# Clone repository
git clone https://github.com/dave2k77/long-range-dependence-project-3.git
cd long-range-dependence-project-3

# Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Unix/MacOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### **2. Run Comprehensive Benchmark**
```python
from lrdbench.analysis.benchmark import ComprehensiveBenchmark

# Initialize benchmark system
benchmark = ComprehensiveBenchmark()

# Run different types of benchmarks
results = benchmark.run_comprehensive_benchmark(
    benchmark_type='classical',  # 'comprehensive', 'classical', 'ML', 'neural'
    contamination_type='additive_gaussian',  # optional: add noise, outliers, etc.
    contamination_level=0.2  # 0.0 to 1.0
)

# Or use convenience methods
results_classical = benchmark.run_classical_benchmark()
results_ml = benchmark.run_ml_benchmark(contamination_type='outliers')
results_neural = benchmark.run_neural_benchmark(contamination_type='trend')
```

### **3. Explore Machine Learning Estimators**
```python
# Run machine learning estimator analysis
from lrdbench.analysis.machine_learning.cnn_estimator import CNNEstimator
from lrdbench.analysis.machine_learning.transformer_estimator import TransformerEstimator
cnn = CNNEstimator()
transformer = TransformerEstimator()
# Configure and run estimation
```

---

## 📊 **Key Features**

### **🔬 Comprehensive Estimator Suite (18 Total)**
- **Temporal Methods**: DFA, R/S, Higuchi, DMA (4 estimators)
- **Spectral Methods**: Periodogram, Whittle, GPH (3 estimators)
- **Wavelet Methods**: Log Variance, Variance, Whittle, CWT (4 estimators)
- **Multifractal Methods**: MFDFA, Wavelet Leaders (2 estimators)
- **Machine Learning**: Random Forest, Gradient Boosting, SVR (3 estimators)
- **Neural Networks**: CNN, Transformer (2 estimators)

### **🎯 Flexible Benchmarking System**
- **Benchmark Types**: Comprehensive, Classical, ML, Neural
- **Contamination Options**: Gaussian noise, outliers, trend, seasonal, missing data
- **Configurable Levels**: Adjustable contamination intensity (0.0 to 1.0)
- **Automatic Reporting**: CSV and JSON output with performance rankings

### **⚡ High-Performance Implementation**
- **JAX Optimization**: GPU acceleration for large-scale computations
- **Numba JIT**: Just-in-time compilation for critical loops
- **Parallel Processing**: Multi-core benchmark execution
- **Memory Efficient**: Optimized data structures and algorithms

### **🧪 Advanced Benchmarking Features**
- **Category-Specific Testing**: Test only classical, ML, or neural estimators
- **Contamination Simulation**: Real-world data quality challenges
- **Performance Metrics**: Execution time, accuracy, and robustness analysis
- **Result Export**: Structured output for further analysis and publication

### **🎯 Production Ready**
- **Pre-trained Models**: All ML and neural models come ready to use
- **No Training Required**: Models work immediately after installation
- **Consistent API**: Unified interface across all estimator types
- **Robust Error Handling**: Graceful fallbacks and comprehensive error reporting

---

## 📚 **Documentation & Resources**

### **📖 Core Documentation**
- **README.md**: This comprehensive overview
- **setup/README.md**: Setup and configuration guide
- **scripts/README.md**: Main Python scripts documentation
- **config/README.md**: Configuration and registry guide
- **assets/README.md**: Images and media assets guide

### **🔧 Setup & Configuration**
- **setup/**: All setup files and configuration guides
- **config/**: Component registry and project configuration
- **Git Bash**: Configured as default shell for development

### **📊 Results & Analysis**
- **confound_results/**: Quality leaderboard and clinical recommendations
- **benchmark_results/**: Comprehensive benchmark results
- **publication_figures/**: Research paper figures and diagrams

---

## 🤝 **Contributing**

This project welcomes contributions from researchers, developers, and practitioners interested in:
- **Long-range dependence estimation**
- **Physics-informed neural networks**
- **Clinical time series analysis**
- **High-performance scientific computing**

### **Development Guidelines**
1. **Follow existing code style** and documentation patterns
2. **Add comprehensive tests** for new features
3. **Update documentation** for any API changes
4. **Use the auto-discovery system** for component integration

---

## 👨‍💻 **Author**

**Davian R. Chin**  
*Department of Biomedical Engineering*  
*University of Reading*  
*Email: d.r.chin@pgr.reading.ac.uk*

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📚 **References**

### **Core Research Papers**
- Beran, J. (1994). Statistics for Long-Memory Processes.
- Mandelbrot, B. B. (1982). The Fractal Geometry of Nature.
- Abry, P., & Veitch, D. (1998). Wavelet analysis of long-range-dependent traffic.
- Muzy, J. F., Bacry, E., & Arneodo, A. (1991). Wavelets and multifractal formalism for singular signals.

### **Neural Network Innovations**
- Hayashi, K., & Nakagawa, K. (2022). fSDE-Net: Generating Time Series Data with Long-term Memory.
- Nakagawa, K., & Hayashi, K. (2024). Lf-Net: Generating Fractional Time-Series with Latent Fractional-Net.
- Li, Z., et al. (2020). Fourier Neural Operator for Parametric Partial Differential Equations.
- Raissi, M., et al. (2019). Physics-informed neural networks: A deep learning framework for solving forward and inverse problems.

---

**For questions, contributions, or collaboration opportunities, please refer to the comprehensive documentation in this repository.**
