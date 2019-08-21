import os
import argparse

from opustools_pkg import OpusGetSents
from opustools_pkg.filter import LengthRatioFilter, LanguageIDFilter, \
    LongSentenceFilter, LongWordFilter, HtmlTagFilter, CharacterScoreFilter, \
    TerminalPunctuationFilter, NonZeroNumeralsFilter

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

        try:
            os.mkdir('filter_files')
        except FileExistsError:
            pass

        self.source_file = open('filter_files/sents.{}'.format(fromto[0]), 'w')
        self.target_file = open('filter_files/sents.{}'.format(fromto[1]), 'w')
        self.score_file = open('filter_files/scores.{0}-{1}'.format(
            fromto[0], fromto[1]) , 'w')
        self.clean_file = open('filter_files/clean.{0}-{1}'.format(
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

        get_sents = OpusGetSents('-d {0} -s {1} -t {2} -r {3} -p {4} -wm '
            'moses -w filter_files/temp filter_files/temp -ln'.format(
                args.d, args.s, args.t, args.r, args.p).split())

        get_sents.printPairs()

        self.sents = get_sents.sents

    def filter(self):
        for pair in self.sents:
            ssent, tsent = pair[0][:-1], pair[1][:-1]
            print(self.lengthRatioFilter.score(ssent, tsent))
            print(self.languageIDFilter.score(ssent, tsent))
            print(self.longSentenceFilter.score(ssent, tsent))
            print(self.longWordFilter.score(ssent, tsent))
            print(self.htmlTagFilter.score(ssent, tsent))
            print(self.characterScoreFilter.score(ssent, tsent))
            print(self.terminalPunctuationFilter.score(ssent, tsent))
            print(self.nonZeroNumeralsFilter.score(ssent, tsent))
            print(ssent, tsent)

of = OpusFilter()
of.filter()

