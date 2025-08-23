use crate::features::co_auto_corr::*;
use crate::features::stats::*;

pub fn abs_diff(a: &[f64], b: &mut [f64]) {
    for i in 1..a.len() {
        b[i - 1] = (a[i] - a[i - 1]).abs();
    }
}

pub fn fc_localsimple(y: &[f64]) -> f64 {
    let mut y1 = vec![0.0; y.len() - 1];
    abs_diff(y, &mut y1);

    mean(&y1)
}

pub fn fc_localsimple_mean_tauresrat(y: &[f64], normalize: bool, train_length: usize) -> f64 {
    if y.iter().any(|&val| val.is_nan() || val.is_infinite()) || y.len() < 2 {
        return f64::NAN;
    }
    
    let data = if normalize {
        zscore_norm2(y)
    } else {
        y.to_vec()
    };

    if data.len() <= train_length {
        return 0.0;
    }

    let mut res = vec![0.0; data.len() - train_length];

    for i in 0..data.len() - train_length {
        let mut yest = 0.0;
        for j in 0..train_length {
            yest += data[i + j];
        }
        yest /= train_length as f64;

        res[i] = data[i + train_length] - yest;
    }

    let res_ac1st_z = co_firstzero(&res, res.len()) as f64;
    let y_ac1st_z = co_firstzero(&data, data.len()) as f64;

    res_ac1st_z / y_ac1st_z
}

pub fn fc_localsimple_mean_stderr(y: &[f64], normalize: bool, train_length: usize) -> f64 {
    if y.iter().any(|&val| val.is_nan() || val.is_infinite()) || y.len() < 2 {
        return f64::NAN;
    }

    let data = if normalize {
        zscore_norm2(y)
    } else {
        y.to_vec()
    };

    if data.len() <= train_length {
        return 0.0;
    }

    let mut res = vec![0.0; data.len() - train_length];

    for i in 0..data.len() - train_length {
        let mut yest = 0.0;
        for j in 0..train_length {
            yest += data[i + j];
        }
        yest /= train_length as f64;

        res[i] = data[i + train_length] - yest;
    }

    stddev(&res)
}

pub fn fc_localsimple_mean3_stderr(y: &[f64], normalize: bool) -> f64 {
    fc_localsimple_mean_stderr(y, normalize, 3)
}

pub fn fc_localsimple_mean1_tauresrat(y: &[f64], normalize: bool) -> f64 {
    fc_localsimple_mean_tauresrat(y, normalize, 1)
}

pub fn fc_localsimple_mean_taures(y: &[f64], train_length: usize) -> usize {
    if y.len() <= train_length {
        return 0;
    }

    let mut res = vec![0.0; y.len() - train_length];

    for i in 0..y.len() - train_length {
        let mut yest = 0.0;
        for j in 0..train_length {
            yest += y[i + j];
        }
        yest /= train_length as f64;

        res[i] = y[i + train_length] - yest;
    }

    co_firstzero(&res, res.len())
}

pub fn fc_localsimple_lfit_taures(y: &[f64]) -> usize {
    let train_length = co_firstzero(y, y.len());

    let mut x_reg = vec![0.0; train_length];
    for i in 1..train_length + 1 {
        x_reg[i - 1] = i as f64;
    }

    let mut res = vec![0.0; y.len() - train_length];

    for i in 0..y.len() - train_length {
        let y_window = &y[i..i + train_length];
        let (m, b) = linreg(&x_reg, y_window).unwrap_or((0.0, 0.0));

        res[i] = y[i + train_length] - (m * (train_length + 1) as f64 + b);
    }

    co_firstzero(&res, res.len())
}
