use num_complex::Complex64;

type Cplx = Complex64;

const PI: f64 = 3.14159265359;

pub fn twiddles(size: usize) -> Vec<Cplx> {
    let mut a = Vec::with_capacity(size);


    for i in 0..size {
        let tmp = Cplx::new(0.0, -PI * i as f64 / size as f64);
        a.push(tmp.exp());
    }

    a
}

fn _fft(a: &mut [Cplx], out: &mut [Cplx], size: usize, step: usize, tw: &[Cplx]) {
    if step < size {
        _fft(out, a, size, step * 2, tw);
        _fft(&mut out[step..], &mut a[step..], size, step * 2, tw);

        for i in (0..size).step_by(2 * step) {
            let t = tw[i] * out[i + step];
            a[i / 2] = out[i] + t;
            a[(i + size) / 2] = out[i] - t;
        }
    }
}

pub fn fft(a: &mut [Cplx], tw: &[Cplx]) {
    let size = a.len();
    let mut out = a.to_vec();
    _fft(a, &mut out, size, 1, tw);
}
