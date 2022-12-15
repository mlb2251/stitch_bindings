Tutorial
========

We will assume you have already installed ``stitch_core``. If not, first see :doc:`intro/install`.

Lets do some basic abstraction learning. Here we'll two programs ``(a a a)`` and ``(b b b)`` and abstract out the common structure as a function ``λx. x x x``

>>> from stitch_core import compress
>>> programs = ["(a a a)", "(b b b)"]
>>> res = compress(programs, iterations=1)
>>> res.rewritten
['(fn_0 a)', '(fn_0 b)']
>>> res.abstractions[0].body
'(#0 #0 #0)'

Abstractions are given unique names ``fn_0``, ``fn_1``, etc., while arguments to these abstractions are represented as ``#0``, ``#1``, etc.

The full :py:func:`stitch_core.compress` function is given as:
.. autofunction:: stitch_core.compress

And may raise an exception if the Rust backend panics:

.. autoexception:: stitch_core.StitchException

or may raise a ``TypeError`` if incorrect argument types are provided.

