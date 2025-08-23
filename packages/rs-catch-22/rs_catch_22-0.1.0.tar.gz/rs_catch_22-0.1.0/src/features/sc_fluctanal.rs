use crate::features::stats::*;

pub fn sc_fluctanal_2_50_1_logi_prop_r1(y: &[f64], lag: usize, how: &str, normalize: bool) -> f64 {
    // NaN check
    if y.iter().any(|&val| val.is_nan() || val.is_infinite()) || y.len() < 2 {
        return f64::NAN;
    }

    let data = if normalize {
        zscore_norm2(y)
    } else {
        y.to_vec()
    };

    let size = data.len();

    // generate log spaced tau vector
    let lin_low = (5.0_f64).ln();
    let lin_high = ((size / 2) as f64).ln();

    let n_tau_steps = 50;
    let tau_step = (lin_high - lin_low) / (n_tau_steps - 1) as f64;

    let mut tau = vec![0; n_tau_steps];
    for i in 0..n_tau_steps {
        tau[i] = (lin_low + i as f64 * tau_step).exp().round() as usize;
    }

    // check for uniqueness, use ascending order
    let mut n_tau = n_tau_steps;
    for i in 0..n_tau_steps - 1 {
        while tau[i] == tau[i + 1] && i < n_tau - 1 {
            for j in i + 1..n_tau_steps - 1 {
                tau[j] = tau[j + 1];
            }
            n_tau -= 1;
        }
    }

    // fewer than 12 points -> leave
    if n_tau < 12 {
        return 0.0;
    }

    let size_cs = size / lag;
    let mut y_cs = vec![0.0; size_cs];

    // transform input vector to cumsum
    y_cs[0] = data[0];
    for i in 0..size_cs - 1 {
        y_cs[i + 1] = y_cs[i] + data[(i + 1) * lag];
    }

    // first generate a support for regression (detrending)
    let mut x_reg = vec![0.0; tau[n_tau - 1]];
    for i in 0..tau[n_tau - 1] {
        x_reg[i] = (i + 1) as f64;
    }

    // iterate over taus, cut signal, detrend and save amplitude of remaining signal
    let mut f = vec![0.0; n_tau];
    for i in 0..n_tau {
        let n_buffer = size_cs / tau[i];
        let mut buffer = vec![0.0; tau[i]];

        f[i] = 0.0;
        for j in 0..n_buffer {
            let y_window = &y_cs[j * tau[i]..(j + 1) * tau[i]];
            let (m, b) = linreg(&x_reg[..tau[i]], y_window).unwrap_or((0.0, 0.0));

            for k in 0..tau[i] {
                buffer[k] = y_cs[j * tau[i] + k] - (m * (k + 1) as f64 + b);
            }

            match how {
                "rsrangefit" => {
                    f[i] += (max_(&buffer) - min_(&buffer)).powi(2);
                }
                "dfa" => {
                    for k in 0..tau[i] {
                        f[i] += buffer[k] * buffer[k];
                    }
                }
                _ => return 0.0,
            }
        }

        match how {
            "rsrangefit" => {
                f[i] = (f[i] / n_buffer as f64).sqrt();
            }
            "dfa" => {
                f[i] = (f[i] / (n_buffer * tau[i]) as f64).sqrt();
            }
            _ => {}
        }
    }

    let mut log_tt = vec![0.0; n_tau];
    let mut log_ff = vec![0.0; n_tau];

    for i in 0..n_tau {
        log_tt[i] = (tau[i] as f64).ln();
        log_ff[i] = f[i].ln();
    }

    let min_points = 6;
    let n_sserr = n_tau - 2 * min_points + 1;
    let mut sserr = vec![0.0; n_sserr];
    let mut buffer = vec![0.0; n_tau - min_points + 1];

    for i in min_points..n_tau - min_points + 1 {
        let (m1, b1) = linreg(&log_tt[..i], &log_ff[..i]).unwrap_or((0.0, 0.0));
        let (m2, b2) = linreg(&log_tt[i - 1..], &log_ff[i - 1..]).unwrap_or((0.0, 0.0));

        sserr[i - min_points] = 0.0;

        for j in 0..i {
            buffer[j] = log_tt[j] * m1 + b1 - log_ff[j];
        }
        sserr[i - min_points] += norm_(&buffer[..i]);

        for j in 0..n_tau - i + 1 {
            buffer[j] = log_tt[j + i - 1] * m2 + b2 - log_ff[j + i - 1];
        }
        sserr[i - min_points] += norm_(&buffer[..n_tau - i + 1]);
    }

    let minimum = min_(&sserr);
    let mut first_min_ind = 0.0;
    for i in 0..n_sserr {
        if sserr[i] == minimum {
            first_min_ind = (i + min_points - 1) as f64;
            break;
        }
    }

    (first_min_ind + 1.0) / n_tau as f64
}

pub fn sc_fluctanal_2_dfa_50_1_2_logi_prop_r1(
    y: &[f64],
    lag: usize,
    how: &str,
    normalize: bool,
) -> f64 {
    sc_fluctanal_2_50_1_logi_prop_r1(y, lag, how, normalize)
}

pub fn sc_fluctanal_2_rsrangefit_50_1_2_logi_prop_r1(
    y: &[f64],
    lag: usize,
    how: &str,
    normalize: bool,
) -> f64 {
    sc_fluctanal_2_50_1_logi_prop_r1(y, lag, how, normalize)
}
