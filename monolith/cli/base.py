import sys
import argparse
from collections import namedtuple


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
        return parser

    def register(self, command):
        name = command().get_name()
        self.registry[name] = command


class BaseCommand(object):

    def get_name(self):
        return getattr(self, 'name', self.__class__.__name__.lower())



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
        arg('label', nargs=1),
    ]

    def handle(self, namespace):
        self.handle_label(label, namespace)

    def handle_label(self, label, namespace):
        raise NotImplementedError

