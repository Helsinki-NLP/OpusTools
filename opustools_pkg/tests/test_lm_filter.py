
import argparse
import logging
import os
import tempfile
import unittest

from opustools_pkg.filter import lm


class TestLMFilter(unittest.TestCase):

    def setUp(self):
        train_args = argparse.Namespace()
        for key, default in lm._VARIKN_TRAINING_PARAMS.items():
            setattr(train_args, key, default)
        self.lmdatafile1 = tempfile.mkstemp()[1]
        self.lmfile1 = tempfile.mkstemp()[1]
        with open(self.lmdatafile1, 'w') as lmdatafile:
            for line in range(10):
                lmdatafile.write('<s> %s </s>\n' % 'a b' * (line + 1))
        train_args.data = self.lmdatafile1
        train_args.model = self.lmfile1
        lm.train(train_args)

    def tearDown(self):
        os.remove(self.lmdatafile1)
        os.remove(self.lmfile1)

    def test_1(self):
        logging.info(self.lmfile1)
        with open(self.lmfile1, 'r') as fobj:
            for line in fobj:
                logging.info(line.strip())
        self.assertTrue(False)
