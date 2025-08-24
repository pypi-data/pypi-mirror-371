"""
Comprehensive Model Demo

This script demonstrates the generation and basic analysis of all four stochastic models:
- ARFIMA (AutoRegressive Fractionally Integrated Moving Average)
- fBm (Fractional Brownian Motion) 
- fGn (Fractional Gaussian Noise)
- MRW (Multifractal Random Walk)

The demo includes:
1. Data generation with different parameters
2. Time series visualization
3. Basic statistical analysis
4. Comparison plots
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import models
try:
    from models.data_models.arfima.arfima_model import ARFIMAModel
    from models.data_models.fbm.fbm_model import FractionalBrownianMotion
    from models.data_models.fgn.fgn_model import FractionalGaussianNoise
    from models.data_models.mrw.mrw_model import MultifractalRandomWalk
    MODELS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some models not available: {e}")
    MODELS_AVAILABLE = False

# Set up plotting style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class ComprehensiveModelDemo:
    """Comprehensive demonstration of all stochastic models."""
    
    def __init__(self, n_samples: int = 1000, seed: int = 42):
        """
        Initialize the demo.
        
        Parameters
        ----------
        n_samples : int
            Number of samples to generate for each model
        seed : int
            Random seed for reproducibility
        """
        self.n_samples = n_samples
        self.seed = seed
        np.random.seed(seed)
        
        # Define model parameters
        self.model_configs = {
            'ARFIMA': {
                'd': 0.3,  # Fractional differencing parameter
                'ar_params': [0.5],  # AR parameters
                'ma_params': [0.2],  # MA parameters
                'sigma': 1.0  # Innovation variance
            },
            'fBm': {
                'H': 0.7,  # Hurst parameter
                'sigma': 1.0  # Scale parameter
            },
            'fGn': {
                'H': 0.6,  # Hurst parameter
                'sigma': 1.0  # Scale parameter
            },
            'MRW': {
                'H': 0.5,  # Hurst parameter
                'lambda_param': 0.1,  # Multifractal parameter
                'sigma': 1.0  # Scale parameter
            }
        }
        
        self.generated_data = {}
        self.models = {}
        
    def generate_all_models(self) -> Dict[str, np.ndarray]:
        """
        Generate data from all available models.
        
        Returns
        -------
        dict
            Dictionary containing generated time series for each model
        """
        if not MODELS_AVAILABLE:
            print("Models not available. Please ensure all model implementations are complete.")
            return {}
            
        print("Generating synthetic data from all models...")
        
        for model_name, config in self.model_configs.items():
            try:
                print(f"  Generating {model_name} data...")
                
                if model_name == 'ARFIMA':
                    model = ARFIMAModel(**config)
                elif model_name == 'fBm':
                    model = FractionalBrownianMotion(**config)
                elif model_name == 'fGn':
                    model = FractionalGaussianNoise(**config)
                elif model_name == 'MRW':
                    model = MultifractalRandomWalk(**config)
                else:
                    continue
                    
                data = model.generate(self.n_samples, seed=self.seed)
                self.generated_data[model_name] = data
                self.models[model_name] = model
                
                print(f"    ✓ Generated {len(data)} samples")
                
            except Exception as e:
                print(f"    ✗ Error generating {model_name}: {e}")
                continue
                
        return self.generated_data
    
    def plot_time_series(self, figsize: Tuple[int, int] = (15, 10)) -> None:
        """Plot time series for all generated models."""
        if not self.generated_data:
            print("No data to plot. Run generate_all_models() first.")
            return
            
        n_models = len(self.generated_data)
        fig, axes = plt.subplots(n_models, 1, figsize=figsize)
        
        if n_models == 1:
            axes = [axes]
            
        for i, (model_name, data) in enumerate(self.generated_data.items()):
            ax = axes[i]
            ax.plot(data, linewidth=0.8, alpha=0.8)
            ax.set_title(f'{model_name} Time Series', fontsize=14, fontweight='bold')
            ax.set_xlabel('Time')
            ax.set_ylabel('Value')
            ax.grid(True, alpha=0.3)
            
            # Add parameter info to title
            if model_name in self.models:
                params = self.models[model_name].get_parameters()
                param_str = ', '.join([f"{k}={v}" for k, v in params.items()])
                ax.set_title(f'{model_name} Time Series\nParameters: {param_str}', 
                           fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.show()
    
    def plot_comparison(self, figsize: Tuple[int, int] = (15, 12)) -> None:
        """Create comparison plots of all models."""
        if not self.generated_data:
            print("No data to plot. Run generate_all_models() first.")
            return
            
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        axes = axes.flatten()
        
        for i, (model_name, data) in enumerate(self.generated_data.items()):
            if i >= len(axes):
                break
                
            ax = axes[i]
            
            # Plot time series
            ax.plot(data, linewidth=0.8, alpha=0.8, label='Time Series')
            ax.set_title(f'{model_name}', fontsize=14, fontweight='bold')
            ax.set_xlabel('Time')
            ax.set_ylabel('Value')
            ax.grid(True, alpha=0.3)
            
            # Add statistics
            mean_val = np.mean(data)
            std_val = np.std(data)
            ax.axhline(mean_val, color='red', linestyle='--', alpha=0.7, 
                      label=f'Mean: {mean_val:.3f}')
            ax.axhline(mean_val + std_val, color='orange', linestyle=':', alpha=0.7,
                      label=f'±1σ: {std_val:.3f}')
            ax.axhline(mean_val - std_val, color='orange', linestyle=':', alpha=0.7)
            ax.legend(fontsize=8)
        
        plt.tight_layout()
        plt.show()
    
    def statistical_summary(self) -> None:
        """Print statistical summary of all generated data."""
        if not self.generated_data:
            print("No data to analyze. Run generate_all_models() first.")
            return
            
        print("\n" + "="*60)
        print("STATISTICAL SUMMARY")
        print("="*60)
        
        for model_name, data in self.generated_data.items():
            print(f"\n{model_name}:")
            print(f"  Length: {len(data)}")
            print(f"  Mean: {np.mean(data):.4f}")
            print(f"  Std: {np.std(data):.4f}")
            print(f"  Min: {np.min(data):.4f}")
            print(f"  Max: {np.max(data):.4f}")
            print(f"  Skewness: {self._calculate_skewness(data):.4f}")
            print(f"  Kurtosis: {self._calculate_kurtosis(data):.4f}")
    
    def _calculate_skewness(self, data: np.ndarray) -> float:
        """Calculate skewness of the data."""
        mean = np.mean(data)
        std = np.std(data)
        return np.mean(((data - mean) / std) ** 3)
    
    def _calculate_kurtosis(self, data: np.ndarray) -> float:
        """Calculate kurtosis of the data."""
        mean = np.mean(data)
        std = np.std(data)
        return np.mean(((data - mean) / std) ** 4) - 3
    
    def run_full_demo(self) -> None:
        """Run the complete demonstration."""
        print("="*60)
        print("COMPREHENSIVE MODEL DEMO")
        print("="*60)
        
        # Generate data
        self.generate_all_models()
        
        if not self.generated_data:
            print("No data was generated. Demo cannot continue.")
            return
        
        # Plot time series
        print("\nGenerating time series plots...")
        self.plot_time_series()
        
        # Plot comparison
        print("\nGenerating comparison plots...")
        self.plot_comparison()
        
        # Statistical summary
        self.statistical_summary()
        
        print("\n" + "="*60)
        print("DEMO COMPLETE")
        print("="*60)


def main():
    """Main function to run the comprehensive demo."""
    # Create demo instance
    demo = ComprehensiveModelDemo(n_samples=1000, seed=42)
    
    # Run the full demonstration
    demo.run_full_demo()


if __name__ == "__main__":
    main()
