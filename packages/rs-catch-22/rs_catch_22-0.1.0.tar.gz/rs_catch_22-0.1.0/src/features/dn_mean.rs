pub fn dn_mean(y: &[f64]) -> f64 {
    if y.iter().any(|&val| val.is_nan()) {
        return f64::NAN;
    }

    y.iter().sum::<f64>() / y.len() as f64
}
