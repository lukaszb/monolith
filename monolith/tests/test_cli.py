import io
import sys
import mock
import argparse
from monolith.compat import unittest
from monolith.cli.base import arg
from monolith.cli.base import ExecutionManager
from monolith.cli.base import BaseCommand
from monolith.cli.base import LabelCommand
from monolith.cli.base import SingleLabelCommand
from monolith.cli.base import Parser
from monolith.cli.exceptions import AlreadyRegistered
from io import StringIO


class DummyCommand(BaseCommand):
    pass


class TestExecutionManager(unittest.TestCase):

    def assertRegistryClassesEqual(self, actual, expected):
        self.assertEqual(list(sorted(actual)), list(sorted(expected)))
        for key in actual:
            self.assertEqual(actual[key].__class__, expected[key],
                "Command class don't match for %r (it's %r but "
                "expected %r)" % (key, actual[key].__class__,
                expected[key]))

    def setUp(self):
        self.manager = ExecutionManager(['foobar'], stderr=StringIO())

    def test_init_prog_name(self):
        self.assertEqual(self.manager.prog_name, 'foobar')

    def test_init_stderr(self):
        manager = ExecutionManager()
        self.assertEqual(manager.stderr, sys.stderr)

    def test_default_argv(self):
        with mock.patch.object(sys, 'argv', ['vcs', 'foo', 'bar']):
            manager = ExecutionManager()
            self.assertEqual(manager.argv, ['foo', 'bar'])

    def test_get_usage(self):
        self.manager.usage = 'foobar baz'
        self.assertEqual(self.manager.get_usage(), 'foobar baz')

    def test_get_parser(self):
        self.manager.usage = 'foo bar'
        parser = self.manager.get_parser()
        self.assertIsInstance(parser, argparse.ArgumentParser)
        self.assertEqual(parser.prog, 'foobar') # argv[0]
        self.assertEqual(parser.usage, 'foo bar')
        self.assertEqual(parser.stream, self.manager.stderr)

    def test_register(self):
        Command = type('Command', (BaseCommand,), {})
        self.manager.register('foo', Command)
        self.assertRegistryClassesEqual(self.manager.registry, {'foo': Command})

    def test_register_raise_if_command_with_same_name_registered(self):
        Command = type('Command', (BaseCommand,), {})
        self.manager.register('foobar', Command)
        with self.assertRaises(AlreadyRegistered):
            self.manager.register('foobar', Command)

    def test_register_respects_force_argument(self):
        Command1 = type('Command', (BaseCommand,), {})
        Command2 = type('Command', (BaseCommand,), {})
        self.manager.register('foobar', Command1)
        self.manager.register('foobar', Command2, force=True)
        self.assertRegistryClassesEqual(self.manager.registry, {
            'foobar': Command2})

    def test_get_commands(self):
        FooCommand = type('FooCommand', (BaseCommand,), {})
        BarCommand = type('BarCommand', (BaseCommand,), {})
        self.manager.register('foo', FooCommand)
        self.manager.register('bar', BarCommand)
        self.assertEqual(list(self.manager.get_commands().keys()), ['bar', 'foo'])
        self.assertRegistryClassesEqual(self.manager.get_commands(), {
            'foo': FooCommand,
            'bar': BarCommand,
        })

    def test_get_commands_to_register(self):
        FooCommand = type('FooCommand', (BaseCommand,), {})
        BarCommand = type('BarCommand', (BaseCommand,), {})

        class Manager(ExecutionManager):

            def get_commands_to_register(self):
                return {
                    'foo': FooCommand,
                    'bar': BarCommand,
                }

        manager = Manager(['foobar'])
        self.assertRegistryClassesEqual(manager.registry, {
            'foo': FooCommand,
            'bar': BarCommand,
        })

    def test_call_command(self):

        class Command(BaseCommand):
            name = 'init'
            handle = mock.Mock()

        self.manager.register('init', Command)
        self.manager.call_command('init')
        self.assertTrue(Command.handle.called)

    def test_called_command_has_prog_name_properly_set(self):

        prog_names = []

        class Command(BaseCommand):
            name = 'init'
            def handle(self, namespace):
                prog_names.append(self.prog_name)

        self.manager.register('init', Command)
        self.manager.call_command('init')
        self.assertEqual(prog_names, ['foobar'])

    def test_call_command_with_args(self):

        class Command(BaseCommand):
            args = [
                arg('-f', '--force', action='store_true', default=False),
            ]
            name = 'add'
            handle = mock.Mock()

        self.manager.register('add', Command)
        self.manager.call_command('add', '-f')
        self.assertTrue(Command.handle.called)
        namespace = Command.handle.call_args[0][0]
        self.assertTrue(namespace.force)

    def test_execute_calls_handle_command(self):

        class Command(BaseCommand):
            args = [
                arg('-f', '--force', action='store_true', default=False),
            ]
            name = 'add'
            handle = mock.Mock()

        self.manager.register('add', Command)
        with mock.patch.object(sys, 'argv', ['prog', 'add', '-f']):
            self.manager.execute()
        namespace = Command.handle.call_args[0][0]
        Command.handle.assert_called_once_with(namespace)


