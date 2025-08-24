use pyo3::prelude::*;

pub mod compression;
pub mod diff;
mod python;
pub mod tensor_patch;
pub mod verification;

/// Main Python module
#[pymodule]
fn tensortracker(m: &Bound<'_, PyModule>) -> PyResult<()> {
    python::register_module(m)?;
    Ok(())
}
