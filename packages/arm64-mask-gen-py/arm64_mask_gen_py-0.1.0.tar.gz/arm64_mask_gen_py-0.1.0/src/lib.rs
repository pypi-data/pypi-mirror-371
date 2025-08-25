use pyo3::prelude::*;
use anyhow::Result;

// call into the existing rust library
use arm64_mask_gen::{parse_template, make_r2_mask_for_a64_template};
// If the arm64-mask-gen crate is built with the `keystone` feature this
// function will be available and we can use the bundled Keystone assembler.
#[allow(unused_imports)]
use arm64_mask_gen::create_keystone_assembler;

#[pyfunction]
fn make_r2_mask(template: &str) -> PyResult<(String, String)> {
    let parsed = parse_template(template);

    // Try to create a Keystone assembler via the underlying crate. If that
    // fails, return a Python RuntimeError with guidance.
    let assembler = match create_keystone_assembler() {
        Ok(a) => a,
        Err(e) => {
            return Err(pyo3::exceptions::PyRuntimeError::new_err(format!(
                "Failed to create assembler: {}. Build the wrapper with the dependency feature 'keystone' enabled and ensure Keystone is installed.",
                e
            )));
        }
    };

    match make_r2_mask_for_a64_template(&parsed, assembler) {
        Ok((p, m)) => Ok((p, m)),
        Err(e) => Err(pyo3::exceptions::PyRuntimeError::new_err(format!("{}", e))),
    }
}

#[pymodule]
fn arm64_mask_gen_py(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(make_r2_mask, m)?)?;
    Ok(())
}
