use pyo3::prelude::*;

mod features;
mod parallel;

use features::co_auto_corr::{
    co_embed2_dist_tau_d_expfit_meandiff, co_f1ecac, co_first_min_ac, co_histogramami_even_2_5,
    co_trev_1_num,
};
use features::dn_histogrammode_10::dn_histogrammode_10;
use features::dn_histogrammode_5::dn_histogrammode_5;
use features::dn_mean::dn_mean;
use features::dn_outlierinclude::{dn_outlierinclude_n_001_mdrmd, dn_outlierinclude_p_001_mdrmd};
use features::dn_spread_std::dn_spread_std;
use features::fc_localsimple::{fc_localsimple_mean1_tauresrat, fc_localsimple_mean3_stderr};
use features::in_automutualinfostats::in_automutualinfostats_40_gaussian_fmmi;
use features::md_hrv::md_hrv_classic_pnn40;
use features::pd_periodicitywang::pd_periodicitywang;
use features::sb_binarystats::{
    bin_binarystats_diff_longsstretch0, bin_binarystats_mean_longstretch1,
};
use features::sb_motifthree::sb_motifthree_quantile_hh;
use features::sb_transitionmatrix::sb_transitionmatrix_3ac_sumdiagcov;
use features::sc_fluctanal::{
    sc_fluctanal_2_dfa_50_1_2_logi_prop_r1, sc_fluctanal_2_rsrangefit_50_1_2_logi_prop_r1,
};
use features::sp_summaries::{sp_summaries_welch_rect_area_5_1, sp_summaries_welch_rect_centroid};
use parallel::{compute_catch22_parallel, extract_catch22_features_cumulative_optimized};

#[pyclass]
pub struct Catch22Result {
    #[pyo3(get)]
    pub names: Vec<String>,
    #[pyo3(get)]
    pub values: Vec<f64>,
}

#[pyfunction]
#[pyo3(signature = (y, normalize=None, catch24=None))]
fn py_catch22_all(y: Vec<f64>, normalize: Option<bool>, catch24: Option<bool>) -> Catch22Result {
    
    let result = compute_catch22_parallel(y, normalize.unwrap_or(true), catch24.unwrap_or(false));

    Catch22Result {
        names: result.names,
        values: result.values,
    }
}

#[pyfunction]
#[pyo3(signature = (y, normalize=None))]
fn py_co_trev_1_num(y: Vec<f64>, normalize: Option<bool>) -> f64 {
    let use_normalization = normalize.unwrap_or(true);
    co_trev_1_num(&y, use_normalization)
}

#[pyfunction]
#[pyo3(signature = (y, normalize=None))]
fn py_co_f1ecac(y: Vec<f64>, normalize: Option<bool>) -> f64 {
    let use_normalization = normalize.unwrap_or(true);
    co_f1ecac(&y, use_normalization)
}

#[pyfunction]
#[pyo3(signature = (y, normalize=None))]
fn py_co_first_min_ac(y: Vec<f64>, normalize: Option<bool>) -> f64 {
    let use_normalization = normalize.unwrap_or(true);
    co_first_min_ac(&y, use_normalization) as f64
}

#[pyfunction]
#[pyo3(signature = (y, normalize=None))]
fn py_co_histogramami_even_2_5(y: Vec<f64>, normalize: Option<bool>) -> f64 {
    let use_normalization = normalize.unwrap_or(true);
    co_histogramami_even_2_5(&y, use_normalization)
}

#[pyfunction]
#[pyo3(signature = (y, normalize=None))]
fn py_dn_histogrammode_5(y: Vec<f64>, normalize: Option<bool>) -> f64 {
    let use_normalization = normalize.unwrap_or(true);
    dn_histogrammode_5(&y, use_normalization)
}

#[pyfunction]
#[pyo3(signature = (y, normalize=None))]
fn py_dn_histogrammode_10(y: Vec<f64>, normalize: Option<bool>) -> f64 {
    let use_normalization = normalize.unwrap_or(true);
    dn_histogrammode_10(&y, use_normalization)
}

#[pyfunction]
#[pyo3(signature = (y, normalize=None))]
fn py_md_hrv_classic_pnn40(y: Vec<f64>, normalize: Option<bool>) -> f64 {
    let use_normalization = normalize.unwrap_or(true);
    md_hrv_classic_pnn40(&y, use_normalization)
}

#[pyfunction]
#[pyo3(signature = (y, normalize=None))]
fn py_sb_binarystats_diff_longsstretch0(y: Vec<f64>, normalize: Option<bool>) -> f64 {
    let use_normalization = normalize.unwrap_or(true);
    bin_binarystats_diff_longsstretch0(&y, use_normalization)
}

