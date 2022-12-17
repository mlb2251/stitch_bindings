
.. list-table::
        :header-rows: 1
        :widths: 30 70

        * - Argument
          - Description
        * - ``programs <val>``
          - The ``List[str]`` of programs to learn abstractions from.
        * - ``tasks <val>``
          - A ``List[str]`` equal in length to ``programs`` that gives names for the task each program is solving. If not provided, defaults to each program solving a unique task. This is only relevant for a DreamCoder-style compression metric that takes a *min* over programs within each task. See :ref:`compression_objectives` for more details.
        * - ``max_arity <val>``
          - max arity of abstractions to find (will find all from 0 to this number inclusive)
            [default: 2]
        * - ``abstraction_prefix <val>``
          - prefix used to generate names of new abstractions, by default we will name our
            abstractions fn_0, fn_1, fn_2, etc [default: fn\_]
        * - ``allow_single_task``
          - allow for abstractions that are only useful in a single task
        * - ``batch <val>``
          - how many worklist items a thread will take at once [default: 1]
        * - ``cost_app <val>``
          - Override ``cost`` with a custom application cost [default: 1]
        * - ``cost_ivar <val>``
          - Override ``cost`` with a custom abstraction variable cost [default: 100]
        * - ``cost_lam <val>``
          - Override ``cost`` with a custom lambda cost [default: 1]
        * - ``cost_prim_default <val>``
          - Override ``cost`` with a custom default primitive cost [default: 100]
        * - ``cost_var <val>``
          - Override ``cost`` with a custom $i variable cost [default: 100]
        * - ``dreamcoder_comparison``
          - anything related to running a dreamcoder comparison
        * - ``dynamic_batch``
          - threads will autoadjust how large their batches are based on the worklist size
        * - ``follow <val>``
          - pattern or abstraction to follow. if ``follow_prune=True`` we will aggressively prune to
            only follow this pattern, otherwise we will just verbosely print when ancestors of this
            pattern are encountered
        * - ``follow_prune``
          - for use with ``--follow``, enables aggressive pruning
        * - ``hole_choice <val>``
          - Method for choosing hole to expand at each step, doesn't have a huge effect [default:
            depth-first] [possible values: random, breadth-first, depth-first, max-largest-subset,
            high-entropy, low-entropy, max-cost, min-cost, many-groups, few-groups, few-apps]
        * - ``iterations <val>``
          - Number of iterations to run compression for (number of inventions to find) [default: 3]
        * - ``inv_arg_cap``
          - disables the edge case handling where argument capture needs to be inverted for
            optimality
        * - ``inv_candidates <val>``
          - Number of invention candidates compression_step should return in a *single* step. Note
            that these will be the top n optimal candidates modulo subsumption pruning (and the
            top-1  is guaranteed to be globally optimal) [default: 1]
        * - ``no_mismatch_check``
          - disables the safety check for the utility being correct; you only want to do this if you
            truly dont mind unsoundness for a minute
        * - ``no_opt``
          - disable all optimizations
        * - ``no_opt_arity_zero``
          - disable the arity zero priming optimization
        * - ``no_opt_force_multiuse``
          - disable the force multiuse pruning optimization
        * - ``no_opt_single_use``
          - disable the single structurally hashed subtree match pruning
        * - ``no_opt_upper_bound``
          - disable the upper bound pruning optimization
        * - ``no_opt_useless_abstract``
          - disable the useless abstraction pruning optimization
        * - ``no_other_util``
          - makes it so utility is based purely on corpus size without adding in the abstraction
            size
        * - ``no_stats``
          - Disable stat logging - note that stat logging in multithreading requires taking a mutex
            so it can be a source of slowdown in the massively multithreaded case, hence this flag
            to disable it
        * - ``no_top_lambda``
          - makes it so inventions cant start with a lambda at the top
        * - ``previous_abstractions <val>``
          - Number of previous abstractions that have been found before this round of compression -
            this is used to calculate what the next abstraction name should be - for example if 2
            abstractions have been found previously then the next abstraction will be fn_2 [default:
            0]
        * - ``print_stats <val>``
          - print stats this often (0 means never) [default: 0]
        * - ``quiet``
          - silence all printing within a compression step. See ``--silent`` to silence truly all
            outputs
        * - ``show_rewritten``
          - print out programs rewritten under abstraction
        * - ``rewrite_check``
          - whenever you finish an invention do a full rewrite to check that rewriting doesnt raise
            a cost mismatch exception
        * - ``rewritten_dreamcoder``
          - include ``rewritten_dreamcoder`` in the output json
        * - ``rewritten_intermediates``
          - include ``rewritten`` from each intermediate rewritten result in the output json after
            each invention
        * - ``silent``
          - zero printouts at all except in the case of a panic. See also --quiet to just silence
            internal printouts during each compression step
        * - ``threads <val>``
          - number of threads (no parallelism if set to 1) [default: 1]
        * - ``utility_by_rewrite``
          - calculate utility exhaustively by performing a full rewrite; mainly used when cost
            mismatches are happening and we need something slow but accurate
        * - ``verbose_best``
          - prints whenever a new best abstraction is found
        * - ``verbose_worklist``
          - prints every worklist item as it is processed (will slow things down a ton due to
            rendering out expressins)
