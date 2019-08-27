"""Word alignment filtering"""

import logging
import os
import subprocess
import tempfile

from . import FilterABC


logger = logging.getLogger(__name__)


EFLOMAL_PATH = os.environ.get('EFLOMAL_PATH')
if EFLOMAL_PATH is None:
    logger.warning("Please set enviroment variable EFLOMAL_PATH to use word alignment scores")
    EFLOMAL_PATH = '.'


class WordAlignment:

    def __init__(self, eflomal_path):
        #self.eflomal_path = '/homeappl/home/miaulamo/appl_taito/eflomal'
        self.eflomal_path = eflomal_path

    def align(self, clean_file=None, src_fwd=None, trg_fwd=None,
            src_score=None, trg_score=None, priors=None):
        #command = ('{0}/align.py -i filter_files/clean.{1}-{2} -f '
        #    'filter_files/{1}-{2}.fwd -r filter_files/{1}-{2}.rev '
        #    '--model 3'.format(
        #        self.eflomal_path, self.src_lang, self.trg_lang).split())
        if src_score and trg_score:
            command = ('{0}/align.py -i {1} -F {2} -R {3} '
                '--model 3 -M 3 --priors {4}'.format(self.eflomal_path,
                    clean_file, src_score, trg_score, priors).split())
        else:
            command = ('{0}/align.py -i {1} -f {2} -r {3} '
                '--model 3'.format(self.eflomal_path, clean_file,
                    src_fwd, trg_fwd).split())

        subprocess.run(command)

    def make_priors(self, clean_file=None, src_fwd=None,
            trg_fwd=None, priors=None):
        command = ('{0}/makepriors.py -i {1} -f {2} -r {3} '
            '--priors {4}'.format(self.eflomal_path, clean_file,
                src_fwd, trg_fwd, priors).split())
        subprocess.run(command)


def create_align_input_file(sentence_pairs):
    inputfile = tempfile.NamedTemporaryFile('w+')
    for sent1, sent2 in sentence_pairs:
        inputfile.write('{} ||| {}\n'.format(sent1, sent2))
    inputfile.flush()
    return inputfile


class WordAlignFilter(FilterABC):
    """Filtering based on eflomal word aligment scores"""

    def __init__(self, src_threshold=0, tgt_threshold=0, priors=None, model=3, **kwargs):
        self.src_threshold = src_threshold
        self.tgt_threshold = tgt_threshold
        self.priors = priors
        self.model = model
        super().__init__(**kwargs)

    def _run(self, input_file, scores_fwd_file, scores_rev_file):
        """Run eflomal alignment"""
        priors_arg = '--priors {}'.format(self.priors) if self.priors else ''
        command = '{path}/align.py -i {input} -F {fwd} -R {rev} --model {model} -M {model} {priors}'.format(
            path=EFLOMAL_PATH, input=input_file, fwd=scores_fwd_file, rev=scores_rev_file,
            model=self.model, priors=priors_arg)
        subprocess.run(command.split())

    def score(self, pairs):
        input_file = create_align_input_file(pairs)
        scores_fwd_file = tempfile.NamedTemporaryFile('w+')
        scores_rev_file = tempfile.NamedTemporaryFile('w+')
        self._run(input_file.name, scores_fwd_file.name, scores_rev_file.name)
        scores_fwd_file.seek(0)
        scores_rev_file.seek(0)
        for line1, line2 in zip(scores_fwd_file, scores_rev_file):
            yield float(line1.strip()), float(line2.strip())
        input_file.close()
        scores_fwd_file.close()
        scores_rev_file.close()

    def accept(self, score):
        src, tgt = score
        return src > self.src_threshold and tgt > self.tgt_threshold

    def filter(self, pairs):
        input_file = create_align_input_file(pairs)
        scores_fwd_file = tempfile.NamedTemporaryFile('w+')
        scores_rev_file = tempfile.NamedTemporaryFile('w+')
        self._run(input_file.name, scores_fwd_file.name, scores_rev_file.name)
        input_file.seek(0)
        scores_fwd_file.seek(0)
        scores_rev_file.seek(0)
        for input_pair, line1, line2 in zip(input_file, scores_fwd_file, scores_rev_file):
            score = float(line1.strip()), float(line2.strip())
            if self.accept(score):
                sent1, sent2 = input_pair.strip().split(' ||| ')
                yield sent1, sent2
        input_file.close()
        scores_fwd_file.close()
        scores_rev_file.close()
