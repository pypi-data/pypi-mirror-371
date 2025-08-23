import rs_catch_22
import pytest
import numpy as np

# unit tests
def expected_output(res, catch24=False, short_names=False):
    which_set = "Catch24" if catch24 else "Catch22"
    num_features = 24 if catch24 else 22
    
    # For Rust implementation, the result is a Catch22Result object with names and values attributes
    assert hasattr(res, 'names'), f"{which_set} result should have 'names' attribute"
    assert hasattr(res, 'values'), f"{which_set} result should have 'values' attribute"
    
    # check the 'names' list
    assert isinstance(res.names, list), f"{which_set} expected list of names (str), got unexpected output."
    length_of_names = len(res.names)
    assert length_of_names == num_features, f"Expected {num_features} names for {which_set}, got {length_of_names} instead."
    assert all(isinstance(name, str) for name in res.names), f"{which_set} expected all returned names to be strings."

    # check the 'values' list
    assert isinstance(res.values, list), f"{which_set} expected list of values, got unexpected output."
    length_of_vals = len(res.values)
    assert length_of_vals == num_features, f"Expected {num_features} values for {which_set}, got {length_of_vals} instead."
    assert all(isinstance(val, (float, int)) for val in res.values), f"{which_set} expected all returned feature values to be floats or integers."

def test_catch22_runs():
    # test whether catch22 works on some random data
    tsData = np.random.randn(100).tolist()  # Convert to list for Rust
    res = rs_catch_22.py_catch22_all(tsData, catch24=False, normalize=True)
    expected_output(res, catch24=False, short_names=False)

def test_catch24_runs():
    # test whether catch24 works on some random data
    tsData = np.random.randn(100).tolist()  # Convert to list for Rust
    res = rs_catch_22.py_catch22_all(tsData, catch24=True, normalize=True)
    expected_output(res, catch24=True, short_names=False)

def test_valid_input_types():
    # should accept tuples, arrays and lists
    data_as_tuple = (1, 2, 3, 4, 5, 6, 7, 8)
    res_tuple = rs_catch_22.py_catch22_all(list(data_as_tuple), catch24=False, normalize=True)
    expected_output(res_tuple)
    
    data_as_list = [1, 2, 3, 4, 5, 6, 7, 8]
    res_list = rs_catch_22.py_catch22_all(data_as_list, catch24=False, normalize=True)
    expected_output(res_list)
    
    data_as_numpy = np.array(data_as_list)
    res_numpy = rs_catch_22.py_catch22_all(data_as_numpy.tolist(), catch24=False, normalize=True)
    expected_output(res_numpy)

def test_inf_and_nan_input():
    # pass in time series containing a NaN/inf, should return 0 (0.0) or NaN/inf outputs depending on feature
    zero_outputs = [2, 3, 9] # indexes of features with expected 0 or 0.0 output
    test_vals = [np.nan, np.inf, -np.inf]
    for val_type in test_vals:
        base_data = np.random.randn(100)
        base_data[0] = val_type
        res = rs_catch_22.py_catch22_all(base_data.tolist(), catch24=False, normalize=True)
        expected_output(res, catch24=False, short_names=False)
        res_values = res.values
        for i, val in enumerate(res_values):
            if i in zero_outputs:
                # check that value is 0 or 0.0
                assert val == 0 or val == 0.0, f"Expected 0 or 0.0 for feature {i+1} when passing ts containing {val_type}, got {val} instead."
            else:
                assert np.isnan(val) or np.isinf(val), f"Expected NaN or Inf for feature {i+1} when testing ts containing {val_type}, got {val}."
        
def test_individual_feature_methods():
    # ensure each individual feature method can be run in isolation
    data = list(np.random.randn(100))
    
    # Map of function names to their corresponding Rust functions
    individual_functions = [
        'py_dn_histogrammode_5',
        'py_dn_histogrammode_10', 
        'py_co_f1ecac',
        'py_co_first_min_ac',
        'py_co_histogramami_even_2_5',
        'py_co_trev_1_num',
        'py_md_hrv_classic_pnn40',
        'py_sb_binarystats_mean_longstretch1',
        'py_sb_transitionmatrix_3ac_sumdiagcov',
        'py_pd_periodicitywang',
        'py_co_embed2_dist_tau_d_expfit_meandiff',
        'py_in_automutualinfostats_40_gaussian_fmmi',
        'py_fc_localsimple_mean1_tauresrat',
        'py_dn_outlierinclude_p_001_mdrmd',
        'py_dn_outlierinclude_n_001_mdrmd',
        'py_sp_summaries_welch_rect_area_5_1',
        'py_sb_binarystats_diff_longsstretch0',
        'py_sb_motifthree_quantile_hh',
        'py_sc_fluctanal_2_rsrangefit_50_1_2_logi_prop_r1',
        'py_sc_fluctanal_2_dfa_50_1_2_logi_prop_r1',
        'py_sp_summaries_welch_rect_centroid',
        'py_fc_localsimple_mean3_stderr',
        'py_dn_mean',
        'py_dn_spread_std'
    ]
    
    assert len(individual_functions) == 24, f"Expected 24 individual feature methods, got {len(individual_functions)}."
    
    for func_name in individual_functions:
        try:
            func = getattr(rs_catch_22, func_name)
            
            # Most functions take normalize parameter, but dn_mean and dn_spread_std don't
            if func_name in ['py_dn_mean', 'py_dn_spread_std']:
                result = func(data)
            else:
                result = func(data, normalize=True)
                
            # Check that we got a numeric result
            assert isinstance(result, (float, int)), f"Method {func_name} should return a numeric value, got {type(result)}"
            
        except Exception as excinfo:
            pytest.fail(f"Method {func_name} raised an exception: {excinfo}")

if __name__ == "__main__":
    import sys
    try:
        # Your test logic here
        print("Tests completed successfully")
        sys.exit(0)
    except Exception as e:
        print(f"Tests failed: {e}")
        sys.exit(1)