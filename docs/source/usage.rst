Usage
=====

.. _installation:

Installation
------------

To use `stitch_core`, first install it using pip:

.. code-block:: console

   $ pip install stitch_core --upgrade

Beep boop
----------------

Babababa ``stitch_core.compress()`` function:

.. autofunction:: stitch_core.compress

The ``beep`` parameter should be either ``"bap"``, ``"boop"``,
or ``"badoop"``. Otherwise, :py:func:`lumache.compress`
will raise an exception.

.. autoexception:: stitch_core.StitchException

For example:

>>> import stitch_core
>>> stitch_core.compress()
['ayy', 'eee', 'beeeeep']
