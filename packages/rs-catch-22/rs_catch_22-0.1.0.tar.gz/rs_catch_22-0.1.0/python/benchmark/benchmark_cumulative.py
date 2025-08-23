import time

from python.helpers import (
    create_large_benchmark_dataset,
    extract_catch22_features_parallel_rs,
    extract_catch22_features_parallel,
    extract_catch22_features_cumulative_rust,
)

# Create a large benchmark dataset to test the performance of the Rust and Python/C versions for the cumulative version of the catch22 features
df = create_large_benchmark_dataset(n_points=1000)

# Initialize timing variables
python_total_time = 0
rust_total_time = 0
rust_optimized_total_time = 0
num_runs = 10

print(f"Running benchmarks with {num_runs} runs...")

# Time Python/C version
print(f"\n=== Python/C version ({num_runs} runs) ===")
for i in range(num_runs):
    start_time = time.time()
    df_py = extract_catch22_features_parallel(df['VALUE'], df, value_column='VALUE', date_column='DATE')
    end_time = time.time()
    run_time = end_time - start_time
    python_total_time += run_time
    print(f"Run {i+1}: {run_time:.4f} seconds")

# Time Rust version
print(f"\n=== Rust version ({num_runs} runs) ===")
for i in range(num_runs):
    start_time = time.time()
    df_rs = extract_catch22_features_parallel_rs(df['VALUE'], df, value_column='VALUE', date_column='DATE')
    end_time = time.time()
    run_time = end_time - start_time
    rust_total_time += run_time
    print(f"Run {i+1}: {run_time:.4f} seconds")

# Time Rust optimized version
print(f"\n=== Rust optimized version ({num_runs} runs) ===")
for i in range(num_runs):
    start_time = time.time()
    df_rs_optimized = extract_catch22_features_cumulative_rust(df['VALUE'], df, value_column='VALUE', date_column='DATE', normalize=True, catch24=True)
    end_time = time.time()
    run_time = end_time - start_time
    rust_optimized_total_time += run_time
    print(f"Run {i+1}: {run_time:.4f} seconds")

# Calculate and display averages
python_avg = python_total_time / num_runs
rust_avg = rust_total_time / num_runs
rust_optimized_avg = rust_optimized_total_time / num_runs

print("\n" + "="*50)
print("BENCHMARK RESULTS")
print("="*50)
print(f"Python/C average time:     {python_avg:.4f} seconds")
print(f"Rust average time:         {rust_avg:.4f} seconds")
print(f"Rust optimized average time: {rust_optimized_avg:.4f} seconds")

# Calculate speedups
if rust_avg < python_avg:
    speedup = python_avg / rust_avg
    print(f"Rust is {speedup:.2f}x faster than Python/C")
else:
    slowdown = rust_avg / python_avg
    print(f"Rust is {slowdown:.2f}x slower than Python/C")

if rust_optimized_avg < python_avg:
    speedup = python_avg / rust_optimized_avg
    print(f"Rust optimized is {speedup:.2f}x faster than Python/C")
else:
    slowdown = rust_optimized_avg / python_avg
    print(f"Rust optimized is {slowdown:.2f}x slower than Python/C")

if rust_optimized_avg < rust_avg:
    speedup = rust_avg / rust_optimized_avg
    print(f"Rust optimized is {speedup:.2f}x faster than regular Rust")
else:
    slowdown = rust_optimized_avg / rust_avg
    print(f"Rust optimized is {slowdown:.2f}x slower than regular Rust")

