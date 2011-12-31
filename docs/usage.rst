.. _usage:

.. testsetup:: *

    from __future__ import print_function
    from monolith.cli import ExecutionManager, BaseCommand, LabelCommand


Usage
=====

Firstly, we need to build an entry point for our command line application. In
``monolith`` it is called *ExecutionManager*.

Execution manager
-----------------

Create our execution manager

.. doctest::

    >>> from monolith.cli import ExecutionManager, BaseCommand
    >>> manager = ExecutionManager()

Creating commands
-----------------

Now let's create simple commands:


.. doctest::

    >>> class FooCommand(BaseCommand):
    ...     def handle(self, namespace):
    ...         print('foo', file=self.stdout)
    ...
    >>> class BarCommand(BaseCommand):
    ...     def handle(self, namespace):
    ...         print('bar', file=self.stdout)
    ...

.. note::

    Commands should write to specific stream explicitly or use *file* keyword
    argument of *print* function, but this would require to add following in
    Python 2.X::

        from __future__ import print_function


Registering commands
--------------------

Now register defined commands:

.. doctest::

    >>> manager.register('foo', FooCommand)
    >>> manager.register('bar', BarCommand)


Commands execution
------------------

... and finally run them:

.. doctest::

    >>> manager.execute(['foo'])
    foo
    >>> manager.execute(['bar'])
    bar


.. note::

    Normally, in your program you would call *execute* method without
    any parameters - this would default to *sys.argv*.


Complete example
----------------

.. literalinclude:: ../examples/git.py

