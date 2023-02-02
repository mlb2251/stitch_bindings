# import the contents of the Rust library into the Python extension
from .stitch_core import compress_backend,rewrite_backend
from typing import Dict, List, Any, Tuple, Union
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

class RewriteResult:
    """
    The result of calling rewrite().

    :param rewritten: a list of programs, where each program has been rewritten using the abstractions
    :type rewritten: List[str]
    :param json: the raw JSON output from the Rust backend, containing lots of additional information
    :type json: Dict[str,Any]
    """
    def __init__(self, json: Dict[str,Any]):
        self.rewritten: List[str] = json['rewritten']
        self.json = json


def from_dreamcoder(json: Dict[str,Any]) -> Dict[str,Any]:
    """
    Takes a dreamcoder-style json dictionary and returns a dictionary of arguments to pass as kwargs to stitch.compress().

    The following keys will be in the returned dictionary:
     - `name_mapping`: This is a mapping from anonymous abstractions to named abstractions, for example from "#(lambda (+ $0 2))" to "fn_2", since
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
    name_mapping = [(f"dreamcoder_abstraction_{i}", anonymous) for (i,anonymous) in enumerate(anonymous_abstractions)]

    programs = []
    tasks = []
    for i, frontier in enumerate(frontiers):
        task = frontier.get("task", str(i))
        for program in frontier["programs"]:
            program = program["program"]
            # replace #(lambda ...) with fn_2 etc. Start with highest numbered fn to avoid mangling bodies of other fns.
            for (name, anonymous) in reversed(name_mapping):
                program = program.replace(anonymous, name)
            assert '#' not in program
            # replace "lambda" with "lam". Note that lambdas always appear with parens to their left and a space to their right
            program = program.replace("(lambda ", "(lam ")
            programs.append(program)
            tasks.append(task)

    return dict(
        programs=programs,
        tasks=tasks,
        name_mapping=name_mapping,
        rewritten_dreamcoder=True,
    )

def from_dreamcoder(json: Dict[str,Any]) -> Dict[str,Any]:
    """
    Takes a dreamcoder-style json dictionary and returns a dictionary of arguments to pass as kwargs to stitch.compress().

    ** Note that this is temporarily ~ 10x slower

    The following keys will be in the returned dictionary:
     - `name_mapping`: This is a mapping from anonymous abstractions to named abstractions, for example from "#(lambda (+ $0 2))" to "fn_2", since
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

    name_mapping = name_mapping_dreamcoder(json)

    programs = []
    tasks = []
    for i, frontier in enumerate(json["frontiers"]):
        for program in frontier["programs"]:
            programs.append(dreamcoder_to_stitch(program["program"], name_mapping))
            tasks.append(frontier.get("task", str(i)))

    return dict(
        programs=programs,
        tasks=tasks,
        name_mapping=name_mapping,
        rewritten_dreamcoder=True
    )

def name_mapping_dreamcoder(json: dict) -> List[Tuple[str,str]]:
    assert "DSL" in json, "This is not a dreamcoder json output file"
    anonymous_abstractions = [production["expression"] for production in json["DSL"]["productions"] if production["expression"].startswith("#")]
    anonymous_abstractions.sort(key=len)
    return [(f"dreamcoder_abstraction_{i}", anonymous) for (i,anonymous) in enumerate(anonymous_abstractions)]

def name_mapping_stitch(json: dict) -> List[Tuple[str,str]]:
    assert "abstractions" in json, "This is not a stitch json output file"
    return [(abstraction['name'], abstraction['dreamcoder']) for abstraction in json['abstractions']]

def dreamcoder_to_stitch(program: Union[str,List[str]], name_mapping: List[Tuple[str,str]]):
    if isinstance(program,(list,tuple)):
        return [dreamcoder_to_stitch(p, name_mapping) for p in program]

    # replace #(lambda ...) with fn_2 etc. Start with highest numbered fn to avoid mangling bodies of other fns.
    for (name, anonymous) in reversed(name_mapping):
        program = program.replace(anonymous, name)
    assert '#' not in program
    # replace "lambda" with "lam". Note that lambdas always appear with parens to their left and a space to their right
    program = program.replace("(lambda ", "(lam ")
    return program

def stitch_to_dreamcoder(program: Union[str,List[str]], name_mapping: List[Tuple[str,str]]):
    if isinstance(program,(list,tuple)):
        return [stitch_to_dreamcoder(p, name_mapping) for p in program]

    # replace lam with lambda
    program = program.replace("(lam ", "(lambda ")

    # ordering here doesnt matter because replace_prim() is precise enough to not mistake
    # fn_10 for being fn_1 etc
    for (name, anonymous) in reversed(name_mapping):
        program = replace_prim(program, name, anonymous)
    
    return program

def replace_prim(program: str, prim: str, new: str) -> str:

    program = program.replace(f" {prim})", f" {new})")
    program = program.replace(f"({prim} ", f"({new} ")

    # we need to do the " {} " case twice to handle multioverlaps like fn_i fn_i fn_i fn_i which will replace at locations 1 and 3
    # in the first replace() and 2 and 4 in the second replace due to overlapping matches.
    program = program.replace(f" {prim} ", f" {new} ").replace(f" {prim} ", f" {new} ")

    # obscure case where entire proram is just the prim
    if program == prim:
        program = new

    # these cases are impossible because any applications must be wrapped in parens,
    # so lets just make sure they dont show up
    assert not program.startswith(f"{prim} ")
    assert not program.endswith(f" {prim}")

    # check that we've replaced all the cases
    assert f" {prim} " not in program
    assert f"({prim} " not in program
    assert f" {prim})" not in program
    assert f"{prim}" != program # case where entire program is just the primitive
    return program




def rewrite(
    programs: List[str],
    abstractions: List[Abstraction],
    **kwargs
    ) -> RewriteResult:
    """
    Rewrites a set of programs with a list of abstractions. Rewrites first with abstractions[0],
    then abstractions[1], etc. Will not perform a rewrite if it is not compressive.

    :param programs: A list of programs to rewrite.
    :type programs: List[str]
    :param abstractions: A list of Abstraction objects to rewrite with.
    :type abstractions: List[Abstraction]
    :param \**kwargs: Additional arguments to pass to the Rust backend. Only the following cost-related arguments from :ref:`compress_kwargs` can be used: ``cost_app``, ``cost_ivar``, ``cost_lam``, ``cost_prim_default``, and ``cost_var``.
    :raises StitchException: If the Rust backend panics.
    :raises TypeError: If the wrong types are provided for arguments.
    :return: A RewriteResult containing the list of rewritten programs and other relevant information
    :rtype: RewriteResult
    """

    # pop these just so we're compatible with all the same kwargs as compress
    kwargs.pop("tasks", None)
    kwargs.pop("name_mapping", None)

    panic_loud = kwargs.pop('panic_loud',False)

    args = " ".join([build_arg(k, v) for k, v in kwargs.items()])

    try:
        (rewritten,json_res) = rewrite_backend(
            programs,
            abstractions,
            panic_loud,
            args
        )
        json_res = json.loads(json_res)
        assert json_res["rewritten"] == rewritten
        return RewriteResult(json_res)
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
    name_mapping = kwargs.pop("name_mapping", None)
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
            name_mapping,
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