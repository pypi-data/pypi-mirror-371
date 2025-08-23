use crate::features::helpers::{cadd, cdiv, cminus, cmul, Cplx};
use std::f64::consts::PI;

pub fn poly(x: &[Cplx], out: &mut [Cplx]) {
    // Initialize output array
    out[0] = Cplx::new(1.0, 0.0);
    for i in 1..out.len() {
        out[i] = Cplx::new(0.0, 0.0);
    }

    let mut out_temp = vec![Cplx::new(0.0, 0.0); out.len()];

    for i in 1..x.len() + 1 {
        // Save old out to avoid reusing already changed values
        for j in 0..out.len() {
            out_temp[j] = out[j];
        }

        for j in 1..i + 1 {
            let temp1 = x[i - 1] * out_temp[j - 1];
            let temp2 = out[j];
            out[j] = temp2 - temp1;
        }
    }
}

pub fn filt(y: &[f64], a: &[f64], b: &[f64], n_coeffs: usize, out: &mut [f64]) {
    // Filter a signal y with the filter coefficients a and b, output to array out
    let offset = y[0];

    for i in 0..y.len() {
        out[i] = 0.0;
        for j in 0..n_coeffs {
            if i >= j {
                out[i] += b[j] * (y[i - j] - offset);
                out[i] -= a[j] * out[i - j];
            } else {
                out[i] += 0.0;
                out[i] -= 0.0;
            }
        }
    }

    // Add offset back
    for i in 0..y.len() {
        out[i] += offset;
    }
}

pub fn reverse_array(a: &mut [f64]) {
    // Reverse the order of the elements in an array. Write back into the input array
    let size = a.len();
    for i in 0..size / 2 {
        a.swap(i, size - 1 - i);
    }
}

pub fn filt_reverse(y: &[f64], a: &[f64], b: &[f64], n_coeffs: usize, out: &mut [f64]) {
    // Filter a signal y with the filter coefficients a and b _in reverse order_, output to array out
    let mut y_temp = y.to_vec();

    reverse_array(&mut y_temp);

    let offset = y_temp[0];

    for i in 0..y.len() {
        out[i] = 0.0;
        for j in 0..n_coeffs {
            if i >= j {
                out[i] += b[j] * (y_temp[i - j] - offset);
                out[i] -= a[j] * out[i - j];
            } else {
                out[i] += 0.0; // b[j] * offset; // 'padding'
                out[i] -= 0.0; // a[j] * offset;
            }
        }
    }

    // Add offset back
    for i in 0..y.len() {
        out[i] += offset;
    }

    reverse_array(out);
}

pub fn butterworth_filter(y: &[f64], n_poles: usize, w: f64, out: &mut [f64]) {
    let pi = PI;
    let v = (w * pi / 2.0).tan();

    // Calculate Q (poles in s-domain)
    let mut q = Vec::with_capacity(n_poles);
    for i in 0..n_poles {
        let tmp1 = Cplx::new(0.0, pi / 2.0);
        let tmp2 = Cplx::new(n_poles as f64, 0.0);
        let q_val = (cdiv(tmp1, tmp2) * Cplx::new((2 + n_poles - 1 + 2 * i) as f64, 0.0))
            .exp()
            .conj();
        q.push(q_val);
    }

    let s_g = v.powi(n_poles as i32);
    let mut s_p = Vec::with_capacity(n_poles);

    for i in 0..n_poles {
        s_p.push(v * q[i]);
    }

    let mut p = Vec::with_capacity(n_poles);
    let mut z = Vec::with_capacity(n_poles);

    let mut prod1m_sp = Cplx::new(1.0, 0.0);

    // Bilinear transform for poles, fill zeros, compute products
    for i in 0..n_poles {
        p.push(cdiv(
            cadd(Cplx::new(1.0, 0.0), s_p[i]),
            cminus(Cplx::new(1.0, 0.0), s_p[i]),
        ));
        z.push(Cplx::new(-1.0, 0.0));

        prod1m_sp = cmul(prod1m_sp, cminus(Cplx::new(1.0, 0.0), s_p[i]));
    }

    let g = s_g / prod1m_sp.re;

    let mut z_poly = vec![Cplx::new(0.0, 0.0); n_poles + 1];
    let mut p_poly = vec![Cplx::new(0.0, 0.0); n_poles + 1];

    // Polynomial coefficients from poles and zeros for filtering
    poly(&z, &mut z_poly);
    poly(&p, &mut p_poly);

    // Coefficients for filtering
    let mut b = vec![0.0; n_poles + 1]; // zeros
    let mut a = vec![0.0; n_poles + 1]; // poles

    for i in 0..n_poles + 1 {
        b[i] = g * z_poly[i].re;
        a[i] = p_poly[i].re;
    }

    // Pad to both sides to avoid end-transients
    let n_fact = 3 * n_poles;
    let mut y_padded = vec![0.0; y.len() + 2 * n_fact];

    for i in 0..n_fact {
        y_padded[i] = 2.0 * y[0] - y[n_fact - i - 1];
        y_padded[n_fact + y.len() + i] = 2.0 * y[y.len() - 1] - y[y.len() - 2 - i];
    }
    for i in 0..y.len() {
        y_padded[n_fact + i] = y[i];
    }

    // Filter in both directions
    let mut out_padded = vec![0.0; y.len() + 2 * n_fact];
    filt(&y_padded, &a, &b, n_poles, &mut out_padded);

    // Create a copy for the reverse filter
    let mut out_temp = out_padded.clone();
    filt_reverse(&out_padded, &a, &b, n_poles, &mut out_temp);
    out_padded = out_temp;

    // Extract the filtered signal
    for i in 0..y.len() {
        out[i] = out_padded[n_fact + i];
    }
}
