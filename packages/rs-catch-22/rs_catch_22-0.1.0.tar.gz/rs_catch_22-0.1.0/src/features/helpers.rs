use std::cmp::Ordering;

use num_complex::Complex64;

pub type Cplx = Complex64;

pub fn mean(y: &[f64]) -> f64 {
    y.iter().sum::<f64>() / y.len() as f64
}

pub fn median(y: &[f64]) -> f64 {
    let mut sorted = y.to_vec();
    sorted.sort_by(|a, b| a.partial_cmp(b).unwrap_or(Ordering::Equal));
    let mid = sorted.len() / 2;
    sorted[mid]
}

fn compare(a: &f64, b: &f64) -> Ordering {
    a.partial_cmp(b).unwrap_or(Ordering::Equal)
}

// Sort function - takes a mutable slice
pub fn sort(y: &mut [f64]) {
    y.sort_by(|a, b| a.partial_cmp(b).unwrap_or(Ordering::Equal));
}

// Linearly spaced vector - returns Vec instead of modifying array
pub fn linspace(start: f64, end: f64, num_groups: usize) -> Vec<f64> {
    let step_size = (end - start) / (num_groups - 1) as f64;
    (0..num_groups)
        .map(|i| start + i as f64 * step_size)
        .collect()
}

pub fn quantile(y: &[f64], quant: f64) -> f64 {
    let size = y.len();
    let mut tmp: Vec<f64> = y.to_vec();
    tmp.sort_by(|a, b| a.partial_cmp(b).unwrap_or(Ordering::Equal));

    // out of range limit?
    let q = 0.5 / size as f64;
    if quant < q {
        return tmp[0]; // min value
    } else if quant > (1.0 - q) {
        return tmp[size - 1]; // max value
    }

    let quant_idx = size as f64 * quant - 0.5;
    let idx_left = quant_idx.floor() as usize;
    let idx_right = quant_idx.ceil() as usize;

    tmp[idx_left]
        + (quant_idx - idx_left as f64) * (tmp[idx_right] - tmp[idx_left])
            / (idx_right - idx_left) as f64
}

pub fn binarize(a: &[f64], how: &str) -> Vec<i32> {
    let m = match how {
        "mean" => mean(a),
        "median" => median(a),
        _ => 0.0,
    };

    a.iter().map(|&x| if x > m { 1 } else { 0 }).collect()
}

pub fn f_entropy(a: &[f64]) -> f64 {
    -a.iter()
        .filter(|&&x| x > 0.0)
        .map(|&x| x * x.ln())
        .sum::<f64>()
}

pub fn subset(a: &[i32], start: usize, end: usize) -> Vec<i32> {
    a[start..end].to_vec()
}

pub fn cmul(x: Cplx, y: Cplx) -> Cplx {
    x * y
}

pub fn cminus(x: Cplx, y: Cplx) -> Cplx {
    x - y
}

pub fn cadd(x: Cplx, y: Cplx) -> Cplx {
    x + y
}

pub fn cdiv(x: Cplx, y: Cplx) -> Cplx {
    x / y
}
