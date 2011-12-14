try:
    import unittest2 as unittest
except ImportError:
    import unittest

try:
    from collections import OrderedDict
except ImportError:
    from monolith.utils.ordereddict import OrderedDict


__all__ = ['unittest', 'OrderedDict']

