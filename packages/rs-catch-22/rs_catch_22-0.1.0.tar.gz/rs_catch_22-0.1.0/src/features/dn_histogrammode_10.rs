use crate::features::histcounts::histcounts;
use crate::features::stats::zscore_norm2;

pub fn dn_histogrammode_10(y: &[f64], normalize: bool) -> f64 {
    // NaN check
    if y.iter().any(|&val| val.is_nan() || val.is_infinite()) {
        return f64::NAN;
    }

    let data = if normalize {
        zscore_norm2(y)
    } else {
        y.to_vec()
    };

    let nbins = 10;
    let (hist_counts, bin_edges) = histcounts(&data, nbins);

    let mut max_count = 0i32;
    let mut num_maxs = 1;
    let mut out = 0.0;

    for i in 0..nbins {
        if hist_counts[i] > max_count {
            max_count = hist_counts[i];
            num_maxs = 1;
            out = (bin_edges[i] + bin_edges[i + 1]) * 0.5;
        } else if hist_counts[i] == max_count {
            num_maxs += 1;
            out += (bin_edges[i] + bin_edges[i + 1]) * 0.5;
        }
    }

    out / num_maxs as f64
}

