# import the contents of the Rust library into the Python extension
from .stitch_core import compress_backend,rewrite_backend
from typing import Optional, Dict, List, Any
import json


class StitchException(Exception):
    pass



class Abstraction:
    def __init__(self, name: str, body: str, arity: int):
        self.name = name
        self.body = body
        self.arity = arity

class CompressionResult:
    def __init__(self, json: Dict[str,Any]):
        self.abstractions = [Abstraction(body=abs["body"], name=abs["name"], arity=abs["arity"]) for abs in json["abstractions"]]
        self.rewritten = json['rewritten']
        self.json = json


def from_dreamcoder(json: Dict[str,Any]):
    """
    Takes a dreamcoder-style dictionary and returns a dictionary of arguments to pass to stitch.compress()
    """

    frontiers = json["frontiers"]
    anonymous_abstractions = [production["expression"] for production in json["DSL"]["productions"] if production["expression"].startswith("#")]
    anonymous_abstractions.sort(key=len)
    anonymous_to_named = [(f"dreamcoder_abstraction_{i}", anonymous) for (i,anonymous) in enumerate(anonymous_abstractions)]

    programs = []
    tasks = []
    for i, frontier in enumerate(frontiers):
        task = frontier.get("task", str(i))
        for program in frontier["programs"]:
            program = program["program"]
            # replace #(lambda ...) with fn_2 etc. Start with highest numbered fn to avoid mangling bodies of other fns.
            for (name, anonymous) in reversed(anonymous_to_named):
                program = program.replace(anonymous, name)
            assert '#' not in program
            programs.append(program)
            tasks.append(task)

    return dict(
        programs=programs,
        tasks=tasks,
        anonymous_to_named=anonymous_to_named
    )

def rewrite(
    programs: List[str],
    abstractions: List[Abstraction],
    **kwargs
    ) -> List[str]:
    """
    todo description
    """

    args = " ".join([build_arg(k, v) for k, v in kwargs.items()])

    return rewrite_backend(
        programs,
        abstractions,
        args
    )

def compress(
    programs: List[str],
    iterations: int,
    max_arity: int = 2,
    threads: int = 1,
    silent: bool = True,
    **kwargs
    ) -> Dict[str,Any]:
    """
    run compression
    """

    tasks = kwargs.pop("tasks", None)
    anonymous_to_named = kwargs.pop("anonymous_to_named", None)

    kwargs.update(dict(
        iterations=iterations,
        max_arity=max_arity,
        threads=threads,
        silent=silent
    ))

    args = " ".join([build_arg(k, v) for k, v in kwargs.items()])

    try:
        res = compress_backend(
            programs,
            tasks,
            anonymous_to_named,
            args)
    except BaseException as e:
        if e.__class__.__name__ == "PanicException":
            raise StitchException(f"Rust backend panicked with exception: {e}")
        else:
            raise # eg TypeError from pyo3 conversion
    
    res = json.loads(res)
    
    return CompressionResult(res)
    

def build_arg(name: str, val) -> str:
    """
    Builds command line argument version of a Python argument, so for example:
    - build_arg("max_arity",3) -> "--max-arity=3"
    - build_arg("silent",True) -> "--silent"
    - build_arg("silent",False) -> ""
    """
    assert isinstance(val, (str, int, bool)), f"unexpected type for argument `{name}`: {type(val)}"
    res = "--" + name.replace("_", "-")
    if isinstance(val,bool):
        if val:
            return res # eg "--silent"
        else:
            return ""
    return f"{res}={val}"