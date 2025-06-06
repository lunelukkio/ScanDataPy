# -*- coding: utf-8 -*-
"""
Created on Thu Dec 29 10:47:47 2022

lunelukkio@gmail.com
"""
import unittest


def suite():
    test_suite = unittest.TestSuite()
    
    test_classes = "test*.py"   # test*.py    for all tests
    #test_classes = "test0*.py"  #   for model
    #test_classes = "test1*.py"  # test1*py    for view
    #test_classes = "test2*.py"  # test2*.py    for controller

    
    all_test_suite = unittest.defaultTestLoader.discover(".", pattern=test_classes)
    print(all_test_suite)
    for ts in all_test_suite:
        test_suite.addTest(ts)

    return test_suite





if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    test_suite = suite()
    runner.run(test_suite)
