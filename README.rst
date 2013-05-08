.. image:: https://secure.travis-ci.org/lukaszb/monolith.png?branch=master
  :target: http://travis-ci.org/lukaszb/monolith

Monolith
========

monolith is simple framwork for creating command line tools. Subcommands are
class based (approach and part of implementation was inspired by Django
management commands, however monolith uses *argparse* instead of *optparse*).

Supported Python versions are 2.6/2.7, 3.2+ and PyPy.

Latest documentation can be found at https://monolith.readthedocs.org/en/latest/.


Example
-------

::

    #!/usr/bin/env python
    """
    Example of how to create git-like execution manager with monolith.
    This is completely fake command.
    """
    from __future__ import print_function
    from monolith.cli import SimpleExecutionManager
    from monolith.cli import BaseCommand
    from monolith.cli import LabelCommand
    from monolith.cli import arg

    class AddCommand(LabelCommand):
        
        def handle_label(self, label, namespace):
            print("A %s" % label)


    class CommitCommand(BaseCommand):
        args = BaseCommand.args + [
            arg('-a', '--add', action='store_true', default=False),
            arg('-m', '--message', help="Commit's message", required=True),
        ]

        def handle(self, namespace):
            print('Commit message: %r' % namespace.message)
            if namespace.add:
                print(' * add switch given!')


    def main():
        manager = SimpleExecutionManager('mygit', commands={
            'add': AddCommand,
            'commit': CommitCommand,
        })
        manager.execute()

    if __name__ == '__main__':
        main()

