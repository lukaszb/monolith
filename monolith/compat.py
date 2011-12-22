from __future__ import unicode_literals
from __future__ import print_function

try:
    import unittest2 as unittest
except ImportError:
    import unittest

try:
    from collections import OrderedDict
except ImportError:
    from monolith.utils.ordereddict import OrderedDict

try:
    unicode = unicode
except NameError:
    basestring = unicode = str


__all__ = ['unittest', 'OrderedDict']

