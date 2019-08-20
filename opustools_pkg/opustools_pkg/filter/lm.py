"""Language model filtering"""

import argparse
import logging
import math
import tempfile

from . import FilterABC


logger = logging.getLogger(__name__)


try:
    import varikn
except ImportError:
    logger.warning("Could not load varikn, language model filtering not supported")


class ConfigurationError(Exception):
    """Configuration error"""
    pass


_VARIKN_TRAINING_PARAMS = {
    'optdata': '',
    'norder': 0,
    'dscale': 0.001,
    'dscale2': 0,
    'arpa': True,
    'use_3nzer': False,
    'absolute': False,
    'cutoffs': '0 0 1'
}


# FIXME: replace args with the actual arguments
def train(args):
    vg = varikn.VarigramTrainer(args.use_3nzer, args.absolute)
    vg.set_datacost_scale(args.dscale)
    vg.set_datacost_scale2(args.dscale2)
    if args.norder > 0:
        vg.set_max_order(args.norder)
    # vg->initialize(infilename, hashs, ndrop, nfirst, optiname, "<s>", smallmem, vocabname);
    vg.initialize(args.data, 0, 0, -1, args.optdata, '<s>', False, '')
    vg.set_cutoffs([int(x) for x in args.cutoffs.split()])
    vg.grow(1)
    vg.write_file(args.model, args.arpa)


def token_perplexity(lm, tokens, entropy=False):
    """Calculate token perplexity for sentence tokens"""
    lpsum = 0.0
    for token in tokens:
        lpsum += lm.token_logprob(token)
    if entropy:
        ppl = -lpsum / lm.processed_tokens() / math.log10(2)
    else:
        ppl = 10**(-lpsum / lm.processed_tokens())
    lm.clear_history()
    lm.init_variables()
    return ppl


def word_perplexity(lm, tokens, entropy=False):
    """Calculate word perplexity for sentence tokens"""
    lpsum = 0.0
    for token in tokens:
        lpsum += lm.word_logprob(token)
    if entropy:
        ppl = -lpsum / lm.processed_words() / math.log10(2)
    else:
        ppl = 10**(-lpsum / lm.processed_words())
    lm.clear_history()
    lm.init_variables()
    return ppl


_VARIKN_PERPLEXITY_PARAMS = {
    'arpa': True,
    'unk': '<UNK>',
    'include_unks': False,
    'css': None,
    'wb': ['<w>'],
    'mb': None,
    'init_hist': 2,
    'interpolate': None,
    'filename': None
}


def _temptokenfile(item):
    _, tmpfname = tempfile.mkstemp()
    with open(tmpfname, 'w') as fobj:
        fobj.write("{}\n".format(item))
    return tmpfname


def get_lm(**kwargs):
    """Return language model initialized for perplexity calculation"""

    args = argparse.Namespace()
    for key, default in _VARIKN_PERPLEXITY_PARAMS.items():
        setattr(args, key, kwargs.get(key, default))

    args.css = _temptokenfile(args.ccs) if args.css else ''
    args.wb = _temptokenfile(args.wb) if args.wb else ''
    args.mb = _temptokenfile(args.mb) if args.mb else ''

    if args.interpolate:
        lms = [args.filename] + [x[1] for x in args.interpolate]
        wsum = sum(float(x[0]) for x in args.interpolate)
        if wsum >= 1:
            logger.warning("Weights are too high!")
        weights = [1 - wsum] + [float(x[0]) for x in args.interpolate]
        tg = varikn.InterTreeGram(lms, weights)
        lm = varikn.Perplexity(tg, args.ccs, args.wb, args.mb, args.unk, not args.include_unks)
    else:
        lm = varikn.Perplexity(
            args.filename, 0 if args.arpa else 1,
            args.ccs, args.wb, args.mb, args.unk, 0, not args.include_unks)
    lm.set_init_hist(args.init_hist)
    return lm



class CrossEntropyFilter(FilterABC):

    s_beg = '<s>'
    s_end = '</s>'

    def __init__(self, src_lm_params=None, tgt_lm_params=None, perplexity=False, threshold=50.0, **kwargs):
        if src_lm_params.get('segmentation', {}).get('type', 'char') != 'char':
            raise ConfigurationError("Only segmentation type supported currently is 'char'")
        self.src_lm_params = src_lm_params
        self.tgt_lm_params = tgt_lm_params
        self.src_lm = get_lm(self.src_lm_params)
        self.tgt_lm = get_lm(self.tgt_lm_params)
        self.perplexity = perplexity
        self.threshold = threshold
        super().__init__(kwargs)

    def char_tokenize(self, sent, params):
        tokens = [s_beg]
        if params['wb']:
            tokens.append(params['wb'])
        for word in sent.strip().split():
            if params['mb'] and params['mb'].endswith('$'):
                for char in word.replace('', params['mb'][:-1] + ' '):
                    tokens.append(char)
            elif params['mb'] and params['mb'].startswith('^'):
                for char in word.replace('', ' ' + params['mb'][1:]):
                    tokens.append(char)
            else:
                tokens += list(word)
            if params['wb']:
                tokens.append(params['wb'])
        tokens.append(s_end)
        return tokens

    def filter(self, sent1, sent2):
        return self.score(sent1, sent2) > self.threshold

    def score(self, sent1, sent2):
        for lm, params, sent in [(self.src_lm, self.src_lm_params, sent1),
                                 (self.src_lm, self.src_lm_params, sent1)]:
            tokens = self.char_tokenize(sent, params)
            use_word = params['wb'] or params['mb']
            return word_perplexity(lm, tokens, not self.perplexity) if use_word else \
                token_perplexity(lm, tokens, not self.perplexity)
