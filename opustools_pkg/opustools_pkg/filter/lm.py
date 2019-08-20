"""Language model filtering"""

import argparse
import logging
import math


logger = logging.getLogger(__name__)


try:
    import varikn
except ImportError:
    logger.warning("Could not load varikn, language model filtering not supported")


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


# FIXME: replace args with the actual arguments
def get_lm(args):
    """Return language model initialized for perplexity calculation"""
    if args.interpolate:
        lms = [args.model.name] + [x[1] for x in args.interpolate]
        wsum = sum(float(x[0]) for x in args.interpolate)
        if wsum >= 1:
            logger.warning("Weights are too high!")
        weights = [1 - wsum] + [float(x[0]) for x in args.interpolate]
        tg = varikn.InterTreeGram(lms, weights)
        lm = varikn.Perplexity(tg, args.ccs, args.wb, args.mb, args.unk, not args.include_unks)
    else:
        lm = varikn.Perplexity(
            args.model.name, 0 if args.arpa else 1,
            args.ccs, args.wb, args.mb, args.unk, 0, not args.include_unks)
    lm.set_init_hist(args.init_hist)
    return lm


# FIXME: replace args with the actual arguments
def evaluate(args):
    lm = get_lm(args)
    use_word = args.wb or args.mb
    for line in args.input:
        tokens = line.strip().split()
        ppl = word_perplexity(lm, tokens, args.entropy) if use_word else token_perplexity(lm, tokens, args.entropy)
        args.output.write("%.6f\n" % ppl)


# FIXME: replace args with the actual arguments
def train(args):
    vg = varikn.VarigramTrainer(args.use_3nzer, args.absolute)
    vg.set_datacost_scale(args.dscale)
    vg.set_datacost_scale2(args.dscale2)
    if args.norder > 0:
        vg.set_max_order(args.norder)
    #vg->initialize(infilename, hashs, ndrop, nfirst, optiname, "<s>", smallmem, vocabname);
    vg.initialize(args.data.name, 0, 0, -1, args.optdata, '<s>', False, '');
    vg.set_cutoffs([int(x) for x in args.cutoffs.split()])
    vg.grow(1);
    vg.write_file(args.model.name, args.arpa);
