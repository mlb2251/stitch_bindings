.. _intro-tutorial:

Tutorial
========

If you have not already installed ``stitch_core``, see :ref:`intro-install`.


Basic Example
^^^^^^^^^^^^^

The programs from the example in the Overview section of the `Stitch paper <https://arxiv.org/abs/2211.16605>`_ could be written as follows::

    programs = [
        "(lam (+ 3 (* (+ 2 4) 2)))",
        "(lam (map (lam (+ 3 (* 4 (+ 3 $0)))) $0))",
        "(lam (* 2 (+ 3 (* $0 (+ 2 1)))))"
    ]

Each program is a string written in a lisp-like lambda calculus syntax:
 * Variables should be written as *de Bruijn* indices (i.e. ``$i`` refers to the variable bound by the ``i`` th lambda above it) so ``λx. λy. x y`` is written ``(lam (lam ($1 $0)))``
 * Lambdas need explicit parentheses around their body so ``(lam + 3 2)`` should instead be written ``(lam (+ 3 2))``. The
   parser outputs an error message explaining this if you make this mistake. Lambdas can also be written with ``lambda`` instead
   of ``lam`` but the output of stitch will always be normalized to use ``lam``.
 * Be sure to balance your parentheses or you will get an error.
 * You don't need to pre-define the language you are using. Any series of tokens with no whitespace that isn't reserved for something else is treated as a language primitive, like ``+``, ``foo``, ``-0.5`` etc. Only ``app`` and ``lam`` are reserved. Primitives may not begin with ``#`` or ``$`` and may not contain parentheses or whitespace.
 * Check out other example programs `here <https://github.com/mlb2251/stitch_bindings/blob/main/data>`__.

The largest common structure in these examples is that they all contain a subterm of the form ``(+ 3 (* _ _))``.
This structure can be represented with the lambda abstraction ``λx. λy. (+ 3 (* y x))``. We can find this with stitch:

