# 🐍 **Main Python Scripts**

This folder contains the core Python scripts for the DataExploratoryProject, including comprehensive benchmarking, Fractional PINO analysis, and confound testing.

## 📁 **Contents**

### **🏆 Core Benchmark Scripts**
- `comprehensive_estimator_benchmark.py` - **Main benchmark script** for all 13 estimators vs all data generators
- `comprehensive_ml_classical_benchmark.py` - Machine learning vs classical estimator comparison
- `confounded_data_benchmark.py` - Confound analysis for realistic clinical conditions

### **🔬 Fractional PINO Scripts**
- `enhanced_fractional_pino_with_true_operators.py` - **Main PINO script** with physics-informed constraints
- `fractional_pino_confound_analysis.py` - PINO-specific confound analysis
- `fractional_pino_confound_benchmark.py` - PINO confound benchmark testing

## 🚀 **Quick Start**

### **1. Run Comprehensive Benchmark**
```bash
# Navigate to scripts folder
cd scripts

# Run main benchmark
python comprehensive_estimator_benchmark.py
```

### **2. Run Fractional PINO Analysis**
```bash
# Run PINO analysis
python enhanced_fractional_pino_with_true_operators.py
```

### **3. Run Confound Analysis**
```bash
# Run confound benchmark
python confounded_data_benchmark.py

# Run PINO confound analysis
python fractional_pino_confound_analysis.py
```

## 📊 **Script Descriptions**

### **comprehensive_estimator_benchmark.py**
- **Purpose**: Comprehensive evaluation of all 13 estimators across all data generators
- **Output**: Performance leaderboard, accuracy metrics, processing times
- **Use Case**: Full framework validation and performance comparison

### **enhanced_fractional_pino_with_true_operators.py**
- **Purpose**: Main Fractional PINO implementation with physics-informed constraints
- **Features**: FNO integration, multi-scale processing, physics constraints
- **Use Case**: Neural operator training and evaluation

### **confounded_data_benchmark.py**
- **Purpose**: Test estimator robustness under realistic clinical conditions
- **Confounds**: Noise, outliers, trends, non-stationarity
- **Use Case**: Clinical validation and robustness assessment

### **fractional_pino_confound_analysis.py**
- **Purpose**: PINO-specific confound analysis and robustness testing
- **Features**: Neural network robustness evaluation
- **Use Case**: Neural method validation under clinical conditions

### **fractional_pino_confound_benchmark.py**
- **Purpose**: Comprehensive PINO confound benchmark testing
- **Output**: Neural vs classical performance comparison
- **Use Case**: End-to-end neural method validation

### **comprehensive_ml_classical_benchmark.py**
- **Purpose**: Machine learning vs classical estimator comparison
- **Methods**: LSTM, GRU, CNN, Transformer, Gradient Boosting
- **Use Case**: Performance baseline establishment

## 🔧 **Configuration**

### **Dependencies**
- Ensure all required packages are installed from `requirements.txt`
- Activate the appropriate virtual environment
- Check component registry for available estimators and data generators

### **Parameters**
- Modify script parameters for different benchmark configurations
- Adjust data generation parameters for specific use cases
- Configure neural network hyperparameters for PINO training

## 📈 **Output & Results**

### **Benchmark Results**
- Performance metrics and rankings
- Processing time comparisons
- Accuracy and reliability assessments
- Clinical application recommendations

### **Visualizations**
- Performance charts and graphs
- Confound analysis plots
- Neural network training curves
- Comparative analysis figures

---

**These scripts provide the complete benchmarking and analysis framework for the DataExploratoryProject, enabling comprehensive evaluation of long-range dependence estimation methods.**
