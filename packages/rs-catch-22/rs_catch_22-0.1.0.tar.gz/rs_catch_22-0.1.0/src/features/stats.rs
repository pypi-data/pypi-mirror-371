pub fn min_(a: &[f64]) -> f64 {
    a.iter().fold(f64::INFINITY, |acc, &x| acc.min(x))
}

pub fn max_(a: &[f64]) -> f64 {
    a.iter().fold(f64::NEG_INFINITY, |acc, &x| acc.max(x))
}

pub fn mean(a: &[f64]) -> f64 {
    let sum: f64 = a.iter().sum();
    sum / a.len() as f64
}

pub fn sum(a: &[f64]) -> f64 {
    a.iter().sum()
}

pub fn cumsum(a: &[f64]) -> Vec<f64> {
    let mut result = Vec::with_capacity(a.len());
    let mut running_sum = 0.0;
    for &val in a {
        running_sum += val;
        result.push(running_sum);
    }
    result
}

pub fn icumsum(a: &[i32]) -> Vec<i32> {
    let mut result = Vec::with_capacity(a.len());
    let mut running_sum = 0;
    for &val in a {
        running_sum += val;
        result.push(running_sum);
    }
    result
}

pub fn isum(a: &[i32]) -> f64 {
    a.iter().map(|&x| x as f64).sum()
}

pub fn median(a: &[f64]) -> f64 {
    let mut sorted = a.to_vec();
    sorted.sort_by(|a, b| a.partial_cmp(b).unwrap());

    let size = sorted.len();
    if size % 2 == 1 {
        sorted[size / 2]
    } else {
        let m1 = size / 2;
        let m2 = m1 - 1;
        (sorted[m1] + sorted[m2]) / 2.0
    }
}

pub fn stddev(a: &[f64]) -> f64 {
    let m = mean(a);
    let variance = a.iter().map(|&x| (x - m).powi(2)).sum::<f64>() / (a.len() - 1) as f64;
    variance.sqrt()
}

pub fn cov(x: &[f64], y: &[f64]) -> f64 {
    assert_eq!(x.len(), y.len());

    let mean_x = mean(x);
    let mean_y = mean(y);

    let covariance = x
        .iter()
        .zip(y.iter())
        .map(|(&xi, &yi)| (xi - mean_x) * (yi - mean_y))
        .sum::<f64>();

    covariance / (x.len() - 1) as f64
}

pub fn cov_mean(x: &[f64], y: &[f64]) -> f64 {
    assert_eq!(x.len(), y.len());

    x.iter()
        .zip(y.iter())
        .map(|(&xi, &yi)| xi * yi)
        .sum::<f64>()
        / x.len() as f64
}

pub fn corr(x: &[f64], y: &[f64]) -> f64 {
    assert_eq!(x.len(), y.len());

    let mean_x = mean(x);
    let mean_y = mean(y);

    let (nom, denom_x, denom_y) =
        x.iter()
            .zip(y.iter())
            .fold((0.0, 0.0, 0.0), |(nom, dx, dy), (&xi, &yi)| {
                let diff_x = xi - mean_x;
                let diff_y = yi - mean_y;
                (
                    nom + diff_x * diff_y,
                    dx + diff_x * diff_x,
                    dy + diff_y * diff_y,
                )
            });

    nom / (denom_x * denom_y).sqrt()
}

pub fn autocorr_lag(x: &[f64], lag: usize) -> f64 {
    corr(&x[..x.len() - lag], &x[lag..])
}

pub fn autocov_lag(x: &[f64], lag: usize) -> f64 {
    cov_mean(&x[..x.len() - lag], &x[lag..])
}

pub fn zscore_norm(a: &mut [f64]) {
    let m = mean(a);
    let sd = stddev(a);
    for val in a.iter_mut() {
        *val = (*val - m) / sd;
    }
}

pub fn zscore_norm2(a: &[f64]) -> Vec<f64> {
    let m = mean(a);
    let sd = stddev(a);
    a.iter().map(|&x| (x - m) / sd).collect()
}

pub fn moment(a: &[f64], start: usize, end: usize, r: i32) -> f64 {
    let window = &a[start..=end];
    let m = mean(window);
    let mr = window.iter().map(|&x| (x - m).powi(r)).sum::<f64>() / window.len() as f64;

    mr / stddev(window) // normalize
}

pub fn diff(a: &[f64]) -> Vec<f64> {
    a.windows(2).map(|w| w[1] - w[0]).collect()
}

pub fn linreg(x: &[f64], y: &[f64]) -> Result<(f64, f64), &'static str> {
    assert_eq!(x.len(), y.len());
    let n = x.len() as f64;

    let sumx = x.iter().sum::<f64>();
    let sumx2 = x.iter().map(|&xi| xi * xi).sum::<f64>();
    let sumxy = x
        .iter()
        .zip(y.iter())
        .map(|(&xi, &yi)| xi * yi)
        .sum::<f64>();
    let sumy = y.iter().sum::<f64>();

    let denom = n * sumx2 - sumx * sumx;
    if denom == 0.0 {
        return Err("Singular matrix. Can't solve the problem.");
    }

    let m = (n * sumxy - sumx * sumy) / denom;
    let b = (sumy * sumx2 - sumx * sumxy) / denom;

    Ok((m, b))
}

pub fn norm_(a: &[f64]) -> f64 {
    a.iter().map(|&x| x * x).sum::<f64>().sqrt()
}