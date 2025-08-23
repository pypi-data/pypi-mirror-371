use crate::features::fft::*;
use crate::features::histcounts::*;
use crate::features::stats::{max_, mean, min_, zscore_norm2};
use num_complex::Complex64;

type Cplx = Complex64;

pub fn nextpow2(n: i32) -> i32 {
    let mut n = n;
    n -= 1;
    n |= n >> 1;
    n |= n >> 2;
    n |= n >> 4;
    n |= n >> 8;
    n |= n >> 16;
    n += 1;
    n
}

pub fn dot_multiply(a: &mut [Cplx], b: &[Cplx]) {
    for (a_val, &b_val) in a.iter_mut().zip(b.iter()) {
        *a_val = *a_val * b_val.conj();
    }
}

// pub fn co_auto_corr(y: &[f64], tau: &[usize]) -> Vec<f64> {
//     let size = y.len();
//     let m = mean(y);
//     let n_fft = (nextpow2(size as i32) << 1) as usize;

//     // Initialize F with zero-padded, mean-centered data
//     let mut f: Vec<Cplx> = Vec::with_capacity(n_fft);

//     // Add mean-centered data
//     for &val in y.iter() {
//         f.push(Cplx::new(val - m, 0.0));
//     }

//     // Zero-pad to n_fft length
//     f.resize(n_fft, Cplx::new(0.0, 0.0));

//     let tw = twiddles(n_fft);
//     fft(&mut f, &tw);
//     let f_clone = f.clone();
//     dot_multiply(&mut f, &f_clone);
//     fft(&mut f, &tw);

//     let divisor = f[0];
//     for val in f.iter_mut() {
//         *val = *val / divisor;
//     }

//     tau.iter().map(|&i| f[i].re).collect()
// }

pub fn co_autocorrs(y: &[f64]) -> Vec<f64> {
    let size = y.len();
    let m = mean(y);
    let n_fft = (nextpow2(size as i32) << 1) as usize;

    // Match C allocation: allocate 2 * nFFT like C does
    let mut f: Vec<Cplx> = Vec::with_capacity(n_fft);

    // Add mean-centered data
    for &val in y.iter() {
        f.push(Cplx::new(val - m, 0.0));
    }

    // Zero-pad to n_fft (not n_fft * 2)
    f.resize(n_fft, Cplx::new(0.0, 0.0));

    // Make sure twiddles match the same size
    let tw = twiddles(n_fft);
    fft(&mut f, &tw);
    let f_clone = f.clone();
    dot_multiply(&mut f, &f_clone);
    fft(&mut f, &tw);

    let divisor = f[0];
    for val in f.iter_mut() {
        *val = *val / divisor;
    }

    // Return exactly n_fft values like C does
    f.iter().take(n_fft).map(|c| c.re).collect()
}

pub fn co_firstzero(y: &[f64], maxtau: usize) -> usize {
    if y.is_empty() {
        return 0;
    }

    let autocorrs = co_autocorrs(y);

    if autocorrs.is_empty() {
        return 0;
    }

    let mut zerocrossind = 0;
    while zerocrossind < maxtau && 
          zerocrossind < autocorrs.len() && 
          autocorrs[zerocrossind] > 0.0 {
        zerocrossind += 1;
    }
    
    zerocrossind
}

pub fn co_f1ecac(y: &[f64], normalize: bool) -> f64 {
    let size = y.len();

    // NaN check
    if y.iter().any(|&val| val.is_nan() || val.is_infinite()) {
        return 0.0;
    }

    if size < 2 {
        return 0.0;
    }

    let data = if normalize {
        zscore_norm2(y)
    } else {
        y.to_vec()
    };

    // compute autocorrelations
    let autocorrs = co_autocorrs(&data);

    // threshold to cross
    let thresh = 1.0 / (1.0_f64).exp();

    for i in 0..(size - 2) {
        if autocorrs[i + 1] < thresh {
            let m = autocorrs[i + 1] - autocorrs[i];
            let dy = thresh - autocorrs[i];
            let dx = dy / m;
            return i as f64 + dx;
        }
    }

    size as f64
}

// pub fn co_embed2_basic_tau_incircle(y: &[f64], radius: f64, tau: Option<usize>) -> f64 {
//     let size = y.len();

//     let tau_intern = tau.unwrap_or_else(|| co_firstzero(y, size));

//     let inside_count = (0..(size - tau_intern))
//         .filter(|&i| y[i] * y[i] + y[i + tau_intern] * y[i + tau_intern] < radius)
//         .count() as f64;

//     inside_count / (size - tau_intern) as f64
// }

