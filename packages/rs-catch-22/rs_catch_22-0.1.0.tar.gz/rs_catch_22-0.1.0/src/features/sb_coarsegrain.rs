use crate::features::helpers::quantile;

pub fn sb_coarse_grain(y: &[f64], how: &str, num_groups: usize, labels: &mut [usize]) {
    if how != "quantile" {
        panic!("ERROR in sb_coarse_grain: unknown coarse-graining method");
    }

    // Create thresholds using quantiles
    let mut thresholds = Vec::with_capacity(num_groups + 1);
    for i in 0..=num_groups {
        let quantile_value = i as f64 / num_groups as f64;
        thresholds.push(quantile(y, quantile_value));
    }

    // Adjust first threshold
    thresholds[0] -= 1.0;

    // Assign labels based on thresholds
    for j in 0..y.len() {
        for i in 0..num_groups {
            if y[j] > thresholds[i] && y[j] <= thresholds[i + 1] {
                labels[j] = i + 1;
                break;
            }
        }
    }
}
