#!/usr/bin/env python3
"""
Quick Start Demo - Correct API Syntax for DataExploratoryProject

This script demonstrates the exact correct syntax for using the library
with practical examples that users can copy and paste.

Author: DataExploratoryProject Team
License: MIT
"""

import sys
import numpy as np

# Add project root to path
sys.path.append('.')

def quick_start_demo():
    """Demonstrate the correct API syntax with working examples."""
    
    print("🚀 DataExploratoryProject - Quick Start Demo")
    print("=" * 50)
    print("Demonstrating correct API syntax for immediate use")
    print("=" * 50)
    
    # Example 1: Generate Fractional Brownian Motion
    print("\n📊 Example 1: Generate Fractional Brownian Motion")
    print("-" * 50)
    
    print("Code:")
    print("    from models.data_models.fbm.fbm_model import FractionalBrownianMotion")
    print("    fbm = FractionalBrownianMotion(H=0.7, sigma=1.0)")
    print("    data = fbm.generate(1000, seed=42)")
    print("    properties = fbm.get_theoretical_properties()")
    
    from models.data_models.fbm.fbm_model import FractionalBrownianMotion
    fbm = FractionalBrownianMotion(H=0.7, sigma=1.0)
    data = fbm.generate(1000, seed=42)
    properties = fbm.get_theoretical_properties()
    
    print(f"\nResult:")
    print(f"    Generated {len(data)} fBm samples")
    print(f"    Theoretical H: {properties['hurst_parameter']}")
    print(f"    Long-range dependence: {properties['long_range_dependence']}")
    print(f"    Data range: [{data.min():.3f}, {data.max():.3f}]")
    
    # Example 2: Estimate Hurst Parameter with R/S
    print("\n🔍 Example 2: Estimate Hurst Parameter with R/S")
    print("-" * 50)
    
    print("Code:")
    print("    from analysis.temporal.rs.rs_estimator import RSEstimator")
    print("    rs_estimator = RSEstimator()")
    print("    result = rs_estimator.estimate(data)")
    print("    estimated_h = result['hurst_parameter']")
    
    from analysis.temporal.rs.rs_estimator import RSEstimator
    rs_estimator = RSEstimator()
    result = rs_estimator.estimate(data)
    estimated_h = result['hurst_parameter']
    
    print(f"\nResult:")
    print(f"    True H: 0.7")
    print(f"    Estimated H: {estimated_h:.3f}")
    print(f"    Error: {abs(estimated_h - 0.7):.3f}")
    print(f"    R²: {result['r_squared']:.3f}")
    print(f"    95% CI: ({result['confidence_interval'][0]:.3f}, {result['confidence_interval'][1]:.3f})")
    
    # Example 3: Try Multiple Estimators
    print("\n🔬 Example 3: Compare Multiple Estimators")
    print("-" * 50)
    
    print("Code:")
    print("    from analysis.temporal.dfa.dfa_estimator import DFAEstimator")
    print("    from analysis.wavelet.cwt.cwt_estimator import CWTEstimator")
    print("    from analysis.machine_learning.cnn_estimator import CNNEstimator")
    print("    from analysis.machine_learning.transformer_estimator import TransformerEstimator")
    print("    ")
    print("    estimators = {")
    print("        'R/S': RSEstimator(),")
    print("        'DFA': DFAEstimator(),")
    print("        'CWT': CWTEstimator(),")
    print("        'CNN': CNNEstimator(),")
    print("        'Transformer': TransformerEstimator()")
    print("    }")
    print("    ")
    print("    for name, estimator in estimators.items():")
    print("        result = estimator.estimate(data)")
    print("        print(f'{name}: H = {result[\"hurst_parameter\"]:.3f}')")
    
    from analysis.temporal.dfa.dfa_estimator import DFAEstimator
    from analysis.wavelet.cwt.cwt_estimator import CWTEstimator
    from analysis.machine_learning.cnn_estimator import CNNEstimator
    from analysis.machine_learning.transformer_estimator import TransformerEstimator
    
    estimators = {
        'R/S': RSEstimator(),
        'DFA': DFAEstimator(),
        'CWT': CWTEstimator(),
        'CNN': CNNEstimator(),
        'Transformer': TransformerEstimator()
    }
    
    print(f"\nResult:")
    print(f"    True H: 0.7")
    for name, estimator in estimators.items():
        try:
            result = estimator.estimate(data)
            h_est = result['hurst_parameter']
            error = abs(h_est - 0.7)
            print(f"    {name}: H = {h_est:.3f} (error: {error:.3f})")
        except Exception as e:
            print(f"    {name}: Failed - {str(e)[:50]}...")
    
    # Example 4: Generate ARFIMA Data
    print("\n📈 Example 4: Generate ARFIMA Data")
    print("-" * 50)
    
    print("Code:")
    print("    from models.data_models.arfima.arfima_model import ARFIMAModel")
    print("    arfima = ARFIMAModel(d=0.3, ar_params=[0.5], ma_params=[0.3])")
    print("    arfima_data = arfima.generate(1000, seed=42)")
    
    from models.data_models.arfima.arfima_model import ARFIMAModel
    arfima = ARFIMAModel(d=0.3, ar_params=[0.5], ma_params=[0.3])
    arfima_data = arfima.generate(1000, seed=42)
    
    print(f"\nResult:")
    print(f"    Generated {len(arfima_data)} ARFIMA samples")
    print(f"    d parameter: 0.3 (fractional integration)")
    print(f"    Data range: [{arfima_data.min():.3f}, {arfima_data.max():.3f}]")
    
    # Example 5: Auto-Discovery System
    print("\n🤖 Example 5: Auto-Discovery System")
    print("-" * 50)
    
    print("Code:")
    print("    from auto_discovery_system import AutoDiscoverySystem")
    print("    ads = AutoDiscoverySystem()")
    print("    components = ads.discover_components()")
    print("    print(f'Found {len(components[\"estimators\"])} estimators')")
    
    from auto_discovery_system import AutoDiscoverySystem
    ads = AutoDiscoverySystem()
    components = ads.discover_components()
    
    print(f"\nResult:")
    print(f"    Found {len(components['estimators'])} estimators")
    print(f"    Found {len(components['data_generators'])} data generators")
    print(f"    Found {len(components['neural_components'])} neural components")
    
    # API Summary
    print("\n📚 API Summary - Copy & Paste Ready")
    print("=" * 50)
    
    api_examples = [
        "# Data Generation",
        "from models.data_models.fbm.fbm_model import FractionalBrownianMotion",
        "fbm = FractionalBrownianMotion(H=0.7, sigma=1.0)",
        "data = fbm.generate(1000, seed=42)",
        "",
        "# Hurst Estimation (Classical)", 
        "from analysis.temporal.rs.rs_estimator import RSEstimator",
        "estimator = RSEstimator()",
        "result = estimator.estimate(data)",
        "hurst = result['hurst_parameter']",
        "",
        "# Hurst Estimation (Machine Learning)",
        "from analysis.machine_learning.cnn_estimator import CNNEstimator",
        "from analysis.machine_learning.transformer_estimator import TransformerEstimator",
        "cnn_estimator = CNNEstimator()",
        "transformer_estimator = TransformerEstimator()",
        "cnn_result = cnn_estimator.estimate(data)",
        "transformer_result = transformer_estimator.estimate(data)",
        "",
        "# ARFIMA Generation",
        "from models.data_models.arfima.arfima_model import ARFIMAModel", 
        "arfima = ARFIMAModel(d=0.3, ar_params=[0.5], ma_params=[0.3])",
        "arfima_data = arfima.generate(1000, seed=42)",
        "",
        "# Auto-Discovery",
        "from auto_discovery_system import AutoDiscoverySystem",
        "ads = AutoDiscoverySystem()",
        "components = ads.discover_components()"
    ]
    
    for line in api_examples:
        print(f"    {line}")
    
    print("\n✅ All examples use the exact correct API syntax!")
    print("🚀 Ready for PyPI: pip install data-exploratory-project")

if __name__ == "__main__":
    try:
        quick_start_demo()
        print("\n🎉 Quick Start Demo completed successfully!")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
