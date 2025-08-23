#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests for rank.py"""
import numpy as np
from numpy.testing import assert_array_equal
import unittest

from compshs.utils.rank import *


class TestRank(unittest.TestCase):

    def test_top_k(self):
        arr = np.array([1, 3, 2])
        res = top_k(arr, 1)
        self.assertTrue(res==1)

        res = top_k(arr, 5)
        exp = np.argsort(-arr)
        assert_array_equal(res, exp)

        res = top_k(arr, 0)
        self.assertEqual(len(res), 0)

        arr = np.array([])
        res = top_k(arr, 1)
        self.assertEqual(len(res), 0)