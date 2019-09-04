import unittest
import json
import argparse

from opustools_pkg.opus_filter import OpusFilter
from opustools_pkg.filter import lm

class TestOpusFilter(unittest.TestCase):

    def setUp(self):
        configuration = {'output_directory': 'filter_files',
            'corpora': {'RF1': {'type': 'OPUS',
              'parameters': {'corpus_name': 'RF',
               'source_language': 'en',
               'target_language': 'sv',
               'release': 'latest',
               'preprocessing': 'xml'}}},
            'filtering': {'RF1': {'src_output': 'RF1_filtered.en',
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
            'scoring': {'RF1': {'output': 'RF1_scores.en-sv.json',
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
               {'CrossEntropyFilter': {'src_lm_params': {'segmentation': {'type': 'char'},
                  'filename': 'RF1_en.arpa'},
                 'tgt_lm_params': {'segmentation': {'type': 'char'},
                  'filename': 'RF1_sv.arpa'},
                 'src_threshold': 50.0,
                 'tgt_threshold': 50.0,
                 'diff_threshold': 10.0}}]}}}

        self.opus_filter = OpusFilter(configuration)

    def test_get_pairs(self):
        pair_gen = self.opus_filter.get_pairs('RF1', 'en', 'sv')
        pair = next(pair_gen)
        for pair in pair_gen:
            pass
        self.assertEqual(pair,
                ('This will ensure the cohesion of Swedish society .',
                'Så kan vi hålla samman Sverige .'))

    def test_clean_data(self):
        self.opus_filter.clean_data()

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

    def test_score_data(self):
        self.opus_filter.train_lms_and_priors()
        self.opus_filter.score_data()

        with open('filter_files/scores.RF1.en-sv.json') as scores_file:
            scores = json.loads(scores_file.readline())
            self.assertEqual(scores[0]['LanguageIDFilter'], [1.0, 0.98])
            self.assertEqual(scores[0]['CharacterScoreFilter'], [1.0, 1.0])
            self.assertEqual(scores[0]['CrossEntropyFilter'],
                    [15.214258903317491, 7.569084909162213])
            self.assertEqual(scores[0]['TerminalPunctuationFilter'], -0.0)
            self.assertEqual(scores[0]['NonZeroNumeralsFilter'], 0.0)
            self.assertEqual(type(scores[0]['WordAlignFilter']), list)

    def test_make_bpe(self):
        train_file = 'filter_files/sents.RF1.en'
        input_file = 'filter_files/sents.RF1.en'
        output_file = 'filter_files/sents.RF1.en.bpe'
        self.opus_filter.make_bpe(train_file, input_file, output_file)
        with open('filter_files/sents.RF1.en.bpe') as bped_file:
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

    def test_segment_line_char(self):
        line = 'this is a test\n'
        line = self.opus_filter.segment_line_char(line)
        self.assertEqual(line,
                '<s> <w> t h i s <w> i s <w> a <w> t e s t <w> </s> \n')

    def test_segment_file(self):
        train_file = 'filter_files/sents.RF1.en'
        input_file = 'filter_files/sents.RF1.en'
        output_file = 'filter_files/sents.RF1.en.bpe'
        self.opus_filter.make_bpe(train_file, input_file, output_file)
        self.opus_filter.segment_file(
                'filter_files/sents.RF1.en.bpe',
                'filter_files/sents.RF1.en.bpe.seg',
                char=False
                )
        with open('filter_files/sents.RF1.en.bpe.seg') as output_file:
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
                'filter_files/sents.RF1.en',
                'filter_files/sents.RF1.en.seg',
                char=False
                )
        with open('filter_files/sents.RF1.en.seg') as output_file:
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

    def test_segment_file_char(self):
        self.opus_filter.segment_file(
                'filter_files/sents.RF1.en',
                'filter_files/sents.RF1.en.seg'
                )
        with open('filter_files/sents.RF1.en.seg') as output_file:
            seg_lines = output_file.readlines()
            self.assertEqual(len(seg_lines), 180)
            self.assertEqual(
                    seg_lines[0],
                    ('<s> <w> S t a t e m e n t <w> o f <w> G o v e r n m e '
                    'n t <w> P o l i c y <w> b y <w> t h e <w> P r i m e <w> '
                    'M i n i s t e r <w> , <w> M r <w> I n g v a r <w> C a r '
                    'l s s o n <w> , <w> a t <w> t h e <w> O p e n i n g <w> '
                    'o f <w> t h e <w> S w e d i s h <w> P a r l i a m e n t '
                    '<w> o n <w> T u e s d a y <w> , <w> 4 <w> O c t o b e r '
                    '<w> , <w> 1 9 8 8 <w> . <w> </s> \n')
                    )

    def test_initial_files(self):
        with open('filter_files/sents.RF1.en') as sents_file_en:
            with open('filter_files/sents.RF1.sv') as sents_file_sv:
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


