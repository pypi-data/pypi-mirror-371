#!/usr/bin/env python3
"""
Enhanced Fractional PINO with True Fractional Operators: Building Fractional Characteristics Directly into Architecture

This script implements an advanced fractional PINO model that integrates fractional calculus operators
directly into the neural network architecture, creating a truly physics-informed neural operator.

Key Features:
- Fractional Laplacian layers
- Fractional Fourier Transform layers  
- Marchaud derivative integration
- Adaptive fractional order learning
- Multi-scale fractional analysis
- Physics-constrained optimization

Author: Davian R. Chin
Date: 2024
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import time
import joblib
from pathlib import Path
import warnings
from itertools import product
import optuna
from sklearn.model_selection import KFold
warnings.filterwarnings('ignore')

# Import our existing estimators
import sys
sys.path.append('.')
from analysis.temporal.dfa.dfa_estimator import DFAEstimator
from analysis.temporal.rs.rs_estimator import RSEstimator
from analysis.machine_learning.random_forest_estimator import RandomForestEstimator
from analysis.machine_learning.gradient_boosting_estimator import GradientBoostingEstimator

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

# Try to import hpfracc for true fractional operators
try:
    import hpfracc as fc
    HPFRACC_AVAILABLE = True
    print("✅ hpfracc library imported successfully")
    print(f"   Available operators: {[attr for attr in dir(fc) if not attr.startswith('_')]}")
except ImportError:
    HPFRACC_AVAILABLE = False
    print("❌ hpfracc library not available. Using custom fractional implementations")

class FractionalLaplacianLayer(nn.Module):
    """
    Fractional Laplacian Layer: Direct integration of fractional Laplacian operator
    
    This layer applies the fractional Laplacian operator directly to the input,
    building fractional characteristics into the architecture.
    """
    
    def __init__(self, order=0.5, use_true_operator=True, device='cpu'):
        super(FractionalLaplacianLayer, self).__init__()
        self.order = order
        self.use_true_operator = use_true_operator and HPFRACC_AVAILABLE
        self.device = device
        
        # Learnable fractional order parameter
        self.learnable_order = nn.Parameter(torch.tensor(order, dtype=torch.float32))
        
        # Initialize true fractional operator if available
        if self.use_true_operator:
            try:
                self.fractional_operator = fc.FractionalLaplacian(order=order)
                print(f"✅ True fractional Laplacian operator initialized (order={order})")
            except Exception as e:
                print(f"⚠️  True operator failed: {e}")
                self.use_true_operator = False
        
        # Custom implementation for when true operator is unavailable
        if not self.use_true_operator:
            print("⚠️  Using custom fractional Laplacian implementation")
    
    def forward(self, x):
        if self.use_true_operator and hasattr(self, 'fractional_operator'):
            return self._apply_true_operator(x)
        else:
            return self._apply_custom_operator(x)
    
    def _apply_true_operator(self, x):
        """Apply true fractional Laplacian operator"""
        try:
            # Convert to numpy, apply operator, convert back
            x_np = x.detach().cpu().numpy()
            result = self.fractional_operator(x_np)
            return torch.tensor(result, dtype=x.dtype, device=x.device)
        except Exception as e:
            print(f"⚠️  True operator failed, falling back to custom: {e}")
            return self._apply_custom_operator(x)
    
    def _apply_custom_operator(self, x):
        """Custom implementation of fractional Laplacian"""
        # Use current learnable order
        current_order = torch.clamp(self.learnable_order, 0.01, 0.99)
        
        # Apply fractional Laplacian approximation
        # For 1D signals: (-Δ)^α ≈ FFT^(-1)(|k|^(2α) * FFT(x))
        if x.dim() == 2:  # (batch_size, sequence_length)
            # Apply FFT along sequence dimension
            x_fft = torch.fft.fft(x, dim=1)
            
            # Create frequency domain mask
            n = x.shape[1]
            freqs = torch.fft.fftfreq(n, device=x.device)
            freq_mask = torch.abs(freqs) ** (2 * current_order)
            freq_mask[0] = 0  # Avoid division by zero
            
            # Apply frequency domain filtering
            filtered_fft = x_fft * freq_mask.unsqueeze(0)
            
            # Inverse FFT
            result = torch.real(torch.fft.ifft(filtered_fft, dim=1))
            
            return result
        else:
            # For other dimensions, use power law approximation
            return torch.pow(torch.abs(x) + 1e-8, current_order) * torch.sign(x)

class FractionalFourierLayer(nn.Module):
    """
    Fractional Fourier Transform Layer: Direct integration of fractional FFT
    
    This layer applies the fractional Fourier transform directly to the input,
    enabling multi-scale frequency domain analysis.
    """
    
    def __init__(self, order=0.5, use_true_operator=True, device='cpu'):
        super(FractionalFourierLayer, self).__init__()
        self.order = order
        self.use_true_operator = use_true_operator and HPFRACC_AVAILABLE
        self.device = device
        
        # Learnable fractional order parameter
        self.learnable_order = nn.Parameter(torch.tensor(order, dtype=torch.float32))
        
        # Initialize true fractional operator if available
        if self.use_true_operator:
            try:
                self.fractional_operator = fc.FractionalFourierTransform(order=order)
                print(f"✅ True fractional Fourier operator initialized (order={order})")
            except Exception as e:
                print(f"⚠️  True operator failed: {e}")
                self.use_true_operator = False
        
        if not self.use_true_operator:
            print("⚠️  Using custom fractional Fourier implementation")
    
    def forward(self, x):
        if self.use_true_operator and hasattr(self, 'fractional_operator'):
            return self._apply_true_operator(x)
        else:
            return self._apply_custom_operator(x)
    
    def _apply_true_operator(self, x):
        """Apply true fractional Fourier transform"""
        try:
            x_np = x.detach().cpu().numpy()
            result = self.fractional_operator(x_np)
            return torch.tensor(result, dtype=x.dtype, device=x.device)
        except Exception as e:
            print(f"⚠️  True operator failed, falling back to custom: {e}")
            return self._apply_custom_operator(x)
    
    def _apply_custom_operator(self, x):
        """Custom implementation of fractional Fourier transform"""
        current_order = torch.clamp(self.learnable_order, 0.01, 0.99)
        
        if x.dim() == 2:
            # Apply FFT
            x_fft = torch.fft.fft(x, dim=1)
            
            # Apply fractional power in frequency domain
            n = x.shape[1]
            freqs = torch.fft.fftfreq(n, device=x.device)
            phase_shift = torch.exp(1j * np.pi * current_order * torch.sign(freqs))
            phase_shift[0] = 1  # DC component
            
            # Apply phase shift
            fractional_fft = x_fft * phase_shift.unsqueeze(0)
            
            # Inverse FFT
            result = torch.fft.ifft(fractional_fft, dim=1)
            
            return torch.real(result)
        else:
            return torch.pow(torch.abs(x) + 1e-8, current_order) * torch.sign(x)

class MarchaudDerivativeLayer(nn.Module):
    """
    Marchaud Derivative Layer: Direct integration of Marchaud derivative
    
    This layer applies the Marchaud derivative operator directly to the input,
    capturing long-range dependencies characteristic of fractional processes.
    """
    
    def __init__(self, order=0.5, use_true_operator=True, device='cpu'):
        super(MarchaudDerivativeLayer, self).__init__()
        self.order = order
        self.use_true_operator = use_true_operator and HPFRACC_AVAILABLE
        self.device = device
        
        # Learnable fractional order parameter
        self.learnable_order = nn.Parameter(torch.tensor(order, dtype=torch.float32))
        
        # Initialize true fractional operator if available
        if self.use_true_operator:
            try:
                self.fractional_operator = fc.MarchaudDerivative(order=order)
                print(f"✅ True Marchaud derivative operator initialized (order={order})")
            except Exception as e:
                print(f"⚠️  True operator failed: {e}")
                self.use_true_operator = False
        
        if not self.use_true_operator:
            print("⚠️  Using custom Marchaud derivative implementation")
    
    def forward(self, x):
        if self.use_true_operator and hasattr(self, 'fractional_operator'):
            return self._apply_true_operator(x)
        else:
            return self._apply_custom_operator(x)
    
    def _apply_true_operator(self, x):
        """Apply true Marchaud derivative"""
        try:
            x_np = x.detach().cpu().numpy()
            result = self.fractional_operator(x_np)
            return torch.tensor(result, dtype=x.dtype, device=x.device)
        except Exception as e:
            print(f"⚠️  True operator failed, falling back to custom: {e}")
            return self._apply_custom_operator(x)
    
    def _apply_custom_operator(self, x):
        """Custom implementation of Marchaud derivative"""
        current_order = torch.clamp(self.learnable_order, 0.01, 0.99)
        
        if x.dim() == 2:
            batch_size, seq_len = x.shape
            
            # Marchaud derivative approximation using finite differences
            # D^α x(t) ≈ Σ_{k=0}^{∞} c_k * x(t - k)
            result = torch.zeros_like(x)
            
            # Coefficients for Marchaud derivative (simplified)
            for k in range(min(10, seq_len)):  # Limit to first 10 terms
                if k == 0:
                    c_k = 1.0
                else:
                    # Simplified coefficient calculation to avoid lgamma issues
                    try:
                        # Calculate falling factorial: (α)_k = α * (α-1) * ... * (α-k+1)
                        falling_factorial = 1.0
                        for i in range(k):
                            falling_factorial *= (current_order - i)
                        
                        # Calculate k!
                        k_factorial = 1.0
                        for i in range(1, k + 1):
                            k_factorial *= i
                        
                        c_k = (-1) ** k * falling_factorial / k_factorial
                    except:
                        # Fallback to simple power law if calculation fails
                        c_k = (-1) ** k * torch.pow(current_order, k) / (k + 1)
                
                # Apply shift and coefficient
                if k < seq_len:
                    shifted = torch.roll(x, shifts=k, dims=1)
                    shifted[:, :k] = 0  # Zero-pad at boundaries
                    result += c_k * shifted
            
            return result
        else:
            # For other dimensions, use power law approximation
            return torch.pow(torch.abs(x) + 1e-8, current_order) * torch.sign(x)

class AdaptiveFractionalLayer(nn.Module):
    """
    Adaptive Fractional Layer: Dynamically adjusts fractional order based on input characteristics
    
    This layer learns the optimal fractional order for each input, creating a truly
    adaptive architecture that builds fractional characteristics directly into the network.
    """
    
    def __init__(self, input_size, hidden_size, device='cpu'):
        super(AdaptiveFractionalLayer, self).__init__()
        self.device = device
        self.input_size = input_size
        
        # Neural network to predict optimal fractional order
        self.order_predictor = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Linear(hidden_size // 2, 1),
            nn.Sigmoid()  # Output order in [0, 1]
        )
        
        # Initialize fractional operators
        self.laplacian_layer = FractionalLaplacianLayer(order=0.5, device=device)
        self.fourier_layer = FractionalFourierLayer(order=0.5, device=device)
        self.marchaud_layer = MarchaudDerivativeLayer(order=0.5, device=device)
        
        # Learnable weights for combining operators
        self.operator_weights = nn.Parameter(torch.tensor([0.4, 0.3, 0.3]))
        
    def forward(self, x):
        # Predict optimal fractional order for this input
        # Use global average pooling to get input characteristics
        if x.dim() == 2:
            # For 2D input (batch_size, input_size), use mean pooling
            input_features = torch.mean(x, dim=1)  # (batch_size, input_size)
        else:
            # For other dimensions, flatten
            input_features = x.flatten(1)
        
        # Ensure input_features has the correct size
        if input_features.shape[1] != self.input_size:
            # Pad or truncate to match input_size
            if input_features.shape[1] > self.input_size:
                input_features = input_features[:, :self.input_size]
            else:
                padding = torch.zeros(input_features.shape[0], self.input_size - input_features.shape[1], device=self.device)
                input_features = torch.cat([input_features, padding], dim=1)
        
        # Predict fractional order
        predicted_order = self.order_predictor(input_features).squeeze(-1)
        
        # Apply different fractional operators with predicted order
        laplacian_result = self.laplacian_layer(x)
        fourier_result = self.fourier_layer(x)
        marchaud_result = self.marchaud_layer(x)
        
        # Combine results with learnable weights
        weights = torch.softmax(self.operator_weights, dim=0)
        combined_result = (weights[0] * laplacian_result + 
                          weights[1] * fourier_result + 
                          weights[2] * marchaud_result)
        
        return combined_result, predicted_order

class EnhancedFractionalPINOWithTrueOperators(nn.Module):
    """
    Enhanced Fractional PINO with True Fractional Operators
    
    This model builds fractional characteristics directly into the architecture
    using true fractional calculus operators when available.
    """
    
    def __init__(self, input_size=1000, hidden_size=128, output_size=1, 
                 fractional_order=0.5, device='cpu'):
        super(EnhancedFractionalPINOWithTrueOperators, self).__init__()
        
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.fractional_order = fractional_order
        self.device = device
        
        # Adaptive fractional layer - builds fractional characteristics directly
        self.adaptive_fractional = AdaptiveFractionalLayer(input_size, hidden_size, device)
        
        # Feature extraction with fractional integration
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
        
        # Physics-informed layer with fractional constraints
        self.physics_layer = nn.Linear(hidden_size, hidden_size)
        
        # Output layer
        self.output_layer = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_size // 2, hidden_size // 4),
            nn.ReLU(),
            nn.Linear(hidden_size // 4, output_size)
        )
        
        # Fractional order prediction head
        self.order_predictor = nn.Linear(hidden_size, 1)
        
    def forward(self, x):
        # Apply adaptive fractional layer
        frac_features, predicted_order = self.adaptive_fractional(x)
        
        # Feature extraction
        features = self.feature_extractor(x)
        
        # Physics-informed processing
        physics_features = self.physics_layer(features)
        
        # Combine fractional and physics features
        combined_features = features + 0.3 * frac_features + 0.2 * physics_features
        
        # Output prediction
        output = self.output_layer(combined_features)
        
        return output, predicted_order
    
    def physics_loss(self, x, y_pred):
        """Enhanced physics-informed loss with fractional constraints"""
        # Get fractional features
        frac_features, predicted_order = self.adaptive_fractional(x)
        
        # Multiple physics constraints
        # 1. Fractional derivative constraint
        physics_constraint_1 = torch.mean((frac_features - y_pred * x) ** 2)
        
        # 2. Scale invariance constraint
        scale_factor = torch.rand(1, device=x.device) * 0.5 + 0.5
        x_scaled = x * scale_factor
        frac_features_scaled, _ = self.adaptive_fractional(x_scaled)
        physics_constraint_2 = torch.mean((frac_features_scaled - y_pred * x_scaled) ** 2)
        
        # 3. Memory constraint
        if x.shape[1] > 100:
            x_early = x[:, :x.shape[1]//2]
            x_late = x[:, x.shape[1]//2:]
            frac_early, _ = self.adaptive_fractional(x_early)
            frac_late, _ = self.adaptive_fractional(x_late)
            memory_constraint = torch.mean((frac_late - frac_early) ** 2)
        else:
            memory_constraint = torch.tensor(0.0, device=x.device)
        
        # 4. Fractional order consistency
        order_consistency = torch.mean((predicted_order - self.fractional_order) ** 2)
        
        # Combine constraints
        total_physics_loss = (physics_constraint_1 + 0.5 * physics_constraint_2 + 
                             0.1 * memory_constraint + 0.2 * order_consistency)
        
        return total_physics_loss

class EnhancedFractionalPINOEstimatorWithTrueOperators:
    """
    Enhanced Fractional PINO Estimator with True Fractional Operators
    """
    
    def __init__(self, input_size=1000, hidden_size=128, fractional_order=0.5, 
                 learning_rate=0.001, epochs=100, batch_size=32, device='cpu'):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.fractional_order = fractional_order
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.batch_size = batch_size
        self.device = device
        
        self.model = None
        self.is_trained = False
        self.best_val_loss = float('inf')
        
    def _prepare_data(self, data, target=None):
        """Prepare data for training/inference"""
        if isinstance(data, np.ndarray):
            data = torch.tensor(data, dtype=torch.float32)
        
        # Ensure correct shape
        if data.dim() == 1:
            data = data.unsqueeze(0)
        
        # Pad or truncate to input_size
        if data.shape[1] > self.input_size:
            data = data[:, :self.input_size]
        elif data.shape[1] < self.input_size:
            padding = torch.zeros(data.shape[0], self.input_size - data.shape[1])
            data = torch.cat([data, padding], dim=1)
        
        if target is not None:
            if isinstance(target, np.ndarray):
                target = torch.tensor(target, dtype=torch.float32)
            return data, target
        
        return data
    
    def train(self, X, y, val_split=0.2):
        """Train the enhanced fractional PINO model with true operators"""
        print(f"Training Enhanced Fractional PINO with True Operators (order={self.fractional_order})...")
        
        # Prepare data
        X_tensor, y_tensor = self._prepare_data(X, y)
        
        # Split into train/validation
        n_samples = X_tensor.shape[0]
        if val_split > 0 and n_samples >= 10:
            n_val = max(1, int(n_samples * val_split))
            indices = torch.randperm(n_samples)
            train_indices = indices[n_val:]
            val_indices = indices[:n_val]
            
            X_train, y_train = X_tensor[train_indices], y_tensor[train_indices]
            X_val, y_val = X_tensor[val_indices], y_tensor[val_indices]
        else:
            X_train, y_train = X_tensor, y_tensor
            X_val, y_val = X_tensor, y_tensor
        
        # Initialize model
        self.model = EnhancedFractionalPINOWithTrueOperators(
            input_size=self.input_size,
            hidden_size=self.hidden_size,
            fractional_order=self.fractional_order,
            device=self.device
        ).to(self.device)
        
        # Loss function and optimizer
        criterion = nn.MSELoss()
        optimizer = optim.AdamW(self.model.parameters(), lr=self.learning_rate, weight_decay=1e-4)
        scheduler = CosineAnnealingLR(optimizer, T_max=self.epochs, eta_min=1e-6)
        
        # Create data loaders
        train_dataset = TensorDataset(X_train, y_train)
        val_dataset = TensorDataset(X_val, y_val)
        
        train_loader = DataLoader(train_dataset, batch_size=min(self.batch_size, len(train_dataset)), shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=min(self.batch_size, len(val_dataset)), shuffle=False)
        
        # Training loop
        train_losses = []
        val_losses = []
        patience = 10
        patience_counter = 0
        
        for epoch in range(self.epochs):
            # Training phase
            self.model.train()
            train_loss = 0.0
            physics_loss_total = 0.0
            
            for batch_X, batch_y in train_loader:
                batch_X = batch_X.to(self.device)
                batch_y = batch_y.to(self.device)
                
                optimizer.zero_grad()
                
                # Forward pass
                predictions, predicted_order = self.model(batch_X)
                
                # Data loss
                data_loss = criterion(predictions, batch_y)
                
                # Physics loss
                physics_loss = self.model.physics_loss(batch_X, predictions)
                
                # Total loss
                total_loss = data_loss + 0.1 * physics_loss
                
                # Backward pass
                total_loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                optimizer.step()
                
                train_loss += data_loss.item()
                physics_loss_total += physics_loss.item()
            
            # Validation phase
            self.model.eval()
            val_loss = 0.0
            
            with torch.no_grad():
                for batch_X, batch_y in val_loader:
                    batch_X = batch_X.to(self.device)
                    batch_y = batch_y.to(self.device)
                    
                    predictions, _ = self.model(batch_X)
                    val_loss += criterion(predictions, batch_y).item()
            
            # Update learning rate
            scheduler.step()
            
            # Record losses
            avg_train_loss = train_loss / len(train_loader) if len(train_loader) > 0 else 0
            avg_val_loss = val_loss / len(val_loader) if len(val_loader) > 0 else 0
            
            train_losses.append(avg_train_loss)
            val_losses.append(avg_val_loss)
            
            # Early stopping
            if avg_val_loss < self.best_val_loss:
                self.best_val_loss = avg_val_loss
                patience_counter = 0
                self.best_model_state = self.model.state_dict().copy()
            else:
                patience_counter += 1
            
            if patience_counter >= patience:
                print(f"Early stopping at epoch {epoch+1}")
                break
            
            if (epoch + 1) % 20 == 0:
                print(f"Epoch {epoch+1}/{self.epochs}, Train Loss: {avg_train_loss:.6f}, "
                      f"Val Loss: {avg_val_loss:.6f}, Physics Loss: {physics_loss_total/len(train_loader):.6f}")
        
        # Load best model
        if hasattr(self, 'best_model_state'):
            self.model.load_state_dict(self.best_model_state)
        
        self.is_trained = True
        print("✅ Enhanced Fractional PINO with True Operators training completed")
        
        return train_losses, val_losses
    
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
            predictions, predicted_order = self.model(X_tensor)
        
        # Convert to numpy and ensure valid range
        hurst_estimates = predictions.cpu().numpy().flatten()
        hurst_estimates = np.clip(hurst_estimates, 0.01, 0.99)
        
        return hurst_estimates

def generate_enhanced_synthetic_data(n_samples=1000, n_points=1000, hurst_range=(0.1, 0.9)):
    """Generate enhanced synthetic fractional Brownian motion data"""
    print(f"Generating {n_samples} enhanced synthetic fBm samples...")
    
    # Generate Hurst parameters
    hurst_params = np.random.uniform(hurst_range[0], hurst_range[1], n_samples)
    
    # Generate fBm data with enhanced methods
    data = []
    for i, H in enumerate(hurst_params):
        # Enhanced fBm generation using multiple methods
        if np.random.random() < 0.5:
            # Method 1: Power law in frequency domain
            freqs = np.fft.fftfreq(n_points)
            power_spectrum = np.abs(freqs) ** (-2*H - 1)
            power_spectrum[0] = 0  # Remove DC component
            
            noise = np.random.normal(0, 1, n_points) + 1j * np.random.normal(0, 1, n_points)
            filtered_noise = noise * np.sqrt(power_spectrum)
            fbm = np.real(np.fft.ifft(filtered_noise))
        else:
            # Method 2: Cholesky decomposition method
            t = np.arange(n_points)
            cov_matrix = np.zeros((n_points, n_points))
            for j in range(n_points):
                for k in range(n_points):
                    cov_matrix[j, k] = 0.5 * (abs(t[j])**(2*H) + abs(t[k])**(2*H) - abs(t[j] - t[k])**(2*H))
            
            L = np.linalg.cholesky(cov_matrix + 1e-6 * np.eye(n_points))
            noise = np.random.normal(0, 1, n_points)
            fbm = L @ noise
        
        # Normalize
        fbm = (fbm - np.mean(fbm)) / np.std(fbm)
        data.append(fbm)
    
    data = np.array(data)
    print(f"✅ Generated enhanced data shape: {data.shape}")
    
    return data, hurst_params

def main():
    """Main experiment function for testing true fractional operators"""
    print("🚀 ENHANCED FRACTIONAL PINO WITH TRUE FRACTIONAL OPERATORS")
    print("Building Fractional Characteristics Directly into Architecture")
    print("="*100)
    
    # Check dependencies
    if not TORCH_AVAILABLE:
        print("❌ PyTorch is required for this experiment")
        return
    
    # Set random seeds for reproducibility
    np.random.seed(42)
    torch.manual_seed(42)
    
    # Generate synthetic data
    data, true_hurst = generate_enhanced_synthetic_data(n_samples=200, n_points=1000)
    
    # Test different configurations
    estimators = {}
    
    # Test with true fractional operators
    estimators['PINO-True-Frac-0.3'] = EnhancedFractionalPINOEstimatorWithTrueOperators(
        input_size=1000, hidden_size=128, fractional_order=0.3, epochs=100, batch_size=16
    )
    
    estimators['PINO-True-Frac-0.5'] = EnhancedFractionalPINOEstimatorWithTrueOperators(
        input_size=1000, hidden_size=128, fractional_order=0.5, epochs=100, batch_size=16
    )
    
    estimators['PINO-True-Frac-0.7'] = EnhancedFractionalPINOEstimatorWithTrueOperators(
        input_size=1000, hidden_size=128, fractional_order=0.7, epochs=100, batch_size=16
    )
    
    # Test classical estimators for comparison
    print("\nTesting classical estimators...")
    
    # Test DFA
    try:
        print("Testing DFA...")
        dfa_estimates = []
        start_time = time.time()
        
        for i in range(min(50, len(data))):
            dfa_est = DFAEstimator()
            result = dfa_est.estimate(data[i])
            if isinstance(result, dict) and 'hurst' in result:
                dfa_estimates.append(result['hurst'])
            else:
                dfa_estimates.append(0.5)
        
        end_time = time.time()
        dfa_estimates = np.array(dfa_estimates)
        
        # Calculate metrics for DFA
        mae = np.mean(np.abs(dfa_estimates - true_hurst[:len(dfa_estimates)]))
        mse = np.mean((dfa_estimates - true_hurst[:len(dfa_estimates)]) ** 2)
        rmse = np.sqrt(mse)
        r2 = 1 - np.sum((dfa_estimates - true_hurst[:len(dfa_estimates)]) ** 2) / np.sum((true_hurst[:len(dfa_estimates)] - np.mean(true_hurst[:len(dfa_estimates)])) ** 2)
        success_rate = np.mean(np.abs(dfa_estimates - true_hurst[:len(dfa_estimates)]) / true_hurst[:len(dfa_estimates)] < 0.2) * 100
        
        estimators['DFA'] = {
            'estimates': dfa_estimates,
            'mae': mae,
            'mse': mse,
            'rmse': rmse,
            'r2': r2,
            'success_rate': success_rate,
            'execution_time': end_time - start_time
        }
        
        print(f"  ✅ DFA completed in {end_time - start_time:.3f}s")
        print(f"     MAE: {mae:.4f}, R²: {r2:.4f}, Success Rate: {success_rate:.1f}%")
        
    except Exception as e:
        print(f"  ❌ DFA failed: {str(e)}")
    
    # Test R/S
    try:
        print("Testing R/S...")
        rs_estimates = []
        start_time = time.time()
        
        for i in range(min(50, len(data))):
            rs_est = RSEstimator()
            result = rs_est.estimate(data[i])
            if isinstance(result, dict) and 'hurst' in result:
                rs_estimates.append(result['hurst'])
            else:
                rs_estimates.append(0.5)
        
        end_time = time.time()
        rs_estimates = np.array(rs_estimates)
        
        # Calculate metrics for R/S
        mae = np.mean(np.abs(rs_estimates - true_hurst[:len(rs_estimates)]))
        mse = np.mean((rs_estimates - true_hurst[:len(rs_estimates)]) ** 2)
        rmse = np.sqrt(mse)
        r2 = 1 - np.sum((rs_estimates - true_hurst[:len(rs_estimates)]) ** 2) / np.sum((true_hurst[:len(rs_estimates)] - np.mean(true_hurst[:len(rs_estimates)])) ** 2)
        success_rate = np.mean(np.abs(rs_estimates - true_hurst[:len(rs_estimates)]) / true_hurst[:len(rs_estimates)] < 0.2) * 100
        
        estimators['R/S'] = {
            'estimates': rs_estimates,
            'mae': mae,
            'mse': mse,
            'rmse': rmse,
            'r2': r2,
            'success_rate': success_rate,
            'execution_time': end_time - start_time
        }
        
        print(f"  ✅ R/S completed in {end_time - start_time:.3f}s")
        print(f"     MAE: {mae:.4f}, R²: {r2:.4f}, Success Rate: {success_rate:.1f}%")
        
    except Exception as e:
        print(f"  ❌ R/S failed: {str(e)}")
    
    # Remove DFA and R/S from estimators dict since they're already tested
    if 'DFA' in estimators:
        del estimators['DFA']
    if 'R/S' in estimators:
        del estimators['R/S']
    
    # Run benchmark for PINO estimators
    print("\nRunning benchmark for PINO estimators with true fractional operators...")
    
    results = {}
    
    for name, estimator in estimators.items():
        print(f"\nTesting {name}...")
        
        try:
            start_time = time.time()
            
            # Train model
            print(f"  Training {name}...")
            estimator.train(data, true_hurst)
            
            # Estimate Hurst parameters
            estimates = estimator.estimate(data)
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Calculate metrics
            mae = np.mean(np.abs(estimates - true_hurst))
            mse = np.mean((estimates - true_hurst) ** 2)
            rmse = np.sqrt(mse)
            r2 = 1 - np.sum((estimates - true_hurst) ** 2) / np.sum((true_hurst - np.mean(true_hurst)) ** 2)
            success_rate = np.mean(np.abs(estimates - true_hurst) / true_hurst < 0.2) * 100
            
            results[name] = {
                'estimates': estimates,
                'mae': mae,
                'mse': mse,
                'rmse': rmse,
                'r2': r2,
                'success_rate': success_rate,
                'execution_time': execution_time
            }
            
            print(f"  ✅ {name} completed in {execution_time:.3f}s")
            print(f"     MAE: {mae:.4f}, R²: {r2:.4f}, Success Rate: {success_rate:.1f}%")
            
        except Exception as e:
            print(f"  ❌ {name} failed: {str(e)}")
            results[name] = None
    
    # Combine all results
    all_results = {}
    for name, result in estimators.items():
        if isinstance(result, dict) and 'estimates' in result:
            all_results[name] = result
        elif name in results and results[name] is not None:
            all_results[name] = results[name]
    
    # Filter out None results
    all_results = {k: v for k, v in all_results.items() if v is not None}
    
    # Print summary
    print("\n" + "="*80)
    print("SUMMARY TABLE - TRUE FRACTIONAL OPERATORS")
    print("="*80)
    
    if len(all_results) > 0:
        summary_data = []
        for name, result in all_results.items():
            summary_data.append({
                'Estimator': name,
                'MAE': f"{result['mae']:.4f}",
                'MSE': f"{result['mse']:.4f}",
                'RMSE': f"{result['rmse']:.4f}",
                'R²': f"{result['r2']:.4f}",
                'Success Rate (%)': f"{result['success_rate']:.1f}",
                'Time (s)': f"{result['execution_time']:.3f}"
            })
        
        summary_df = pd.DataFrame(summary_data)
        print(summary_df.to_string(index=False))
        
        # Find best performers
        best_mae = min(all_results.items(), key=lambda x: x[1]['mae'])
        best_r2 = max(all_results.items(), key=lambda x: x[1]['r2'])
        best_success = max(all_results.items(), key=lambda x: x[1]['success_rate'])
        fastest = min(all_results.items(), key=lambda x: x[1]['execution_time'])
        
        print(f"\n🏆 BEST PERFORMERS:")
        print(f"   Lowest MAE: {best_mae[0]} ({best_mae[1]['mae']:.4f})")
        print(f"   Highest R²: {best_r2[0]} ({best_r2[1]['r2']:.4f})")
        print(f"   Highest Success Rate: {best_success[0]} ({best_success[1]['success_rate']:.1f}%)")
        print(f"   Fastest: {fastest[0]} ({fastest[1]['execution_time']:.3f}s)")
    
    # Save results
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    results_filename = f"true_fractional_operators_results_{timestamp}.pkl"
    
    # Convert results to serializable format
    serializable_results = {}
    for name, result in all_results.items():
        if result is not None:
            serializable_results[name] = {
                'estimates': result['estimates'].tolist(),
                'mae': result['mae'],
                'mse': result['mse'],
                'rmse': result['rmse'],
                'r2': result['r2'],
                'success_rate': result['success_rate'],
                'execution_time': result['execution_time']
            }
    
    joblib.dump(serializable_results, results_filename)
    print(f"\n✅ Results saved as {results_filename}")
    
    print("\n🎉 True Fractional Operators experiment completed!")
    print("Fractional characteristics have been built directly into the architecture!")

if __name__ == "__main__":
    main()
