use std::collections::HashMap;
use std::fmt::Display;

use pyo3::types::PyDict;
use stitch_core::*;
use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
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
    max_arity = "2",
    threads = "1",
    rewritten_intermediates = "false",
    rewritten_dreamcoder = "false",
    silent = "true",
    kwargs="**"
)]
#[pyo3(text_signature = "(a, b, /)")]
// #[allow(clippy::too_many_arguments)]
fn compress_backend(
    py: Python,
    programs: Vec<String>,
    iterations: usize,
    max_arity: usize,
    threads: usize,
    rewritten_intermediates: bool,
    rewritten_dreamcoder: bool,
    silent: bool,
    kwargs: Option<HashMap<String,String>>,
) -> String {


    let kwargs: Vec<String> = kwargs.map(|d| d.iter().map(|(k,v)| arg(k,v)).collect()).unwrap_or_default();

    let args: String = vec![
        String::from("compress"),
        arg("iterations", iterations),
        arg("max-arity", max_arity),
        arg("threads", threads),
        arg("rewritten-intermediates", rewritten_intermediates),
        arg("rewritten-dreamcoder", rewritten_dreamcoder),
        arg("silent", silent),
        kwargs.join(" "),
    ].join(" ");


    let cfg = match MultistepCompressionConfig::try_parse_from(args.split_whitespace()) {
        Ok(cfg) => cfg,
        Err(e) => panic!("Error parsing arguments: {}", e),
    };

    let input = Input {
        train_programs: programs,
        test_programs: None,
        tasks: None,
        prev_dc_inv_to_inv_strs: Vec::new(),
    };
    
    // release the GIL and call compression
    let (_step_results, json_res) = py.allow_threads(||
        multistep_compression(&input, &cfg)
    );


    // return as something you could json.loads(out) from in python
    json_res.to_string()
}

/// A Python module implemented in Rust.
#[pymodule]
fn stitch(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(compress_backend, m)?)?;
    Ok(())
}



fn arg(name: &str, val: impl Display) -> String {
    let mut s = String::from("--");
    s += &name.replace("_", "-");
    let val = val.to_string();
    if val == "true" {
        return s;
    }
    if val == "false" {
        return String::new();
    }
    s += &format!("={val}");
    s
}