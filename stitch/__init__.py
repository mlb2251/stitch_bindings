# import the contents of the Rust library into the Python extension
from .stitch import *
from typing import Optional, Dict, List, Any
import json

def compress_from_file(
    file: str,
    fmt: str,
    iterations: int,
    max_arity: int = 2,
    threads: int = 1,
    rewritten_intermediates: bool = False,
    rewritten_dreamcoder: bool = False,
    silent: bool = True,
    **kwargs
    ) -> Dict[str,Any]:
    """
    todo docstring
    """


def compress(
    programs: List[str],
    iterations: int,
    max_arity: int = 2,
    threads: int = 1,
    rewritten_intermediates: bool = False,
    rewritten_dreamcoder: bool = False,
    silent: bool = True,
    **kwargs
    ) -> Dict[str,Any]:
    """
    todo docstring
    """

    kwargs = {k: str(v) for k, v in kwargs.items()}

    return json.loads(compress_backend(
        programs,
        iterations,
        max_arity,
        threads,
        rewritten_intermediates,
        rewritten_dreamcoder,
        silent,
        # **kwargs
    ))


def call_backend(programs, **kwargs) -> str:
    """
    todo docstring
    """
    args = " ".join([build_arg(k, v) for k, v in kwargs.items()])
    return compress_backend(programs, args)

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