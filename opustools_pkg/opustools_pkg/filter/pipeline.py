import sys

from . import LengthRatioFilter, LanguageIDFilter, \
    LengthFilter, LongWordFilter, HtmlTagFilter, CharacterScoreFilter, \
    TerminalPunctuationFilter, NonZeroNumeralsFilter
from .lm import CrossEntropyFilter
from .word_alignment import WordAlignFilter


class FilterPipeline:
    """Pipeline for combining multiple filters"""

    def __init__(self, filters=None):
        self.filters = [] if filters is None else filters

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
        """Return dictionary of filter scores for a list of sentence pairs"""
        scores = [{} for p in range(len(pairs))]
        for f in self.filters:
            num = 0
            filter_gen = f.score(pairs)
            for score in filter_gen:
                scores[num][f.__class__.__name__] = score
                num += 1
        return scores

    def filter(self, pairs):
        """Yield sentence pairs accepted by all filters"""
        for f in self.filters:
            pairs = f.filter(pairs)
        return pairs
