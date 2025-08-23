use crate::features::co_auto_corr::*;
use crate::features::fft::*;
use crate::features::stats::{cumsum, mean, norm_, zscore_norm2};
use num_complex::Complex64;

pub fn welch(y: &[f64], nfft: usize, fs: f64, window: &[f64]) -> (Vec<f64>, Vec<f64>) {
    let size = y.len();
    let window_width = window.len();

    let dt = 1.0 / fs;
    let df = 1.0 / (nextpow2(window_width as i32) as f64) / dt;
    let m = mean(y);

    // number of windows, should be 1
    let k = ((size as f64) / (window_width as f64 / 2.0)).floor() as usize - 1;

    // normalising scale factor
    let kmu = k as f64 * norm_(window).powi(2);

    let mut p = vec![0.0; nfft];

    // fft variables
    let mut f = vec![Complex64::new(0.0, 0.0); nfft];
    let tw = twiddles(nfft);

    let mut xw = vec![0.0; window_width];

    for i in 0..k {
        // apply window
        for j in 0..window_width {
            let idx = j + (i as f64 * window_width as f64 / 2.0) as usize;
            xw[j] = window[j] * y[idx];
        }

        // initialise F
        for j in 0..window_width {
            f[j] = Complex64::new(xw[j] - m, 0.0);
        }
        for j in window_width..nfft {
            f[j] = Complex64::new(0.0, 0.0);
        }

        fft(&mut f, &tw);

        for l in 0..nfft {
            p[l] += f[l].norm().powi(2);
        }
    }

    let nout = nfft / 2 + 1;
    let mut pxx = vec![0.0; nout];

    for i in 0..nout {
        pxx[i] = p[i] / kmu * dt;
        if i > 0 && i < nout - 1 {
            pxx[i] *= 2.0;
        }
    }

    let mut freq = vec![0.0; nout];
    for i in 0..nout {
        freq[i] = i as f64 * df;
    }

    (pxx, freq)
}

pub fn sp_summaries_welch_rect(y: &[f64], what: &str, normalize: bool) -> f64 {
    // NaN check
    if y.iter().any(|&val| val.is_nan() || val.is_infinite()) {
        return f64::NAN;
    }

    let data = if normalize {
        zscore_norm2(y)
    } else {
        y.to_vec()
    };

    // rectangular window for Welch-spectrum
    let window = vec![1.0; data.len()];

    let fs = 1.0; // sampling frequency
    let n = nextpow2(y.len() as i32) as usize;

    // compute Welch-power
    let (s, f) = welch(&data, n, fs, &window);
    let n_welch = s.len();

    // angular frequency and spectrum on that
    let mut w = vec![0.0; n_welch];
    let mut sw = vec![0.0; n_welch];

    let pi = std::f64::consts::PI;
    for i in 0..n_welch {
        w[i] = 2.0 * pi * f[i];
        sw[i] = s[i] / (2.0 * pi);

        if sw[i].is_infinite() {
            return 0.0;
        }
    }

    // Check array length before accessing indices
    if w.len() < 2 {
        return f64::NAN;
    }

    let dw = w[1] - w[0];

    let cs_s = cumsum(&sw);

    let output = match what {
        "centroid" => {
            let cs_s_thres = cs_s[n_welch - 1] * 0.5;
            let mut centroid = 0.0;
            for i in 0..n_welch {
                if cs_s[i] > cs_s_thres {
                    centroid = w[i];
                    break;
                }
            }
            centroid
        }
        "area_5_1" => {
            let mut area_5_1 = 0.0;
            for i in 0..n_welch / 5 {
                area_5_1 += sw[i];
            }
            area_5_1 * dw
        }
        _ => 0.0,
    };

    output
}

pub fn sp_summaries_welch_rect_area_5_1(y: &[f64], normalize: bool) -> f64 {
    sp_summaries_welch_rect(y, "area_5_1", normalize)
}

pub fn sp_summaries_welch_rect_centroid(y: &[f64], normalize: bool) -> f64 {
    sp_summaries_welch_rect(y, "centroid", normalize)
}
