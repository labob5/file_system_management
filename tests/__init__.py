import unittest


def suite():
    from tests.test_directories import TestDirectories
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDirectories))
    return suite