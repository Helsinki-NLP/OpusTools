"""Language model filtering"""

import argparse
import copy
import logging
import math
import tempfile

from . import FilterABC, ConfigurationError


logger = logging.getLogger(__name__)


try:
    import varikn
except ImportError:
    logger.warning("Could not load varikn, language model filtering not supported")


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
    'ccs': None,
    'wb': '<w>',
    'mb': None,
    'init_hist': 2,
    'interpolate': None,
    'filename': None
}


def get_perplexity_params(params):
    new = copy.copy(_VARIKN_PERPLEXITY_PARAMS)
    new.update(params)
    return new


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

    args.ccs = _temptokenfile(args.ccs) if args.ccs else ''
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
    lm.init_variables()
    return lm



class CrossEntropyFilter(FilterABC):

    s_beg = '<s>'
    s_end = '</s>'

    def __init__(self, src_lm_params=None, tgt_lm_params=None, perplexity=False,
                 src_threshold=50.0, tgt_threshold=50.0, diff_threshold=10.0, **kwargs):
        if not src_lm_params or not tgt_lm_params:
            raise ConfigurationError("Language model configurations need to be defined")
        if src_lm_params.get('segmentation', {}).get('type', 'char') != 'char':
            raise ConfigurationError("Only segmentation type supported currently is 'char'")
        self.src_lm_params = src_lm_params
        self.tgt_lm_params = tgt_lm_params
        self.src_lm = get_lm(**self.src_lm_params)
        self.tgt_lm = get_lm(**self.tgt_lm_params)
        self.perplexity = perplexity
        self.src_threshold = src_threshold
        self.tgt_threshold = tgt_threshold
        self.diff_threshold = diff_threshold
        super().__init__(**kwargs)

    def char_tokenize(self, sent, params):
        mb = params['mb']
        wb = params['wb']
        tokens = [self.s_beg]
        if wb:
            tokens.append(wb)
        for word in sent.strip().split():
            if mb and mb.endswith('$'):
                for char in word.replace('', mb[:-1] + ' '):
                    tokens.append(char)
            elif mb and mb.startswith('^'):
                for char in word.replace('', ' ' + mb[1:]):
                    tokens.append(char)
            else:
                tokens += list(word)
            if wb:
                tokens.append(wb)
        tokens.append(self.s_end)
        return tokens

    def accept(self, score):
        src, tgt = score
        diff = abs(src - tgt)
        return src < self.src_threshold and tgt < self.tgt_threshold and diff < self.diff_threshold

    def score(self, pairs):
        for sent1, sent2 in pairs:
            scores = []
            for lm, params, sent in [(self.src_lm, self.src_lm_params, sent1),
                                     (self.tgt_lm, self.tgt_lm_params, sent2)]:
                fullparams = get_perplexity_params(params)
                tokens = self.char_tokenize(sent, fullparams)
                use_word = fullparams['wb'] or fullparams['mb']
                scores.append(word_perplexity(lm, tokens, not self.perplexity) if use_word else \
                              token_perplexity(lm, tokens, not self.perplexity))
            yield scores
