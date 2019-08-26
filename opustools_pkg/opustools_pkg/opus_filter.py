import os
import argparse
import json

from . import OpusRead
from .filter import LengthRatioFilter, LanguageIDFilter, \
    LongSentenceFilter, LongWordFilter, HtmlTagFilter, CharacterScoreFilter, \
    TerminalPunctuationFilter, NonZeroNumeralsFilter, CleanCorpusN, \
    WordAlignment

class OpusGetSents(OpusRead):

    def __init__(self, arguments):
        super().__init__(arguments)
        self.sents = []

    def sendPairOutput(self, wpair):
        self.sents.append(wpair)

class OpusFilter:

    def __init__(self):
        parser = argparse.ArgumentParser(prog='opus_filter',
            description='Filter OPUS bitexts')

        parser.add_argument('-d', help='Corpus name', metavar='corpus_name',
            required=True)
        parser.add_argument('-s', help='Source language', metavar='langid',
            required=True)
        parser.add_argument('-t', help='Target language', metavar='langid',
            required=True)
        parser.add_argument('-r', help='Release (default=latest)',
            metavar='version',
            default='latest')
        parser.add_argument('-p',
            help='Pre-process-type (raw, xml or parsed, default=xml)',
            default='xml', choices=['raw', 'xml', 'parsed'])

        args = parser.parse_args()
        fromto = sorted([args.s, args.t])
        self.fromto = fromto

        try:
            os.mkdir('filter_files')
        except FileExistsError:
            pass

        self.source_file = open('filter_files/sents.{}'.format(fromto[0]), 'w')
        self.target_file = open('filter_files/sents.{}'.format(fromto[1]), 'w')
        self.source_clean= open('filter_files/clean.{}'.format(fromto[0]), 'w')
        self.target_clean= open('filter_files/clean.{}'.format(fromto[1]), 'w')
        self.score_file = open('filter_files/scores.{0}-{1}.json'.format(
            fromto[0], fromto[1]) , 'w')

        self.lengthRatioFilter = LengthRatioFilter()
        self.languageIDFilter = LanguageIDFilter(
            src_lang=fromto[0], tgt_lang=fromto[1])
        self.longSentenceFilter = LongSentenceFilter()
        self.longWordFilter = LongWordFilter()
        self.htmlTagFilter = HtmlTagFilter()
        self.characterScoreFilter = CharacterScoreFilter()
        self.terminalPunctuationFilter = TerminalPunctuationFilter()
        self.nonZeroNumeralsFilter = NonZeroNumeralsFilter()
        self.cleanCorpusN = CleanCorpusN()
        self.wordAlignment = WordAlignment(eflomal_path='/home/mikko/eflomal')

        get_sents = OpusGetSents('-d {0} -s {1} -t {2} -r {3} -p {4} -wm '
            'moses -w filter_files/temp filter_files/temp -ln'.format(
                args.d, args.s, args.t, args.r, args.p).split())

        get_sents.printPairs()

        self.sents = get_sents.sents

    def filter(self):
        scores = {}
        number = 0
        for pair in self.sents:
            number += 1
            ssent, tsent = pair[0][:-1], pair[1][:-1]
            if (self.lengthRatioFilter.filter(ssent, tsent) and
                    self.longSentenceFilter.filter(ssent, tsent) and
                    self.longWordFilter.filter(ssent, tsent) and
                    self.htmlTagFilter.filter(ssent, tsent) and
                    self.characterScoreFilter.filter(ssent, tsent)):
                self.source_clean.write('{}\n'.format(ssent))
                self.target_clean.write('{}\n'.format(tsent))
            src_langid, tgt_langid = self.languageIDFilter.score(ssent, tsent)
            src_charscore, tgt_charscore = self.characterScoreFilter.score(
                ssent, tsent)
            entry = {
                'src': ssent,
                'tgt': tsent,
                'src_lang-id': src_langid,
                'tgt_lang-id': tgt_langid,
                'src_char-score': src_charscore,
                'tgt_char-score': tgt_charscore,
                'term-punct':
                    self.terminalPunctuationFilter.score(ssent, tsent),
                'non-zero': self.nonZeroNumeralsFilter.score(ssent, tsent),
                'clean-corpus': self.cleanCorpusN.score(ssent, tsent)
                }
            scores[number] = entry
        self.score_file.write(json.dumps(scores))
        self.source_file.close()
        self.target_file.close()
        self.score_file.close()
        self.source_clean.close()
        self.target_clean.close()

    def word_alignment_score(self):
        self.wordAlignment.align(
                src_file='filter_files/clean.{}'.format(self.fromto[0]),
                trg_file='filter_files/clean.{}'.format(self.fromto[1]),
                src_fwd='filter_files/{0}-{1}.fwd'.format(self.fromto[0],
                    self.fromto[1]),
                trg_fwd='filter_files/{0}-{1}.rev'.format(self.fromto[0],
                    self.fromto[1])
            )
        self.wordAlignment.make_priors(
                src_file='filter_files/clean.{}'.format(self.fromto[0]),
                trg_file='filter_files/clean.{}'.format(self.fromto[1]),
                src_fwd='filter_files/{0}-{1}.fwd'.format(self.fromto[0],
                    self.fromto[1]),
                trg_fwd='filter_files/{0}-{1}.rev'.format(self.fromto[0],
                    self.fromto[1]),
                priors='filter_files/{0}-{1}.priors'.format(self.fromto[0],
                    self.fromto[1])
            )
        self.wordAlignment.align(
                src_file='filter_files/clean.{}'.format(self.fromto[0]),
                trg_file='filter_files/clean.{}'.format(self.fromto[1]),
                src_score='filter_files/{0}-{1}.fwd'.format(self.fromto[0],
                    self.fromto[1]),
                trg_score='filter_files/{0}-{1}.rev'.format(self.fromto[0],
                    self.fromto[1]),
                priors='filter_files/{0}-{1}.priors'.format(self.fromto[0],
                    self.fromto[1])
            )



