# import the contents of the Rust library into the Python extension
from .stitch_core import compress_backend,rewrite_backend
from typing import Dict, List, Any
import json

class StitchException(Exception):
    """Raised when the Stitch's Rust backend panics"""
    pass

class Abstraction:
    """
    A functional abstraction

    :param name: the name of the abstraction, like "fn_0"
    :type name: str
    :param body: the body of the abstraction, like "(+ 3 (* #1 #0))". Variables are represented as "#0", "#1", etc.
    :type body: str
    :param arity: the arity of the abstraction, like 2
    :type arity: int
    """
    def __init__(self, name: str, body: str, arity: int):
        self.name = name
        self.body = body
        self.arity = arity
    def __repr__(self):
        args = ','.join([f'#{i}' for i in range(self.arity)])
        return f"{self.name}({args}) := {self.body}"

class CompressionResult:
    """
    The result of calling compress().

    :param abstractions: a list of Abstraction objects
    :type abstractions: List[Abstraction]
    :param rewritten: a list of programs, where each program has been rewritten using the abstractions
    :type rewritten: List[str]
    :param json: the raw JSON output from the Rust backend, containing lots of additional information
    :type json: Dict[str,Any]
    """
    def __init__(self, json: Dict[str,Any]):
        self.abstractions: List[Abstraction] = [Abstraction(body=abs["body"], name=abs["name"], arity=abs["arity"]) for abs in json["abstractions"]]
        self.rewritten: List[str] = json['rewritten']
        self.json = json


def from_dreamcoder(json: Dict[str,Any]) -> Dict[str,Any]:
    """
    Takes a dreamcoder-style json dictionary and returns a dictionary of arguments to pass as kwargs to stitch.compress().

    The following keys will be in the returned dictionary:
     - `anonymous_to_named`: This is a mapping from anonymous abstractions to named abstractions, for example from "#(lambda (+ $0 2))" to "fn_2", since
       DreamCoder operates over anonymous abstractions while Stitch operates over named ones. Since there isn't a canonical ordering to the anonymous
       abstractions in a dreamcoder-style json, this function will sort them by length and use that as the ordering, since this has the property that
       abstractions used within larger abstractions will be named first.
     - `programs`: These are the programs translated from anonymous format to named format
     - `tasks`: These are the tasks associated with each program, since DreamCoder has a concept of tasks. See also :ref:`compression_objectives`.
     - `rewritten_dreamcoder=True`: This is a flag that tells compress() to return the dreamcoder-formatted programs in the `.json["rewritten_dreamcoder]` fied of its output.

    :param json: A dreamcoder-style json dictionary.
    :type json: Dict[str,Any]
    :return: A dictionary of arguments to pass as kwargs to stitch.compress().
    :rtype: Dict[str,Any]
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
            # replace "lambda" with "lam". Note that lambdas always appear with parens to their left and a space to their right
            program = program.replace("(lambda ", "(lam ")
            programs.append(program)
            tasks.append(task)

    return dict(
        programs=programs,
        tasks=tasks,
        anonymous_to_named=anonymous_to_named,
        rewritten_dreamcoder=True,
    )

def rewrite(
    programs: List[str],
    abstractions: List[Abstraction],
    **kwargs
    ) -> List[str]:
    """
    Rewrites a set of programs with a list of abstractions. Rewrites first with abstractions[0],
    then abstractions[1], etc. Will not perform a rewrite if it is not compressive.

    :param programs: A list of programs to rewrite.
    :type programs: List[str]
    :param abstractions: A list of Abstraction objects to rewrite with.
    :type abstractions: List[Abstraction]
    :param \**kwargs: Additional arguments to pass to the Rust backend. These are the same as :ref:`compress_kwargs` since rewriting performs a form of compression under the hood, however most are not relevant to rewriting.
    :raises StitchException: If the Rust backend panics.
    :raises TypeError: If the wrong types are provided for arguments.
    :return: A list of rewritten programs.
    :rtype: List[str]
    """

    panic_loud = kwargs.pop('panic_loud',False)

    args = " ".join([build_arg(k, v) for k, v in kwargs.items()])

    try:
        return rewrite_backend(
            programs,
            abstractions,
            panic_loud,
            args
        )
    except BaseException as e:
        if e.__class__.__name__ == "PanicException":
            raise StitchException(f"Rust backend panicked with exception: {e}")
        else:
            raise # eg TypeError from pyo3 conversion


def compress(
    programs: List[str],
    iterations: int,
    max_arity: int = 2,
    threads: int = 1,
    silent: bool = True,
    **kwargs
    ) -> CompressionResult:
    """
    Runs abstraction learning on a list of programs, optimizing for a compression objective (see :ref:`compression_objectives`).
    This will run for at most ``iterations`` steps, on each step finding the most compressive abstraction, and rewriting the programs
    to use it, then passing the rewritten programs onto the next iteration of compression. If no compressive abstraction exists on an
    iteration, compress() will stop early before its ``iterations`` limit is reached.

    Learned abstractions can call earlier abstractions that were learned, thus building up a hierarchy of increasingly complex abstractions.

    :param programs: A list of programs to learn abstractions from.
    :type programs: List[str]
    :param iterations: The maximum number of iterations to run abstraction learning for.
    :type iterations: int
    :param max_arity: The maximum arity of abstractions to learn.
    :type max_arity: int
    :param threads: The number of threads to use.
    :type threads: int
    :param silent: Whether to print progress to stdout.
    :type silent: bool
    :param \**kwargs: Additional arguments to pass to the Rust backend. See :ref:`compress_kwargs` for a full listing.
    :raises StitchException: If the Rust backend panics.
    :raises TypeError: If the wrong types are provided for arguments.
    :return: A CompressionResult object containing the learned abstractions, rewritten programs, and other details from the run.
    :rtype: CompressionResult
    """

    tasks = kwargs.pop("tasks", None)
    anonymous_to_named = kwargs.pop("anonymous_to_named", None)
    panic_loud = kwargs.pop('panic_loud',False)

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
            panic_loud,
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