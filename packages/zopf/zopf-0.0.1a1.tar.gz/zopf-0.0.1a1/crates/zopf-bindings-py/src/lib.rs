use pyo3::prelude::*;
use zopf;

#[pyfunction]
fn launch_cli() -> PyResult<()> {
    let args = std::env::args().skip(1).collect::<Vec<_>>();
    zopf::cli::run(args);
    Ok(())
}

#[pymodule]
fn _bindings(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_wrapped(wrap_pyfunction!(launch_cli))?;

    Ok(())
}
