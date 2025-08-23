use crate::features::helpers::*;
use crate::features::sb_coarsegrain::*;
use crate::features::stats::*;

pub fn sb_motifthree_quantile_hh(y: &[f64], normalize: bool) -> f64 {
    if y.iter().any(|&val| val.is_nan() || val.is_infinite()) || y.len() < 2 {
        return f64::NAN;
    }

    let data = if normalize {
        zscore_norm2(y)
    } else {
        y.to_vec()
    };

    let size = data.len();
    let alphabet_size = 3;

    // transfer to alphabet
    let mut yt = vec![0; size];
    sb_coarse_grain(&data, "quantile", alphabet_size, &mut yt);

    // words of length 1
    let mut r1 = vec![Vec::new(); alphabet_size];
    let mut sizes_r1 = vec![0; alphabet_size];

    for i in 0..alphabet_size {
        for j in 0..size {
            if yt[j] == i + 1 {
                r1[i].push(j);
                sizes_r1[i] += 1;
            }
        }
    }

    // words of length 2 - remove last item if it's at the end
    for i in 0..alphabet_size {
        if sizes_r1[i] != 0 && r1[i][sizes_r1[i] - 1] == size - 1 {
            r1[i].pop();
            sizes_r1[i] -= 1;
        }
    }

    // 2D arrays for length 2 words
    let mut r2 = vec![vec![Vec::new(); alphabet_size]; alphabet_size];
    let mut sizes_r2 = vec![vec![0; alphabet_size]; alphabet_size];
    let mut out2 = vec![vec![0.0; alphabet_size]; alphabet_size];

    // fill r2 arrays
    for i in 0..alphabet_size {
        for j in 0..alphabet_size {
            for k in 0..sizes_r1[i] {
                let tmp_idx = yt[r1[i][k] + 1];
                if tmp_idx == j + 1 {
                    r2[i][j].push(r1[i][k]);
                    sizes_r2[i][j] += 1;
                }
            }
            out2[i][j] = sizes_r2[i][j] as f64 / (size as f64 - 1.0);
        }
    }

    // calculate entropy
    let mut hh = 0.0;
    for i in 0..alphabet_size {
        hh += f_entropy(&out2[i]);
    }

    hh
}

