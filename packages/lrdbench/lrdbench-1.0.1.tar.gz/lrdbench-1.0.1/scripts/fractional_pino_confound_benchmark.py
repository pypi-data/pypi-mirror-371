#!/usr/bin/env python3
"""
Fractional PINO Confound Benchmark: Test Enhanced Fractional PINO Against Data Quality Issues

This script systematically tests the enhanced fractional PINO model against various classes of 
confounded data to assess its robustness and compare it with classical estimators.
This is a key component for the research paper on physics-informed fractional operator learning.
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import time
import psutil
import warnings
from pathlib import Path
from typing import Dict, List, Tuple, Any
import traceback
from scipy import signal, stats
import joblib
from itertools import product

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Import our existing estimators for comparison
import sys
sys.path.append('.')
from analysis.temporal.dfa.dfa_estimator import DFAEstimator
from analysis.temporal.rs.rs_estimator import RSEstimator
from analysis.spectral.gph.gph_estimator import GPHEstimator
from analysis.wavelet.cwt.cwt_estimator import CWTEstimator

# Import data models
from models.data_models.fbm.fbm_model import FractionalBrownianMotion
from models.data_models.fgn.fgn_model import FractionalGaussianNoise

# Import PyTorch for neural networks
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader, TensorDataset
    from torch.optim.lr_scheduler import ReduceLROnPlateau, CosineAnnealingLR
    TORCH_AVAILABLE = True
    print("✅ PyTorch imported successfully")
except ImportError:
    TORCH_AVAILABLE = False
    print("❌ PyTorch not available. Please install with: pip install torch")

# Import hpfracc for fractional calculus
try:
    import hpfracc as fc
    HPFRACC_AVAILABLE = True
    print("✅ hpfracc library imported successfully")
except ImportError:
    HPFRACC_AVAILABLE = False
    print("❌ hpfracc library not available. Using placeholder fractional operators")

class EnhancedFractionalPINO(nn.Module):
    """
    Enhanced Fractional PINO Model for Confound Benchmarking
    
    This is the same model from enhanced_fractional_pino_experiment_fixed.py
    but optimized for confound testing.
    """
    
    def __init__(self, input_size=1000, hidden_size=128, output_size=1, 
                 fractional_order=0.5, operator_type='marchaud', device='cpu'):
        super(EnhancedFractionalPINO, self).__init__()
        
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.fractional_order = fractional_order
        self.operator_type = operator_type
        self.device = device
        
        # Neural network layers with enhanced architecture
        self.feature_extractor = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.BatchNorm1d(hidden_size),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.BatchNorm1d(hidden_size),
            nn.Dropout(0.2)
        )
        
        # Physics-informed layer (fractional calculus integration)
        self.physics_layer = nn.Linear(hidden_size, hidden_size)
        
        # Enhanced output layer with residual connections
        self.output_layer = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_size // 2, hidden_size // 4),
            nn.ReLU(),
            nn.Linear(hidden_size // 4, output_size)
        )
        
        # Initialize fractional calculus operators
        if HPFRACC_AVAILABLE:
            if operator_type == 'marchaud':
                self.fractional_operator = fc.MarchaudDerivative(order=fractional_order)
            elif operator_type == 'laplacian':
                self.fractional_operator = fc.FractionalLaplacian(order=fractional_order)
            elif operator_type == 'fourier':
                self.fractional_operator = fc.FractionalFourierTransform(order=fractional_order)
            elif operator_type == 'hybrid':
                self.marchaud_op = fc.MarchaudDerivative(order=fractional_order)
                self.laplacian_op = fc.FractionalLaplacian(order=fractional_order)
                self.fourier_op = fc.FractionalFourierTransform(order=fractional_order)
                self.fractional_operator = None
            else:
                self.fractional_operator = fc.MarchaudDerivative(order=fractional_order)
        else:
            self.fractional_operator = None
            print("⚠️  Using placeholder fractional operator")
    
    def apply_fractional_operator(self, x):
        """Apply fractional calculus operator to input"""
        if HPFRACC_AVAILABLE:
            # Convert to numpy, apply operator, convert back
            x_np = x.detach().cpu().numpy()
            
            if self.operator_type == 'hybrid':
                # Apply multiple operators and combine
                x_marchaud = self.marchaud_op(x_np)
                x_laplacian = self.laplacian_op(x_np)
                x_fourier = self.fourier_op(x_np)
                
                # Combine operators (weighted average)
                x_frac = 0.4 * x_marchaud + 0.3 * x_laplacian + 0.3 * x_fourier
            else:
                x_frac = self.fractional_operator(x_np)
            
            return torch.tensor(x_frac, dtype=x.dtype, device=x.device)
        else:
            # Placeholder: simple power law transformation
            return torch.pow(torch.abs(x) + 1e-8, self.fractional_order)
    
    def physics_loss(self, x, y_pred):
        """Enhanced physics-informed loss incorporating multiple fractional calculus constraints"""
        # Apply fractional operator to input
        x_frac = self.apply_fractional_operator(x)
        
        # Multiple physics constraints
        # 1. Fractional derivative constraint
        physics_constraint_1 = torch.mean((x_frac - y_pred * x) ** 2)
        
        # 2. Scale invariance constraint (fractional processes are scale-invariant)
        scale_factor = torch.rand(1, device=x.device) * 0.5 + 0.5
        x_scaled = x * scale_factor
        x_frac_scaled = self.apply_fractional_operator(x_scaled)
        physics_constraint_2 = torch.mean((x_frac_scaled - y_pred * x_scaled) ** 2)
        
        # 3. Memory constraint (fractional processes have long memory)
        if x.shape[1] > 100:
            x_early = x[:, :x.shape[1]//2]
            x_late = x[:, x.shape[1]//2:]
            x_frac_early = self.apply_fractional_operator(x_early)
            x_frac_late = self.apply_fractional_operator(x_late)
            memory_constraint = torch.mean((x_frac_late - x_frac_early) ** 2)
        else:
            memory_constraint = torch.tensor(0.0, device=x.device)
        
        # Combine constraints
        total_physics_loss = physics_constraint_1 + 0.5 * physics_constraint_2 + 0.1 * memory_constraint
        
        return total_physics_loss
    
    def forward(self, x):
        # Feature extraction
        features = self.feature_extractor(x)
        
        # Physics-informed processing
        physics_features = self.physics_layer(features)
        
        # Apply fractional operator to physics features
        frac_features = self.apply_fractional_operator(physics_features)
        
        # Output prediction
        output = self.output_layer(frac_features)
        
        return output

class FractionalPINOEstimator:
    """
    Fractional PINO Estimator optimized for confound benchmarking
    """
    
    def __init__(self, input_size=1000, hidden_size=128, fractional_order=0.5, 
                 operator_type='marchaud', learning_rate=0.001, epochs=50, 
                 batch_size=32, device='cpu', use_scheduler=True):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.fractional_order = fractional_order
        self.operator_type = operator_type
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.batch_size = batch_size
        self.device = device
        self.use_scheduler = use_scheduler
        
        self.model = None
        self.is_trained = False
        self.best_val_loss = float('inf')
        
    def _prepare_data(self, data, target=None):
        """Prepare data for training/inference"""
        if isinstance(data, np.ndarray):
            data = torch.tensor(data, dtype=torch.float32)
        
        # Ensure correct shape - data should be 2D (batch_size, sequence_length)
        if data.dim() == 1:
            data = data.unsqueeze(0)  # Add batch dimension
        
        # Pad or truncate to input_size
        if data.shape[1] > self.input_size:
            data = data[:, :self.input_size]
        elif data.shape[1] < self.input_size:
            # Pad with zeros
            padding = torch.zeros(data.shape[0], self.input_size - data.shape[1])
            data = torch.cat([data, padding], dim=1)
        
        if target is not None:
            if isinstance(target, np.ndarray):
                target = torch.tensor(target, dtype=torch.float32)
            if target.dim() == 1:
                target = target.unsqueeze(0)  # Add batch dimension
            return data, target
        
        return data
    
    def train(self, X, y, val_split=0.2):
        """Train the fractional PINO model with validation"""
        # Ensure X and y are numpy arrays
        if isinstance(X, list):
            X = np.array(X)
        if isinstance(y, list):
            y = np.array(y)
        
        # Prepare data
        X_tensor, y_tensor = self._prepare_data(X, y)
        
        # Ensure we have enough samples for validation split
        n_samples = X_tensor.shape[0]
        if n_samples < 10:
            val_split = 0.0
        
        if val_split > 0:
            # Split into train/validation
            n_val = max(1, int(n_samples * val_split))
            indices = torch.randperm(n_samples)
            
            train_indices = indices[n_val:]
            val_indices = indices[:n_val]
            
            X_train, y_train = X_tensor[train_indices], y_tensor[train_indices]
            X_val, y_val = X_tensor[val_indices], y_tensor[val_indices]
        else:
            # Use all data for training
            X_train, y_train = X_tensor, y_tensor
            X_val, y_val = X_tensor, y_tensor
        
        # Initialize model
        self.model = EnhancedFractionalPINO(
            input_size=self.input_size,
            hidden_size=self.hidden_size,
            fractional_order=self.fractional_order,
            operator_type=self.operator_type,
            device=self.device
        ).to(self.device)
        
        # Loss function and optimizer
        criterion = nn.MSELoss()
        optimizer = optim.AdamW(self.model.parameters(), lr=self.learning_rate, weight_decay=1e-4)
        
        # Learning rate scheduler
        if self.use_scheduler:
            scheduler = CosineAnnealingLR(optimizer, T_max=self.epochs, eta_min=1e-6)
        
        # Create data loaders
        train_dataset = TensorDataset(X_train, y_train)
        val_dataset = TensorDataset(X_val, y_val)
        
        train_loader = DataLoader(train_dataset, batch_size=min(self.batch_size, len(train_dataset)), shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=min(self.batch_size, len(val_dataset)), shuffle=False)
        
        # Training loop with early stopping
        patience = 10
        patience_counter = 0
        
        for epoch in range(self.epochs):
            # Training phase
            self.model.train()
            train_loss = 0.0
            
            for batch_X, batch_y in train_loader:
                batch_X = batch_X.to(self.device)
                batch_y = batch_y.to(self.device)
                
                # Forward pass
                optimizer.zero_grad()
                predictions = self.model(batch_X)
                
                # Data loss
                data_loss = criterion(predictions, batch_y)
                
                # Physics loss
                physics_loss = self.model.physics_loss(batch_X, predictions)
                
                # Total loss (weighted combination)
                total_loss = data_loss + 0.1 * physics_loss
                
                # Backward pass
                total_loss.backward()
                
                # Gradient clipping
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                
                optimizer.step()
                
                train_loss += data_loss.item()
            
            # Validation phase
            self.model.eval()
            val_loss = 0.0
            
            with torch.no_grad():
                for batch_X, batch_y in val_loader:
                    batch_X = batch_X.to(self.device)
                    batch_y = batch_y.to(self.device)
                    
                    predictions = self.model(batch_X)
                    val_loss += criterion(predictions, batch_y).item()
            
            # Update learning rate
            if self.use_scheduler:
                scheduler.step()
            
            # Early stopping
            avg_val_loss = val_loss / len(val_loader) if len(val_loader) > 0 else 0
            
            if avg_val_loss < self.best_val_loss:
                self.best_val_loss = avg_val_loss
                patience_counter = 0
                # Save best model
                self.best_model_state = self.model.state_dict().copy()
            else:
                patience_counter += 1
            
            if patience_counter >= patience:
                break
        
        # Load best model
        if hasattr(self, 'best_model_state'):
            self.model.load_state_dict(self.best_model_state)
        
        self.is_trained = True
        
        return True
    
    def estimate(self, data):
        """Estimate Hurst parameter using trained model"""
        if not self.is_trained:
            raise ValueError("Model must be trained before estimation")
        
        # Prepare data
        X_tensor = self._prepare_data(data)
        X_tensor = X_tensor.to(self.device)
        
        # Make prediction
        self.model.eval()
        with torch.no_grad():
            predictions = self.model(X_tensor)
        
        # Convert to numpy and ensure valid range
        hurst_estimates = predictions.cpu().numpy().flatten()
        hurst_estimates = np.clip(hurst_estimates, 0.01, 0.99)  # Valid Hurst range
        
        return hurst_estimates

class FractionalPINOConfoundBenchmark:
    """
    Comprehensive benchmark for testing Fractional PINO against various confounds
    """
    
    def __init__(self):
        self.results = []
        self.confound_types = [
            'clean', 'noise', 'outliers', 'trends', 'seasonality', 
            'missing_data', 'smoothing', 'heteroscedasticity', 'nonstationarity'
        ]
        
        # Define confound parameters
        self.confound_params = {
            'noise': {'noise_level': 0.1},
            'outliers': {'outlier_ratio': 0.05},
            'trends': {'trend_strength': 0.5},
            'seasonality': {'seasonal_strength': 0.3},
            'missing_data': {'missing_ratio': 0.1},
            'smoothing': {'window_size': 5},
            'heteroscedasticity': {'variance_factor': 0.5},
            'nonstationarity': {'segment_length': 100}
        }
        
        # Initialize estimators
        self.estimators = self._initialize_estimators()
        
    def _initialize_estimators(self):
        """Initialize all estimators for comparison"""
        estimators = {}
        
        # Classical estimators for comparison
        estimators['DFA'] = {
            'class': DFAEstimator,
            'params': {},
            'category': 'temporal'
        }
        
        estimators['R/S'] = {
            'class': RSEstimator,
            'params': {},
            'category': 'temporal'
        }
        
        estimators['GPH'] = {
            'class': GPHEstimator,
            'params': {},
            'category': 'spectral'
        }
        
        estimators['CWT'] = {
            'class': CWTEstimator,
            'params': {'scales': np.logspace(1, 2, 8)},
            'category': 'wavelet'
        }
        
        # Fractional PINO variants
        if TORCH_AVAILABLE:
            estimators['PINO-Marchaud'] = {
                'class': FractionalPINOEstimator,
                'params': {
                    'input_size': 1000,
                    'hidden_size': 128,
                    'fractional_order': 0.5,
                    'operator_type': 'marchaud',
                    'learning_rate': 0.001,
                    'epochs': 30,
                    'batch_size': 32,
                    'device': 'cpu'
                },
                'category': 'neural'
            }
            
            estimators['PINO-Laplacian'] = {
                'class': FractionalPINOEstimator,
                'params': {
                    'input_size': 1000,
                    'hidden_size': 128,
                    'fractional_order': 0.5,
                    'operator_type': 'laplacian',
                    'learning_rate': 0.001,
                    'epochs': 30,
                    'batch_size': 32,
                    'device': 'cpu'
                },
                'category': 'neural'
            }
            
            estimators['PINO-Hybrid'] = {
                'class': FractionalPINOEstimator,
                'params': {
                    'input_size': 1000,
                    'hidden_size': 128,
                    'fractional_order': 0.5,
                    'operator_type': 'hybrid',
                    'learning_rate': 0.001,
                    'epochs': 30,
                    'batch_size': 32,
                    'device': 'cpu'
                },
                'category': 'neural'
            }
        
        return estimators
    
    def apply_confound(self, data: np.ndarray, confound_type: str, confound_params: Dict) -> np.ndarray:
        """Apply a specific confound to the data."""
        confounded_data = data.copy()
        
        if confound_type == 'clean':
            return confounded_data
        
        elif confound_type == 'noise':
            noise_level = confound_params['noise_level']
            noise = np.random.normal(0, noise_level, len(data))
            confounded_data += noise
        
        elif confound_type == 'outliers':
            outlier_ratio = confound_params['outlier_ratio']
            n_outliers = int(len(data) * outlier_ratio)
            outlier_indices = np.random.choice(len(data), n_outliers, replace=False)
            outlier_magnitude = 3 * np.std(data)
            confounded_data[outlier_indices] += np.random.choice([-1, 1], n_outliers) * outlier_magnitude
        
        elif confound_type == 'trends':
            trend_strength = confound_params['trend_strength']
            # Linear trend
            linear_trend = np.linspace(0, trend_strength, len(data))
            # Quadratic trend
            quadratic_trend = trend_strength * (np.linspace(-1, 1, len(data)) ** 2)
            confounded_data += linear_trend + quadratic_trend
        
        elif confound_type == 'seasonality':
            seasonal_strength = confound_params['seasonal_strength']
            # Multiple seasonal components
            t = np.arange(len(data))
            seasonal1 = seasonal_strength * np.sin(2 * np.pi * t / 50)  # Short period
            seasonal2 = seasonal_strength * 0.5 * np.sin(2 * np.pi * t / 100)  # Medium period
            confounded_data += seasonal1 + seasonal2
        
        elif confound_type == 'missing_data':
            missing_ratio = confound_params['missing_ratio']
            n_missing = int(len(data) * missing_ratio)
            missing_indices = np.random.choice(len(data), n_missing, replace=False)
            confounded_data[missing_indices] = np.nan
        
        elif confound_type == 'smoothing':
            window_size = confound_params['window_size']
            if window_size > 1:
                confounded_data = signal.convolve(data, np.ones(window_size)/window_size, mode='same')
        
        elif confound_type == 'heteroscedasticity':
            variance_factor = confound_params['variance_factor']
            # Create varying variance pattern
            variance_pattern = 1 + variance_factor * np.sin(np.linspace(0, 4*np.pi, len(data)))
            confounded_data *= np.sqrt(variance_pattern)
        
        elif confound_type == 'nonstationarity':
            segment_length = confound_params['segment_length']
            n_segments = len(data) // segment_length
            
            for i in range(n_segments):
                start_idx = i * segment_length
                end_idx = start_idx + segment_length
                
                # Add different mean to each segment
                segment_mean = np.random.normal(0, 0.5)
                confounded_data[start_idx:end_idx] += segment_mean
        
        return confounded_data
    
    def test_single_estimator(self, estimator_name: str, estimator_info: Dict, 
                             data: np.ndarray, true_hurst: float) -> Dict[str, Any]:
        """Test a single estimator and return detailed results."""
        try:
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            # Create estimator instance
            estimator = estimator_info['class'](**estimator_info['params'])
            
            # For neural estimators, we need to train first
            if estimator_info['category'] == 'neural':
                # Generate training data
                n_train_samples = 100
                train_data = []
                train_hurst = []
                
                for _ in range(n_train_samples):
                    H = np.random.uniform(0.1, 0.9)
                    fbm = FractionalBrownianMotion(H=H)
                    sample = fbm.generate(1000)
                    train_data.append(sample)
                    train_hurst.append(H)
                
                # Train the model
                estimator.train(train_data, train_hurst, val_split=0.2)
                
                # Run estimation
                results = estimator.estimate(data)
                estimated_hurst = results[0] if isinstance(results, (list, np.ndarray)) else results
            else:
                # Classical estimators
                results = estimator.estimate(data)
                
                # Extract estimated Hurst parameter
                estimated_hurst = results.get('hurst_parameter', None)
                if estimated_hurst is None:
                    for key in ['H', 'hurst', 'fractal_dimension']:
                        if key in results:
                            estimated_hurst = results[key]
                            break
            
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            execution_time = end_time - start_time
            memory_usage = end_memory - start_memory
            
            # Calculate accuracy metrics
            if estimated_hurst is not None and true_hurst is not None:
                absolute_error = abs(estimated_hurst - true_hurst)
                relative_error = absolute_error / true_hurst if true_hurst != 0 else float('inf')
                squared_error = (estimated_hurst - true_hurst) ** 2
            else:
                absolute_error = relative_error = squared_error = float('inf')
            
            result = {
                'estimator_name': estimator_name,
                'estimated_hurst': estimated_hurst,
                'true_hurst': true_hurst,
                'execution_time': execution_time,
                'memory_usage': memory_usage,
                'absolute_error': absolute_error,
                'relative_error': relative_error,
                'squared_error': squared_error,
                'success': True,
                'raw_results': results
            }
            
            return result
            
        except Exception as e:
            print(f"Error testing {estimator_name}: {str(e)}")
            return {
                'estimator_name': estimator_name,
                'estimated_hurst': None,
                'true_hurst': true_hurst,
                'execution_time': 0,
                'memory_usage': 0,
                'absolute_error': float('inf'),
                'relative_error': float('inf'),
                'squared_error': float('inf'),
                'success': False,
                'error': str(e)
            }
    
    def run_benchmark(self, n_samples_per_confound=20, hurst_range=(0.1, 0.9)):
        """Run the comprehensive confound benchmark"""
        print("🚀 Starting Fractional PINO Confound Benchmark")
        print("="*60)
        
        results = []
        
        for confound_type in self.confound_types:
            print(f"\n📊 Testing confound: {confound_type}")
            
            for i in range(n_samples_per_confound):
                # Generate true Hurst parameter
                true_hurst = np.random.uniform(hurst_range[0], hurst_range[1])
                
                # Generate clean fBm data
                fbm = FractionalBrownianMotion(H=true_hurst)
                clean_data = fbm.generate(1000)
                
                # Apply confound
                if confound_type == 'clean':
                    confounded_data = clean_data
                else:
                    confounded_data = self.apply_confound(clean_data, confound_type, self.confound_params[confound_type])
                
                # Skip if data contains NaN (missing data case)
                if np.any(np.isnan(confounded_data)):
                    # For missing data, interpolate
                    confounded_data = pd.Series(confounded_data).interpolate().values
                
                # Test each estimator
                for estimator_name, estimator_info in self.estimators.items():
                    print(f"  Testing {estimator_name} on sample {i+1}/{n_samples_per_confound}")
                    
                    result = self.test_single_estimator(estimator_name, estimator_info, confounded_data, true_hurst)
                    result['confound_type'] = confound_type
                    result['sample_id'] = i
                    
                    results.append(result)
        
        self.results = results
        print(f"\n✅ Benchmark completed! Total tests: {len(results)}")
        
        return results
    
    def analyze_results(self):
        """Analyze and summarize benchmark results"""
        if not self.results:
            print("No results to analyze. Run benchmark first.")
            return
        
        # Convert to DataFrame
        df = pd.DataFrame(self.results)
        
        # Filter successful results
        successful_df = df[df['success'] == True].copy()
        
        if len(successful_df) == 0:
            print("No successful results to analyze.")
            return
        
        # Calculate summary statistics by confound type and estimator
        summary = successful_df.groupby(['confound_type', 'estimator_name']).agg({
            'absolute_error': ['mean', 'std'],
            'relative_error': ['mean', 'std'],
            'execution_time': ['mean', 'std'],
            'memory_usage': ['mean', 'std'],
            'success': 'count'
        }).round(4)
        
        # Flatten column names
        summary.columns = ['_'.join(col).strip() for col in summary.columns]
        summary = summary.reset_index()
        
        # Calculate success rates
        success_rates = df.groupby(['confound_type', 'estimator_name'])['success'].agg(['sum', 'count'])
        success_rates['success_rate'] = (success_rates['sum'] / success_rates['count'] * 100).round(1)
        success_rates = success_rates.reset_index()
        
        # Merge with summary
        final_summary = summary.merge(success_rates[['confound_type', 'estimator_name', 'success_rate']], 
                                    on=['confound_type', 'estimator_name'])
        
        return final_summary, successful_df
    
    def plot_results(self, save_path=None):
        """Create comprehensive visualization of results"""
        if not self.results:
            print("No results to plot. Run benchmark first.")
            return
        
        summary, successful_df = self.analyze_results()
        
        if len(successful_df) == 0:
            print("No successful results to plot.")
            return
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Fractional PINO Confound Benchmark Results', fontsize=16, fontweight='bold')
        
        # 1. Mean Absolute Error by Confound Type
        ax1 = axes[0, 0]
        pivot_mae = successful_df.pivot_table(
            values='absolute_error', 
            index='confound_type', 
            columns='estimator_name', 
            aggfunc='mean'
        )
        pivot_mae.plot(kind='bar', ax=ax1, width=0.8)
        ax1.set_title('Mean Absolute Error by Confound Type')
        ax1.set_ylabel('Mean Absolute Error')
        ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax1.tick_params(axis='x', rotation=45)
        
        # 2. Success Rate by Confound Type
        ax2 = axes[0, 1]
        success_pivot = successful_df.groupby(['confound_type', 'estimator_name'])['success'].count().unstack()
        total_tests = successful_df.groupby(['confound_type', 'estimator_name']).size().unstack()
        success_rate_pivot = (success_pivot / total_tests * 100).fillna(0)
        success_rate_pivot.plot(kind='bar', ax=ax2, width=0.8)
        ax2.set_title('Success Rate by Confound Type')
        ax2.set_ylabel('Success Rate (%)')
        ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax2.tick_params(axis='x', rotation=45)
        
        # 3. Execution Time Comparison
        ax3 = axes[1, 0]
        pivot_time = successful_df.pivot_table(
            values='execution_time', 
            index='confound_type', 
            columns='estimator_name', 
            aggfunc='mean'
        )
        pivot_time.plot(kind='bar', ax=ax3, width=0.8)
        ax3.set_title('Mean Execution Time by Confound Type')
        ax3.set_ylabel('Execution Time (seconds)')
        ax3.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax3.tick_params(axis='x', rotation=45)
        
        # 4. Estimator Performance Heatmap
        ax4 = axes[1, 1]
        estimator_performance = successful_df.groupby('estimator_name')['absolute_error'].mean().sort_values()
        colors = plt.cm.viridis(np.linspace(0, 1, len(estimator_performance)))
        bars = ax4.bar(range(len(estimator_performance)), estimator_performance.values, color=colors)
        ax4.set_title('Overall Estimator Performance (Mean Absolute Error)')
        ax4.set_ylabel('Mean Absolute Error')
        ax4.set_xticks(range(len(estimator_performance)))
        ax4.set_xticklabels(estimator_performance.index, rotation=45, ha='right')
        
        # Add value labels on bars
        for bar, value in zip(bars, estimator_performance.values):
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                    f'{value:.3f}', ha='center', va='bottom', fontsize=8)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"📊 Results plot saved to {save_path}")
        
        plt.show()
        
        return fig

def main():
    """Main function to run the fractional PINO confound benchmark"""
    print("🔬 Fractional PINO Confound Benchmark")
    print("Testing Enhanced Fractional PINO against Data Quality Issues")
    print("="*70)
    
    # Check dependencies
    if not TORCH_AVAILABLE:
        print("❌ PyTorch is required for this benchmark")
        return
    
    # Set random seeds for reproducibility
    np.random.seed(42)
    torch.manual_seed(42)
    
    # Create benchmark instance
    benchmark = FractionalPINOConfoundBenchmark()
    
    # Run benchmark
    results = benchmark.run_benchmark(n_samples_per_confound=15)  # Reduced for faster testing
    
    # Analyze results
    summary, successful_df = benchmark.analyze_results()
    
    # Print summary
    print("\n📊 BENCHMARK SUMMARY")
    print("="*50)
    print(summary.to_string(index=False))
    
    # Create visualization
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    plot_path = f"fractional_pino_confound_benchmark_{timestamp}.png"
    benchmark.plot_results(save_path=plot_path)
    
    # Save results
    results_path = f"fractional_pino_confound_results_{timestamp}.pkl"
    joblib.dump({
        'results': results,
        'summary': summary,
        'successful_df': successful_df,
        'timestamp': timestamp
    }, results_path)
    
    print(f"\n✅ Results saved to {results_path}")
    print(f"📊 Plot saved to {plot_path}")
    
    # Print key findings
    print("\n🔍 KEY FINDINGS")
    print("="*30)
    
    # Best overall estimator
    best_overall = summary.loc[summary['absolute_error_mean'].idxmin()]
    print(f"Best overall estimator: {best_overall['estimator_name']} (MAE: {best_overall['absolute_error_mean']:.4f})")
    
    # Best neural estimator
    neural_summary = summary[summary['estimator_name'].str.contains('PINO')]
    if len(neural_summary) > 0:
        best_neural = neural_summary.loc[neural_summary['absolute_error_mean'].idxmin()]
        print(f"Best neural estimator: {best_neural['estimator_name']} (MAE: {best_neural['absolute_error_mean']:.4f})")
    
    # Most robust confound
    confound_summary = summary.groupby('confound_type')['absolute_error_mean'].mean().sort_values()
    most_robust_confound = confound_summary.index[0]
    least_robust_confound = confound_summary.index[-1]
    print(f"Most robust confound: {most_robust_confound} (avg MAE: {confound_summary.iloc[0]:.4f})")
    print(f"Least robust confound: {least_robust_confound} (avg MAE: {confound_summary.iloc[-1]:.4f})")
    
    print("\n🎉 Benchmark completed successfully!")

if __name__ == "__main__":
    main()
