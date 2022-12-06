# import the contents of the Rust library into the Python extension
# optional: include the documentation from the Rust module
from .stitch import *
# from .stitch import __all__, __doc__
from typing import Optional, Dict, List, Any
import json

# __all__ = __all__ + ["foo"]


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
    mr foo
    bar
    """
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