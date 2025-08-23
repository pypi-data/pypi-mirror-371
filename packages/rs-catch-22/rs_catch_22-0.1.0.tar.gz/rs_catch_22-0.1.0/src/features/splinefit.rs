const PIECES: usize = 2;
const N_BREAKS: usize = 3;
const DEG: usize = 3;
const N_SPLINE: usize = 4;
const PIECES_EXT: usize = 8;

pub fn matrix_multiply(
    a: &[f64],
    size_a1: usize,
    size_a2: usize,
    b: &[f64],
    size_b1: usize,
    size_b2: usize,
    c: &mut [f64],
) {
    if size_a2 != size_b1 {
        return;
    }

    for i in 0..size_a1 {
        for j in 0..size_b2 {
            c[i * size_b2 + j] = 0.0;
            for k in 0..size_b1 {
                c[i * size_b2 + j] += a[i * size_a2 + k] * b[k * size_b2 + j];
            }
        }
    }
}

pub fn matrix_times_vector(a: &[f64], size_a1: usize, size_a2: usize, b: &[f64], c: &mut [f64]) {
    if size_a2 != b.len() {
        return;
    }

    for i in 0..size_a1 {
        c[i] = 0.0;
        for k in 0..b.len() {
            c[i] += a[i * size_a2 + k] * b[k];
        }
    }
}

pub fn gauss_elimination(a: &[f64], b: &[f64], x: &mut [f64]) {
    let size = b.len();

    // Create temp matrix and vector
    let mut a_elim = vec![vec![0.0; size]; size];
    let mut b_elim = vec![0.0; size];

    // Initialize to A and b
    for i in 0..size {
        for j in 0..size {
            a_elim[i][j] = a[i * size + j];
        }
        b_elim[i] = b[i];
    }

    // Create triangular matrix
    for i in 0..size {
        for j in (i + 1)..size {
            let factor = a_elim[j][i] / a_elim[i][i];

            // Subtract in vector
            b_elim[j] = b_elim[j] - factor * b_elim[i];

            // Go through entries of this row
            for k in i..size {
                a_elim[j][k] = a_elim[j][k] - factor * a_elim[i][k];
            }
        }
    }

    // Go backwards through triangular matrix and solve for x
    for i in (0..size).rev() {
        let mut b_minus_a_temp = b_elim[i];
        for j in (i + 1)..size {
            b_minus_a_temp -= x[j] * a_elim[i][j];
        }
        x[i] = b_minus_a_temp / a_elim[i][i];
    }
}

pub fn lsqsolve_sub(a: &[f64], size_a1: usize, size_a2: usize, b: &[f64], x: &mut [f64]) {
    // Create temp matrices and vector
    let mut at = vec![0.0; size_a2 * size_a1];
    let mut ata = vec![0.0; size_a2 * size_a2];
    let mut atb = vec![0.0; size_a2];

    // Transpose A
    for i in 0..size_a1 {
        for j in 0..size_a2 {
            at[j * size_a1 + i] = a[i * size_a2 + j];
        }
    }

    // Compute A^T * A
    matrix_multiply(&at, size_a2, size_a1, a, size_a1, size_a2, &mut ata);

    // Compute A^T * b
    matrix_times_vector(&at, size_a2, size_a1, b, &mut atb);

    // Solve (A^T * A) * x = A^T * b
    gauss_elimination(&ata, &atb, x);
}

fn i_limit(x: i32, lim: i32) -> i32 {
    if x < lim {
        x
    } else {
        lim
    }
}

fn icumsum(input: &[i32], size: usize, output: &mut [i32]) {
    output[0] = input[0];
    for i in 1..size {
        output[i] = output[i - 1] + input[i];
    }
}