pub fn sb_motifthree(y: &[f64], how: &str) -> Vec<f64> {
    let mut size = y.len();
    let alphabet_size = 3;
    let mut out = Vec::new();

    let mut yt = vec![0; size];

    match how {
        "quantile" => {
            sb_coarse_grain(y, "quantile", alphabet_size, &mut yt);
        }
        "diffquant" => {
            let diff_y = diff(y);
            sb_coarse_grain(&diff_y, "quantile", alphabet_size, &mut yt);
            size -= 1;
        }
        _ => {
            panic!("ERROR in sb_motifthree: Unknown how method");
        }
    }

    // words of length 1
    let mut r1 = vec![Vec::new(); alphabet_size];
    let mut sizes_r1 = vec![0; alphabet_size];
    let mut out1 = vec![0.0; alphabet_size];

    for i in 0..alphabet_size {
        for j in 0..size {
            if yt[j] == i + 1 {
                r1[i].push(j);
                sizes_r1[i] += 1;
            }
        }
        let tmp = sizes_r1[i] as f64 / size as f64;
        out1[i] = tmp;
        out.push(tmp);
    }
    out.push(f_entropy(&out1));

    // words of length 2
    // remove last item if it's at the end
    for i in 0..alphabet_size {
        if sizes_r1[i] != 0 && r1[i][sizes_r1[i] - 1] == size - 1 {
            r1[i].pop();
            sizes_r1[i] -= 1;
        }
    }

    let mut r2 = vec![vec![Vec::new(); alphabet_size]; alphabet_size];
    let mut sizes_r2 = vec![vec![0; alphabet_size]; alphabet_size];
    let mut out2 = vec![vec![0.0; alphabet_size]; alphabet_size];

    for i in 0..alphabet_size {
        for j in 0..alphabet_size {
            for k in 0..sizes_r1[i] {
                let tmp_idx = yt[r1[i][k] + 1];
                if tmp_idx == j + 1 {
                    r2[i][j].push(r1[i][k]);
                    sizes_r2[i][j] += 1;
                }
            }
            let tmp = sizes_r2[i][j] as f64 / (size - 1) as f64;
            out2[i][j] = tmp;
            out.push(tmp);
        }
    }

    let mut tmp = 0.0;
    for i in 0..alphabet_size {
        tmp += f_entropy(&out2[i]);
    }
    out.push(tmp);

    // words of length 3
    for i in 0..alphabet_size {
        for j in 0..alphabet_size {
            if sizes_r2[i][j] != 0 && r2[i][j][sizes_r2[i][j] - 1] == size - 2 {
                r2[i][j].pop();
                sizes_r2[i][j] -= 1;
            }
        }
    }

    let mut r3 = vec![vec![vec![Vec::new(); alphabet_size]; alphabet_size]; alphabet_size];
    let mut sizes_r3 = vec![vec![vec![0; alphabet_size]; alphabet_size]; alphabet_size];
    let mut out3 = vec![vec![vec![0.0; alphabet_size]; alphabet_size]; alphabet_size];

    for i in 0..alphabet_size {
        for j in 0..alphabet_size {
            for k in 0..alphabet_size {
                for l in 0..sizes_r2[i][j] {
                    let tmp_idx = yt[r2[i][j][l] + 2];
                    if tmp_idx == k + 1 {
                        r3[i][j][k].push(r2[i][j][l]);
                        sizes_r3[i][j][k] += 1;
                    }
                }
                let tmp = sizes_r3[i][j][k] as f64 / (size - 2) as f64;
                out3[i][j][k] = tmp;
                out.push(tmp);
            }
        }
    }

    tmp = 0.0;
    for i in 0..alphabet_size {
        for j in 0..alphabet_size {
            tmp += f_entropy(&out3[i][j]);
        }
    }
    out.push(tmp);

    // words of length 4
    for i in 0..alphabet_size {
        for j in 0..alphabet_size {
            for k in 0..alphabet_size {
                if sizes_r3[i][j][k] != 0 && r3[i][j][k][sizes_r3[i][j][k] - 1] == size - 3 {
                    r3[i][j][k].pop();
                    sizes_r3[i][j][k] -= 1;
                }
            }
        }
    }

    let mut r4 = vec![
        vec![vec![vec![Vec::new(); alphabet_size]; alphabet_size]; alphabet_size];
        alphabet_size
    ];
    let mut sizes_r4 =
        vec![vec![vec![vec![0; alphabet_size]; alphabet_size]; alphabet_size]; alphabet_size];
    let mut out4 =
        vec![vec![vec![vec![0.0; alphabet_size]; alphabet_size]; alphabet_size]; alphabet_size];

    for i in 0..alphabet_size {
        for j in 0..alphabet_size {
            for k in 0..alphabet_size {
                for l in 0..alphabet_size {
                    for m in 0..sizes_r3[i][j][k] {
                        let tmp_idx = yt[r3[i][j][k][m] + 3];
                        if tmp_idx == l + 1 {
                            r4[i][j][k][l].push(r3[i][j][k][m]);
                            sizes_r4[i][j][k][l] += 1;
                        }
                    }
                    let tmp = sizes_r4[i][j][k][l] as f64 / (size - 3) as f64;
                    out4[i][j][k][l] = tmp;
                    out.push(tmp);
                }
            }
        }
    }

    tmp = 0.0;
    for i in 0..alphabet_size {
        for j in 0..alphabet_size {
            for k in 0..alphabet_size {
                tmp += f_entropy(&out4[i][j][k]);
            }
        }
    }
    out.push(tmp);

    out
}
