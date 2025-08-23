use crate::features::stats::{max_, min_, stddev};

pub fn num_bins_auto(y: &[f64]) -> usize {
    let max_val = max_(y);
    let min_val = min_(y);

    if stddev(y) < 0.001 {
        return 0;
    }

    ((max_val - min_val) / (3.5 * stddev(y) / (y.len() as f64).powf(1.0 / 3.0))).ceil() as usize
}

pub fn histcounts_preallocated(
    y: &[f64],
    n_bins: usize,
    bin_counts: &mut [i32],
    bin_edges: &mut [f64],
) {
    // Find min and max
    let min_val = y.iter().fold(f64::MAX, |a, &b| a.min(b));
    let max_val = y.iter().fold(f64::MIN, |a, &b| a.max(b));

    // Derive bin width
    let bin_step = (max_val - min_val) / n_bins as f64;

    // Initialize bin counts to zero
    bin_counts.fill(0);

    // Count occurrences
    for &val in y {
        let mut bin_ind = ((val - min_val) / bin_step) as usize;
        if bin_ind >= n_bins {
            bin_ind = n_bins - 1;
        }
        bin_counts[bin_ind] += 1;
    }

    // Set bin edges
    for i in 0..=n_bins {
        bin_edges[i] = i as f64 * bin_step + min_val;
    }
}

pub fn histcounts(y: &[f64], n_bins: usize) -> (Vec<i32>, Vec<f64>) {
    // Find min and max
    let min_val = y.iter().fold(f64::MAX, |a, &b| a.min(b));
    let max_val = y.iter().fold(f64::MIN, |a, &b| a.max(b));

    // Auto-determine bins if needed (though we pass n_bins explicitly in this version)
    let actual_n_bins = if n_bins == 0 {
        num_bins_auto(y)
    } else {
        n_bins
    };

    // Derive bin width
    let bin_step = (max_val - min_val) / actual_n_bins as f64;

    // Initialize bin counts
    let mut bin_counts = vec![0i32; actual_n_bins];

    // Count occurrences
    for &val in y {
        let mut bin_ind = ((val - min_val) / bin_step) as usize;
        if bin_ind >= actual_n_bins {
            bin_ind = actual_n_bins - 1;
        }
        bin_counts[bin_ind] += 1;
    }

    // Create bin edges
    let bin_edges: Vec<f64> = (0..=actual_n_bins)
        .map(|i| i as f64 * bin_step + min_val)
        .collect();

    (bin_counts, bin_edges)
}

pub fn histbinassign(y: &[f64], bin_edges: &[f64]) -> Vec<i32> {
    let mut bin_identity = vec![0; y.len()];

    for (i, &val) in y.iter().enumerate() {
        // if not in any bin -> 0
        bin_identity[i] = 0;

        // go through bin edges
        for (j, &edge) in bin_edges.iter().enumerate() {
            if val < edge {
                bin_identity[i] = j as i32;
                break;
            }
        }
    }

    bin_identity
}

pub fn histcount_edges(y: &[f64], bin_edges: &[f64]) -> Vec<i32> {
    let mut histcounts = vec![0; bin_edges.len()];

    for &val in y {
        // go through bin edges
        for (j, &edge) in bin_edges.iter().enumerate() {
            if val <= edge {
                histcounts[j] += 1;
                break;
            }
        }
    }

    histcounts
}
