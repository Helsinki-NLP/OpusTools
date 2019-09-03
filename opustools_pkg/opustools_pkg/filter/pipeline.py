"""Filter pipeline"""

import itertools
import sys

from . import LengthRatioFilter, LanguageIDFilter, \
    LengthFilter, LongWordFilter, HtmlTagFilter, CharacterScoreFilter, \
    TerminalPunctuationFilter, NonZeroNumeralsFilter
from .lm import CrossEntropyFilter
from .word_alignment import WordAlignFilter


def grouper(iterable, n):
    """Split data into fixed-length chunks"""
    it = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(it, n))
        if not chunk:
            return
        yield chunk


class FilterPipeline:
    """Pipeline for combining multiple filters"""

    def __init__(self, filters=None):
        self.filters = [] if filters is None else filters
        self._chunksize = 10000

    @classmethod
    def from_config(cls, config):
        """Initilize filter pipeline from configuration dictionary"""
        pipeline = cls()
        for f in config:
            name = next(iter(f.keys()))
            attributes = f[name]
            filter_ = getattr(sys.modules[__name__], name)
            pipeline.filters.append(filter_(**attributes))
        return pipeline
        
    def score(self, pairs):
        """Yield dictionaries of filter scores for sentence pairs"""
        fnames = [f.__class__.__name__ for f in self.filters]
        for chunk in grouper(pairs, self._chunksize):
            for scores in zip(*[f.score(chunk) for f in self.filters]):
                yield {fnames[idx]: score for idx, score in enumerate(scores)}

    def filter(self, pairs):
        """Yield sentence pairs accepted by all filters"""
        for f in self.filters:
            pairs = f.filter(pairs)
        return pairs
