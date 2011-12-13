import argparse
import unittest
from monolith.cli.base import ExecutionManager
from monolith.cli.base import BaseCommand
from monolith.cli.base import arg


class DummyCommand(BaseCommand):
    pass


class TestExecutionManager(unittest.TestCase):

    def setUp(self):
        self.manager = ExecutionManager()

    def test_get_prog(self):
        self.manager.prog = 'foobar'
        self.assertEqual(self.manager.get_prog(), 'foobar')

    def test_get_usage(self):
        self.manager.usage = 'foobar baz'
        self.assertEqual(self.manager.get_usage(), 'foobar baz')

    def test_get_parser(self):
        self.manager.prog = 'foo'
        self.manager.usage = 'bar'
        parser = self.manager.get_parser()
        self.assertIsInstance(parser, argparse.ArgumentParser)
        self.assertEqual(parser.prog, 'foo')
        self.assertEqual(parser.usage, 'bar')

    def test_register(self):
        Command = type('Command', (BaseCommand,), {'name': 'foobar'})
        self.manager.register(Command)
        self.assertEqual(self.manager.registry, {'foobar': Command})


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

