use ::stitch_core::*;
use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use clap::Parser;

/// todo add docstring
#[pyfunction(
    programs,
    tasks,
    anonymous_to_named,
    args
)]
fn compress_backend(
    py: Python,
    programs: Vec<String>,
    tasks: Option<Vec<String>>,
    anonymous_to_named: Option<Vec<(String,String)>>,
    args: String,
) -> PyResult<String> {

    // disable the printing of panics, so that the only panic we see is the one that gets passed along in an Exception to Python
    std::panic::set_hook(Box::new(|_| {}));

    let cfg = match MultistepCompressionConfig::try_parse_from(format!("compress {args}").split_whitespace()) {
        Ok(cfg) => cfg,
        Err(e) => panic!("Error parsing arguments: {}", e),
    };
    
    // release the GIL and call compression
    let (_step_results, json_res) = py.allow_threads(||
        multistep_compression(&programs, tasks, anonymous_to_named, &cfg)
    );

    // return as something you could json.loads(out) from in python
    Ok(json_res.to_string())
}

/// todo add docstring
#[pyfunction(
    programs,
    abstractions,
    args
)]
fn rewrite_backend(
    py: Python,
    programs: Vec<String>,
    abstractions: Vec<&PyAny>,
    args: String,
) -> PyResult<Vec<String>> {

    // disable the printing of panics, so that the only panic we see is the one that gets passed along in an Exception to Python
    std::panic::set_hook(Box::new(|_| {}));

    let cfg = match CompressionStepConfig::try_parse_from(format!("compress {args}").split_whitespace()) {
        Ok(cfg) => cfg,
        Err(e) => panic!("Error parsing arguments: {}", e),
    };

    let programs: Vec<ExprOwned> = programs.iter().map(|p| {
        let mut set = ExprSet::empty(Order::ChildFirst, false, false);
        let idx = set.parse_extend(p).unwrap();
        ExprOwned::new(set,idx)
        }
    ).collect();

    let abstractions = abstractions.iter().map(|a| {
        let mut set = ExprSet::empty(Order::ChildFirst, false, false);
        let idx = set.parse_extend(&a.getattr("body")?.extract::<String>()?).unwrap();
        Ok(Invention {
            body: ExprOwned::new(set,idx),
            arity: a.getattr("arity")?.extract::<usize>()?,
            name: a.getattr("name")?.extract::<String>()?
        })
    }
    ).collect::<PyResult<Vec<_>>>()?;
    
    // release the GIL and call rewriting
    let rewritten = py.allow_threads(||
        rewrite_with_inventions(&programs, &abstractions, &cfg)
    );

    let res = rewritten.iter().map(|s| s.to_string()).collect();

    // return as something you could json.loads(out) from in python
    Ok(res)
}



/// A Python module implemented in Rust.
#[pymodule]
fn stitch_core(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(compress_backend, m)?)?;
    m.add_function(wrap_pyfunction!(rewrite_backend, m)?)?;
    Ok(())
}