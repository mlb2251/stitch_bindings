.. _intro-tutorial:

Tutorial
========

We will assume you have already installed ``stitch_core``. If not, first see :ref:`intro-install`.

Lets do some basic abstraction learning. Here we'll two programs ``(a a a)`` and ``(b b b)`` and abstract out the common structure as a function ``λx. x x x``

>>> from stitch_core import compress
>>> programs = ["(a a a)", "(b b b)"]
>>> res = compress(programs, iterations=1)
>>> res.rewritten
['(fn_0 a)', '(fn_0 b)']
>>> res.abstractions[0].body
'(#0 #0 #0)'

Abstractions are given unique names ``fn_0``, ``fn_1``, etc., while arguments to these abstractions are represented as ``#0``, ``#1``, etc.

We could then rewrite a new set of programs using this same abstraction like so:
>>> from stitch_core import rewrite
>>> programs_to_rewrite = ["(c c c)", "(d d d)"]
>>> rewrite(programs_to_rewrite, res.abstractions)
['(fn_0 c)', '(fn_0 d)']


The full :py:func:`stitch_core.compress` function is given as:

.. autofunction:: stitch_core.compress

And may raise an exception if the Rust backend panics:

.. autoexception:: stitch_core.StitchException

or may raise a ``TypeError`` if incorrect argument types are provided.

The full :py:func:`stitch_core.rewrite` function is given as:

.. autofunction:: stitch_core.rewrite

The example from the Overview section of the `Stitch paper <https://arxiv.org/abs/2211.16605>`_ could be written as::

    from stitch_core import compress
    programs = [
        "(lam (+ 3 (* (+ 2 4) 2)))",
        "(lam (map (lam (+ 3 (* 4 (+ 3 $0)))) $0))",
        "(lam (* 2 (+ 3 (* $0 (+ 2 1)))))"
    ]
    res = compress(programs, iterations=1, max_arity=2)
    assert res.abstractions[0].body == '(+ 3 (* #1 #0))'
    assert res.rewritten == [
        '(lam (fn_0 2 (+ 2 4)))',
        '(lam (map (lam (fn_0 (+ 3 $0) 4)) $0))',
        '(lam (* 2 (fn_0 (+ 2 1) $0)))'
        ]

Loading from a file (in this case ``data/cogsci/nuts-bolts.json`` from the repo)::

    with open('../data/cogsci/nuts-bolts.json','r') as f:
        programs = json.load(f)
    res = compress(programs, iterations=3, max_arity=3)
    assert res.abstractions[0].body == '(T (repeat (T l (M 1 0 -0.5 (/ 0.5 (tan (/ pi #1))))) #1 (M 1 (/ (* 2 pi) #1) 0 0)) (M #0 0 0 0))'
    assert res.abstractions[1].body == '(repeat (T (T #2 (M 0.5 0 0 0)) (M 1 0 (* #1 (cos (/ pi 4))) (* #1 (sin (/ pi 4))))) #0 (M 1 (/ (* 2 pi) #0) 0 0))'
    assert res.abstractions[2].body == '(T (T c (M 2 0 0 0)) (M #0 0 0 0))'

Working with a DreamCoder-format json file::

    from stitch_core import compress
    with open('../data/dc/origami/iteration_0_3.json','r') as f:
        dreamcoder_json = json.load(f)
    kwargs = from_dreamcoder(dreamcoder_json)
    res = compress(**kwargs, iterations=3, max_arity=3)
    assert res.abstractions[0].body == '(if (empty? (cdr #0)) #2 (#1 (cdr #0)))'


Catching a StitchException, in this case from a malformed program (unbalanced parentheses)::
    
    from stitch_core import StitchException
    bad_programs = ["(a a a"]
    try:
        out_json = compress(bad_programs, iterations=3)
        assert False, "Should have thrown an exception"
    except StitchException as e:
        pass
