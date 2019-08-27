import sys

from . import LengthRatioFilter, LanguageIDFilter, \
    LongSentenceFilter, LongWordFilter, HtmlTagFilter, CharacterScoreFilter, \
    TerminalPunctuationFilter, NonZeroNumeralsFilter, CleanCorpusN

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

