import sys
import argparse
from collections import namedtuple
from monolith.compat import OrderedDict
from monolith.cli.exceptions import AlreadyRegistered


Argument = namedtuple('Argument', 'args kwargs')


def arg(*args, **kwargs):
    return Argument(args, kwargs)


class ExecutionManager(object):
    usage = None

    def __init__(self, argv=None, file=None):
        if argv is None:
            argv = [a for a in sys.argv]
        self.prog_name = argv[0]
        self.argv = argv[1:]
        self.registry = {}
        self.file = file or sys.stderr

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
            cmdparser = subparsers.add_parser(cmd.name, help=cmd.help)
            for argument in cmd.get_args():
                cmdparser.add_argument(*argument.args, **argument.kwargs)
            cmdparser.set_defaults(func=cmd.handle)

        return parser

    def register(self, name, command, force=False):
        if not force and name in self.registry:
            raise AlreadyRegistered('Command %r is already registered' % name)
        self.registry[name] = command

    def get_commands(self):
        """
        Returns commands stored in the registry (sorted by name).
        """
        commands = OrderedDict()
        for cmd in sorted(self.registry.keys()):
            commands[cmd] = self.registry[cmd]
        return commands

    def call_command(self, cmd, *argv):
        """
        Runs a command.

        :param cmd: command to run (key at the registry)
        :param argv: arguments that would be passed to the command
        """
        parser = self.get_parser()
        args = [cmd] + list(argv)
        namespace = parser.parse_args(args)
        namespace.func(namespace)

    def execute(self):
        parser = self.get_parser()
        namespace = parser.parse_args()
        if hasattr(namespace, 'func'):
            namespace.func(namespace)


class BaseCommand(object):
    help = ''
    args = []
    name = 'command'

    def get_args(self):
        return self.args or []

    def handle(self, namespace):
        raise NotImplementedError



class LabelCommand(BaseCommand):
    labels_required = True

    def get_labels_arg(self):
        nargs = self.labels_required and '+' or '*'
        return arg('labels', nargs=nargs)

    def get_args(self):
        return [self.get_labels_arg()]

    def handle(self, namespace):
        for label in namespace.labels:
            self.handle_label(label, namespace)
        else:
            self.handle_no_labels(namespace)

    def handle_label(self, label, namespace):
        raise NotImplementedError

    def handle_no_labels(self, namespace):
        pass


class SingleLabelCommand(BaseCommand):
    default_label_value = None

    def get_label_arg(self):
        return arg('label', default=self.default_label_value, nargs='?')

    def get_args(self):
        return [self.get_label_arg()]

    def handle(self, namespace):
        self.handle_label(namespace.label, namespace)

    def handle_label(self, label, namespace):
        raise NotImplementedError


def get_command_name(command):
    """
    Returns name of the given ``command`` (either ``name`` attribute
    or lower-cased name of the class).
    """

