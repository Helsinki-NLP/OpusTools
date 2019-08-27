import sys

from . import LengthRatioFilter, LanguageIDFilter, \
    LengthFilter, LongWordFilter, HtmlTagFilter, CharacterScoreFilter, \
    TerminalPunctuationFilter, NonZeroNumeralsFilter#, CleanCorpusN

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
        scores = []
        num = 0
        for f in self.filters:
            filter_gen = f.score(pairs)
            scores.append([])
            for score in filter_gen:
                scores[num].append((f.__class__.__name__, score))
            num += 1

        entries = []
        for i in range(len(scores[0])):
            entry = {}
            for j in range(len(scores)):
                entry[scores[j][i][0]] = scores[j][i][1]
            entries.append(entry)

        return entries


