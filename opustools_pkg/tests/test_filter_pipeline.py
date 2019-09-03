import unittest

from opustools_pkg.filter.pipeline import FilterPipeline

class TestFilterPipeline(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.config = [
                {'LengthFilter': {'min_length': 1, 'max_length': 100,
                    'unit': 'word'}},
                {'LengthRatioFilter': {'threshold': 3, 'unit': 'word'}},
                {'LongWordFilter': {'threshold': 40}},
                {'HtmlTagFilter': {}},
                {'CharacterScoreFilter': {'src_script': 'latin-1',
                    'tgt_script': 'latin-1', 'src_threshold': 1,
                    'tgt_threshold': 1}},
                {'LanguageIDFilter': {'src_lang': 'en', 'tgt_lang': 'sv',
                    'src_threshold': 0, 'tgt_threshold': 0}},
                {'TerminalPunctuationFilter': {'threshold': -2}},
                {'NonZeroNumeralsFilter': {'threshold': 0.5}}
           ]

    def test_from_config(self):
        fp = FilterPipeline.from_config(self.config)

        self.assertEqual(len(fp.filters), 8)

    def test_score(self):
        fp = FilterPipeline.from_config(self.config)
        pairs = [('That safeguards our independence .',
                    ('Kränkningar av svenskt territorium kommer aldrig att '
                    'accepteras .')),
                ('1245..',
                    '12345.....')]
        scores = list(fp.score(pairs))
        self.assertEqual(scores[0],
                {'LengthFilter': (5, 9),
                    'LengthRatioFilter': 1.8,
                    'LongWordFilter': 12,
                    'HtmlTagFilter': (False, False),
                    'CharacterScoreFilter': (1.0, 1.0),
                    'LanguageIDFilter': (1.0, 1.0),
                    'TerminalPunctuationFilter': -0.0,
                    'NonZeroNumeralsFilter': 1.0})
        self.assertEqual(scores[1],
                {'LengthFilter': (1, 1),
                    'LengthRatioFilter': 1.0,
                    'LongWordFilter': 10,
                    'HtmlTagFilter': (False, False),
                    'CharacterScoreFilter': (1.0, 1.0),
                    'LanguageIDFilter': (0.17, 0.0),
                    'TerminalPunctuationFilter': -2.1972245773362196,
                    'NonZeroNumeralsFilter': 0.8888888888888888})

    def test_filter(self):
        fp = FilterPipeline.from_config(self.config)
        pairs = [('test', ''),
                (' '.join(['w' for i in range(101)]), 'test'),
                (''.join(['c' for i in range(41)]), 'test'),
                ('<s>test', 'test'),
                ('test', 'Φtest'),
                ('Tämä lause on kirjoitettu suomeksi.',
                    'This sentence is written in English.'),
                ('test', 'test...............'),
                ('1', '99999999999'),
                ('This sentence is written in English.',
                    'Denna mening är skriven på svenska.')]
        filtered = list(fp.filter(pairs))
        self.assertEqual(filtered, [('This sentence is written in English.',
                    'Denna mening är skriven på svenska.')])
        rev_pairs = [p for p in reversed(pairs)]
        filtered = list(fp.filter(rev_pairs))
        self.assertEqual(filtered, [('This sentence is written in English.',
                    'Denna mening är skriven på svenska.')])


