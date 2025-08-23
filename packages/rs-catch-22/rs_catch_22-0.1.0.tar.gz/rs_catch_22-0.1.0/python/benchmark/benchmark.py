import rs_catch_22
import pycatch22
import numpy as np
import time

# Set a fixed seed for reproducible results
np.random.seed(42)
y = np.random.rand(1000)

# Initialize timing variables
python_total_time = 0
rust_total_time = 0
num_runs = 10_000

print("Running benchmarks...")

# Time Python implementation
print(f"\n=== Python pycatch22 ({num_runs} runs) ===")
for i in range(num_runs):
    start_time = time.time()
    result_catch22 = pycatch22.catch22_all(y, catch24=True)
    end_time = time.time()
    run_time = end_time - start_time
    python_total_time += run_time
    print(f"Run {i+1}: {run_time:.4f} seconds")

# Time Rust implementation  
print(f"\n=== Rust rs_catch_22 ({num_runs} runs) ===")
for i in range(num_runs):
    start_time = time.time()
    result_rust_catch22 = rs_catch_22.py_catch22_all(y, catch24=True, normalize=True)
    end_time = time.time()
    run_time = end_time - start_time
    rust_total_time += run_time
    print(f"Run {i+1}: {run_time:.4f} seconds")

# Calculate and display averages
python_avg = python_total_time / num_runs
rust_avg = rust_total_time / num_runs

print("\n" + "="*50)
print("BENCHMARK RESULTS")
print("="*50)
print(f"Python average time: {python_avg:.4f} seconds")
print(f"Rust average time:   {rust_avg:.4f} seconds")

if rust_avg < python_avg:
    speedup = python_avg / rust_avg
    print(f"Rust is {speedup:.2f}x faster")
else:
    slowdown = rust_avg / python_avg
    print(f"Rust is {slowdown:.2f}x slower") 

