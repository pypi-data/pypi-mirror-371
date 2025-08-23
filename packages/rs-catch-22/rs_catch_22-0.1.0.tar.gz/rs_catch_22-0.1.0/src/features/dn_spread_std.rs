use crate::features::stats::stddev;

pub fn dn_spread_std(y: &[f64]) -> f64 {
    // NaN check
    if y.iter().any(|&val| val.is_nan()) {
        return f64::NAN;
    }

    let std = stddev(y);

    std
}
