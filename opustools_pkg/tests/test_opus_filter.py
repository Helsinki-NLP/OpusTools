import unittest
import argparse
import json

from opustools_pkg.opus_filter import OpusFilter
from opustools_pkg.filter import lm

class TestOpusFilter(unittest.TestCase):

    def setUp(self):
        self.args = argparse.Namespace()
        self.args.d = 'RF'
        self.args.s = 'en'
        self.args.t = 'sv'
        self.args.r = 'latest'
        self.args.p = 'xml'
        self.opus_filter = OpusFilter(self.args)
        self.opus_filter.sents_to_file()

    def test_clean_data(self):
        config = [
                {'LengthFilter': {'min_length': 5, 'max_length': 5}},
                {'LengthRatioFilter': {'threshold': 1.1}},
                {'LongWordFilter': {}},
                {'HtmlTagFilter': {}},
                {'CharacterScoreFilter': {}}
           ]

        self.opus_filter.clean_data(config)

        with open('filter_files/clean.en-sv') as clean:
            self.assertEqual(
                    clean.readlines(),
                    ['Welfare presupposes fair distribution . ||| '
                    'Kommunerna får stabila spelregler .\n']
                    )

    def test_score_data(self):
        config = [
                {'LanguageIDFilter': {'src_lang': 'en', 'tgt_lang': 'sv'}},
                {'CharacterScoreFilter': {}},
                {'TerminalPunctuationFilter': {}},
                {'NonZeroNumeralsFilter': {}}
               ]

        self.opus_filter.score_data(config)

        with open('filter_files/scores.en-sv.json') as scores_file:
            scores = json.loads(scores_file.readline())
            self.assertEqual(
                    scores[0],
                    {'LanguageIDFilter': [1.0, 0.98],
                        'CharacterScoreFilter': [1.0, 1.0],
                        'TerminalPunctuationFilter': -0.0,
                        'NonZeroNumeralsFilter': 0.0}
                    )

    def test_make_bpe(self):
        train_file = 'filter_files/sents.en'
        input_file = 'filter_files/sents.en'
        output_file = 'filter_files/sents.en.bpe'
        self.opus_filter.make_bpe(train_file, input_file, output_file)
        with open('filter_files/sents.en.bpe') as bped_file:
            bped_lines = bped_file.readlines()
            self.assertEqual(len(bped_lines), 180)
            self.assertEqual(
                bped_lines[0],
                ('St@@ at@@ ement of Government Policy by the P@@ rime '
                'M@@ ini@@ st@@ er , Mr In@@ g@@ v@@ ar C@@ ar@@ l@@ '
                's@@ son , at the O@@ pen@@ ing of the Swedish Parliament '
                'on T@@ u@@ es@@ day , 4 O@@ c@@ to@@ b@@ er , 198@@ 8 .\n')
                )

    def test_segment_line(self):
        line = self.opus_filter.segment_line(
                ('St@@ at@@ ement of Government Policy by the P@@ rime '
                'M@@ ini@@ st@@ er , Mr In@@ g@@ v@@ ar C@@ ar@@ l@@ '
                's@@ son , at the O@@ pen@@ ing of the Swedish Parliament '
                'on T@@ u@@ es@@ day , 4 O@@ c@@ to@@ b@@ er , 198@@ 8 .\n')
                )
        self.assertEqual(
                line,
                ('<s> <w> St@@ at@@ ement <w> of <w> Government <w> Policy '
                '<w> by <w> the <w> P@@ rime <w> M@@ ini@@ st@@ er <w> , '
                '<w> Mr <w> In@@ g@@ v@@ ar <w> C@@ ar@@ l@@ s@@ son <w> , '
                '<w> at <w> the <w> O@@ pen@@ ing <w> of <w> the <w> '
                'Swedish <w> Parliament <w> on <w> T@@ u@@ es@@ day <w> , '
                '<w> 4 <w> O@@ c@@ to@@ b@@ er <w> , <w> 198@@ 8 <w> . <w> '
                '</s> \n')
                )
        line = self.opus_filter.segment_line(
                ('Statement of Government Policy by the Prime Minister , '
                'Mr Ingvar Carlsson , at the Opening of the Swedish '
                'Parliament on Tuesday , 4 October , 1988 .\n')
                )
        self.assertEqual(
                line,
                ('<s> <w> Statement <w> of <w> Government <w> Policy <w> '
                'by <w> the <w> Prime <w> Minister <w> , <w> Mr <w> Ingvar '
                '<w> Carlsson <w> , <w> at <w> the <w> Opening <w> of <w> '
                'the <w> Swedish <w> Parliament <w> on <w> Tuesday <w> , '
                '<w> 4 <w> October <w> , <w> 1988 <w> . <w> </s> \n')
                )

    def test_segment_file(self):
        train_file = 'filter_files/sents.en'
        input_file = 'filter_files/sents.en'
        output_file = 'filter_files/sents.en.bpe'
        self.opus_filter.make_bpe(train_file, input_file, output_file)
        self.opus_filter.segment_file(
                'filter_files/sents.en.bpe',
                'filter_files/sents.en.bpe.seg'
                )
        with open('filter_files/sents.en.bpe.seg') as output_file:
            seg_lines = output_file.readlines()
            self.assertEqual(len(seg_lines), 180)
            self.assertEqual(
                    seg_lines[0],
                    ('<s> <w> St@@ at@@ ement <w> of <w> Government <w> '
                    'Policy <w> by <w> the <w> P@@ rime <w> M@@ ini@@ st@@ '
                    'er <w> , <w> Mr <w> In@@ g@@ v@@ ar <w> C@@ ar@@ l@@ '
                    's@@ son <w> , <w> at <w> the <w> O@@ pen@@ ing <w> of '
                    '<w> the <w> Swedish <w> Parliament <w> on <w> T@@ u@@ '
                    'es@@ day <w> , <w> 4 <w> O@@ c@@ to@@ b@@ er <w> , <w> '
                    '198@@ 8 <w> . <w> </s> \n')
                    )
        self.opus_filter.segment_file(
                'filter_files/sents.en',
                'filter_files/sents.en.seg'
                )
        with open('filter_files/sents.en.seg') as output_file:
            seg_lines = output_file.readlines()
            self.assertEqual(len(seg_lines), 180)
            self.assertEqual(
                    seg_lines[0],
                    ('<s> <w> Statement <w> of <w> Government <w> Policy <w> '
                    'by <w> the <w> Prime <w> Minister <w> , <w> Mr <w> Ingvar '
                    '<w> Carlsson <w> , <w> at <w> the <w> Opening <w> of <w> '
                    'the <w> Swedish <w> Parliament <w> on <w> Tuesday <w> , '
                    '<w> 4 <w> October <w> , <w> 1988 <w> . <w> </s> \n')
                    )

    def test_sents_to_file(self):
        with open('filter_files/sents.en') as sents_file_en:
            with open('filter_files/sents.sv') as sents_file_sv:
                sents_en = sents_file_en.readlines()
                sents_sv = sents_file_sv.readlines()
                self.assertEqual(len(sents_en), 180)
                self.assertEqual(len(sents_sv), 180)
                self.assertEqual(
                        sents_en[0],
                        ('Statement of Government Policy by the Prime '
                        'Minister , Mr Ingvar Carlsson , at the Opening '
                        'of the Swedish Parliament on Tuesday , 4 October '
                        ', 1988 .\n')
                        )
                self.assertEqual(sents_sv[0], 'REGERINGSFÖRKLARING .\n')

