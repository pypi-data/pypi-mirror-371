import pandas as pd
import numpy as np
import pytest
from python.helpers import (
    create_large_benchmark_dataset,
    extract_catch22_features_parallel,
    extract_catch22_features_cumulative_rust
)

def create_test_dataframes():
    """Create test dataframes for comparison"""
    df = create_large_benchmark_dataset(n_points=250)
    df_py = extract_catch22_features_parallel(df['VALUE'], df, value_column='VALUE', date_column='DATE')
    df_rs = extract_catch22_features_cumulative_rust(df['VALUE'], df, value_column='VALUE', date_column='DATE', normalize=True, catch24=True)
    return df_rs, df_py

def test_dataframe_shapes():
    """Test that Rust and Python dataframes have the same shape"""
    df_rs, df_py = create_test_dataframes()
    assert df_rs.shape == df_py.shape, f"DataFrames have different shapes: Rust={df_rs.shape}, Python={df_py.shape}"

def test_dataframe_columns():
    """Test that Rust and Python dataframes have the same columns"""
    df_rs, df_py = create_test_dataframes()
    rs_cols = set(df_rs.columns)
    py_cols = set(df_py.columns)
    
    missing_in_rust = py_cols - rs_cols
    missing_in_python = rs_cols - py_cols
    
    if missing_in_rust:
        pytest.fail(f"Columns missing in Rust DF: {missing_in_rust}")
    if missing_in_python:
        pytest.fail(f"Columns missing in Python DF: {missing_in_python}")

def test_dataframe_values():
    """Test that Rust and Python dataframes have equivalent values"""
    df_rs, df_py = create_test_dataframes()
    
    # Get common columns and align dataframes
    rs_cols = set(df_rs.columns)
    py_cols = set(df_py.columns)
    common_cols = list(rs_cols.intersection(py_cols))
    
    df_rs_aligned = df_rs[common_cols].copy()
    df_py_aligned = df_py[common_cols].copy()
    
    # Sort both dataframes by the first column to ensure proper alignment
    if len(common_cols) > 0:
        first_col = common_cols[0]
        df_rs_aligned = df_rs_aligned.sort_values(first_col).reset_index(drop=True)
        df_py_aligned = df_py_aligned.sort_values(first_col).reset_index(drop=True)
    
    # Compare row by row
    differences_found = []
    min_rows = min(len(df_rs_aligned), len(df_py_aligned))
    tol = 1e-12
    
    for idx in range(min_rows):
        row_rs = df_rs_aligned.iloc[idx]
        row_py = df_py_aligned.iloc[idx]
        
        col_differences = []
        for col in common_cols:
            val_rs = row_rs[col]
            val_py = row_py[col]
            
            # Handle NaN comparisons
            if pd.isna(val_rs) and pd.isna(val_py):
                continue
            elif pd.isna(val_rs) or pd.isna(val_py):
                col_differences.append(f"{col}: RS={val_rs}, PY={val_py}")
            # Handle numeric comparisons with tolerance
            elif isinstance(val_rs, (int, float)) and isinstance(val_py, (int, float)):
                if not np.isclose(val_rs, val_py, rtol=tol, atol=tol):
                    diff = abs(val_rs - val_py)
                    col_differences.append(f"{col}: RS={val_rs}, PY={val_py} (diff={diff:.2e})")
            # Handle string/other comparisons
            else:
                if val_rs != val_py:
                    col_differences.append(f"{col}: RS={val_rs}, PY={val_py}")
        
        if col_differences:
            differences_found.append({
                'row': idx,
                'differences': col_differences
            })
    
    # If differences found, fail with detailed information
    if differences_found:
        error_msg = f"Found {len(differences_found)} rows with differences out of {min_rows} total rows.\n"
        error_msg += "First 5 differences:\n"
        
        for i, diff in enumerate(differences_found[:5]):
            error_msg += f"Row {diff['row']}: {'; '.join(diff['differences'][:3])}\n"
            if len(diff['differences']) > 3:
                error_msg += f"  ... and {len(diff['differences'])-3} more differences\n"
        
        if len(differences_found) > 5:
            error_msg += f"... and {len(differences_found)-5} more rows with differences\n"
        
        pytest.fail(error_msg)

