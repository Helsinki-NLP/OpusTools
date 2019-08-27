import unittest

from opustools_pkg.filter.pipeline import FilterPipeline

class TestFilterPipeline(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.config = [{'LanguageIDFilter':
                            {'src_lang': 'en',
                            'tgt_lang': 'sv',
                            'src_threshold': 0,
                            'tgt_threshold': 0}},
                        {'TerminalPunctuationFilter':
                            {'threshold': -2}},
                        {'NonZeroNumeralsFilter':
                            {'threshold': 0.5}},
                        {'CharacterScoreFilter':
                            {'src_script': 'latin-1',
                            'tgt_script': 'latin-1',
                            'src_threshold': 1,
                            'tgt_threshold': 1}}]

    def test_from_config(self):
        fp = FilterPipeline.from_config(self.config)

        self.assertEqual(len(fp.filters), 4)

    def test_score(self):
        fp = FilterPipeline.from_config(self.config)
        pairs = [('That safeguards our independence .',
                    ('Kränkningar av svenskt territorium kommer aldrig att '
                    'accepteras .')),
                ('1245..',
                    '12345.....')]
        scores = fp.score(pairs)
        self.assertEqual(scores[0],
                {'LanguageIDFilter': (1.0, 1.0),
                    'TerminalPunctuationFilter': -0.0,
                    'NonZeroNumeralsFilter': 1.0,
                    'CharacterScoreFilter': (1.0, 1.0)})
        self.assertEqual(scores[1],
                {'LanguageIDFilter': (0.17, 0.0),
                    'TerminalPunctuationFilter': -2.1972245773362196,
                    'NonZeroNumeralsFilter': 0.8888888888888888,
                    'CharacterScoreFilter': (1.0, 1.0)})

