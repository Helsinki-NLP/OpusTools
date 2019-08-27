import sys

from yaml import load, Loader

from . import LengthRatioFilter, LanguageIDFilter, \
    LongSentenceFilter, LongWordFilter, HtmlTagFilter, CharacterScoreFilter, \
    TerminalPunctuationFilter, NonZeroNumeralsFilter, CleanCorpusN

class FilterPipeline:

    def __init__(self):
        pass

    @classmethod
    def from_config(cls, config):
        pipeline = cls()
        cls.filters = []
        with open(config) as conf_file:
            filter_list = load(conf_file, Loader=Loader)
        for f in filter_list:
            name, attributes = f.popitem()
            filter_ = getattr(sys.modules[__name__], name)
            cls.filters.append(filter_(**attributes))

        return pipeline

