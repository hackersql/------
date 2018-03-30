import os
import sys
import unittest
import test.support

this_dir_path = os.path.abspath(os.path.dirname(__file__))

def get_tests_modules(path=this_dir_path):
    """This will import and yield modules whose names start with test_
    and are inside packages found in path."""
    py_ext = '.py'

    for name in os.listdir(path):
        if name.startswith('test_') and name.endswith(py_ext):
            yield __import__(name[:-len(py_ext)])

def get_tests():
    """Yield all the tests in the modules found by get_tests_modules."""
    for module in get_tests_modules():
        for test in getattr(module, 'tests'):
            yield test

if __name__ == "__main__":
    test.support.use_resources = ['gui']
    test.support.run_unittest(*get_tests())
