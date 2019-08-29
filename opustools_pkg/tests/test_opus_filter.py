import unittest
import json

from opustools_pkg.opus_filter import OpusFilter

class Args:
    def __init__(self):
        pass

class TestOpusFilter(unittest.TestCase):

    def setUp(self):
        self.args = Args()
        self.args.d = 'RF'
        self.args.s = 'en'
        self.args.t = 'sv'
        self.args.r = 'latest'
        self.args.p = 'xml'

    def test_clean_data(self):
        config = [
                {'LengthFilter': {'min_length': 5, 'max_length': 5}},
                {'LengthRatioFilter': {'threshold': 1.1}},
                {'LongWordFilter': {}},
                {'HtmlTagFilter': {}},
                {'CharacterScoreFilter': {}}
           ]

        opus_filter = OpusFilter(self.args)
        opus_filter.clean_data(config)

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

        opus_filter = OpusFilter(self.args)
        opus_filter.score_data(config)

        with open('filter_files/scores.en-sv.json') as scores_file:
            scores = json.loads(scores_file.readline())
            self.assertEqual(
                    scores[0],
                    {
                        'LanguageIDFilter': [1.0, 0.98],
                        'CharacterScoreFilter': [1.0, 1.0],
                        'TerminalPunctuationFilter': -0.0,
                        'NonZeroNumeralsFilter': 0.0}
                    )

    def test_sents_to_file(self):
        opus_filter = OpusFilter(self.args)
        opus_filter.sents_to_file()

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