#[pyfunction]
#[pyo3(signature = (y, normalize=None))]
fn py_sb_transitionmatrix_3ac_sumdiagcov(y: Vec<f64>, normalize: Option<bool>) -> f64 {
    let use_normalization = normalize.unwrap_or(true);
    sb_transitionmatrix_3ac_sumdiagcov(&y, use_normalization)
}

#[pyfunction]
#[pyo3(signature = (y, normalize=None))]
fn py_sb_binarystats_mean_longstretch1(y: Vec<f64>, normalize: Option<bool>) -> f64 {
    let use_normalization = normalize.unwrap_or(true);
    bin_binarystats_mean_longstretch1(&y, use_normalization)
}

#[pyfunction]
#[pyo3(signature = (y, normalize=None))]
fn py_pd_periodicitywang(y: Vec<f64>, normalize: Option<bool>) -> f64 {
    let use_normalization = normalize.unwrap_or(true);
    pd_periodicitywang(&y, use_normalization) as f64
}

#[pyfunction]
#[pyo3(signature = (y, normalize=None))]
fn py_co_embed2_dist_tau_d_expfit_meandiff(y: Vec<f64>, normalize: Option<bool>) -> f64 {
    let use_normalization = normalize.unwrap_or(true);
    co_embed2_dist_tau_d_expfit_meandiff(&y, use_normalization)
}

#[pyfunction]
#[pyo3(signature = (y, normalize=None))]
fn py_in_automutualinfostats_40_gaussian_fmmi(y: Vec<f64>, normalize: Option<bool>) -> f64 {
    let use_normalization = normalize.unwrap_or(true);
    in_automutualinfostats_40_gaussian_fmmi(&y, use_normalization)
}

#[pyfunction]
#[pyo3(signature = (y, normalize=None))]
fn py_fc_localsimple_mean1_tauresrat(y: Vec<f64>, normalize: Option<bool>) -> f64 {
    let use_normalization = normalize.unwrap_or(true);
    fc_localsimple_mean1_tauresrat(&y, use_normalization)
}

#[pyfunction]
#[pyo3(signature = (y, normalize=None))]
fn py_fc_localsimple_mean3_stderr(y: Vec<f64>, normalize: Option<bool>) -> f64 {
    let use_normalization = normalize.unwrap_or(true);
    fc_localsimple_mean3_stderr(&y, use_normalization)
}

#[pyfunction]
#[pyo3(signature = (y, normalize=None))]
fn py_dn_outlierinclude_p_001_mdrmd(y: Vec<f64>, normalize: Option<bool>) -> f64 {
    let use_normalization = normalize.unwrap_or(true);
    dn_outlierinclude_p_001_mdrmd(&y, use_normalization)
}

#[pyfunction]
#[pyo3(signature = (y, normalize=None))]
fn py_dn_outlierinclude_n_001_mdrmd(y: Vec<f64>, normalize: Option<bool>) -> f64 {
    let use_normalization = normalize.unwrap_or(true);
    dn_outlierinclude_n_001_mdrmd(&y, use_normalization)
}

#[pyfunction]
#[pyo3(signature = (y, normalize=None))]
fn py_sp_summaries_welch_rect_area_5_1(y: Vec<f64>, normalize: Option<bool>) -> f64 {
    let use_normalization = normalize.unwrap_or(true);
    sp_summaries_welch_rect_area_5_1(&y, use_normalization)
}

#[pyfunction]
#[pyo3(signature = (y, normalize=None))]
fn py_sp_summaries_welch_rect_centroid(y: Vec<f64>, normalize: Option<bool>) -> f64 {
    let use_normalization = normalize.unwrap_or(true);
    sp_summaries_welch_rect_centroid(&y, use_normalization)
}

#[pyfunction]
#[pyo3(signature = (y, normalize=None))]
fn py_sb_motifthree_quantile_hh(y: Vec<f64>, normalize: Option<bool>) -> f64 {
    let use_normalization = normalize.unwrap_or(true);
    sb_motifthree_quantile_hh(&y, use_normalization)
}

#[pyfunction]
#[pyo3(signature = (y, normalize=None))]
fn py_sc_fluctanal_2_dfa_50_1_2_logi_prop_r1(y: Vec<f64>, normalize: Option<bool>) -> f64 {
    let use_normalization = normalize.unwrap_or(true);
    sc_fluctanal_2_dfa_50_1_2_logi_prop_r1(&y, 2, "dfa", use_normalization)
}

#[pyfunction]
#[pyo3(signature = (y, normalize=None))]
fn py_sc_fluctanal_2_rsrangefit_50_1_2_logi_prop_r1(y: Vec<f64>, normalize: Option<bool>) -> f64 {
    let use_normalization = normalize.unwrap_or(true);
    sc_fluctanal_2_rsrangefit_50_1_2_logi_prop_r1(&y, 1, "rsrangefit", use_normalization)
}