pub fn co_embed2_dist_tau_d_expfit_meandiff(y: &[f64], normalize: bool) -> f64 {
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
    let mut tau = co_firstzero(&data, size);

    if tau > size / 10 {
        tau = (size / 10) as usize;
    }

    // Compute distances
    let mut d = Vec::with_capacity(size - tau - 1);
    for i in 0..size - tau - 1 {
        let dist =
            ((data[i + 1] - data[i]).powi(2) + (data[i + tau] - data[i + tau + 1]).powi(2)).sqrt();

        if dist.is_nan() {
            return f64::NAN;
        }
        d.push(dist);
    }

    // Mean for exponential fit
    let l = mean(&d);

    // Count histogram bin contents
    let n_bins = num_bins_auto(&d);
    if n_bins == 0 {
        return 0.0;
    }

    let mut hist_counts = vec![0; n_bins];
    let mut bin_edges = vec![0.0; n_bins + 1];
    histcounts_preallocated(&d, n_bins, &mut hist_counts, &mut bin_edges);

    // Normalize to probability
    let mut hist_counts_norm = vec![0.0; n_bins];
    for i in 0..n_bins {
        hist_counts_norm[i] = hist_counts[i] as f64 / (size - tau - 1) as f64;
    }

    // Compute exponential fit differences
    let mut d_expfit_diff = vec![0.0; n_bins];
    for i in 0..n_bins {
        let expf = (-(bin_edges[i] + bin_edges[i + 1]) * 0.5 / l).exp() / l;
        let expf = if expf < 0.0 { 0.0 } else { expf };
        d_expfit_diff[i] = (hist_counts_norm[i] - expf).abs();
    }

    mean(&d_expfit_diff)
}

pub fn co_first_min_ac(y: &[f64], normalize: bool) -> usize {
    // NaN check
    if y.iter().any(|&val| val.is_nan() || val.is_infinite()) || y.len() < 2 {
        return 0;
    }

    let data = if normalize {
        zscore_norm2(y)
    } else {
        y.to_vec()
    };

    let size = data.len();

    let autocorrs = co_autocorrs(&data);

    for i in 1..(size - 1) {
        if autocorrs[i] < autocorrs[i - 1] && autocorrs[i] < autocorrs[i + 1] {
            return i;
        }
    }

    size
}

pub fn co_trev_1_num(y: &[f64], normalize: bool) -> f64 {
    // NaN check
    for &value in y {
        if value.is_nan() {
            return f64::NAN;
        }
    }

    let data = if normalize {
        zscore_norm2(y)
    } else {
        y.to_vec()
    };

    let tau = 1;
    let size = data.len();

    // Create vector for differences
    let diff_temp: Vec<f64> = (0..size - tau)
        .map(|i| (data[i + 1] - data[i]).powi(3))
        .collect();

    mean(&diff_temp)
}

pub fn co_histogramami_even_2_5(y: &[f64], normalize: bool) -> f64 {
    // NaN and infinite check - return NaN for both
    if y.iter().any(|&val| val.is_nan() || val.is_infinite()) {
        return f64::NAN;
    }

    let size = y.len();

    if size <= 1 {
        return f64::NAN;
    }

    let data = if normalize {
        zscore_norm2(y)
    } else {
        y.to_vec()
    };

    let tau = 2;
    let num_bins = 5;

    let mut y1 = Vec::with_capacity(size - tau);
    let mut y2 = Vec::with_capacity(size - tau);

    for i in 0..size - tau {
        y1.push(data[i]);
        y2.push(data[i + tau]);
    }

    let max_value = max_(&data);
    let min_value = min_(&data);
    let bin_step = (max_value - min_value + 0.2) / num_bins as f64;

    let mut bin_edges = Vec::with_capacity(num_bins + 1);
    for i in 0..num_bins + 1 {
        bin_edges.push(min_value + bin_step * i as f64 - 0.1);
    }

    // Count histogram bin contents
    let bins1 = histbinassign(&y1, &bin_edges);
    let bins2 = histbinassign(&y2, &bin_edges);

    let mut bins12 = Vec::with_capacity(size - tau);
    let mut bin_edges12 = Vec::with_capacity((num_bins + 1) * (num_bins + 1));

    for i in 0..size - tau {
        bins12.push((bins1[i] - 1) * (num_bins + 1) as i32 + bins2[i]);
    }

    for i in 0..(num_bins + 1) * (num_bins + 1) {
        bin_edges12.push(i as f64 + 1.0);
    }

    // Joint histogram
    let joint_hist_linear = histcount_edges(
        &bins12.iter().map(|&x| x as f64).collect::<Vec<f64>>(),
        &bin_edges12,
    );

    // Transfer to 2D histogram (no last bin, as in original implementation)
    let mut pij = vec![vec![0.0; num_bins]; num_bins];
    let mut sum_bins = 0;

    for i in 0..num_bins {
        for j in 0..num_bins {
            pij[j][i] = joint_hist_linear[i * (num_bins + 1) + j] as f64;
            sum_bins += joint_hist_linear[i * (num_bins + 1) + j];
        }
    }

    // Normalize
    for i in 0..num_bins {
        for j in 0..num_bins {
            pij[j][i] /= sum_bins as f64;
        }
    }

    // Marginals
    let mut pi = vec![0.0; num_bins];
    let mut pj = vec![0.0; num_bins];

    for i in 0..num_bins {
        for j in 0..num_bins {
            pi[i] += pij[i][j];
            pj[j] += pij[i][j];
        }
    }

    // Mutual information
    let mut ami = 0.0;
    for i in 0..num_bins {
        for j in 0..num_bins {
            if pij[i][j] > 0.0 {
                ami += pij[i][j] * (pij[i][j] / (pj[j] * pi[i])).ln();
            }
        }
    }

    ami
}
