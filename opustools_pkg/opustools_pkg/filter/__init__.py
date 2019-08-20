"""Corpus filtering"""

import abc
import logging

from langid.langid import LanguageIdentifier, model


class FilterABC(metaclass=abc.ABCMeta):
    """Abstract base class for sentence pair filters"""

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        if kwargs:
            logging.warning("Ignoring extra keyword arguments: ", kwargs)

    @abc.abstractmethod
    def filter(self, sent1, sent2):
        """Return True if pair is accepted, False otherwise"""
        pass

    @abc.abstractmethod
    def score(self, sent1, sent2):
        """Return score for the sentence pair"""
        pass


class LengthRatioFilter(FilterABC):
    """Character length ratio (0 < score < 1)"""

    def __init__(self, threshold=3, **kwargs):
        self.threshold = threshold
        super().__init__(**kwargs)

    def score(self, sent1, sent2):
        lens = sorted([len(sent1), len(sent2)])
        return lens[1] / lens[0]

    def filter(self, sent1, sent2):
        return self.score(sent1, sent2) < self.threshold


class LanguageIDFilter(FilterABC):
    """Language identification confidence filter"""

    def __init__(self, src_lang=None, tgt_lang=None, threshold=0, **kwargs):
        if not (isinstance(src_lang, str) and isinstance(tgt_lang, str)):
            logging.error("Both source and target languages need to be defined")
            raise ValueError("Strings expected, got: %s %s" % (src_lang, tgt_lang))
        self.threshold = threshold
        self.identifier = LanguageIdentifier.from_modelstring(model, norm_probs=True)
        super().__init__(**kwargs)

    def score(self, sent1, sent2):
        try:
            lidetails = self.identifier.classify(sentence)
        except Exception as e:
            lidetails = ('un', 0.0)
        lilan, liconf = [str(round(x,2)) if type(x) == float else x for x in lidetails]
        if lilan != lan:
            liconf = 0.0
        return liconf

    def filter(self, sent1, sent2):
        return self.score(sent1, sent2) > self.threshold