pub fn splinefit(y: &[f64], y_out: &mut [f64]) -> i32 {
    let size = y.len();

    // x-positions of spline-nodes
    let mut breaks = [0; N_BREAKS];
    breaks[0] = 0;
    breaks[1] = (size as f64 / 2.0).floor() as i32 - 1;
    breaks[2] = size as i32 - 1;

    // spacing
    let mut h0 = [0; 2];
    h0[0] = breaks[1] - breaks[0];
    h0[1] = breaks[2] - breaks[1];

    // repeat spacing
    let mut h_copy = [0; 4];
    h_copy[0] = h0[0];
    h_copy[1] = h0[1];
    h_copy[2] = h0[0];
    h_copy[3] = h0[1];

    // to the left
    let mut hl = [0; DEG];
    hl[0] = h_copy[DEG - 0];
    hl[1] = h_copy[DEG - 1];
    hl[2] = h_copy[DEG - 2];

    let mut hl_cs = [0; DEG]; // cumulative sum
    icumsum(&hl, DEG, &mut hl_cs);

    let mut bl = [0; DEG];
    for i in 0..DEG {
        bl[i] = breaks[0] - hl_cs[i];
    }

    // to the right
    let mut hr = [0; DEG];
    hr[0] = h_copy[0];
    hr[1] = h_copy[1];
    hr[2] = h_copy[2];

    let mut hr_cs = [0; DEG]; // cumulative sum
    icumsum(&hr, DEG, &mut hr_cs);

    let mut br = [0; DEG];
    for i in 0..DEG {
        br[i] = breaks[2] + hr_cs[i];
    }

    // add breaks
    let mut breaks_ext = [0; 3 * DEG];
    for i in 0..DEG {
        breaks_ext[i] = bl[DEG - 1 - i];
        breaks_ext[i + 3] = breaks[i];
        breaks_ext[i + 6] = br[i];
    }

    let mut h_ext = [0; 3 * DEG - 1];
    for i in 0..DEG * 3 - 1 {
        h_ext[i] = breaks_ext[i + 1] - breaks_ext[i];
    }

    // initialize polynomial coefficients
    let mut coefs = vec![vec![0.0; N_SPLINE + 1]; N_SPLINE * PIECES_EXT];
    for i in (0..N_SPLINE * PIECES_EXT).step_by(N_SPLINE) {
        coefs[i][0] = 1.0;
    }

    // expand h using the index matrix ii
    let mut ii = vec![vec![0; PIECES_EXT]; DEG + 1];
    for i in 0..PIECES_EXT {
        ii[0][i] = i_limit(0 + i as i32, PIECES_EXT as i32 - 1);
        ii[1][i] = i_limit(1 + i as i32, PIECES_EXT as i32 - 1);
        ii[2][i] = i_limit(2 + i as i32, PIECES_EXT as i32 - 1);
        ii[3][i] = i_limit(3 + i as i32, PIECES_EXT as i32 - 1);
    }

    // expanded h
    let mut h = vec![0.0; (DEG + 1) * PIECES_EXT];
    for i in 0..N_SPLINE * PIECES_EXT {
        let ii_flat = ii[i % N_SPLINE][i / N_SPLINE];
        h[i] = h_ext[ii_flat as usize] as f64;
    }

    // recursive generation of B-splines
    let mut q = vec![vec![0.0; PIECES_EXT]; N_SPLINE];
    for k in 1..N_SPLINE {
        // antiderivatives of splines
        for j in 0..k {
            for l in 0..N_SPLINE * PIECES_EXT {
                coefs[l][j] *= h[l] / (k - j) as f64;
            }
        }

        for l in 0..N_SPLINE * PIECES_EXT {
            q[l % N_SPLINE][l / N_SPLINE] = 0.0;
            for m in 0..N_SPLINE {
                q[l % N_SPLINE][l / N_SPLINE] += coefs[l][m];
            }
        }

        // cumsum
        for l in 0..PIECES_EXT {
            for m in 1..N_SPLINE {
                q[m][l] += q[m - 1][l];
            }
        }

        for l in 0..N_SPLINE * PIECES_EXT {
            if l % N_SPLINE == 0 {
                coefs[l][k] = 0.0;
            } else {
                coefs[l][k] = q[l % N_SPLINE - 1][l / N_SPLINE];
            }
        }

        // normalize antiderivatives by max value
        let mut fmax = vec![0.0; PIECES_EXT * N_SPLINE];
        for i in 0..PIECES_EXT {
            for j in 0..N_SPLINE {
                fmax[i * N_SPLINE + j] = q[N_SPLINE - 1][i];
            }
        }

        for j in 0..k + 1 {
            for l in 0..N_SPLINE * PIECES_EXT {
                coefs[l][j] /= fmax[l];
            }
        }

        // diff to adjacent antiderivatives
        for i in 0..(N_SPLINE * PIECES_EXT) - DEG {
            for j in 0..k + 1 {
                coefs[i][j] -= coefs[DEG + i][j];
            }
        }
        for i in (0..N_SPLINE * PIECES_EXT).step_by(N_SPLINE) {
            coefs[i][k] = 0.0;
        }
    }

    // scale coefficients
    let mut scale = vec![1.0; N_SPLINE * PIECES_EXT];
    for k in 0..N_SPLINE - 1 {
        for i in 0..N_SPLINE * PIECES_EXT {
            scale[i] /= h[i];
        }
        for i in 0..N_SPLINE * PIECES_EXT {
            coefs[i][(N_SPLINE - 1) - (k + 1)] *= scale[i];
        }
    }

    // reduce pieces and sort coefficients by interval number
    let mut jj = vec![vec![0; PIECES]; N_SPLINE];
    for i in 0..N_SPLINE {
        for j in 0..PIECES {
            if i == 0 {
                jj[i][j] = N_SPLINE * (1 + j);
            } else {
                jj[i][j] = DEG;
            }
        }
    }

    for i in 1..N_SPLINE {
        for j in 0..PIECES {
            jj[i][j] += jj[i - 1][j];
        }
    }

    let mut coefs_out = vec![vec![0.0; N_SPLINE]; N_SPLINE * PIECES];
    for i in 0..N_SPLINE * PIECES {
        let jj_flat = jj[i % N_SPLINE][i / N_SPLINE] - 1;
        for j in 0..N_SPLINE {
            coefs_out[i][j] = coefs[jj_flat][j];
        }
    }

    // create first B-splines to feed into optimization
    let mut xs_b = vec![0; size * N_SPLINE];
    let mut index_b = vec![0; size * N_SPLINE];

    let mut break_ind = 1;
    for i in 0..size {
        if i >= breaks[break_ind] as usize && break_ind < N_BREAKS - 1 {
            break_ind += 1;
        }
        for j in 0..N_SPLINE {
            xs_b[i * N_SPLINE + j] = i as i32 - breaks[break_ind - 1];
            index_b[i * N_SPLINE + j] = j + (break_ind - 1) * N_SPLINE;
        }
    }

    let mut v_b = vec![0.0; size * N_SPLINE];
    for i in 0..size * N_SPLINE {
        v_b[i] = coefs_out[index_b[i]][0];
    }

    for i in 1..N_SPLINE {
        for j in 0..size * N_SPLINE {
            v_b[j] = v_b[j] * xs_b[j] as f64 + coefs_out[index_b[j]][i];
        }
    }

    let mut a = vec![0.0; size * (N_SPLINE + 1)];
    let mut break_ind = 0;
    for i in 0..N_SPLINE * size {
        if i / N_SPLINE >= breaks[1] as usize {
            break_ind = 1;
        }
        a[(i % N_SPLINE) + break_ind + (i / N_SPLINE) * (N_SPLINE + 1)] = v_b[i];
    }

    let mut x = vec![0.0; N_SPLINE + 1];
    lsqsolve_sub(&a, size, N_SPLINE + 1, y, &mut x);

    // coeffs of B-splines to combine by optimised weighting in x
    let mut c = vec![vec![0.0; N_SPLINE * PIECES]; PIECES + N_SPLINE - 1];

    for i in 0..N_SPLINE * N_SPLINE * PIECES {
        let c_row = i % N_SPLINE + (i / N_SPLINE) % 2;
        let c_col = i / N_SPLINE;

        let coef_row = i % (N_SPLINE * 2);
        let coef_col = i / (N_SPLINE * 2);

        c[c_row][c_col] = coefs_out[coef_row][coef_col];
    }

    // final coefficients
    let mut coefs_spline = vec![vec![0.0; N_SPLINE]; PIECES];

    // multiply with x
    for j in 0..N_SPLINE * PIECES {
        let coef_col = j / PIECES;
        let coef_row = j % PIECES;

        for i in 0..N_SPLINE + 1 {
            coefs_spline[coef_row][coef_col] += c[i][j] * x[i];
        }
    }

    // compute piecewise polynomial
    for i in 0..size {
        let second_half = if i < breaks[1] as usize { 0 } else { 1 };
        y_out[i] = coefs_spline[second_half][0];
    }

    for i in 1..N_SPLINE {
        for j in 0..size {
            let second_half = if j < breaks[1] as usize { 0 } else { 1 };
            y_out[j] = y_out[j] * (j as f64 - breaks[1] as f64 * second_half as f64)
                + coefs_spline[second_half][i];
        }
    }

    0
}
