import unittest
import json
import argparse
import os

from opustools_pkg.opus_filter import OpusFilter
from opustools_pkg.filter import lm

class TestOpusFilter(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        configuration = {'output_directory': 'filter_files',
            'corpora': {'RF1': {'type': 'OPUS',
              'parameters': {'corpus_name': 'RF',
               'source_language': 'en',
               'target_language': 'sv',
               'release': 'latest',
               'preprocessing': 'xml',
               'src_filename': 'RF1_sents.en',
               'tgt_filename': 'RF1_sents.sv'}}},
              'filtering': {'RF1': {'src_input': 'RF1_sents.en',
              'tgt_input': 'RF1_sents.sv',
              'src_output': 'RF1_filtered.en',
              'tgt_output': 'RF1_filtered.sv',
              'filters': [{'LanguageIDFilter': {'src_lang': 'en',
                 'tgt_lang': 'sv',
                 'src_threshold': 0,
                 'tgt_threshold': 0}},
               {'TerminalPunctuationFilter': {'threshold': -2}},
               {'NonZeroNumeralsFilter': {'threshold': 0.5}},
               {'CharacterScoreFilter': {'src_script': 'latin-1',
                 'tgt_script': 'latin-1',
                 'src_threshold': 1,
                 'tgt_threshold': 1}}]}},
            'models': [{'type': 'ngram',
              'data': 'RF1_filtered.en',
              'language': 'en',
              'parameters': {'segmentation': {'type': 'char'},
               'norder': 20,
               'dscale': 0.001},
              'model': 'RF1_en.arpa'},
             {'type': 'ngram',
              'data': 'RF1_filtered.sv',
              'language': 'sv',
              'parameters': {'segmentation': {'type': 'char'},
               'norder': 20,
               'dscale': 0.001},
              'model': 'RF1_sv.arpa'},
             {'type': 'alignment',
              'src_data': 'RF1_filtered.en',
              'tgt_data': 'RF1_filtered.sv',
              'parameters': {'model': 3},
              'output': 'RF1_align.priors'}],
            'scoring': {'RF1': {'src_input': 'RF1_sents.en',
              'tgt_input': 'RF1_sents.sv',
              'output': 'RF1_scores.en-sv.jsonl',
              'filters': [{'LanguageIDFilter': {'src_lang': 'en',
                 'tgt_lang': 'sv',
                 'src_threshold': 0,
                 'tgt_threshold': 0}},
               {'TerminalPunctuationFilter': {'threshold': -2}},
               {'NonZeroNumeralsFilter': {'threshold': 0.5}},
               {'CharacterScoreFilter': {'src_script': 'latin-1',
                 'tgt_script': 'latin-1',
                 'src_threshold': 1,
                 'tgt_threshold': 1}},
               {'WordAlignFilter': {'priors': 'RF1_align.priors',
                 'model': 3,
                 'src_threshold': 0,
                 'tgt_threshold': 0}},
               {'CrossEntropyFilter': {'src_lm_params':
                   {'segmentation': {'type': 'char'},
                  'filename': 'RF1_en.arpa'},
                 'tgt_lm_params': {'segmentation': {'type': 'char'},
                  'filename': 'RF1_sv.arpa'},
                 'src_threshold': 50.0,
                 'tgt_threshold': 50.0,
                 'diff_threshold': 10.0}}]}}}

        self.opus_filter = OpusFilter(configuration)
        self.opus_filter.clean_data()
        self.opus_filter.train_models()

    def test_get_pairs(self):
        pair_gen = self.opus_filter.get_pairs('RF1_sents.en', 'RF1_sents.sv')
        pair = next(pair_gen)
        for pair in pair_gen:
            pass
        self.assertEqual(pair,
                ('This will ensure the cohesion of Swedish society .',
                'Så kan vi hålla samman Sverige .'))

    def test_clean_data(self):
        with open('filter_files/RF1_filtered.en') as clean:
            self.assertEqual(
                    clean.readline(),
                    'Your Majesties , Your Royal Highnesses , Mr Speaker , '
                    'Members of the Swedish Parliament .\n'
                    )
        with open('filter_files/RF1_filtered.sv') as clean:
            self.assertEqual(
                    clean.readline(),
                    'Eders Majestäter , Eders Kungliga Högheter , herr '
                    'talman , ledamöter av Sveriges riksdag !\n'
                    )

    def test_train_models(self):
        self.assertTrue(os.path.isfile('filter_files/RF1_align.priors'))
        self.assertTrue(os.path.isfile('filter_files/RF1_en.arpa'))
        self.assertTrue(os.path.isfile('filter_files/RF1_en.arpa'))

    def test_score_data(self):
        self.opus_filter.score_data()

        with open('filter_files/RF1_scores.en-sv.jsonl') as scores_file:
            score = json.loads(scores_file.readline())
            self.assertEqual(score['LanguageIDFilter'], [1.0, 0.98])
            self.assertEqual(score['CharacterScoreFilter'], [1.0, 1.0])
            self.assertEqual(score['CrossEntropyFilter'],
                    [15.214258903317491, 7.569084909162213])
            self.assertEqual(score['TerminalPunctuationFilter'], -0.0)
            self.assertEqual(score['NonZeroNumeralsFilter'], 0.0)
            self.assertEqual(type(score['WordAlignFilter']), list)


    def test_initial_files(self):
        with open('filter_files/RF1_sents.en') as sents_file_en:
            with open('filter_files/RF1_sents.sv') as sents_file_sv:
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


