# import the contents of the Rust library into the Python extension
from .stitch_core import compress_backend,rewrite_backend
from typing import Dict, List, Any, Tuple, Union
import json

class StitchException(Exception):
    """Raised when the Stitch's Rust backend panics"""
    pass
class ParseError(Exception):
    pass

class InvalidAbstractionException(Exception):
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
        assert not body.startswith("#"), "This abstractions is in dreamcoder format – use Abstraction.from_dreamcoder() instead"
        self.arity = arity
    
    def __repr__(self):
        args = ','.join([f'#{i}' for i in range(self.arity)])
        return f"{self.name}({args}) := {self.body}"

    @staticmethod
    def from_dreamcoder(name:str, dreamcoder_abstraction: str, name_mapping: List[Tuple[str,str]]):
        """
        Takes a dreamcoder-style abstraction like "#(lambda (foo $0 (#(lambda bar $0))))" and returns an Abstraction object.
        """

        # We can start by running the dreamcoder_to_stitch() utility for programs, which will replace any
        # dreamcoder-style abstraction invocations like #(...) with fn_0(...) etc, and will also convert all `lambda`s to `lam`s.
        assert dreamcoder_abstraction.startswith("#")
        abstraction = dreamcoder_to_stitch(dreamcoder_abstraction[1:], name_mapping)

        sexpr = parse(abstraction)
        sexpr, num_lambdas = strip_lambdas(sexpr)
        sexpr = dc_to_stitch_vars(sexpr, 0, num_lambdas)
        body = show_sexpr(sexpr)
        assert '#' not in body
        return Abstraction(name, body, num_lambdas)


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
    Takes a dreamcoder-style json dictionary and returns a dictionary of arguments to pass as kwargs to compress() or rewrite().

    The following keys will be in the returned dictionary:
     - `name_mapping`: see name_mapping_dreamcoder()
     - `programs`: These are the programs translated from dreamcoder format to stitch format, see dreamcoder_to_stitch()
     - `tasks`: These are the tasks associated with each program, since DreamCoder has a concept of tasks. See also :ref:`compression_objectives`.
     - `rewritten_dreamcoder=True`: This is a flag that tells compress() to return the dreamcoder-formatted programs in the `.json["rewritten_dreamcoder]` fied of its output.

    :param json: A dreamcoder-style json dictionary.
    :type json: Dict[str,Any]
    :return: A dictionary of arguments to pass as kwargs to compress() or rewrite()
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
    """
    Takes a dreamcoder-style json dictionary and returns a list of tuples of the form (name, anonymous_abstraction)
    where name is the name of the abstraction (like "fn_0") and anonymous_abstraction is the dreamcoder-format 
    anonymous abstraction like "#(lambda (foo (#(lambda bar $0))))". This is useful for translating back and forth
    between dreamcoder and stitch formats in conjunction with dreamcoder_to_stitch() and stitch_to_dreamcoder().

    Note that name mappings can be added together but must always be ordered such that later abstractions are later
    in the list, so that they don't accidentally get mangled by earlier abstractions during dreamcoder_to_stitch().

    This function sorts the abstractions by length, so that longer abstractions are later in the list which will avoid
    the mangling problem as well.
    """
    assert "DSL" in json, "This is not a dreamcoder json output"
    anonymous_abstractions = [production["expression"] for production in json["DSL"]["productions"] if production["expression"].startswith("#")]
    anonymous_abstractions.sort(key=len)
    return [(f"dreamcoder_abstraction_{i}", anonymous) for (i,anonymous) in enumerate(anonymous_abstractions)]

def name_mapping_stitch(json: dict) -> List[Tuple[str,str]]:
    """
    Same as name_mapping_dreamcoder() but when starting from a stitch output json, such as the .json
    field of CompressionResult.
    """
    assert "abstractions" in json, "This is not a stitch json output"
    return [(abstraction['name'], abstraction['dreamcoder']) for abstraction in json['abstractions']]

def dreamcoder_to_stitch(program: Union[str,List[str]], name_mapping: List[Tuple[str,str]]):
    """
    Translates a program or list of programs from dreamcoder format to stitch format using the name_mapping
    obtained from name_mapping_dreamcoder() or name_mapping_stitch().
    """
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
    """
    Translates a program or list of programs from stitch format to dreamcoder format using the name_mapping
    obtained from name_mapping_dreamcoder() or name_mapping_stitch().
    """

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
    """
    Replaces all instances of `prim` in `program` with `new`. We use this when prim is something
    like "fn_1" and new is something like "#(lambda (foo (#(lambda bar $0))))" and we want to be
    careful not to mangle something like "fn_10" or "some_fn_1" which would get mangled if we naively
    did a string replace.
    """
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

    :param programs: A list of programs to rewrite in stitch format. See dreamcoder_to_stitch() or from_dreamcoder() for translating to this format from dreamcoder.
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

        # since we have no way to pass a name_mapping to the backend, these results will be
        # mangled so to save people the pain lets just pop them off for now
        json_res.pop("rewritten_dreamcoder")
        for a in json_res["abstractions"]:
            a.pop("rewritten_dreamcoder")

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

    :param programs: A list of programs to learn abstractions from in stitch format. See dreamcoder_to_stitch() or from_dreamcoder() for translating to this format from dreamcoder.
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


