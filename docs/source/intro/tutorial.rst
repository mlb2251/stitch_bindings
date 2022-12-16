.. _intro-tutorial:

Tutorial
========

We will assume you have already installed ``stitch_core``. If not, first see :ref:`intro-install`.


Minimal Example
^^^^^^^^^^^^^^^

Lets do some basic abstraction learning. Here we'll two programs ``(a a a)`` and ``(b b b)`` and abstract out the common structure as a function ``λx. x x x``

>>> from stitch_core import compress
>>> programs = ["(a a a)", "(b b b)"]
>>> res = compress(programs, iterations=1)
>>> res.rewritten
['(fn_0 a)', '(fn_0 b)']
>>> res.abstractions[0]
fn_0(#0) := (#0 #0 #0)
>>> res.abstractions[0].name
'fn_0'
>>> res.abstractions[0].body
'(#0 #0 #0)'
>>> res.abstractions[0].arity
1


Abstractions are given unique names ``fn_0``, ``fn_1``, etc., while arguments to these abstractions are represented as ``#0``, ``#1``, etc.

We could then rewrite a new set of programs using this same abstraction like so:

>>> from stitch_core import rewrite
>>> rewrite(["(c c c)", "(d d d)"], res.abstractions)
['(fn_0 c)', '(fn_0 d)']


API
^^^

.. autofunction:: stitch_core.compress

.. autoclass:: stitch_core.CompressionResult

.. autoclass:: stitch_core.Abstraction

.. autoexception:: stitch_core.StitchException

The full :py:func:`stitch_core.rewrite` function is given as:

.. autofunction:: stitch_core.rewrite


More Examples
^^^^^^^^^^^^^

The example from the Overview section of the `Stitch paper <https://arxiv.org/abs/2211.16605>`_ could be written as::

    from stitch_core import compress
    programs = [
        "(lam (+ 3 (* (+ 2 4) 2)))",
        "(lam (map (lam (+ 3 (* 4 (+ 3 $0)))) $0))",
        "(lam (* 2 (+ 3 (* $0 (+ 2 1)))))"
    ]
    res = compress(programs, iterations=1, max_arity=2)

>>> res.abstractions[0]
fn_0(#0,#1) := (+ 3 (* #1 #0))
>>> res.rewritten
[
    '(lam (fn_0 2 (+ 2 4)))',
    '(lam (map (lam (fn_0 (+ 3 $0) 4)) $0))',
    '(lam (* 2 (fn_0 (+ 2 1) $0)))'
]

Loading from a file (`example file <https://github.com/mlb2251/stitch_bindings/blob/main/data/cogsci/nuts-bolts.json>`__)::

    with open('../data/cogsci/nuts-bolts.json','r') as f:
        programs = json.load(f)
    res = compress(programs, iterations=3, max_arity=3)

>>> res.abstractions
[
    fn_0(#0,#1) := (T (repeat (T l (M 1 0 -0.5 (/ 0.5 (tan (/ pi #1))))) #1 (M 1 (/ (* 2 pi) #1) 0 0)) (M #0 0 0 0)),
    fn_1(#0,#1,#2) := (repeat (T (T #2 (M 0.5 0 0 0)) (M 1 0 (* #1 (cos (/ pi 4))) (* #1 (sin (/ pi 4))))) #0 (M 1 (/ (* 2 pi) #0) 0 0)),
    fn_2(#0) := (T (T c (M 2 0 0 0)) (M #0 0 0 0))
]

Working with a DreamCoder-format json file (`example file <https://github.com/mlb2251/stitch_bindings/blob/main/data/dc/origami/iteration_0_3.json>`__)::

    from stitch_core import from_dreamcoder
    with open('../data/dc/origami/iteration_0_3.json','r') as f:
        dreamcoder_json = json.load(f)
    kwargs = from_dreamcoder(dreamcoder_json)
    res = compress(**kwargs, iterations=3, max_arity=3)

>>> res.abstractions[0]
fn_0(#0,#1,#2) := (if (empty? (cdr #0)) #2 (#1 (cdr #0)))

Catching a StitchException, in this case from a malformed program (unbalanced parentheses)::

    from stitch_core import StitchException
    bad_programs = ["(a a a"]
    try:
        out_json = compress(bad_programs, iterations=3)
        assert False, "Should have thrown an exception"
    except StitchException as e:
        print(f"caught exception: {e}")
