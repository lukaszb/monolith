import os
import sys
import argparse
from collections import namedtuple
from monolith.compat import OrderedDict
from monolith.compat import unicode
from monolith.cli.exceptions import AlreadyRegistered


Argument = namedtuple('Argument', 'args kwargs')


def arg(*args, **kwargs):
    return Argument(args, kwargs)


class Parser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        self.stream = kwargs.pop('stream', sys.stderr)
        super(Parser, self).__init__(*args, **kwargs)

    def _print_message(self, message, file=None):
        if file is None:
            file = self.stream
        super(Parser, self)._print_message(unicode(message), file)


class ExecutionManager(object):
    usage = None
    completion = False
    completion_env_var_name = ''

    def __init__(self, argv=None, stream=None, stdout=None):
        if argv is None:
            argv = [a for a in sys.argv]
        self.prog_name = os.path.basename(argv[0])
        self.argv = argv[1:]
        self.registry = {}
        self.stream = stream or sys.stderr
        self.stdout = stdout or sys.stdout

        for name, Command in self.get_commands_to_register().items():
            self.register(name, Command)

    def get_usage(self):
        return self.usage

    def get_parser(self):
        parser = Parser(prog=self.prog_name, usage=self.get_usage(),
            stream=self.stream)
        subparsers = parser.add_subparsers(
            title='subcommands',
        )
        for name, command in self.registry.items():
            cmdparser = subparsers.add_parser(name, help=command.help)
            for argument in command.get_args():
                cmdparser.add_argument(*argument.args, **argument.kwargs)
            cmdparser.set_defaults(func=command.handle)

        return parser

    def register(self, name, Command, force=False):
        if not force and name in self.registry:
            raise AlreadyRegistered('Command %r is already registered' % name)
        command = Command(self.prog_name, self.stream)
        self.registry[name] = command
        command.post_register(self)

    def get_commands(self):
        """
        Returns commands stored in the registry (sorted by name).
        """
        commands = OrderedDict()
        for cmd in sorted(self.registry.keys()):
            commands[cmd] = self.registry[cmd]
        return commands

    def get_commands_to_register(self):
        return {}

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
        if self.completion:
            self.autocomplete()
        parser = self.get_parser()
        namespace = parser.parse_args()
        if hasattr(namespace, 'func'):
            namespace.func(namespace)

    def autocomplete(self):
        if self.completion_env_var_name not in os.environ:
            return
        cwords = os.environ['COMP_WORDS'].split()[1:]
        cword = int(os.environ['COMP_CWORD'])
        try:
            current = cwords[cword-1]
        except IndexError:
            current = ''
        cmd_names = self.get_commands().keys()

        if current:
            self.stdout.write(unicode(' '.join(
                [name for name in cmd_names if name.startswith(current)])))

        sys.exit(1)


class BaseCommand(object):
    help = ''
    args = []
    name = 'command'

    def __init__(self, prog_name=None, stream=None):
        self.prog_name = prog_name or ''
        self.stream = stream or sys.stdout

    def get_args(self):
        return self.args or []

    def handle(self, namespace):
        raise NotImplementedError

    def post_register(self, manager):
        pass


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
    label_default_value = None
    args = []

    def get_label_arg(self):
        return arg('label', default=self.label_default_value, nargs='?')

    def get_args(self):
        return self.args + [self.get_label_arg()]

    def handle(self, namespace):
        self.handle_label(namespace.label, namespace)

    def handle_label(self, label, namespace):
        raise NotImplementedError


def get_command_name(command):
    """
    Returns name of the given ``command`` (either ``name`` attribute
    or lower-cased name of the class).
    """