def test_dataframe_comparison_detailed():
    """Detailed comparison test that saves differences to file for analysis"""
    df_rs, df_py = create_test_dataframes()
    
    # Get common columns and align dataframes
    rs_cols = set(df_rs.columns)
    py_cols = set(df_py.columns)
    common_cols = list(rs_cols.intersection(py_cols))
    
    df_rs_aligned = df_rs[common_cols].copy()
    df_py_aligned = df_py[common_cols].copy()
    
    # Sort both dataframes by the first column to ensure proper alignment
    if len(common_cols) > 0:
        first_col = common_cols[0]
        df_rs_aligned = df_rs_aligned.sort_values(first_col).reset_index(drop=True)
        df_py_aligned = df_py_aligned.sort_values(first_col).reset_index(drop=True)
    
    # Compare and save detailed results
    differences_found = []
    min_rows = min(len(df_rs_aligned), len(df_py_aligned))
    exact_matches = 0
    tol = 1e-12
    
    for idx in range(min_rows):
        row_rs = df_rs_aligned.iloc[idx]
        row_py = df_py_aligned.iloc[idx]
        
        row_exact_match = True
        col_differences = []
        
        for col in common_cols:
            val_rs = row_rs[col]
            val_py = row_py[col]
            
            # Handle NaN comparisons
            if pd.isna(val_rs) and pd.isna(val_py):
                continue
            elif pd.isna(val_rs) or pd.isna(val_py):
                row_exact_match = False
                col_differences.append(f"{col}: RS={val_rs}, PY={val_py}")
            # Handle numeric comparisons with tolerance
            elif isinstance(val_rs, (int, float)) and isinstance(val_py, (int, float)):
                if not np.isclose(val_rs, val_py, rtol=tol, atol=tol):
                    row_exact_match = False
                    diff = abs(val_rs - val_py)
                    col_differences.append(f"{col}: RS={val_rs}, PY={val_py} (diff={diff:.2e})")
            # Handle string/other comparisons
            else:
                if val_rs != val_py:
                    row_exact_match = False
                    col_differences.append(f"{col}: RS={val_rs}, PY={val_py}")
        
        if row_exact_match:
            exact_matches += 1
        else:
            differences_found.append({
                'row': idx,
                'differences': col_differences
            })
    
    # Save detailed differences to file if any found
    if differences_found:
        with open('detailed_differences.txt', 'w') as f:
            f.write("DETAILED ROW-BY-ROW DIFFERENCES\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Total rows compared: {min_rows}\n")
            f.write(f"Exact matches: {exact_matches}\n")
            f.write(f"Rows with differences: {len(differences_found)}\n\n")
            
            for diff in differences_found:
                f.write(f"Row {diff['row']}:\n")
                
                # Write full row data
                f.write("Rust row data:\n")
                rs_row = df_rs_aligned.iloc[diff['row']]
                for col in common_cols:
                    f.write(f"  {col}: {rs_row[col]}\n")
                
                f.write("\nPython row data:\n")
                py_row = df_py_aligned.iloc[diff['row']]
                for col in common_cols:
                    f.write(f"  {col}: {py_row[col]}\n")
                
                f.write("\nDifferences:\n")
                for col_diff in diff['differences']:
                    f.write(f"  {col_diff}\n")
                f.write("\n" + "="*50 + "\n\n")
    
    # This test passes even if differences are found - it's just for analysis
    # The actual assertion test is in test_dataframe_values()
    match_percentage = (exact_matches / min_rows) * 100 if min_rows > 0 else 0
    print(f"DataFrame comparison: {exact_matches}/{min_rows} rows match ({match_percentage:.1f}%)")
    if differences_found:
        print(f"Detailed differences saved to 'detailed_differences.txt'")

# Add this at the end like the other test files
if __name__ == "__main__":
    import sys
    try:
        test_dataframe_shapes()
        test_dataframe_columns()
        test_dataframe_values()
        test_dataframe_comparison_detailed()
        print("Tests completed successfully")
        sys.exit(0)
    except Exception as e:
        print(f"Tests failed: {e}")
        sys.exit(1)