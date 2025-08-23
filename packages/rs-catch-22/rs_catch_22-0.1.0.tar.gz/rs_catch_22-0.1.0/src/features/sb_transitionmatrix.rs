use crate::features::co_auto_corr::*;
use crate::features::sb_coarsegrain::*;
use crate::features::stats::*;

pub fn sb_transitionmatrix_3ac_sumdiagcov(y: &[f64], normalize: bool) -> f64 {
    // NaN and const check
    if y.iter().any(|&val| val.is_nan() || val.is_infinite()) {
        return f64::NAN;
    }

    // Check if constant
    if y.iter().all(|&val| val == y[0]) {
        return f64::NAN;
    }

    let data = if normalize {
        zscore_norm2(y)
    } else {
        y.to_vec()
    };

    let n_groups = 3;
    let tau = co_firstzero(&data, data.len());

    let y_filt = data.clone();

    // Downsample
    let n_down = (data.len() - 1) / tau + 1;
    let mut y_down = Vec::with_capacity(n_down);

    for i in 0..n_down {
        y_down.push(y_filt[i * tau]);
    }

    // Transfer to alphabet
    let mut y_cg = vec![0; n_down];
    sb_coarse_grain(&y_down, "quantile", n_groups, &mut y_cg);

    // Initialize transition matrix
    let mut t = vec![vec![0.0; n_groups]; n_groups];

    // Build transition matrix
    for j in 0..n_down - 1 {
        t[y_cg[j] - 1][y_cg[j + 1] - 1] += 1.0;
    }

    // Normalize
    for i in 0..n_groups {
        for j in 0..n_groups {
            t[i][j] /= (n_down - 1) as f64;
        }
    }

    // Extract columns
    let mut columns = vec![vec![0.0; n_groups]; n_groups];
    for i in 0..n_groups {
        for j in 0..n_groups {
            columns[j][i] = t[i][j];
        }
    }

    // Calculate covariance matrix
    let mut cov_matrix = vec![vec![0.0; n_groups]; n_groups];
    for i in 0..n_groups {
        for j in i..n_groups {
            let cov_temp = cov(&columns[i], &columns[j]);
            cov_matrix[i][j] = cov_temp;
            cov_matrix[j][i] = cov_temp;
        }
    }

    // Sum diagonal elements
    let mut sum_diag_cov = 0.0;
    for i in 0..n_groups {
        sum_diag_cov += cov_matrix[i][i];
    }

    sum_diag_cov
}
