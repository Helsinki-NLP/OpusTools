import os
import argparse
import json

from yaml import load, Loader

from . import OpusRead

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
        parser.add_argument('-f', help='yaml file to specify filters',
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

        with open(args.f) as yaml_file:
            filters = load(yaml_file, Loader=Loader)

        get_sents = OpusGetSents('-d {0} -s {1} -t {2} -r {3} -p {4} -wm '
            'moses -w filter_files/temp filter_files/temp -ln'.format(
                args.d, args.s, args.t, args.r, args.p).split())

        get_sents.printPairs()

        self.sents = get_sents.sents

    def clean_data(self):
        clean_file= open('filter_files/clean.{0}-{1}'.format(
            self.fromto[0], self.fromto[1]), 'w')
        for pair in self.sents:
            ssent, tsent = pair[0][:-1], pair[1][:-1]
            if (self.lengthRatioFilter.filter(ssent, tsent) and
                    self.longSentenceFilter.filter(ssent, tsent) and
                    self.longWordFilter.filter(ssent, tsent) and
                    self.htmlTagFilter.filter(ssent, tsent) and
                    self.characterScoreFilter.filter(ssent, tsent)):
                clean_file.write('{0} ||| {1}\n'.format(ssent, tsent))
        clean_file.close()

    def filter(self):
        source_file = open('filter_files/sents.{}'.format(self.fromto[0]), 'w')
        target_file = open('filter_files/sents.{}'.format(self.fromto[1]), 'w')

        scores = {}
        number = 0
        for pair in self.sents:
            number += 1
            ssent, tsent = pair[0][:-1], pair[1][:-1]
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
                #'clean-corpus': self.cleanCorpusN.score(ssent, tsent)
                }
            scores[number] = entry
        source_file.close()
        target_file.close()

        score_file = open('filter_files/scores.{0}-{1}.json'.format(
            self.fromto[0], self.fromto[1]) , 'w')
        score_file.write(json.dumps(scores))
        score_file.close()

    def word_alignment_score(self):
        self.wordAlignment.align(
                clean_file='filter_files/clean.{0}-{1}'.format(
                    self.fromto[0], self.fromto[1]),
                src_fwd='filter_files/{0}-{1}.fwd'.format(self.fromto[0],
                    self.fromto[1]),
                trg_fwd='filter_files/{0}-{1}.rev'.format(self.fromto[0],
                    self.fromto[1])
            )
        self.wordAlignment.make_priors(
                clean_file='filter_files/clean.{0}-{1}'.format(
                    self.fromto[0], self.fromto[1]),
                src_fwd='filter_files/{0}-{1}.fwd'.format(self.fromto[0],
                    self.fromto[1]),
                trg_fwd='filter_files/{0}-{1}.rev'.format(self.fromto[0],
                    self.fromto[1]),
                priors='filter_files/{0}-{1}.priors'.format(self.fromto[0],
                    self.fromto[1])
            )
        self.wordAlignment.align(
                clean_file='filter_files/clean.{0}-{1}'.format(
                    self.fromto[0], self.fromto[1]),
                src_score='filter_files/{0}-{1}.fwd'.format(self.fromto[0],
                    self.fromto[1]),
                trg_score='filter_files/{0}-{1}.rev'.format(self.fromto[0],
                    self.fromto[1]),
                priors='filter_files/{0}-{1}.priors'.format(self.fromto[0],
                    self.fromto[1])
            )