class TestBaseCommand(unittest.TestCase):

    def test_get_args(self):
        Command = type('Command', (BaseCommand,), {'args': ['foo', 'bar']})
        command = Command()
        self.assertEqual(command.get_args(), ['foo', 'bar'])

    def test_handle_raises_error(self):
        with self.assertRaises(NotImplementedError):
            BaseCommand().handle(argparse.Namespace())

    def test_post_register_hooks(self):
        Command = type('Command', (BaseCommand,), {'args': ['foo', 'bar']})

        class Command(BaseCommand):
            def post_register(self, manager):
                manager.completion = True

        manager = ExecutionManager()
        self.assertFalse(manager.completion)
        manager.register('completion', Command)
        self.assertTrue(manager.completion)


class TestLabelCommand(unittest.TestCase):

    def test_handle_raise_if_handle_label_not_implemented(self):
        command = LabelCommand()
        with self.assertRaises(NotImplementedError):
            command.handle(argparse.Namespace(labels=['foo']))

    def test_handle_calls_handle_label(self):
        namespace = argparse.Namespace(labels=['foo', 'bar'])
        command = LabelCommand()
        command.handle_label = mock.Mock()
        command.handle(namespace)
        self.assertEqual(command.handle_label.call_args_list, [
            arg('foo', namespace),
            arg('bar', namespace),
        ])

    def test_labels_required_true(self):
        Command = type('Command', (LabelCommand,), {'labels_required': True})
        command = Command()
        self.assertEqual(command.get_args()[0].kwargs.get('nargs'), '+')

    def test_labels_required_false(self):
        Command = type('Command', (LabelCommand,), {'labels_required': False})
        command = Command()
        self.assertEqual(command.get_args()[0].kwargs.get('nargs'), '*')

    def test_handle_no_labels_called_if_no_labels_given(self):
        Command = type('Command', (LabelCommand,), {'labels_required': False})
        command = Command()
        command.handle_no_labels = mock.Mock()
        namespace = argparse.Namespace(labels=[])
        command.handle(namespace)
        command.handle_no_labels.assert_called_once_with(namespace)


class TestSingleLabelCommand(unittest.TestCase):

    def test_get_label_arg(self):
        Command = type('Command', (SingleLabelCommand,), {})
        label_arg = Command().get_label_arg()
        self.assertEqual(label_arg, arg('label',
            default=Command.label_default_value, nargs='?'))

    def test_get_args(self):
        Command = type('Command', (SingleLabelCommand,), {})
        command = Command()
        self.assertEqual(command.get_args(), [command.get_label_arg()])

    def test_handle_raise_if_handle_label_not_implemented(self):
        command = SingleLabelCommand()
        with self.assertRaises(NotImplementedError):
            command.handle(argparse.Namespace(label='foo'))

    def test_handle_calls_handle_label(self):
        namespace = argparse.Namespace(label='foobar')
        command = SingleLabelCommand()
        command.handle_label = mock.Mock()
        command.handle(namespace)
        self.assertEqual(command.handle_label.call_args_list, [
            arg('foobar', namespace),
        ])


class TestArg(unittest.TestCase):

    def test_args(self):
        self.assertEqual(arg(1, 2, 'foo', bar='baz').args, (1, 2, 'foo'))

    def test_kargs(self):
        self.assertEqual(arg(1, 2, 'foo', bar='baz').kwargs, {'bar': 'baz'})


class TestParser(unittest.TestCase):

    def setUp(self):
        self.stream = io.StringIO()
        self.parser = Parser(stream=self.stream)

    def test_print_message_default_file(self):
        self.parser._print_message('foobar')
        self.assertEqual(self.stream.getvalue(), 'foobar')

