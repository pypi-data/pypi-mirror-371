use crate::features::stats::{mean, zscore_norm2};

pub fn bin_binarystats_diff_longsstretch0(y: &[f64], normalize: bool) -> f64 {
    // NaN check
    if y.iter().any(|&val| val.is_nan() || val.is_infinite()) || y.len() < 2 {
        return f64::NAN;
    }

    let data = if normalize {
        zscore_norm2(y)
    } else {
        y.to_vec()
    };

    // binarize
    let mut y_bin = Vec::with_capacity(data.len() - 1);
    for i in 0..data.len() - 1 {
        let diff_temp = data[i + 1] - data[i];
        y_bin.push(if diff_temp < 0.0 { 0 } else { 1 });
    }

    // Find longest stretch of 0s
    let mut max_stretch0 = 0;
    let mut last1 = 0;

    for i in 0..y_bin.len() {
        if y_bin[i] == 1 || i == y_bin.len() - 1 {
            let stretch0 = i - last1;
            if stretch0 > max_stretch0 {
                max_stretch0 = stretch0;
            }
            last1 = i;
        }
    }

    max_stretch0 as f64
}

pub fn bin_binarystats_mean_longstretch1(y: &[f64], normalize: bool) -> f64 {
    // NaN check
    if y.iter().any(|&val| val.is_nan() || val.is_infinite()) || y.len() < 2 {
        return f64::NAN;
    }

    let data = if normalize {
        zscore_norm2(y)
    } else {
        y.to_vec()
    };

    // binarize
    let y_mean = mean(&data);
    let mut y_bin = Vec::with_capacity(data.len() - 1);
    for i in 0..data.len() - 1 {
        y_bin.push(if data[i] - y_mean <= 0.0 { 0 } else { 1 });
    }

    // Find longest stretch of 1s
    let mut max_stretch1 = 0;
    let mut last0 = 0;

    for i in 0..y_bin.len() {
        if y_bin[i] == 0 || i == y_bin.len() - 1 {
            let stretch1 = i - last0;
            if stretch1 > max_stretch1 {
                max_stretch1 = stretch1;
            }
            last0 = i;
        }
    }

    max_stretch1 as f64
}
