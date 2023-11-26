
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
          - Max arity of abstractions to find (will find arities from 0 to this number inclusive).
            Note that scaling with arity can be very expensive [default: 2]
        * - ``abstraction_prefix <val>``
          - Prefix used to generate names of new abstractions, by default we will name our
            abstractions fn_0, fn_1, fn_2, etc [default: fn\_]
        * - ``allow_single_task``
          - Allow for abstractions that are only useful in a single task (defaults to False like
            DreamCoder)
        * - ``batch <val>``
          - How many worklist items a thread will take at once [default: 1]
        * - ``cost_app <val>``
          - Sets cost for applications in the lambda calculus [default: 1]
        * - ``cost_ivar <val>``
          - Sets cost for ``#i`` abstraction variables [default: 100]
        * - ``cost_lam <val>``
          - Sets cost for lambdas [default: 1]
        * - ``cost_prim_default <val>``
          - Sets cost for primitives like ``+`` and ``*`` [default: 100]
        * - ``cost_var <val>``
          - Sets cost for ``$i`` variables [default: 100]
        * - ``dreamcoder_comparison``
          - Extra printouts related to running a dreamcoder comparison. Section 6.1 of Stitch paper
            https://arxiv.org/abs/2211.16605
        * - ``dynamic_batch``
          - Threads will autoadjust how large their batches are based on the worklist size
        * - ``eta_long``
          - Puts result into eta-long form when rewriting (also requires beta-normal form). This can
            be useful for programs that will be used to train top down synthesizers, but it also
            restricts what abstractions can be found a bit (i.e. only those that can be put in
            beta-normal eta-long form are allowed)
        * - ``follow <val>``
          - Pattern or abstraction to follow and give prinouts about. If ``follow_prune=True`` we will
            aggressively prune to only follow this pattern, otherwise we will just verbosely print
            when ancestors of this pattern are encountered
        * - ``follow_prune``
          - For use with ``follow``, enables aggressive pruning. Useful for ensuring that it is
            *possible* to find a particular abstraction by guiding the search directly towards it
        * - ``hole_choice <val>``
          - Method for choosing hole to expand at each step. Doesn't have a huge effect [default:
            depth-first] [possible values: random, breadth-first, depth-first, max-largest-subset,
            high-entropy, low-entropy, max-cost, min-cost, many-groups, few-groups, few-apps]
        * - ``iterations <val>``
          - Maximum number of iterations to run compression for (number of inventions to find,
            though stitch will stop early if no compressive abstraction exists) [default: 3]
        * - ``inv_arg_cap``
          - Enables edge case handling where inverting the argument capture subsumption pruning is
            needed for optimality. Generally not relevant just included for completeness, see the
            footnoted section of Section 4.3 of the Stitch paper https://arxiv.org/abs/2211.16605
        * - ``inv_candidates <val>``
          - [currently not used] Number of invention candidates compression_step should return in a
            *single* step. Note that these will be the top n optimal candidates modulo subsumption
            pruning (and the top-1 is guaranteed to be globally optimal) [default: 1]
        * - ``no_curried_bodies``
          - Forbid abstraction bodies rooted to the left of an app (see also no_curried_metavars and
            eta_long)
        * - ``no_curried_metavars``
          - Forbid metavariables to the left of an app
        * - ``no_mismatch_check``
          - Disables the safety check for the utility being correct; you only want to do this if you
            truly dont mind unsoundness for a minute
        * - ``no_opt``
          - Disable all optimizations
        * - ``no_opt_arity_zero``
          - Disable the arity zero optimization, which searches first for the most compressive
            arity-zero abstraction since this is extremely fast to find and provides a good starting
            point for our upper bound pruning. In practice this isn't a very important optimization
        * - ``no_opt_force_multiuse``
          - Disable *redundant argument elimination* pruning (aka "force multiuse"). Section 4.3 of
            Stitch paper https://arxiv.org/abs/2211.16605 This is a fairly important optimization
            (ablation study in Section 6.4 of Stitch paper)
        * - ``no_opt_single_use``
          - Disable the single structurally hashed subtree match pruning. This is a very minor
            optimization that allows discarding certain abstractions that only match at a single
            unique subtree as long as that subtree lacks free variables, because arity zero
            abstractions are always superior in this case
        * - ``no_opt_upper_bound``
          - Disable *upper bound* based pruning. Section 4.2 of Stitch paper
            https://arxiv.org/abs/2211.16605 This is an extremely important optimization (ablation
            study in Section 6.4 of Stitch paper)
        * - ``no_opt_useless_abstract``
          - Disable *argument capture* pruning (aka "useless abstraction pruning"). Section 4.3 of
            Stitch paper https://arxiv.org/abs/2211.16605 This is an extremely important
            optimization (ablation study in Section 6.4 of Stitch paper)
        * - ``no_other_util``
          - Switch to utility based purely on program size without adding in the abstraction size
            (aka the "structure penalty" in DreamCoder)
        * - ``no_stats``
          - Disable stat logging - note that stat logging in multithreading requires taking a mutex
            so it can be a source of slowdown in the massively multithreaded case, hence this flag
            to disable it
        * - ``previous_abstractions <val>``
          - Number of previous abstractions that have been found before this round of compression -
            this is used to calculate what the next abstraction name should be - for example if 2
            abstractions have been found previously then the next abstraction will be fn_2 [default:
            0]
        * - ``print_stats <val>``
          - Print stats this often (0 means never) [default: 0]
        * - ``quiet``
          - Silence all printing within a compression step. See ``silent`` to silence all outputs
            between compression steps as well
        * - ``show_rewritten``
          - Print out programs rewritten under abstraction
        * - ``rewrite_check``
          - Used for soundness testing. Whenever you finish an invention do a full rewrite to check
            that rewriting doesnt raise a cost mismatch exception
        * - ``rewritten_dreamcoder``
          - Include the dreamcoder-format rewritten programs in the output
        * - ``rewritten_intermediates``
          - For each abstraction learned, includes the rewritten programs right after learning that
            abstraction in the output. If ``rewritten_dreamcoder`` is also specified, then the
            rewritten programs in dreamcoder format will also be included
        * - ``silent``
          - Disables all prinouts except in the case of a panic. See also ``quiet`` to just silence
            internal printouts during each compression step In Python this defaults to True
        * - ``structure_penalty <val>``
          - DreamCoder style structure penalty - must be positive. Overall utility is this
            difference in corpus size minus structure_penalty * abstraction_size [default: 1.0]
        * - ``threads <val>``
          - Number of threads to use for compression (no parallelism if set to 1) [default: 1]
        * - ``utility_by_rewrite``
          - Calculate utility exhaustively by performing a full rewrite. Used for debugging when
            cost mismatch exceptions are happening and we need something slow but accurate as a
            temporary solution
        * - ``verbose_best``
          - Prints whenever a new best abstraction is found
        * - ``verbose_rewrite``
          - Very verbose when rewriting happens - turns off --silent and --quiet which are usually
            forced on in rewriting
        * - ``verbose_worklist``
          - Prints every worklist item as it is processed (will slow things down a ton due to
            rendering out expressions)
