
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
                lmdatafile.write('<s> <w> %s</s>\n' % ('a b <w> ' * (line + 1)))
        self.lmdatafile2 = tempfile.mkstemp()[1]
        self.lmfile2 = tempfile.mkstemp()[1]
        with open(self.lmdatafile2, 'w') as lmdatafile:
            for line in range(10):
                lmdatafile.write('<s> <w> %s</s>\n' % ('A B <w> ' * (line + 1)))
        train_args.data = self.lmdatafile1
        train_args.model = self.lmfile1
        lm.train(train_args)
        train_args.data = self.lmdatafile2
        train_args.model = self.lmfile2
        lm.train(train_args)
        logging.info(self.lmfile1)
        with open(self.lmfile1, 'r') as fobj:
            for line in fobj:
                logging.info(line.strip())
        logging.info(self.lmfile2)
        with open(self.lmfile2, 'r') as fobj:
            for line in fobj:
                logging.info(line.strip())

    def tearDown(self):
        os.remove(self.lmdatafile1)
        os.remove(self.lmfile1)
        os.remove(self.lmdatafile2)
        os.remove(self.lmfile2)

    def test_filter(self):
        src_lm_params = {'filename': self.lmfile1}
        tgt_lm_params = {'filename': self.lmfile2}
        cefilter = lm.CrossEntropyFilter(
            src_threshold=10, tgt_threshold=10, diff_threshold=5,
            src_lm_params=src_lm_params, tgt_lm_params=tgt_lm_params)
        inputs = [('ab', 'AB'), ('abbb abbb', 'AB'), ('ab', 'BAA'), ('abbb', 'BA'), ('abbb', 'AB')]
        scores = []
        bools = []
        for score in cefilter.score(inputs):
            scores.append(score)
            bools.append(cefilter.accept(score))
        logging.info(scores)
        self.assertSequenceEqual(bools, [True, False, False, True, False])
