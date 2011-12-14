import sys
import mock
import argparse
import unittest
from monolith.cli.base import ExecutionManager
from monolith.cli.base import BaseCommand
from monolith.cli.base import arg
from StringIO import StringIO


class DummyCommand(BaseCommand):
    pass


class TestExecutionManager(unittest.TestCase):

    def setUp(self):
        self.manager = ExecutionManager(['foobar'], stdout=StringIO(),
            stderr=StringIO())

    def test_init_prog_name(self):
        self.assertEqual(self.manager.prog_name, 'foobar')

    def test_init_stdout(self):
        manager = ExecutionManager()
        self.assertEqual(manager.stdout, sys.stdout)

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

    def test_register(self):
        Command = type('Command', (BaseCommand,), {'name': 'foobar'})
        self.manager.register(Command)
        self.assertEqual(self.manager.registry, {'foobar': Command})

    def test_get_commands(self):
        FooCommand = type('FooCommand', (BaseCommand,), {'name': 'foo'})
        BarCommand = type('BarCommand', (BaseCommand,), {'name': 'bar'})
        self.manager.register(FooCommand)
        self.manager.register(BarCommand)
        self.assertEqual(self.manager.get_commands(), {
            'bar': BarCommand,
            'foo': FooCommand,
        })

    def test_run_command(self):

        class Command(BaseCommand):
            name = 'init'
            handle = mock.Mock()

        self.manager.register(Command)
        self.manager.run_command('init')
        self.assertTrue(Command.handle.called)

    def test_run_command_with_args(self):

        class Command(BaseCommand):
            args = [
                arg('-f', '--force', action='store_true', default=False),
            ]
            name = 'add'
            handle = mock.Mock()

        self.manager.register(Command)
        self.manager.run_command('add', '-f')
        self.assertTrue(Command.handle.called)
        namespace = Command.handle.call_args[0][0]
        self.assertTrue(namespace.force)


class TestBaseCommand(unittest.TestCase):

    def test_get_name_defaults_to_lower_cased_class_name(self):
        cmd = type('Command', (BaseCommand,), {})()
        self.assertEqual(cmd.get_name(), 'command')

    def test_get_name(self):
        cmd = type('Command', (BaseCommand,), {'name': 'foobar'})()
        self.assertEqual(cmd.get_name(), 'foobar')


class TestArg(unittest.TestCase):

    def test_args(self):
        self.assertEqual(arg(1, 2, 'foo', bar='baz').args, (1, 2, 'foo'))

    def test_kargs(self):
        self.assertEqual(arg(1, 2, 'foo', bar='baz').kwargs, {'bar': 'baz'})

