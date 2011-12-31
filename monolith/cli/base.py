import os
import sys
import argparse
from collections import namedtuple
from monolith.compat import OrderedDict
from monolith.compat import unicode
from monolith.cli.exceptions import AlreadyRegistered


Argument = namedtuple('Argument', 'args kwargs')


def arg(*args, **kwargs):
    """
    Returns *Argument* namedtuple in format: ``(args, kwargs)``. In example::
    
        >>> arg(1, 2, 'foo', 'bar')
        Argument(args=(1, 2, 'foo', 'bar'), kwargs={})
        >>> arg('a', 1, foo='bar')
        Argument(args=('a', 1), kwargs={'foo': 'bar'})

    """
    return Argument(args, kwargs)


class Parser(argparse.ArgumentParser):
    """
    Subclass of ``argparse.ArgumentParser`` providing more control over output
    stream.
    """
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
    parser_cls = Parser

    def __init__(self, argv=None, stderr=None, stdout=None):
        if argv is None:
            argv = [a for a in sys.argv]
        self.prog_name = os.path.basename(argv[0])
        self.argv = argv[1:]
        self.registry = {}
        self.stderr = stderr or sys.stderr
        self.stdout = stdout or sys.stdout

        for name, Command in self.get_commands_to_register().items():
            self.register(name, Command)

    def get_usage(self):
        """
        Returns *usage* text of the main application parser.
        """
        return self.usage

    def get_parser(self):
        """
        Returns :class:`monolith.cli.Parser` instance for this
        *ExecutionManager*.
        """
        parser = self.parser_cls(prog=self.prog_name, usage=self.get_usage(),
            stream=self.stderr)
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
        """
        Registers given ``Command`` (as given ``name``) at this
        *ExecutionManager*'s registry.

        :param name: name in the registry under which given ``Command``
          should be stored.
        :param Command: should be subclass of
          :class:``monolith.cli.base.BaseCommand``
        :param force: Forces registration if set to ``True`` - even if another
          command was already registered, it would be overridden and no
          execption would be raised. Defaults to ``False``.

        :raises AlreadyRegistered: If another command was already registered
          under given ``name``.
        """
        if not force and name in self.registry:
            raise AlreadyRegistered('Command %r is already registered' % name)
        command = Command(self.prog_name, self.stdout)
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
        """
        Returns dictionary (*name* / *Command* or string pointing at the
        command class.
        """
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

    def execute(self, argv=None):
        """
        Executes command based on given arguments.
        """
        if self.completion:
            self.autocomplete()
        parser = self.get_parser()
        namespace = parser.parse_args(argv)
        if hasattr(namespace, 'func'):
            namespace.func(namespace)

    def autocomplete(self):
        """
        If *completion* is enabled, this method would write to ``self.stdout``
        completion words separated with space.
        """
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
    """
    Base command class that should be subclassed by concrete commands.

    **Attributes**

    - ``help``: Help description for this command. Defaults to empty string.
    - ``args``: List of :class:`Argument` instances. Defaults to empty list.
    - ``prog_name``: Program name of *ExecutionManager* within which this
      command is run. Defaults to ``None``.
    - ``stdout``: File-like object. Command should write to it. Defaults to
      ``sys.stdout``.
    """
    help = ''
    args = []

    def __init__(self, prog_name=None, stdout=None):
        self.prog_name = prog_name or ''
        self.stdout = stdout or sys.stdout

    def get_args(self):
        """
        Returns list of :class:`Argument` instances for the parser. By default,
        it returns ``self.args``.
        """
        return self.args or []

    def handle(self, namespace):
        """
        Handles given ``namespace`` and executes command. Should be overridden
        at subclass.
        """
        raise NotImplementedError

    def post_register(self, manager):
        """
        Performs actions once this command is registered within given
        ``manager``. By default it does nothing.
        """
        pass


class LabelCommand(BaseCommand):
    """
    Command that works on given position arguments (*labels*). By default, at
    least one *label* is required. This is controlled by *labels_required*
    attribute.

    **Extra attributes**:

    - ``labels_required``: If ``True``, at least one *label* is required,
      otherwise no positional arguments could be given. Defaults to ``True``.
    """
    labels_required = True

    def get_labels_arg(self):
        """
        Returns argument for *labels*.
        """
        nargs = self.labels_required and '+' or '*'
        return arg('labels', nargs=nargs)

    def get_args(self):
        return self.args + [self.get_labels_arg()]

    def handle(self, namespace):
        """
        Handles given ``namespace`` by calling ``handle_label`` method
        for each given *label*.
        """
        for label in namespace.labels:
            self.handle_label(label, namespace)
        else:
            self.handle_no_labels(namespace)

    def handle_label(self, label, namespace):
        """
        Handles single *label*. Should be overridden at subclass.
        """
        raise NotImplementedError

    def handle_no_labels(self, namespace):
        """
        Performs some action if no *lables* were given. By default it does
        nothing.
        """
        pass


class SingleLabelCommand(BaseCommand):
    """
    Command that works on given positional argument (*label*).

    **Extra arguments**:

    - ``label_default_value``: If no *label* were given, this would be default
      value that would be passed to ``namespace``. Defaults to ``None``.
    """
    label_default_value = None

    def get_label_arg(self):
        """
        Returns argument for *label*.
        """
        return arg('label', default=self.label_default_value, nargs='?')

    def get_args(self):
        return self.args + [self.get_label_arg()]

    def handle(self, namespace):
        """
        Calls ``handle_label`` method for given *label*.
        """
        self.handle_label(namespace.label, namespace)

    def handle_label(self, label, namespace):
        """
        Handles *label*. Should be overridden at subclass.
        """
        raise NotImplementedError

