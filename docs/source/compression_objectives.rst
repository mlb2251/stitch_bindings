.. _compression_objectives:

Compression Objectives
======================

By default, if you pass :py:func:`stitch_core.compress` a list of ``programs``, it will find the abstraction that minimizes
the cost metric (see :ref`cost_metrics`) in the programs once they are rewritten to use the abstraction, plus the size of the abstraction itself.
Formally for an abstraction ``A``:

.. math::

   cost(A) + \sum_{p \in programs} cost(rewrite(p,A))


If you pass ``iterations=3`` then
after finding the first abstraction and rewriting the programs with it, Stitch will then compress the rewritten programs to find yet another abstraction
building on the first, and so on until the specified number of ``iterations`` have been run. Note that Stitch will stop early if there are no abstractions
with positive compression.

In program synthesis you might have a set of programs that all solve the same task. In this case, you may want to weight each task equally regardless
of how many solved programs it contains. DreamCoder approaches this problem by only counting the smallest rewritten program in the sum for each task.
Formally for an abstraction ``A``:

.. math::

   cost(A) + \sum_{task \in T} \min_{p \in task} cost(rewrite(p,A))

Stitch optimizes for this objective if a mapping of programs to tasks is provided in the ``tasks`` keyword argument is passed to ``compress`` (see :ref:`compress_kwargs`).

