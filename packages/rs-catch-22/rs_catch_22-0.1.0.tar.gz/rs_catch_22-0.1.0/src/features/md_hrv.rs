use crate::features::stats::{diff, zscore_norm2};

pub fn md_hrv_classic_pnn40(y: &[f64], normalize: bool) -> f64 {
    // NaN and infinite check - return NaN for both
    if y.iter().any(|&val| val.is_nan() || val.is_infinite()) {
        return f64::NAN;
    }

    let data = if normalize {
        zscore_norm2(y)
    } else {
        y.to_vec()
    };

    let pnnx: f64 = 40.0;

    let diffs = diff(&data);

    let mut pnn40 = 0.0;

    for i in 0..diffs.len() {
        if (diffs[i].abs() * 1000.0) > pnnx {
            pnn40 += 1.0;
        }
    }

    pnn40 / (diffs.len() as f64)
}
