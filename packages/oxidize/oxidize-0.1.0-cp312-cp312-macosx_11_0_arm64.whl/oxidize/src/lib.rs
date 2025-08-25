use pyo3::prelude::*;

pub mod io;

pub use io::xml_parser::*;

#[pymodule]
fn oxidize(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(parse_xml_file_to_json_file, m)?)?;
    m.add_function(wrap_pyfunction!(parse_xml_file_to_json_string, m)?)?;
    m.add_function(wrap_pyfunction!(parse_xml_string_to_json_file, m)?)?;
    m.add_function(wrap_pyfunction!(parse_xml_string_to_json_string, m)?)?;
    Ok(())
}






