use crate::features::splinefit::*;
use crate::features::stats::*;

pub fn pd_periodicitywang(y: &[f64], normalize: bool) -> i32 {
    if y.iter().any(|&val| val.is_nan() || val.is_infinite()) {
        return 0;
    }

    let data = if normalize {
        zscore_norm2(y)
    } else {
        y.to_vec()
    };

    const TH: f64 = 0.01;

    let mut yspline = vec![0.0; data.len()];
    splinefit(&data, &mut yspline);

    let mut ysub = vec![0.0; data.len()];
    for i in 0..data.len() {
        ysub[i] = data[i] - yspline[i];
    }

    for i in 0..data.len() {
        ysub[i] = data[i] - yspline[i];
    }

    let acmax = (data.len() as f64 / 3.0).ceil() as usize;

    let mut acf = vec![0.0; acmax];
    for tau in 1..=acmax {
        acf[tau - 1] = autocov_lag(&ysub, tau);
    }

    // find troughs and peaks
    let mut troughs = Vec::new();
    let mut peaks = Vec::new();

    for i in 1..acmax - 1 {
        let slope_in = acf[i] - acf[i - 1];
        let slope_out = acf[i + 1] - acf[i];

        if slope_in < 0.0 && slope_out > 0.0 {
            troughs.push(i);
        } else if slope_in > 0.0 && slope_out < 0.0 {
            peaks.push(i);
        }
    }

    // search through all peaks for one that meets the conditions
    for &i_peak in &peaks {
        let the_peak = acf[i_peak];

        // find trough before this peak
        let mut j = -1i32;
        for (idx, &trough) in troughs.iter().enumerate() {
            if trough < i_peak {
                j = idx as i32;
            } else {
                break;
            }
        }

        if j == -1 {
            continue;
        }

        let i_trough = troughs[j as usize];
        let the_trough = acf[i_trough];

        // (b) difference between peak and trough is at least 0.01
        if the_peak - the_trough < TH {
            continue;
        }

        // (c) peak corresponds to positive correlation
        if the_peak < 0.0 {
            continue;
        }

        // use this frequency that first fulfils all conditions
        return i_peak as i32;
    }

    0
}
