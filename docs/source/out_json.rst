.. _out-json:

Output JSON format
==================

Here we detail the ``.json`` field of the :py:class:`stitch_core.CompressionResult` object, which contains lots of additional
outputs and information on the compression process.

Example json
^^^^^^^^^^^^

Lets run 2 steps of compression (``iterations=2``) on the following 4 examples::

    programs = [
        "f a a",
        "f b b",
        "foo bar (f c c) (f c c)",
        "foo bar x x"
    ]
    res = stitch_core.compress(programs,iterations=2,rewritten_dreamcoder=True,rewritten_intermediates=True)

Here we passed a few extra flags to compression to include extra information in the output json (see :ref:`compress_kwargs` or the output json description below for details).

The ``.abstractions`` and ``.rewritten`` fields show the two abstractions that are found as expected:

>>> res.abstractions
[
    fn_0(#0) := (foo bar #0 #0),
    fn_1(#0) := (f #0 #0)
]
>>> res.rewritten
[
    '(fn_1 a)',
    '(fn_1 b)',
    '(fn_0 (fn_1 c))',
    '(fn_0 x)'
]

The ``.json`` field is the our main interest here. Here's the output for this example, for reference:

>>> import pprint; pprint.pp(res.json)
{'cmd': '/opt/homebrew/Cellar/python@3.10/3.10.8/Frameworks/Python.framework/Versions/3.10/Resources/Python.app/Contents/MacOS/Python',
 'args': {'iterations': 2,
          'abstraction_prefix': 'fn_',
          'previous_abstractions': 0,
          'shuffle': False,
          'truncate': None,
          'no_opt': False,
          'silent': True,
          'step': {'max_arity': 2,
                   'threads': 1,
                   'no_stats': False,
                   'batch': 1,
                   'dynamic_batch': False,
                   'inv_candidates': 1,
                   'hole_choice': 'DepthFirst',
                   'cost': 'Dreamcoder',
                   'cost_lam': None,
                   'cost_app': None,
                   'cost_var': None,
                   'cost_ivar': None,
                   'cost_prim_default': None,
                   'no_mismatch_check': False,
                   'no_top_lambda': False,
                   'follow': None,
                   'follow_prune': False,
                   'verbose_worklist': False,
                   'verbose_best': False,
                   'print_stats': 0,
                   'show_rewritten': False,
                   'rewritten_dreamcoder': True,
                   'rewritten_intermediates': True,
                   'inv_arg_cap': False,
                   'no_opt_single_use': False,
                   'allow_single_task': False,
                   'no_opt_upper_bound': False,
                   'no_opt_force_multiuse': False,
                   'no_opt_useless_abstract': False,
                   'no_opt_arity_zero': False,
                   'no_other_util': False,
                   'rewrite_check': False,
                   'utility_by_rewrite': False,
                   'dreamcoder_comparison': False,
                   'quiet': True}},
 'original_cost': 1814,
 'final_cost': 905,
 'compression_ratio': 2.0044198895027625,
 'num_abstractions': 2,
 'original': ['(f a a)',
              '(f b b)',
              '(foo bar (f c c) (f c c))',
              '(foo bar x x)'],
 'rewritten': ['(fn_1 a)', '(fn_1 b)', '(fn_0 (fn_1 c))', '(fn_0 x)'],
 'rewritten_dreamcoder': ['(#(lambda (f $0 $0)) a)',
                          '(#(lambda (f $0 $0)) b)',
                          '(#(lambda (foo bar $0 $0)) (#(lambda (f $0 $0)) c))',
                          '(#(lambda (foo bar $0 $0)) x)'],
 'abstractions': [{'body': '(foo bar #0 #0)',
                   'dreamcoder': '#(lambda (foo bar $0 $0))',
                   'arity': 1,
                   'name': 'fn_0',
                   'utility': 403,
                   'final_cost': 1208,
                   'compression_ratio': 1.5016556291390728,
                   'cumulative_compression_ratio': 1.5016556291390728,
                   'num_uses': 2,
                   'rewritten': ['(f a a)',
                                 '(f b b)',
                                 '(fn_0 (f c c))',
                                 '(fn_0 x)'],
                   'rewritten_dreamcoder': ['(f a a)',
                                            '(f b b)',
                                            '(#(lambda (foo bar $0 $0)) (f c '
                                            'c))',
                                            '(#(lambda (foo bar $0 $0)) x)'],
                   'uses': [{'fn_0 (f c c)': '(foo bar (f c c) (f c c))'},
                            {'fn_0 x': '(foo bar x x)'}]},
                  {'body': '(f #0 #0)',
                   'dreamcoder': '#(lambda (f $0 $0))',
                   'arity': 1,
                   'name': 'fn_1',
                   'utility': 201,
                   'final_cost': 905,
                   'compression_ratio': 1.3348066298342542,
                   'cumulative_compression_ratio': 2.0044198895027625,
                   'num_uses': 3,
                   'rewritten': ['(fn_1 a)',
                                 '(fn_1 b)',
                                 '(fn_0 (fn_1 c))',
                                 '(fn_0 x)'],
                   'rewritten_dreamcoder': ['(#(lambda (f $0 $0)) a)',
                                            '(#(lambda (f $0 $0)) b)',
                                            '(#(lambda (foo bar $0 $0)) '
                                            '(#(lambda (f $0 $0)) c))',
                                            '(#(lambda (foo bar $0 $0)) x)'],
                   'uses': [{'fn_1 a': '(f a a)'},
                            {'fn_1 b': '(f b b)'},
                            {'fn_1 c': '(f c c)'}]}]}

Description of JSON Fields
^^^^^^^^^^^^^^^^^^^^^^^^^^

 - ``cmd``: This field can be ignored in the Python bindings, it is the command of the process running compression
 - ``args``: These are all the arguments that were passed to compression, see also :ref:`compress_kwargs`.
 - ``original_cost``: This is the cost of the original set of programs, see also :ref:`cost_metrics`.
 - ``final_cost``: This is the cost of the final set of programs, see also :ref:`cost_metrics`.
 - ``compression_ratio``: This is the ratio of the original cost to the final cost.
 - ``num_abstractions``: This is the number of abstractions that were found. Note that if there are *no* compressive abstractions
   to find on an iteration, then this can be less than the number of ``iterations`` passed to ``compress()``.
 - ``original``: This is the original set of programs.
 - ``rewritten``: This is the set of programs after rewriting with the found abstractions.
 - ``rewritten_dreamcoder``: This is the set of programs after rewriting with the found abstractions, but in the format
   that Dreamcoder uses where lambdas are written as ``lambda`` instead of ``lam`` and abstractions are written anonymously
   with the ``#()`` syntax instead of giving them names like ``fn_0``. This is set to ``None`` unless ``rewritten_dreamcoder=True``.
 - ``abstractions``: This is a list of all abstractions that were found. Each abstraction has the following fields:
    - ``body``: This is the body of the abstraction, just like the ``.body`` field of ``stitch_core.Abstraction``
    - ``dreamcoder``: This is the body of the abstraction, but in the format that Dreamcoder uses where lambdas are written as ``lambda`` instead of ``lam`` and abstractions are written anonymously with the ``#()`` syntax instead of giving them names like ``fn_0``.
    - ``arity``: This is the arity of the abstraction, just like the ``.arity`` field of ``stitch_core.Abstraction``
    - ``name``: This is the name of the abstraction, just like the ``.name`` field of ``stitch_core.Abstraction``
    - ``utility``: This is the utility of the abstraction defined as the difference between the initial and final cost of the set of programs when introducing this abstraction.
    - ``final_cost``: This is the cost of the set of programs after introducing this abstraction.
    - ``compression_ratio``: This is the ratio of the original cost to the final cost after introducing this abstraction.
    - ``cumulative_compression_ratio``: This is the ratio of the original cost to the final cost after introducing this abstraction and all abstractions that were found before it.
    - ``num_uses``: This is the number of times this abstraction was used in the final set of programs.
    - ``rewritten``: This is the set of programs after rewriting with this abstraction (and any abstractions that came before it). This field is only present if ``rewritten_intermediates=True``.
    - ``rewritten_dreamcoder``: This is the set of programs after rewriting with this abstraction (and any abstractions that came before it), but in the format that Dreamcoder uses where lambdas are written as ``lambda`` instead of ``lam`` and abstractions are written anonymously with the ``#()`` syntax instead of giving them names like ``fn_0``. This field is only present if ``rewritten_intermediates=True`` and ``rewritten_dreamcoder=True``.
    - ``uses``: This is a list of all the unique uses of this abstraction in the final set of programs. Each use is a dictionary mapping from the abstraction applied to its arguments to the original subtree before this rewrite happened. If the abstraction is used with the same arguments in multiple places, only one copy appears here - these are the *unique* uses.
