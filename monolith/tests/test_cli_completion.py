import io
import os
import sys
import mock
import argparse
from monolith.compat import unittest
from monolith.cli.base import arg
from monolith.cli.base import ExecutionManager
from monolith.cli.base import BaseCommand
from monolith.cli.completion import CompletionCommand


class TestCompletionCommand(unittest.TestCase):

    def test_get_env_var_name(self):
        command = CompletionCommand('foo')
        self.assertEqual(command.get_env_var_name(), 'FOO_AUTO_COMPLETE')

    def test_get_completion_snippet(self):
        command = CompletionCommand('foo')
        command.template = '%(prog_name)s | %(ENV_VAR_NAME)s'
        self.assertEqual(command.get_completion_snippet(),
            'foo | FOO_AUTO_COMPLETE')

    def test_handle(self):
        stream = io.StringIO()
        command = CompletionCommand('foo', stream)
        command.template = 'bar'
        command.handle(argparse.Namespace())
        self.assertEqual(stream.getvalue(), 'bar')

    def test_post_register(self):
        manager = ExecutionManager()
        with mock.patch.object(CompletionCommand, 'get_env_var_name') as m:
            m.return_value = 'FOO_AUTO_COMPLETE'
            manager.register('completion', CompletionCommand)
        self.assertTrue(manager.completion)
        self.assertEqual(manager.completion_env_var_name, 'FOO_AUTO_COMPLETE')


@mock.patch.object(os, 'environ', {'PROG_AUTO_COMPLETE': '1'})
class TestAutocomplete(unittest.TestCase):

    def setUp(self):
        self.stream = io.StringIO()
        self.stdout = io.StringIO()
        self.manager = ExecutionManager(stderr=self.stream, stdout=self.stdout)
        self.manager
        Command = type('Command', (BaseCommand,), {})
        CompCommand = type('CompCommand', (CompletionCommand,), {})

        class AddCommand(BaseCommand):
            args = BaseCommand.args + [
                arg('-f', '--force', action='store_true', default=False),
            ]

        self.manager.register('add', AddCommand)
        self.manager.register('annotate', Command)
        self.manager.register('init', Command)
        self.manager.register('completion', CompCommand)
        self.manager.completion = True
        self.manager.completion_env_var_name = 'PROG_AUTO_COMPLETE'

    @mock.patch.object(sys, 'argv', ['prog', 'a'])
    def test_autocomplete_returns_none_if_env_var_not_defined(self):
        with mock.patch.object(os, 'environ', {}):
            self.assertEqual(self.manager.autocomplete(), None)

    @mock.patch.object(sys, 'argv', ['prog', 'a'])
    def test_manager_execute_calls_autocomplete(self):
        self.manager.autocomplete = mock.Mock()
        stream = io.StringIO()
        with mock.patch.object(sys, 'stderr', stream):
            with self.assertRaises(SystemExit):
                self.manager.execute()
        self.manager.autocomplete.assert_called_once_with()

    @mock.patch.object(sys, 'argv', ['prog', 'a'])
    def test_autocomplete_returns_completes_for_subcommands(self):
        os.environ['COMP_WORDS'] = 'prog a'
        os.environ['COMP_CWORD'] = '1'
        stream = io.StringIO()
        with mock.patch.object(sys, 'stderr', stream):
            with self.assertRaises(SystemExit):
                self.manager.execute()
        self.assertEqual(self.stdout.getvalue(), 'add annotate')

    @mock.patch.object(sys, 'argv', ['prog', 'a'])
    def test_autocomplete_returns_none_if_wrong_COMP_CWORD_set(self):
        os.environ['COMP_WORDS'] = 'prog a'
        os.environ['COMP_CWORD'] = '3'
        stream = io.StringIO()
        with mock.patch.object(sys, 'stderr', stream):
            with self.assertRaises(SystemExit):
                self.manager.execute()
        self.assertEqual(self.stdout.getvalue(), '')

    # skip until we implement completion for subcommands' arguments
    #@mock.patch.object(sys, 'argv', ['prog', 'add', '--fo'])
    #def test_autocomplete_returns_completes_for_subcommands_args(self):
        #os.environ['COMP_WORDS'] = 'prog add --fo'
        #os.environ['COMP_CWORD'] = '2'
        #stream = io.StringIO()
        #with mock.patch.object(sys, 'stderr', stream):
            #with self.assertRaises(SystemExit):
                #self.manager.execute()
        #self.assertEqual(self.stdout.getvalue(), '--force')

