import io
import os
import sys
import mock
import argparse
from monolith.compat import unittest
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

    @mock.patch.object(os, 'environ', {'PROG_AUTO_COMPLETE': '1'})
    @mock.patch.object(sys, 'argv', ['prog', 'a'])
    def test_manager_execute_calls_autocomplete(self):
        manager = ExecutionManager(['foobar'], stream=io.StringIO())
        Command = type('Command', (BaseCommand,), {})
        CompCommand = type('CompCommand', (CompletionCommand,), {})
        CompCommand.autocomplete = mock.Mock()

        manager.register('add', Command)
        manager.register('annotate', Command)
        manager.register('init', Command)
        manager.register('completion', CompCommand)
        stream = io.StringIO()

        with mock.patch.object(sys, 'stderr', stream):
            try:
                manager.execute()
            except SystemExit:
                pass
        manager.autocomplete.assert_called_once_with()

