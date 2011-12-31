#!/usr/bin/env python
"""
Example of how to create git-like execution manager with monolith.
This is completely fake command.
"""
from __future__ import print_function
from __future__ import unicode_literals
from monolith.cli import ExecutionManager
from monolith.cli import LabelCommand
from monolith.cli import SingleLabelCommand
from monolith.cli import arg
from monolith.cli import CompletionCommand


class AddCommand(LabelCommand):
    
    def handle_label(self, label, namespace):
        print("A %s" % label, file=self.stdout)


class InitCommand(SingleLabelCommand):
    label = 'directory'
    label_required = False
    label_default_value = '.'
    args = SingleLabelCommand.args + [
        arg('--bare', help='Create a bare repository.', default=False,
            action='store_true'),
    ]

    def handle_label(self, label, namespace):
        print("Initialized empty Git repository in %s.git" % label,
            file=self.stdout)


def get_manager(**kwargs):
    manager = ExecutionManager(**kwargs)
    manager.register('add', AddCommand)
    manager.register('init', InitCommand)
    manager.register('completion', CompletionCommand),
    return manager

def main():
    manager = get_manager()
    manager.execute()


if __name__ == '__main__':
    main()

