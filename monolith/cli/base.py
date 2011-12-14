import sys
import argparse
from collections import namedtuple
from collections import OrderedDict


Argument = namedtuple('Argument', 'args kwargs')


def arg(*args, **kwargs):
    return Argument(args, kwargs)


class ExecutionManager(object):
    usage = 'USAGE'

    def __init__(self, argv=None, stdout=None, stderr=None):
        if argv is None:
            argv = [a for a in sys.argv]
        self.prog_name = argv[0]
        self.argv = argv[1:]
        self.registry = {}
        self.stdout = stdout or sys.stdout
        self.stderr = stderr or sys.stderr

    def get_usage(self):
        return self.usage

    def get_parser(self):
        parser = argparse.ArgumentParser(prog=self.prog_name,
            usage=self.get_usage())
        subparsers = parser.add_subparsers(
            title='subcommands',
        )
        for Command in self.registry.values():
            cmd = Command()
            cmdparser = subparsers.add_parser(cmd.get_name(), help=cmd.help)
            for argument in cmd.args:
                cmdparser.add_argument(*argument.args, **argument.kwargs)
            cmdparser.set_defaults(func=cmd.handle)

        return parser

    def register(self, command):
        name = command().get_name()
        self.registry[name] = command

    def get_commands(self):
        """
        Returns commands stored in the registry (sorted by name).
        """
        commands = OrderedDict()
        for cmd in sorted(self.registry.keys()):
            commands[cmd] = self.registry[cmd]
        return commands

    def run_command(self, cmd, *args):
        """
        Runs command.

        :param cmd: command to run (key at the registry)
        :param argv: arguments passed to the command
        """
        argv = [cmd] + list(args)
        parser = self.get_parser()
        namespace = parser.parse_args(argv)
        namespace.func(namespace)

    def execute(self):
        parser = self.get_parser()
        namespace = parser.parse_args()
        namespace.func(namespace)


class BaseCommand(object):
    help = ''
    args = []

    def get_name(self):
        return getattr(self, 'name', self.__class__.__name__.lower())

    def handle(self, namespace):
        raise NotImplementedError



class LabelCommand(BaseCommand):
    args = [
        arg('labels', nargs='+'),
    ]

    def handle(self, namespace):
        for label in namespace.labels:
            self.handle_label(label, namespace)

    def handle_label(self, label, namespace):
        raise NotImplementedError


class SingleLabelCommand(BaseCommand):
    args = [
        arg('label', default='.', nargs='?'),
    ]

    def handle(self, namespace):
        self.handle_label(namespace.label, namespace)

    def handle_label(self, label, namespace):
        raise NotImplementedError