#[pyfunction]
fn py_dn_mean(y: Vec<f64>) -> f64 {
    dn_mean(&y)
}

#[pyfunction]
fn py_dn_spread_std(y: Vec<f64>) -> f64 {
    dn_spread_std(&y)
}

// Add this new PyClass for the cumulative result
#[pyclass]
#[derive(Debug, Clone)]
pub struct CumulativeFeatures {
    #[pyo3(get)]
    pub feature_names: Vec<String>,
    #[pyo3(get)]
    pub values: Vec<Vec<f64>>,
}

// Add this Python function
#[pyfunction]
#[pyo3(signature = (series, normalize=None, catch24=None, value_column_name=None))]
fn py_extract_catch22_features_cumulative(
    series: Vec<f64>, 
    normalize: Option<bool>, 
    catch24: Option<bool>,
    value_column_name: Option<String>
) -> CumulativeFeatures {
    let normalize = normalize.unwrap_or(true);
    let catch24 = catch24.unwrap_or(false);
    
    let result = extract_catch22_features_cumulative_optimized(
        &series, 
        normalize, 
        catch24, 
        value_column_name.as_deref()
    );

    // Extract feature names from the first row (they should be consistent)
    let feature_names: Vec<String> = if let Some(first_row) = result.data.first() {
        let mut names: Vec<String> = first_row.keys().cloned().collect();
        names.sort(); // Ensure consistent ordering
        names
    } else {
        Vec::new()
    };
    
    // Extract values in the same order as feature names
    let values: Vec<Vec<f64>> = result.data.iter().map(|row| {
        feature_names.iter().map(|name| {
            row.get(name).copied().unwrap_or(f64::NAN)
        }).collect()
    }).collect();
    
    CumulativeFeatures {
        feature_names,
        values,
    }
}

#[pymodule]
fn rs_catch_22(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Catch22Result>()?;
    m.add_class::<CumulativeFeatures>()?;
    m.add_function(wrap_pyfunction!(py_catch22_all, m)?)?;
    m.add_function(wrap_pyfunction!(py_co_trev_1_num, m)?)?;
    m.add_function(wrap_pyfunction!(py_dn_histogrammode_10, m)?)?;
    m.add_function(wrap_pyfunction!(py_dn_histogrammode_5, m)?)?;
    m.add_function(wrap_pyfunction!(py_co_f1ecac, m)?)?;
    m.add_function(wrap_pyfunction!(py_co_first_min_ac, m)?)?;
    m.add_function(wrap_pyfunction!(py_co_histogramami_even_2_5, m)?)?;
    m.add_function(wrap_pyfunction!(py_md_hrv_classic_pnn40, m)?)?;
    m.add_function(wrap_pyfunction!(py_dn_mean, m)?)?;
    m.add_function(wrap_pyfunction!(py_dn_spread_std, m)?)?;
    m.add_function(wrap_pyfunction!(py_sb_binarystats_diff_longsstretch0, m)?)?;
    m.add_function(wrap_pyfunction!(py_sb_binarystats_mean_longstretch1, m)?)?;
    m.add_function(wrap_pyfunction!(py_sb_transitionmatrix_3ac_sumdiagcov, m)?)?;
    m.add_function(wrap_pyfunction!(py_pd_periodicitywang, m)?)?;
    m.add_function(wrap_pyfunction!(
        py_co_embed2_dist_tau_d_expfit_meandiff,
        m
    )?)?;
    m.add_function(wrap_pyfunction!(
        py_in_automutualinfostats_40_gaussian_fmmi,
        m
    )?)?;
    m.add_function(wrap_pyfunction!(py_fc_localsimple_mean1_tauresrat, m)?)?;
    m.add_function(wrap_pyfunction!(py_fc_localsimple_mean3_stderr, m)?)?;
    m.add_function(wrap_pyfunction!(py_dn_outlierinclude_p_001_mdrmd, m)?)?;
    m.add_function(wrap_pyfunction!(py_dn_outlierinclude_n_001_mdrmd, m)?)?;
    m.add_function(wrap_pyfunction!(py_sp_summaries_welch_rect_area_5_1, m)?)?;
    m.add_function(wrap_pyfunction!(py_sp_summaries_welch_rect_centroid, m)?)?;
    m.add_function(wrap_pyfunction!(py_sb_motifthree_quantile_hh, m)?)?;
    m.add_function(wrap_pyfunction!(
        py_sc_fluctanal_2_dfa_50_1_2_logi_prop_r1,
        m
    )?)?;
    m.add_function(wrap_pyfunction!(
        py_sc_fluctanal_2_rsrangefit_50_1_2_logi_prop_r1,
        m
    )?)?;
    m.add_function(wrap_pyfunction!(py_extract_catch22_features_cumulative, m)?)?;
    Ok(())
}