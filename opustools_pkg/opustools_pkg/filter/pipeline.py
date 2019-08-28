import sys

from . import LengthRatioFilter, LanguageIDFilter, \
    LengthFilter, LongWordFilter, HtmlTagFilter, CharacterScoreFilter, \
    TerminalPunctuationFilter, NonZeroNumeralsFilter
from .lm import CrossEntropyFilter
from .word_alignment import WordAlignFilter

class FilterPipeline:

    def __init__(self):
        self.filters = []

    @classmethod
    def from_config(cls, config):
        pipeline = cls()
        for f in config:
            name = next(iter(f.keys()))
            attributes = f[name]
            filter_ = getattr(sys.modules[__name__], name)
            pipeline.filters.append(filter_(**attributes))

        return pipeline

    def score(self, pairs):
        scores = [{} for p in range(len(pairs))]
        for f in self.filters:
            num = 0
            filter_gen = f.score(pairs)
            for sco in filter_gen:
                scores[num][f.__class__.__name__] = sco
                num += 1

        return scores


