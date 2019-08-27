
import argparse
import logging
import os
import tempfile
import unittest

from opustools_pkg.filter import word_alignment


class TestAlignFilter(unittest.TestCase):

    def test_1(self):
        data1 = ['%s.' % ('ab ' * (line + 1)) for line in range(10)]
        data2 = ['%s.' % ('AB ' * (line + 1)) for line in range(10)]
        align_filter = word_alignment.WordAlignFilter()
        scores = []
        bools = []
        for score in align_filter.score(zip(data1, data2)):
            scores.append(score)
            bools.append(align_filter.accept(score))
        logging.info(scores)
        #self.assertTrue(False)
        #self.assertSequenceEqual(bools, [True, False, False, True, False])
