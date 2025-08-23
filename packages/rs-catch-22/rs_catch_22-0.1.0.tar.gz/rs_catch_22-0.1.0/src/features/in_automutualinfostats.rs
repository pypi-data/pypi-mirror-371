use crate::features::stats::*;

pub fn in_automutualinfostats_40_gaussian_fmmi(y: &[f64], normalize: bool) -> f64 {
    if y.iter().any(|&val| val.is_nan() || val.is_infinite()) || y.len() < 2 {
        return f64::NAN;
    }

    let data = if normalize {
        zscore_norm2(y)
    } else {
        y.to_vec()
    };

    let mut tau = 40;
    let size = data.len();

    if tau > (size as f64 / 2.0).ceil() as usize {
        tau = (size as f64 / 2.0).ceil() as usize;
    }

    let mut ami = vec![0.0; tau];

    for i in 0..tau {
        let ac = autocorr_lag(&data, i + 1);
        ami[i] = -0.5 * (1.0 - ac * ac).ln();
    }

    // find first minimum of automutual information
    let mut fmmi = tau as f64;
    for i in 1..tau - 1 {
        if ami[i] < ami[i - 1] && ami[i] < ami[i + 1] {
            fmmi = i as f64;
            break;
        }
    }

    fmmi
}