>>> from stitch_core import compress
>>> res = compress(programs, iterations=1, max_arity=2)
>>> res.abstractions[0]
fn_0(#0,#1) := (+ 3 (* #1 #0))
>>> res.abstractions[0].name
'fn_0'
>>> res.abstractions[0].body
'(+ 3 (* #1 #0))'
>>> res.abstractions[0].arity
2
>>> res.rewritten
[
    '(lam (fn_0 2 (+ 2 4)))',
    '(lam (map (lam (fn_0 (+ 3 $0) 4)) $0))',
    '(lam (* 2 (fn_0 (+ 2 1) $0)))'
]

Here ``iterations=1`` controls the number of abstractions that are learned.
Abstractions are named like ``fn_0``, ``fn_1``, etc., while arguments to these abstractions are 
named like ``#0``, ``#1``, etc.

We could rewrite a new set of programs using this learned abstraction like so:

>>> from stitch_core import rewrite
>>> rewrite(["(lam (+ 3 (* (+ 1 1) 1)))", "(lam (- 5 (+ 3 (* $0 (+ 2 1)))))"], res.abstractions)
[
    '(lam (fn_0 1 (+ 1 1)))',
    '(lam (- 5 (fn_0 (+ 2 1) $0)))'
]

Note that ``res.json`` contains a huge amount of extra outputs and information, see :ref:`out-json` for details. This includes statistics
on how much compression is achieved, how many times each abstraction is used, what arguments are passed to
the abstraction each time it is used, etc. Additional kwargs can control the inclusion
of extra information as well, for example if ``compress(rewritten_intermediates=True)`` is passed
then the intermediate programs after each iteration of compression are included in the output.

There is a lot of customizability in :py:func:`stitch_core.compress` (see :ref:`compress_kwargs` for a full list of options), anything supported by
the Rust library is also supported in these Python bindings.

Functions & Classes
^^^^^^^^^^^^^^^^^^^

.. autofunction:: stitch_core.compress

.. autoclass:: stitch_core.CompressionResult

.. autoclass:: stitch_core.Abstraction

.. autofunction:: stitch_core.rewrite

.. autofunction:: stitch_core.from_dreamcoder

.. autoexception:: stitch_core.StitchException

Loading from a file
^^^^^^^^^^^^^^^^^^^

Loading from `this file <https://github.com/mlb2251/stitch_bindings/blob/main/data/cogsci/nuts-bolts.json>`__ from the data set of `Wong et al. 2022 <https://arxiv.org/abs/2205.05666>`__::

    with open('../data/cogsci/nuts-bolts.json','r') as f:
        programs = json.load(f)
    res = compress(programs, iterations=3, max_arity=3)

>>> res.abstractions
[
    fn_0(#0,#1) := (T (repeat (T l (M 1 0 -0.5 (/ 0.5 (tan (/ pi #1))))) #1 (M 1 (/ (* 2 pi) #1) 0 0)) (M #0 0 0 0)),
    fn_1(#0,#1,#2) := (repeat (T (T #2 (M 0.5 0 0 0)) (M 1 0 (* #1 (cos (/ pi 4))) (* #1 (sin (/ pi 4))))) #0 (M 1 (/ (* 2 pi) #0) 0 0)),
    fn_2(#0) := (T (T c (M 2 0 0 0)) (M #0 0 0 0))
]

Working with DreamCoder-format compression inputs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Loading from `this file <https://github.com/mlb2251/stitch_bindings/blob/main/data/dc/origami/iteration_0_3.json>`__::

    from stitch_core import from_dreamcoder
    with open('../data/dc/origami/iteration_0_3.json','r') as f:
        dreamcoder_json = json.load(f)
    kwargs = from_dreamcoder(dreamcoder_json)
    res = compress(**kwargs, iterations=3, max_arity=3)

>>> res.abstractions[0]
fn_0(#0,#1,#2) := (if (empty? (cdr #0)) #2 (#1 (cdr #0)))

Note that the rewritten results in ``res.rewritten`` are in Stitch format, but DreamCoder format can
be found in ``res.json["rewritten_dreamcoder"]`` as long as ``rewritten_dreamcoder=True`` is passed
as an argument to compress() or rewrite(). Additionally, ``res.json["abstractions"][i]["dreamcoder"]`` contains the
body of the i-th abstraction in DreamCoder format.

Catching a StitchException
^^^^^^^^^^^^^^^^^^^^^^^^^^

For example, catching the StitchException raised by compressing a malformed program (unbalanced parentheses)::

    from stitch_core import StitchException
    bad_programs = ["(a a a"]
    try:
        out_json = compress(bad_programs, iterations=3)
        assert False, "Should have thrown an exception"
    except StitchException as e:
        print(f"caught exception: {e}")

Verbose Compression
^^^^^^^^^^^^^^^^^^^

To run stitch in verbose mode, pass ``silent=False`` to :py:func:`stitch_core.compress`::

    res = compress(programs, iterations=1, max_arity=2, silent=False)

This will produce a lot of output, ending in some lines like::

    =======Compression Summary=======
    Found 1 inventions
    Cost Improvement: (1.33x better) 806 -> 604
    fn_0 (1.33x wrt orig): utility: 200 | final_cost: 604 | 1.33x | uses: 2 | body: [fn_0 arity=1: (#0 #0 #0)]
    Time: 0ms

Primer on the this output:
    - ``Cost Improvement: (1.33x better) 806 -> 604``: here we see that by the cost metric (which by default values terminals like ``foo`` and ``a`` as ``100`` and nonterminals like applications and lambdas as ``1``) our programs were rewritten to be 1.33x smaller.
    - ``fn_0``: this is the name the new primitive was assigned
    - ``(1.33x wrt orig)``: this is a *cumulative* measure of compression (ie "with respect to original"), so if we were learning more than one abstraction it would represent the accumulated compression over all previous abstractions
    - ``utility: 200``: This is the utility, which corresponds to the difference in program cost before and after rewriting.
    - ``final_cost: 604``: final cost of programs after rewriting
    - ``1.33x``: compression gained from this abstraction - again, only relevant when learning more than one abstraction
    - ``uses: 2``: the abstraction is used twice in the set of programs
    - ``body: [fn_0 arity=1: (#0 #0 #0)]``: this is the abstraction itself! ``(#0 #0 #0)`` is equivalent to ``λx. (x x x)`` - the first abstraction variable is always ``#0``, the second is ``#1``, etc.

Also note that ``res.json`` contains even more detail about the compression process.