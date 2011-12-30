.. _usage:

.. testsetup:: *

    from __future__ import print_function
    from monolith.cli import ExecutionManager, BaseCommand, LabelCommand


Usage
=====

Firstly, we need to build an entry point for our command line application. In
``monolith`` it is called *ExecutionManager*.

Create our execution manager

.. doctest::

    >>> from monolith.cli import ExecutionManager, BaseCommand
    >>> manager = ExecutionManager()

Now we need to register commands. Let's create two simple command classes:


.. doctest::

    >>> class FooCommand(BaseCommand):
    ...     def handle(self, namespace):
    ...         print('foo', file=self.stdout)
    ...

.. note::

    Please note that we do not use *print* at command's handler. Commands should
    write to specific stream explicitly or use *file* keyword argument of print
    function, but this would require to add following in Python 2.X::

        from __future__ import print_function


.. doctest::

    >>> class BarCommand(BaseCommand):
    ...     def handle(self, namespace):
    ...         print('bar', file=self.stdout)
    ...


Now register defined commands:

.. doctest::

    >>> manager.register('foo', FooCommand)
    >>> manager.register('bar', BarCommand)


... and finally run them:

.. doctest::

    >>> manager.execute(['foo'])
    foo
    >>> manager.execute(['bar'])
    bar

