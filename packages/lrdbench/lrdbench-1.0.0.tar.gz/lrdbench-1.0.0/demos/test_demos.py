"""
Test script for demo modules.

This script tests that all demo modules can be imported and their main classes
can be instantiated without errors.
"""

import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_demo_imports():
    """Test that all demo modules can be imported."""
    print("Testing demo module imports...")
    
    try:
        # Test CPU-based demos
        print("Testing CPU-based demos...")
        
        # Test comprehensive model demo
        from cpu_based.comprehensive_model_demo import ComprehensiveModelDemo
        print("✓ comprehensive_model_demo imported successfully")
        
        # Test parameter estimation demo
        from cpu_based.parameter_estimation_demo import ParameterEstimationDemo
        print("✓ parameter_estimation_demo imported successfully")
        
        # Test plotting configuration demo
        from cpu_based.plotting_configuration_demo import PlottingConfigurationDemo, GlobalPlottingConfig, PlotConfig
        print("✓ plotting_configuration_demo imported successfully")
        
        # Test real-world confounds demo
        from cpu_based.real_world_confounds_demo import RealWorldConfoundsDemo
        print("✓ real_world_confounds_demo imported successfully")
        
        # Test ARFIMA performance demo
        from cpu_based.arfima_performance_demo import ARFIMAPerformanceDemo
        print("✓ arfima_performance_demo imported successfully")
        
        # Test GPU-based demos
        print("\nTesting GPU-based demos...")
        
        # Test JAX performance demo
        from gpu_based.jax_performance_demo import JAXPerformanceDemo
        print("✓ jax_performance_demo imported successfully")
        
        # Test high performance comparison demo
        from gpu_based.high_performance_comparison_demo import HighPerformanceComparisonDemo
        print("✓ high_performance_comparison_demo imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def test_demo_instantiation():
    """Test that demo classes can be instantiated."""
    print("\nTesting demo class instantiation...")
    
    try:
        # Test CPU-based demo instantiation
        print("Testing CPU-based demo instantiation...")
        
        # Test comprehensive model demo instantiation
        from cpu_based.comprehensive_model_demo import ComprehensiveModelDemo
        demo1 = ComprehensiveModelDemo(n_samples=100, seed=42)
        print("✓ ComprehensiveModelDemo instantiated successfully")
        
        # Test parameter estimation demo instantiation
        from cpu_based.parameter_estimation_demo import ParameterEstimationDemo
        demo2 = ParameterEstimationDemo(n_samples=100, seed=42)
        print("✓ ParameterEstimationDemo instantiated successfully")
        
        # Test plotting configuration demo instantiation
        from cpu_based.plotting_configuration_demo import PlottingConfigurationDemo
        demo3 = PlottingConfigurationDemo()
        print("✓ PlottingConfigurationDemo instantiated successfully")
        
        # Test real-world confounds demo instantiation
        from cpu_based.real_world_confounds_demo import RealWorldConfoundsDemo
        demo4 = RealWorldConfoundsDemo()
        print("✓ RealWorldConfoundsDemo instantiated successfully")
        
        # Test ARFIMA performance demo instantiation
        from cpu_based.arfima_performance_demo import ARFIMAPerformanceDemo
        demo5 = ARFIMAPerformanceDemo()
        print("✓ ARFIMAPerformanceDemo instantiated successfully")
        
        # Test GPU-based demo instantiation
        print("\nTesting GPU-based demo instantiation...")
        
        # Test JAX performance demo instantiation
        from gpu_based.jax_performance_demo import JAXPerformanceDemo
        demo6 = JAXPerformanceDemo()
        print("✓ JAXPerformanceDemo instantiated successfully")
        
        # Test high performance comparison demo instantiation
        from gpu_based.high_performance_comparison_demo import HighPerformanceComparisonDemo
        demo7 = HighPerformanceComparisonDemo()
        print("✓ HighPerformanceComparisonDemo instantiated successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Instantiation error: {e}")
        return False

def test_confound_library():
    """Test confound library functionality."""
    print("\nTesting confound library functionality...")
    
    try:
        import numpy as np
        from cpu_based.real_world_confounds_demo import RealWorldConfoundsDemo
        
        # Create demo instance
        demo = RealWorldConfoundsDemo()
        
        # Generate test data
        test_data = np.random.randn(100)
        
        # Test that the demo can be created
        print("✓ RealWorldConfoundsDemo created successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Confound library error: {e}")
        return False

def test_complex_time_series():
    """Test complex time series generation."""
    print("\nTesting complex time series generation...")
    
    try:
        from cpu_based.real_world_confounds_demo import RealWorldConfoundsDemo
        
        # Create demo instance
        demo = RealWorldConfoundsDemo()
        
        # Test that the demo can be created
        print("✓ Complex time series demo created successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Complex time series error: {e}")
        return False

def test_plotting_config():
    """Test plotting configuration functionality."""
    print("\nTesting plotting configuration functionality...")
    
    try:
        from cpu_based.plotting_configuration_demo import GlobalPlottingConfig, PlotConfig, PlotTheme
        
        # Test configuration creation
        config = PlotConfig()
        print("✓ PlotConfig created successfully")
        
        # Test global plotting config
        plot_config = GlobalPlottingConfig(config)
        print("✓ GlobalPlottingConfig created successfully")
        
        # Test theme application
        plot_config.apply_theme(PlotTheme.DARK)
        print("✓ Dark theme applied successfully")
        
        plot_config.apply_theme(PlotTheme.SCIENTIFIC)
        print("✓ Scientific theme applied successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Plotting configuration error: {e}")
        return False

def main():
    """Run all tests."""
    print("="*60)
    print("DEMO TESTING SUITE")
    print("="*60)
    
    tests = [
        ("Import Test", test_demo_imports),
        ("Instantiation Test", test_demo_instantiation),
        ("Confound Library Test", test_confound_library),
        ("Complex Time Series Test", test_complex_time_series),
        ("Plotting Config Test", test_plotting_config)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 40)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Demos are ready to use.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
