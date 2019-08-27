"""Corpus filtering"""

import abc
import logging
import string
import math
import difflib

from langid.langid import LanguageIdentifier, model
from bs4 import BeautifulSoup as bs

from .word_alignment import WordAlignment


class ConfigurationError(Exception):
    """Configuration error for filters"""
    pass


class FilterABC(metaclass=abc.ABCMeta):
    """Abstract base class for sentence pair filters"""

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        if kwargs:
            logging.warning("Ignoring extra keyword arguments: ", kwargs)

    @abc.abstractmethod
    def score(self, pairs):
        """For each sentence pair, yield score(s)"""
        pass

    @abc.abstractmethod
    def accept(self, score):
        """Return filtering decision for score"""
        pass

    def filter(self, pairs):
        """For each sentence pair, yield True if pair is accepted, False otherwise"""
        for score in self.score(pairs):
            yield self.accept(score)


class LengthFilter(FilterABC):
    """Sentence length filter"""

    def __init__(self, min_length=1, max_length=100, unit='word', **kwargs):
        if unit not in ('word', 'char', 'character'):
            raise ConfigurationError(
                "Unit has to be either 'word', 'char', or 'character', not '%s'" % unit)
        self.min_length = min_length
        self.max_length = max_length
        self.unit = unit
        super().__init__(**kwargs)

    def score(self, pairs):
        for sent1, sent2 in pairs:
            if self.unit == 'word':
                length1 = len(sent1.split())
                length2 = len(sent2.split())
            else:
                length1 = len(sent1)
                length2 = len(sent2)
            yield length1, length2

    def accept(self, score):
        length1, length2 = score
        return (length1 >= self.min_length and length2 >= self.min_length and
                length1 <= self.max_length and length2 <= self.max_length)


class LengthRatioFilter(FilterABC):
    """Character length ratio"""

    def __init__(self, threshold=3, unit='word', **kwargs):
        if unit not in ('word', 'char', 'character'):
            raise ConfigurationError(
                "Unit has to be either 'word', 'char', or 'character', not '%s'" % unit)
        self.threshold = threshold
        self.unit = unit
        super().__init__(**kwargs)

    def score(self, pairs):
        for sent1, sent2 in pairs:
            if self.unit == 'word':
                length1 = len(sent1.split())
                length2 = len(sent2.split())
            else:
                length1 = len(sent1)
                length2 = len(sent2)
            if length1 == 0 or length2 == 0:
                yield float('inf')
            else:
                lens = sorted([length1, length2])
                yield lens[1] / lens[0]

    def accept(self, score):
        return score < self.threshold

    
class LongWordFilter(FilterABC):
    """Word length filter"""

    def __init__(self, threshold=40, **kwargs):
        self.threshold = threshold
        super().__init__(**kwargs)

    def score(self, pairs):
        for sent1, sent2 in pairs:
            longest = 0
            for w in sent1.split() + sent2.split():
                if len(w) > longest:
                    longest = len(w)
            yield longest

    def accept(self, score):
        return score < self.threshold


class HtmlTagFilter(FilterABC):
    """Html tag filter"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def score(self, pairs):
        for sent1, sent2 in pairs:
            src_tags = bool(bs(sent1, 'html.parser').find())
            tgt_tags = bool(bs(sent2, 'html.parser').find())
            yield src_tags, tgt_tags

    def accept(self, score):
        src_tags, tgt_tags = score
        return not (src_tags or tgt_tags)


class CharacterScoreFilter(FilterABC):
    """Proportion of character are in the given script"""

    def __init__(self, src_script='latin-1', tgt_script='latin-1',
            src_threshold=1, tgt_threshold=1, **kwargs):
        self.src_script = src_script
        self.tgt_script = tgt_script
        self.src_threshold = src_threshold
        self.tgt_threshold = tgt_threshold
        super().__init__(**kwargs)

    def characterScore(self, sent, script):
        total = 0
        invalid = 0
        for c in sent:
            if c not in string.whitespace and c not in string.punctuation:
                total += 1
                try:
                    c.encode(script)
                except UnicodeEncodeError:
                    invalid += 1
        if total == 0:
            return 1.0
        proper = total-invalid
        return proper/total

    def score(self, pairs):
        for sent1, sent2 in pairs:
            src_score = self.characterScore(sent1, self.src_script)
            tgt_score = self.characterScore(sent2, self.tgt_script)
            yield src_score, tgt_score

    def accept(self, score):
        src_score, tgt_score = score
        return (src_score >= self.src_threshold and
                tgt_score >= self.tgt_threshold)


class LanguageIDFilter(FilterABC):
    """Language identification confidence filter"""

    def __init__(self, src_lang=None, tgt_lang=None, src_threshold=0, tgt_threshold=0, **kwargs):
        if not (isinstance(src_lang, str) and isinstance(tgt_lang, str)):
            logging.error("Both source and target languages need to be defined")
            raise ValueError("Strings expected, got: %s %s" % (src_lang, tgt_lang))
        self.src_lang = src_lang
        self.tgt_lang = tgt_lang
        self.src_threshold = src_threshold
        self.tgt_threshold = tgt_threshold
        self.identifier = LanguageIdentifier.from_modelstring(model, norm_probs=True)
        super().__init__(**kwargs)

    def confidence(self, sentence, lan):
        try:
            lidetails = self.identifier.classify(sentence)
        except Exception as e:
            lidetails = ('un', 0.0)
        lilan, liconf = [round(x,2) if type(x) == float else x for x in lidetails]
        if lilan != lan:
            liconf = 0.0
        return liconf

    def score(self, pairs):
        for sent1, sent2 in pairs:
            src_score = self.confidence(sent1, self.src_lang)
            tgt_score = self.confidence(sent2, self.tgt_lang)
            yield src_score, tgt_score

    def accept(self, score):
        score1, score2 = score
        return score1 > self.src_threshold and score2 > self.tgt_threshold


class TerminalPunctuationFilter(FilterABC):
    """Penalty score with respect to the co-occurrence of terminal
        punctuation marks"""

    def __init__(self, threshold=-2, **kwargs):
        self.threshold = threshold
        super().__init__(**kwargs)

    def score(self, pairs):
        for sent1, sent2 in pairs:
            spun = len([c for c in sent1 if c in ['.', '?', '!']])
            tpun = len([c for c in sent2 if c in ['.', '?', '!']])
            score = abs(spun-tpun)
            if spun > 1:
                score += spun - 1
            if tpun > 1:
                score += tpun - 1
            score = -math.log(score + 1)
            yield score

    def accept(self, score):
        return score >= self.threshold


class NonZeroNumeralsFilter(FilterABC):
    """Similarity measure between numerals of the two sentences with
        zeros removed"""

    def __init__(self, threshold=0.5, **kwargs):
        self.threshold = threshold
        super().__init__(**kwargs)

    def score(self, pairs):
        for sent1, sent2 in pairs:
            snums = [int(c) for c in sent1 if c in string.digits and c != '0']
            tnums = [int(c) for c in sent2 if c in string.digits and c != '0']
            seq = difflib.SequenceMatcher(None, snums, tnums)
            yield seq.ratio()

    def accept(self, score):
        return score >= self.threshold
