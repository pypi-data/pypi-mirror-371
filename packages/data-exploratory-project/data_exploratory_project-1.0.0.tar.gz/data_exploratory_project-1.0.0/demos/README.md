# Demo Scripts

This directory contains comprehensive demonstration scripts for the Data Modeling and Generation Project. The demos are organized into two categories based on their computational requirements and optimization targets.

## 📁 Directory Structure

```
demos/
├── cpu_based/          # CPU-optimized demos
│   ├── parameter_estimation_demo.py
│   ├── estimator_benchmark.py
│   ├── arfima_performance_demo.py
│   ├── plotting_configuration_demo.py
│   ├── comprehensive_model_demo.py
│   └── real_world_confounds_demo.py
├── gpu_based/          # GPU-accelerated demos
│   ├── jax_performance_demo.py
│   └── high_performance_comparison_demo.py
├── README.md           # This file
├── test_demos.py       # Demo testing utilities
└── __init__.py
```

## 🖥️ CPU-Based Demos

**Location**: `demos/cpu_based/`

These demos are optimized for CPU computation and do not require GPU acceleration. They showcase the core functionality using standard Python libraries and CPU-optimized implementations.

### Available Demos:
- **Parameter Estimation Demo**: Tests all 13 estimators across different data models
- **Estimator Benchmark**: Automated performance benchmarking
- **ARFIMA Performance Demo**: Showcases optimized ARFIMA implementation
- **Plotting Configuration Demo**: Global plotting system demonstration
- **Comprehensive Model Demo**: End-to-end data model testing
- **Real-World Confounds Demo**: Robustness testing against contaminations

**Requirements**: Standard Python environment with NumPy, SciPy, Matplotlib, Numba

**Best for**: Development, testing, small datasets, environments without GPU

## 🚀 GPU-Based Demos

**Location**: `demos/gpu_based/`

These demos leverage GPU acceleration for high-performance computation, showcasing JAX-optimized implementations for large-scale analysis.

### Available Demos:
- **JAX Performance Demo**: GPU-accelerated estimator performance
- **High Performance Comparison Demo**: Comprehensive CPU vs GPU comparison

**Requirements**: NVIDIA GPU, CUDA, JAX with GPU support

**Best for**: Large datasets, performance testing, research, high-throughput analysis

## 🎯 Quick Start

### For CPU Users:
```bash
cd demos/cpu_based
python parameter_estimation_demo.py
```

### For GPU Users:
```bash
cd demos/gpu_based
python jax_performance_demo.py --device gpu
```

## 📊 Demo Categories Overview

| Category | Purpose | Data Size | Performance | Requirements |
|----------|---------|-----------|-------------|--------------|
| **CPU-Based** | Core functionality, development, testing | Small-Medium (<10K points) | Good | Standard Python |
| **GPU-Based** | High-performance, research, large-scale | Large (>10K points) | Excellent | NVIDIA GPU + CUDA |

## 🔧 Common Features

All demos include:
- **CI-friendly flags**: `--no-plot`, `--save-plots`, `--save-dir`
- **Comprehensive error handling**: Robust validation and error recovery
- **Progress indicators**: Real-time feedback for long operations
- **Documentation**: Detailed docstrings and usage examples
- **Modular design**: Easy to extend and customize

## 📈 Performance Characteristics

### CPU-Based Demos
- **Speed**: Optimized for typical desktop/laptop systems
- **Memory**: Efficient memory usage for standard workloads
- **Compatibility**: Works on any Python environment
- **Scalability**: Good performance up to ~10K data points

### GPU-Based Demos
- **Speed**: 10-100x faster for large datasets
- **Memory**: Optimized GPU memory usage
- **Scalability**: Excellent performance scaling with data size
- **Batch Processing**: Efficient parallel computation

## 🛠️ Installation

### Basic Requirements (CPU Demos)
```bash
pip install numpy scipy matplotlib seaborn pandas numba
```

### GPU Requirements (GPU Demos)
```bash
# Install JAX with GPU support
pip install --upgrade "jax[cuda]" -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html

# Additional requirements
pip install numpy scipy matplotlib seaborn pandas
```

## 🧪 Testing

Run the demo test suite to verify all demos work correctly:

```bash
python test_demos.py
```

## 📝 Usage Examples

### Basic Parameter Estimation
```bash
# CPU version
cd demos/cpu_based
python parameter_estimation_demo.py --no-plot

# GPU version (if available)
cd demos/gpu_based
python jax_performance_demo.py --device gpu --batch-size 1000
```

### Performance Benchmarking
```bash
# CPU benchmarking
cd demos/cpu_based
python estimator_benchmark.py --sizes 1000,2000,5000

# GPU benchmarking
cd demos/gpu_based
python high_performance_comparison_demo.py --sizes 1000,5000,10000,20000
```

### Real-World Testing
```bash
# Robustness testing
cd demos/cpu_based
python real_world_confounds_demo.py --n-samples 2000 --save-dir results/
```

## 🎨 Visualization

All demos generate comprehensive visualizations:
- **Parameter estimation plots**: Accuracy and performance comparisons
- **Scaling plots**: Performance vs data size relationships
- **Robustness plots**: Estimator performance under contamination
- **Statistical plots**: Distribution and correlation analysis

## 📊 Output Formats

Demos generate various output formats:
- **Console output**: Progress information and results
- **Plots**: Matplotlib/Seaborn visualizations
- **CSV files**: Numerical results and statistics
- **Reports**: Detailed analysis and recommendations
- **Logs**: Performance metrics and timing information

## 🔍 Troubleshooting

### Common Issues
1. **Import errors**: Ensure all dependencies are installed
2. **Memory errors**: Reduce data size or batch size
3. **GPU not detected**: Check CUDA installation and JAX GPU support
4. **Performance issues**: Verify hardware compatibility and driver versions

### Getting Help
- Check individual demo README files for specific instructions
- Review error messages for troubleshooting hints
- Ensure Python environment has all required dependencies
- For GPU issues, verify CUDA and JAX installation

## 📚 Additional Resources

- **API Documentation**: `documentation/api_reference/`
- **User Guides**: `documentation/user_guides/`
- **Project Instructions**: `documentation/project_instructions.md`
- **Test Suite**: `tests/` directory

---

*For detailed information about each demo category, see the README files in `cpu_based/` and `gpu_based/` directories.*
