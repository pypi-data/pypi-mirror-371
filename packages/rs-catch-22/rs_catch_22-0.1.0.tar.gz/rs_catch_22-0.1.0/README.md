# rs-catch-22 🦀

A high-performance Rust implementation of the catch22 time-series feature extraction library, offering **4.38x faster** computation compared to the original Python implementation.

## Overview

**rs-catch-22** is a Rust-based reimplementation of the canonical catch22 time-series feature set, originally developed as [pycatch22](https://github.com/DynamicsAndNeuralSystems/pycatch22). This package provides Python bindings for all 22 time-series features (plus optional mean and standard deviation for catch24) with significant performance improvements through Rust's zero-cost abstractions and parallel computation.

catch22 is a collection of 22 time-series features coded in C that can be run from Python, R, Matlab, and Julia. This Rust implementation maintains full compatibility with the original API while delivering substantial performance gains.

## Key Features

- ⚡ **Massive Performance Gains**: 4.6x faster for individual features, up to 14.48x faster for batch processing
- 🦀 **Memory Safe**: Built with Rust's ownership system for guaranteed memory safety  
- 🔄 **Parallel Processing**: Leverages Rayon for concurrent feature computation across multiple time series
- 🐍 **Drop-in Replacement**: Identical API to pycatch22 with seamless integration
- 📊 **Complete Feature Set**: All 22 canonical features + optional mean/std (catch24)
- 🎯 **Optimized Dependencies**: Minimal external dependencies optimized for performance at compile time
- 🔢 **Batch Processing**: Highly optimized cumulative feature extraction for large datasets, seeing improvements of 14x

### Individual Features
Benchmarking results on 1,000-point time series (10,000 runs average):
- **Python pycatch22:** 0.0024 seconds
- **Rust rs-catch-22:** 0.0006 seconds  
- **Performance:** **4.38x faster**

### Batch Processing  
Benchmarking results on 1,000 time series (10 runs average):
- **Python pycatch22 cumulative:** 1.0723 seconds
- **Rust rs_catch_22 cumulative:** 0.3895 seconds
- **Rust rs_catch_22 parallelized:** 0.0740 seconds

**Performance Summary:**
- Rust is **2.75x faster** than Python/C
- Rust optimized is **14.48x faster** than Python/C  
- Rust optimized is **5.26x faster** than regular Rust

*Benchmark files: [`python/benchmark/benchmark.py`](python/benchmark/benchmark.py) and [`python/benchmark/benchmark_cumulative.py`](python/benchmark/benchmark_cumulative.py)*
