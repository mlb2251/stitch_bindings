// #![cfg(features="python")]

use stitch_core::*;
use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use serde_json::{json,Value};
use clap::Parser;


/// Calls compression.rs::compression(), and has a similar API to bin/compress.rs
/// `programs` should be a list of program strings. `tasks` should be a list of task name strings,
/// with length equal to that of programs. Keyword arguments exist for
/// all the parameters of CompressionStepConfig (eg max_arity etc). `iterations` controls
/// the number of inventions that are returned.
/// Returns: a json string similar to the output of bin/compress.rs with some minor changes.
/// You can parse this string with `import json; json.loads(output)`.
#[pyfunction(
    programs,
    iterations,
    args,
)]
fn compression(
    py: Python,
    programs: Vec<String>,
    iterations: usize,
    args: String,
) -> String {

    let cfg = &MultistepCompressionConfig::parse_from(format!("compress {args}").split_whitespace());

    let input = Input {
        train_programs: programs,
        test_programs: None,
        tasks: None,
        prev_dc_inv_to_inv_strs: Vec::new(),
    };
    
    // release the GIL and call compression
    let (_step_results, json_res) = py.allow_threads(||
        multistep_compression(&input, cfg)
    );


    // return as something you could json.loads(out) from in python
    json_res.to_string()
}

/// A Python module implemented in Rust.
#[pymodule]
fn stitch(_py: Python, m: &PyModule) -> PyResult<()> {
    // m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    // m.add_function(wrap_pyfunction!(soot, m)?)?;
    m.add_function(wrap_pyfunction!(compression, m)?)?;
    Ok(())
}