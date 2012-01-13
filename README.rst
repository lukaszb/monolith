
Monolith
========

monolith is simple framwork for creating command line tools. Subcommands are
class based (approach and part of implementation was inspired by Django
management commands, however monolith uses *argparse* instead of *optparse*).

Supported Python versions are 2.6/2.7 and 3.2+.

Example
-------

::

    #!/usr/bin/env python
    """
    Example of how to create git-like execution manager with monolith.
    This is completely fake command.
    """
    from __future__ import print_function
    from __future__ import unicode_literals
    from monolith.cli import ExecutionManager
    from monolith.cli import LabelCommand
    from monolith.cli import arg
    from monolith.cli import CompletionCommand


    class AddCommand(LabelCommand):
        
        def handle_label(self, label, namespace):
            print("A %s" % label, file=self.stdout)


    def main(**kwargs):
        manager = ExecutionManager(**kwargs)
        manager.register('add', AddCommand)
        manager.register('completion', CompletionCommand),
        manager.execute()

    if __name__ == '__main__':
        main()