def sexpr_replace(sexpr, old, new):
    if isinstance(old, str):
        fn_old = lambda x: x == old
    else:
        fn_old = old
    if isinstance(new, str):
        fn_new = lambda _: new
    else:
        fn_new = new
    assert callable(fn_old)
    assert callable(fn_new)

    if fn_old(sexpr):
        return fn_new(sexpr)
    else:
        if isinstance(sexpr, list):
            return [sexpr_replace(x, fn_old, fn_new) for x in sexpr]
        else:
            assert isinstance(sexpr, str)
            return sexpr

def strip_lambdas(sexpr):
    num_lambdas = 0
    while isinstance(sexpr, list) and len(sexpr) > 0 and (sexpr[0] == "lambda" or sexpr[0] == "lam"):
        assert len(sexpr) == 2, "lambda should only take one argument (the body)"
        num_lambdas += 1
        sexpr = sexpr[1]
    return sexpr, num_lambdas

def dc_to_stitch_vars(sexpr, depth, num_args):
    if isinstance(sexpr, str):
        if sexpr.startswith("$"):
            # this is a de Bruijn index
            idx = int(sexpr[1:])
            if idx >= depth:
                # #(foo (lambda ($0 $1))) -> #(foo (lambda ($0 #0)))
                shifted = idx - depth
                # note the larger the $i the higher outside of the abstraction
                # it points ie to an earlier argument and thus the lower the #j it
                # corresponds to. As a test case at depth 0 and 2 args, $0 becomes #1
                new_idx = num_args - shifted - 1 
                if new_idx < 0:
                    raise InvalidAbstractionException("abstraction contains free variables")
                return "#" + str(new_idx)
        return sexpr
    else:
        assert isinstance(sexpr, list)
        if len(sexpr) > 0 and sexpr[0] in ("lambda", "lam"):
            return [sexpr[0]] + [dc_to_stitch_vars(e, depth + 1, num_args) for e in sexpr[1:]]
        else:
            return [dc_to_stitch_vars(e, depth, num_args) for e in sexpr]

def show_sexpr(sexpr):
    if isinstance(sexpr, str):
        return sexpr
    elif isinstance(sexpr, list):
        if len(sexpr) != 0 and isinstance(sexpr[0], str) and sexpr[0].startswith("#"):
            return "#(" + " ".join([show_sexpr(s) for s in sexpr[1:]]) + ")"
        return "(" + " ".join([show_sexpr(s) for s in sexpr]) + ")"


def parse(original_s: str):
    """
    Parses a string into an s-expression. Such as
    "(+ 3 (* 2 4))" -> ["+", "3", ["*", "2", "4"]]

    Note that dreamcoder-style (baz #(foo bar)) get parsed as
    ["baz" ["#", "foo", "bar"]] i.e. the `#` symbol is moved *into* the list of children as the first item
    for ease of identifying when a subexpression is a learned abstraction
    """

    assert original_s.count('#(') == original_s.count('#'), "parser assumes all `#` symbols are followed by a `(` but this is not the case here"

    # add guaranteed parens around whole thing and guaranteed spacing around parens so they parse into their own items
    s = original_s.replace("#(","(# ").replace("(", " ( ").replace(")", " ) ")

    # `split` will skip all quantities of all forms of whitespace
    items = s.split()
    if len(items) == 0:
        raise ParseError("SExpr parse called on empty (or all whitespace) string")
    if items[1] == ")":
        raise ParseError("SExpr starts with a closeparen")

    # this is a single symbol like "foo" or "bar"
    if len(items) == 1:
        return items[0]

    i=-1
    expr_stack = []
    # num_open_parens = Int[]

    while True:
        i += 1

        if i > len(items)-1:
            raise ParseError(f"unbalanced parens: unclosed parens in {original_s}")

        if items[i] == "(":
            expr_stack.append([])
        elif items[i] == ")":
            # end an expression: pop the last SExpr off of expr_stack and add it to the SExpr at one level before that

            if len(expr_stack) == 1:
                if i != len(items)-1:
                    raise ParseError(f"trailing characters after final closeparen in {original_s}")
                break

            last = expr_stack.pop()
            expr_stack[-1].append(last)
        else:
            # any other item like "foo" or "+" is a symbol
            expr_stack[-1].append(items[i])

    assert len(expr_stack) != 0, "unreachable - should have been caught by the first check for string emptiness"
    if len(expr_stack) != 1:
        raise ParseError(f"unbalanced parens: not enough close parens in {original_s}")

    return expr_stack.pop()