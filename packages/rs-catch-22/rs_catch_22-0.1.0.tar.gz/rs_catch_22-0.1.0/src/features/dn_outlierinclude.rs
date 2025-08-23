use crate::features::stats::*;

pub fn dn_outlierinclude_np_001_mdrmd(y: &[f64], normalize: bool, sign: i32) -> f64 {
    if y.iter().any(|&val| val.is_nan() || val.is_infinite()) || y.len() < 2 {
        return f64::NAN;
    }

    let data = if normalize {
        zscore_norm2(y)
    } else {
        y.to_vec()
    };

    let size = data.len();
    let inc = 0.01;
    let mut tot = 0;
    let mut ywork = vec![0.0; size];

    // apply sign and check constant time series
    let mut constant_flag = true;
    for i in 0..size {
        if data[i] != data[0] {
            constant_flag = false;
        }

        // apply sign, save in new variable
        ywork[i] = sign as f64 * data[i];

        // count pos/ negs
        if ywork[i] >= 0.0 {
            tot += 1;
        }
    }

    if constant_flag {
        return 0.0; // if constant, return 0
    }

    // find maximum (or minimum, depending on sign)
    let maxval = max_(&ywork);

    // maximum value too small? return 0
    if maxval < inc {
        return 0.0;
    }

    let nthresh = (maxval / inc + 1.0) as usize;

    // save the indices where y > threshold
    let mut r = vec![0.0; size];

    // save the median over indices with absolute value > threshold
    let mut ms_dti1 = vec![0.0; nthresh];
    let mut ms_dti3 = vec![0.0; nthresh];
    let mut ms_dti4 = vec![0.0; nthresh];

    for j in 0..nthresh {
        let mut high_size = 0;

        for i in 0..size {
            if ywork[i] >= j as f64 * inc {
                r[high_size] = (i + 1) as f64;
                high_size += 1;
            }
        }

        // intervals between high-values
        let mut dt_exc = vec![0.0; high_size];

        for i in 0..high_size - 1 {
            dt_exc[i] = r[i + 1] - r[i];
        }

        ms_dti1[j] = mean(&dt_exc[..high_size - 1]);
        ms_dti3[j] = (high_size - 1) as f64 * 100.0 / tot as f64;
        ms_dti4[j] = median(&r[..high_size]) / (size as f64 / 2.0) - 1.0;
    }

    let trimthr = 2;
    let mut mj = 0;
    let mut fbi = nthresh - 1;

    for i in 0..nthresh {
        if ms_dti3[i] > trimthr as f64 {
            mj = i;
        }
        if ms_dti1[nthresh - 1 - i].is_nan() {
            fbi = nthresh - 1 - i;
        }
    }

    let trim_limit = if mj < fbi { mj } else { fbi };
    median(&ms_dti4[..trim_limit + 1])
}

pub fn dn_outlierinclude_p_001_mdrmd(y: &[f64], normalize: bool) -> f64 {
    dn_outlierinclude_np_001_mdrmd(y, normalize, 1)
}

pub fn dn_outlierinclude_n_001_mdrmd(y: &[f64], normalize: bool) -> f64 {
    dn_outlierinclude_np_001_mdrmd(y, normalize, -1)
}

// pub fn dn_outlierinclude_abs_001(y: &[f64], normalize: bool) -> f64 {
//     let data = if normalize {
//         zscore_norm2(y)
//     } else {
//         y.to_vec()
//     };

//     let size = data.len();
//     let inc = 0.01;
//     let mut max_abs = 0.0;
//     let mut y_abs = vec![0.0; size];

//     for i in 0..size {
//         y_abs[i] = if data[i] > 0.0 { data[i] } else { -data[i] };

//         if y_abs[i] > max_abs {
//             max_abs = y_abs[i];
//         }
//     }

//     let nthresh = (max_abs / inc + 1.0) as usize;

//     // save the indices where y > threshold
//     let mut high_inds = vec![0.0; size];

//     // save the median over indices with absolute value > threshold
//     let mut ms_dti3 = vec![0.0; nthresh];
//     let mut ms_dti4 = vec![0.0; nthresh];

//     for j in 0..nthresh {
//         let mut high_size = 0;

//         for i in 0..size {
//             if y_abs[i] >= j as f64 * inc {
//                 high_inds[high_size] = i as f64;
//                 high_size += 1;
//             }
//         }

//         // median
//         let median_out = median(&high_inds[..high_size]);

//         ms_dti3[j] = (high_size - 1) as f64 * 100.0 / size as f64;
//         ms_dti4[j] = median_out / (size as f64 / 2.0) - 1.0;
//     }

//     let trimthr = 2;
//     let mut mj = 0;
//     for i in 0..nthresh {
//         if ms_dti3[i] > trimthr as f64 {
//             mj = i;
//         }
//     }

//     median(&ms_dti4[..mj])
// }
