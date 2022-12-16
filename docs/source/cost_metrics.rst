.. _cost_metrics:

Cost Metrics
============

By default, Stitch follows DreamCoder's cost metric, which values terminals like ``+`` or ``3`` or ``$0`` as having a cost of ``100``, and nonterminals (i.e. applications and lambdas) as having a cost of `1`.
Thus, the program ``(+ 2 3)``, which is syntactic sugar for ``(app (app + 2) 3)``, has a cost of ``302`` since it has two applications and 3 terminals.

However, Stitch is actually compatible with a broad range of cost metrics, as described in Section 4.1 of the `Stitch paper <https://arxiv.org/abs/2211.16605>`__ and detailed below.


The following arguments are available for both :py:func:`stitch_core.compress` and :py:func:`stitch_core.rewrite` (from :ref:`compress_kwargs`):
 - ``cost_app``: sets the cost of an application
 - ``cost_lam``: sets the cost of a lambda
 - ``cost_ivar``: sets the cost of the abstraction variable symbol ``#0`` in the body of an abstraction
 - ``cost_var``: sets the cost of a variable like ``$0``
 - ``cost_prim_default``: sets the cost of a language primitive.

Note that all costs must be non-negative.

Internally, Stitch also supports taking a mapping from primitive names to costs, but this is not yet exposed in the Python API. See `this tracking issue <https://github.com/mlb2251/stitch_bindings/issues/5>`__.