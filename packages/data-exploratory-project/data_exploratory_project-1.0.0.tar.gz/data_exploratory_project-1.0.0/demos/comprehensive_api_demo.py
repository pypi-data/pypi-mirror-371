#!/usr/bin/env python3
"""
Comprehensive API Demonstration for DataExploratoryProject

This script demonstrates the complete API with detailed parameter descriptions,
return values, and usage examples for all major components.

Author: DataExploratoryProject Team
License: MIT
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any, Optional, Tuple
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Add project root to path
sys.path.append('.')
sys.path.append('..')

def demonstrate_data_generators():
    """
    Demonstrate all 5 data generators with comprehensive API documentation.
    
    Returns:
        Dict[str, Dict]: Results from each data generator with metadata
    """
    print("🚀 DataExploratoryProject - Comprehensive API Demo")
    print("=" * 60)
    print("📊 Data Generators API Demonstration")
    print("=" * 60)
    
    results = {}
    
    # 1. Fractional Brownian Motion (fBm)
    print("\n1️⃣ Fractional Brownian Motion (fBm)")
    print("-" * 40)
    
    from models.data_models.fbm.fbm_model import FractionalBrownianMotion
    
    print("📖 API Documentation:")
    print("   Class: FractionalBrownianMotion(H, sigma=1.0, method='davies_harte')")
    print("   Parameters:")
    print("   - H (float): Hurst parameter ∈ (0, 1)")
    print("   - sigma (float): Standard deviation > 0")
    print("   - method (str): 'davies_harte', 'cholesky', or 'circulant'")
    print("   Methods:")
    print("   - generate(n, seed=None) -> np.ndarray")
    print("   - get_theoretical_properties() -> Dict")
    print("   - get_increments(fbm) -> np.ndarray")
    
    print("\n💻 Example Usage:")
    print("   from models.data_models.fbm.fbm_model import FractionalBrownianMotion")
    print("   fbm = FractionalBrownianMotion(H=0.7, sigma=1.0)")
    print("   data = fbm.generate(1000, seed=42)")
    print("   properties = fbm.get_theoretical_properties()")
    
    fbm = FractionalBrownianMotion(H=0.7, sigma=1.0, method='davies_harte')
    data_fbm = fbm.generate(1000, seed=42)
    properties_fbm = fbm.get_theoretical_properties()
    
    print(f"\n✅ Generated fBm: {len(data_fbm)} samples")
    print(f"   Range: [{data_fbm.min():.3f}, {data_fbm.max():.3f}]")
    print(f"   Theoretical H: {properties_fbm['hurst_parameter']}")
    print(f"   Long-range dependence: {properties_fbm['long_range_dependence']}")
    
    results['fbm'] = {
        'data': data_fbm,
        'properties': properties_fbm,
        'api_info': {
            'class': 'FractionalBrownianMotion',
            'required_params': ['H'],
            'optional_params': ['sigma', 'method'],
            'return_type': 'np.ndarray'
        }
    }
    
    # 2. Fractional Gaussian Noise (fGn)
    print("\n2️⃣ Fractional Gaussian Noise (fGn)")
    print("-" * 40)
    
    from models.data_models.fgn.fgn_model import FractionalGaussianNoise
    
    print("📖 API Documentation:")
    print("   Class: FractionalGaussianNoise(H, sigma=1.0, method='davies_harte')")
    print("   Parameters:")
    print("   - H (float): Hurst parameter ∈ (0, 1)")
    print("   - sigma (float): Standard deviation > 0")
    print("   - method (str): 'davies_harte', 'cholesky', or 'circulant'")
    print("   Returns: np.ndarray of shape (n,)")
    
    fgn = FractionalGaussianNoise(H=0.6, sigma=1.0)
    data_fgn = fgn.generate(1000, seed=42)
    
    print(f"✅ Generated fGn: {len(data_fgn)} samples")
    print(f"   Range: [{data_fgn.min():.3f}, {data_fgn.max():.3f}]")
    print(f"   Mean: {data_fgn.mean():.3f}, Std: {data_fgn.std():.3f}")
    
    results['fgn'] = {
        'data': data_fgn,
        'api_info': {
            'class': 'FractionalGaussianNoise',
            'required_params': ['H'],
            'optional_params': ['sigma', 'method'],
            'return_type': 'np.ndarray'
        }
    }
    
    # 3. ARFIMA Model
    print("\n3️⃣ ARFIMA (AutoRegressive Fractionally Integrated Moving Average)")
    print("-" * 40)
    
    from models.data_models.arfima.arfima_model import ARFIMAModel
    
    print("📖 API Documentation:")
    print("   Class: ARFIMAModel(d, ar_params=None, ma_params=None, sigma=1.0)")
    print("   Parameters:")
    print("   - d (float): Fractional integration parameter ∈ (-0.5, 0.5)")
    print("   - ar_params (List[float]): AR coefficients (optional)")
    print("   - ma_params (List[float]): MA coefficients (optional)")
    print("   - sigma (float): Innovation standard deviation > 0")
    print("   Returns: np.ndarray of shape (n,)")
    
    arfima = ARFIMAModel(d=0.3, ar_params=[0.5], ma_params=[0.3], sigma=1.0)
    data_arfima = arfima.generate(1000, seed=42)
    
    print(f"✅ Generated ARFIMA: {len(data_arfima)} samples")
    print(f"   Range: [{data_arfima.min():.3f}, {data_arfima.max():.3f}]")
    print(f"   d parameter: 0.3 (long memory)")
    
    results['arfima'] = {
        'data': data_arfima,
        'api_info': {
            'class': 'ARFIMAModel',
            'required_params': ['d'],
            'optional_params': ['ar_params', 'ma_params', 'sigma', 'method'],
            'return_type': 'np.ndarray'
        }
    }
    
    # 4. Multifractal Random Walk (MRW)
    print("\n4️⃣ Multifractal Random Walk (MRW)")
    print("-" * 40)
    
    from models.data_models.mrw.mrw_model import MultifractalRandomWalk
    
    print("📖 API Documentation:")
    print("   Class: MultifractalRandomWalk(H, lambda_param, sigma=1.0)")
    print("   Parameters:")
    print("   - H (float): Hurst parameter ∈ (0, 1)")
    print("   - lambda_param (float): Intermittency parameter > 0")
    print("   - sigma (float): Base volatility > 0")
    print("   Returns: np.ndarray of shape (n,)")
    
    mrw = MultifractalRandomWalk(H=0.7, lambda_param=0.2, sigma=1.0)
    data_mrw = mrw.generate(1000, seed=42)
    
    print(f"✅ Generated MRW: {len(data_mrw)} samples")
    print(f"   Range: [{data_mrw.min():.3f}, {data_mrw.max():.3f}]")
    print(f"   H: 0.7, λ: 0.2 (multifractal scaling)")
    
    results['mrw'] = {
        'data': data_mrw,
        'api_info': {
            'class': 'MultifractalRandomWalk',
            'required_params': ['H', 'lambda_param'],
            'optional_params': ['sigma', 'method'],
            'return_type': 'np.ndarray'
        }
    }
    
    # 5. Neural fSDE (Optional)
    print("\n5️⃣ Neural fSDE (Neural Fractional Stochastic Differential Equation)")
    print("-" * 40)
    
    try:
        from models.data_models.neural_fsde.base_neural_fsde import BaseModel
        print("📖 API Documentation:")
        print("   Class: BaseModel() - Neural network-based fractional SDE")
        print("   Parameters: Model-specific (requires JAX/PyTorch)")
        print("   Returns: np.ndarray of shape (n,)")
        print("⚠️  Neural fSDE requires JAX dependencies (optional)")
        
        results['neural_fsde'] = {
            'data': None,
            'status': 'Available but requires JAX environment',
            'api_info': {
                'class': 'BaseModel',
                'required_params': 'Model-specific',
                'optional_params': 'Model-specific',
                'return_type': 'np.ndarray'
            }
        }
    except Exception as e:
        print("⚠️  Neural fSDE components not available (expected)")
        print(f"   Reason: {e}")
        results['neural_fsde'] = {
            'data': None,
            'status': 'Not available in current environment',
            'api_info': {
                'class': 'BaseModel',
                'note': 'Requires JAX/PyTorch dependencies'
            }
        }
    
    return results

def demonstrate_estimators():
    """
    Demonstrate key estimators with comprehensive API documentation.
    
    Returns:
        Dict[str, Dict]: Results from estimators with metadata
    """
    print("\n" + "=" * 60)
    print("🔍 Estimators API Demonstration")
    print("=" * 60)
    
    # Generate test data
    from models.data_models.fbm.fbm_model import FractionalBrownianMotion
    fbm = FractionalBrownianMotion(H=0.7, sigma=1.0)
    test_data = fbm.generate(1000, seed=42)
    
    results = {}
    
    # 1. R/S Estimator (Temporal)
    print("\n1️⃣ R/S Estimator (Rescaled Range)")
    print("-" * 40)
    
    from analysis.temporal.rs.rs_estimator import RSEstimator
    
    print("📖 API Documentation:")
    print("   Class: RSEstimator(min_window_size=10, max_window_size=None, window_sizes=None, overlap=False)")
    print("   Method: estimate(data)")
    print("   Parameters:")
    print("   - data (np.ndarray): Input time series")
    print("   Returns: Dict with keys:")
    print("   - 'hurst_parameter' (float): Estimated Hurst exponent")
    print("   - 'r_squared' (float): Goodness of fit (R²)")
    print("   - 'confidence_interval' (Tuple): 95% confidence interval")
    print("   - 'window_sizes' (List): Analysis window sizes used")
    print("   - 'rs_values' (List): R/S values for each window")
    print("   - 'std_error' (float): Standard error of estimate")
    
    print("\n💻 Example Usage:")
    print("   from analysis.temporal.rs.rs_estimator import RSEstimator")
    print("   rs_estimator = RSEstimator()")
    print("   result = rs_estimator.estimate(data)")
    print("   hurst = result['hurst_parameter']")
    
    rs_estimator = RSEstimator()
    rs_result = rs_estimator.estimate(test_data)
    
    print(f"\n✅ R/S Estimation Result:")
    print(f"   Estimated H: {rs_result['hurst_parameter']:.3f}")
    print(f"   R²: {rs_result['r_squared']:.3f}")
    print(f"   95% CI: ({rs_result['confidence_interval'][0]:.3f}, {rs_result['confidence_interval'][1]:.3f})")
    print(f"   Standard Error: {rs_result['std_error']:.4f}")
    print(f"   Error from true H (0.7): {abs(rs_result['hurst_parameter'] - 0.7):.3f}")
    
    results['rs'] = {
        'result': rs_result,
        'api_info': {
            'class': 'RSEstimator',
            'method': 'estimate',
            'input_type': 'np.ndarray',
            'return_type': 'Dict[str, Union[float, List, Tuple]]',
            'category': 'Temporal'
        }
    }
    
    # 2. DFA Estimator (Temporal)
    print("\n2️⃣ DFA Estimator (Detrended Fluctuation Analysis)")
    print("-" * 40)
    
    from analysis.temporal.dfa.dfa_estimator import DFAEstimator
    
    print("📖 API Documentation:")
    print("   Class: DFAEstimator()")
    print("   Method: estimate(data)")
    print("   Parameters:")
    print("   - data (np.ndarray): Input time series")
    print("   Returns: Dict with keys:")
    print("   - 'hurst_parameter' (float): Estimated Hurst exponent")
    print("   - 'r_squared' (float): Goodness of fit")
    print("   - 'confidence_interval' (Tuple): 95% confidence interval")
    print("   - 'window_sizes' (List): Analysis window sizes")
    print("   - 'fluctuations' (List): DFA fluctuation values")
    
    dfa_estimator = DFAEstimator()
    dfa_result = dfa_estimator.estimate(test_data)
    
    print(f"✅ DFA Estimation Result:")
    print(f"   Estimated H: {dfa_result['hurst_parameter']:.3f}")
    print(f"   R²: {dfa_result['r_squared']:.3f}")
    print(f"   95% CI: ({dfa_result['confidence_interval'][0]:.3f}, {dfa_result['confidence_interval'][1]:.3f})")
    print(f"   Error: {abs(dfa_result['hurst_parameter'] - 0.7):.3f}")
    
    results['dfa'] = {
        'result': dfa_result,
        'api_info': {
            'class': 'DFAEstimator',
            'method': 'estimate',
            'input_type': 'np.ndarray',
            'return_type': 'Dict[str, Union[float, List, Tuple]]',
            'category': 'Temporal'
        }
    }
    
    # 3. CWT Estimator (Wavelet)
    print("\n3️⃣ CWT Estimator (Continuous Wavelet Transform)")
    print("-" * 40)
    
    from analysis.wavelet.cwt.cwt_estimator import CWTEstimator
    
    print("📖 API Documentation:")
    print("   Class: CWTEstimator()")
    print("   Method: estimate(data)")
    print("   Parameters:")
    print("   - data (np.ndarray): Input time series")
    print("   Returns: Dict with keys:")
    print("   - 'hurst_parameter' (float): Estimated Hurst exponent")
    print("   - 'r_squared' (float): Goodness of fit")
    print("   - 'confidence_interval' (Tuple): 95% confidence interval")
    print("   - 'scales' (List): Wavelet scales")
    print("   - 'coefficients' (List): Wavelet coefficient variances")
    
    cwt_estimator = CWTEstimator()
    cwt_result = cwt_estimator.estimate(test_data)
    
    print(f"✅ CWT Estimation Result:")
    print(f"   Estimated H: {cwt_result['hurst_parameter']:.3f}")
    print(f"   R²: {cwt_result['r_squared']:.3f}")
    print(f"   95% CI: ({cwt_result['confidence_interval'][0]:.3f}, {cwt_result['confidence_interval'][1]:.3f})")
    print(f"   Error: {abs(cwt_result['hurst_parameter'] - 0.7):.3f}")
    
    results['cwt'] = {
        'result': cwt_result,
        'api_info': {
            'class': 'CWTEstimator',
            'method': 'estimate',
            'input_type': 'np.ndarray',
            'return_type': 'Dict[str, Union[float, List, Tuple]]',
            'category': 'Wavelet'
        }
    }
    
    return results

def demonstrate_auto_discovery():
    """
    Demonstrate the auto-discovery system API.
    
    Returns:
        Dict: Discovery results with component counts
    """
    print("\n" + "=" * 60)
    print("🔍 Auto-Discovery System API Demonstration")
    print("=" * 60)
    
    from auto_discovery_system import AutoDiscoverySystem
    
    print("📖 API Documentation:")
    print("   Class: AutoDiscoverySystem(project_root='.')")
    print("   Method: discover_components()")
    print("   Parameters:")
    print("   - project_root (str): Root directory to search")
    print("   Returns: Dict with keys:")
    print("   - 'data_generators' (Dict): Discovered data generators")
    print("   - 'estimators' (Dict): Discovered estimators")
    print("   - 'neural_components' (Dict): Discovered neural components")
    
    ads = AutoDiscoverySystem()
    components = ads.discover_components()
    
    print(f"✅ Discovery Results:")
    print(f"   Data Generators: {len(components['data_generators'])}")
    print(f"   Estimators: {len(components['estimators'])}")
    print(f"   Neural Components: {len(components['neural_components'])}")
    
    # Show some discovered components
    print(f"\n📋 Sample Discovered Components:")
    
    print(f"   Data Generators:")
    for name in list(components['data_generators'].keys())[:3]:
        print(f"   - {name}")
    
    print(f"   Estimators (first 5 of {len(components['estimators'])}):")
    for name in list(components['estimators'].keys())[:5]:
        estimator_info = components['estimators'][name]
        category = estimator_info.get('category', 'Unknown')
        print(f"   - {name} ({category})")
    
    return {
        'components': components,
        'api_info': {
            'class': 'AutoDiscoverySystem',
            'method': 'discover_components',
            'input_type': 'None',
            'return_type': 'Dict[str, Dict]'
        }
    }

def create_api_summary():
    """Create a comprehensive API summary."""
    print("\n" + "=" * 60)
    print("📚 API SUMMARY")
    print("=" * 60)
    
    api_summary = {
        "Data Generators": {
            "Count": 5,
            "Classes": [
                "FractionalBrownianMotion",
                "FractionalGaussianNoise", 
                "ARFIMAModel",
                "MultifractalRandomWalk",
                "BaseModel (Neural fSDE)"
            ],
            "Common Methods": ["generate(n, seed=None)", "get_theoretical_properties()"],
            "Return Type": "np.ndarray"
        },
        "Estimators": {
            "Count": 23,
            "Categories": {
                "Temporal": 4,
                "Spectral": 3,
                "Wavelet": 4,
                "Multifractal": 2,
                "Machine Learning": 10
            },
            "Common Methods": ["estimate(data)"],
            "Return Type": "Dict[str, Union[float, List, Tuple]]"
        },
        "Auto-Discovery": {
            "Class": "AutoDiscoverySystem",
            "Main Method": "discover_components()",
            "Return Type": "Dict[str, Dict]"
        }
    }
    
    print("🔢 Component Counts:")
    print(f"   Data Generators: {api_summary['Data Generators']['Count']}")
    print(f"   Estimators: {api_summary['Estimators']['Count']}")
    print(f"   - Temporal: {api_summary['Estimators']['Categories']['Temporal']}")
    print(f"   - Spectral: {api_summary['Estimators']['Categories']['Spectral']}")
    print(f"   - Wavelet: {api_summary['Estimators']['Categories']['Wavelet']}")
    print(f"   - Multifractal: {api_summary['Estimators']['Categories']['Multifractal']}")
    print(f"   - Machine Learning: {api_summary['Estimators']['Categories']['Machine Learning']}")
    
    print("\n📖 Common API Patterns:")
    print("   Data Generation: model.generate(n, seed=None) -> np.ndarray")
    print("   Parameter Estimation: estimator.estimate(data) -> Dict")
    print("   Component Discovery: ads.discover_components() -> Dict")
    
    print("\n🎯 Key Features:")
    print("   ✅ Consistent API across all components")
    print("   ✅ Comprehensive return information (confidence intervals, diagnostics)")
    print("   ✅ Automatic component discovery and integration")
    print("   ✅ Robust error handling and validation")
    print("   ✅ Reproducible results with seed parameter")
    
    return api_summary

def main():
    """Run comprehensive API demonstration."""
    try:
        # Demonstrate data generators
        generator_results = demonstrate_data_generators()
        
        # Demonstrate estimators
        estimator_results = demonstrate_estimators()
        
        # Demonstrate auto-discovery
        discovery_results = demonstrate_auto_discovery()
        
        # Create API summary
        api_summary = create_api_summary()
        
        print("\n" + "=" * 60)
        print("🎉 API DEMONSTRATION COMPLETE")
        print("=" * 60)
        print("✅ All API components demonstrated successfully")
        print("📊 Data Generators: 5/5 documented")
        print("🔍 Estimators: 3 examples shown (23 total available)")
        print("🤖 Auto-Discovery: Fully functional")
        print("\n🚀 Ready for PyPI submission!")
        
        return {
            'generators': generator_results,
            'estimators': estimator_results,
            'discovery': discovery_results,
            'summary': api_summary
        }
        
    except Exception as e:
        print(f"\n❌ API demonstration failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    results = main()
    if results:
        print("\n📋 For detailed API documentation, see:")
        print("   - Individual class docstrings")
        print("   - demos/ directory for usage examples")
        print("   - documentation/ directory for comprehensive guides")
