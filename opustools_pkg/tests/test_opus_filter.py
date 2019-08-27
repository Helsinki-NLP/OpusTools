import unittest

from opustools_pkg import filter as opusfilter


class TestOpusFilter(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.lengthFilter = opusfilter.LengthFilter()
        self.lengthRatioFilter = opusfilter.LengthRatioFilter()
        self.longWordFilter = opusfilter.LongWordFilter()
        self.htmlTagFilter = opusfilter.HtmlTagFilter()
        self.characterScoreFilter = opusfilter.CharacterScoreFilter()
        self.languageIDFilter = opusfilter.LanguageIDFilter(src_lang='en', tgt_lang='fi')
        self.terminalPunctuationFilter = opusfilter.TerminalPunctuationFilter()
        self.nonZeroNumeralsFilter = opusfilter.NonZeroNumeralsFilter()

    def test_LengthRatioFilter_score(self):
        score = next(self.lengthRatioFilter.score(
            [('This sentence has five words', 'This one has four')]))
        self.assertEqual(score, 1.25)
        score = next(self.lengthRatioFilter.score(
            [('This one has four', 'This sentence has five words')]))
        self.assertEqual(score, 1.25)
        score = next(self.lengthRatioFilter.score(
            [('', 'This sentence has five words')]))
        self.assertEqual(score, float('inf'))

    def test_LengthRatioFilter_filter(self):
        answer = next(self.lengthRatioFilter.filter(
            [('This sentence has five words', 'This one has four')]))
        self.assertTrue(answer)
        answer = next(self.lengthRatioFilter.filter(
            [('One', 'This one has four')]))
        self.assertFalse(answer)
        answer = next(self.lengthRatioFilter.filter(
            [('', 'This one has four')]))
        self.assertFalse(answer)
        self.lengthRatioFilter.threshold = 1.25
        answer = next(self.lengthRatioFilter.filter(
            [('This sentence has five words', 'This one has four')]))
        self.assertFalse(answer)
        answer = next(self.lengthRatioFilter.filter(
            [('This sentence has five words more', 'This one has four more')]))
        self.assertTrue(answer)

    def test_LengthFilter_score(self):
        sent1 = ' '.join('word' for i in range(99))
        sent2 = ' '.join('word' for i in range(62))
        score = next(self.lengthFilter.score([(sent1, sent2)]))
        self.assertEqual(score, (99, 62))

    def test_LengthFilter_filter(self):
        sent1 = ' '.join('word' for i in range(99))
        sent2 = ' '.join('word' for i in range(62))
        answer = next(self.lengthFilter.filter([(sent1, sent2)]))
        self.assertTrue(answer)
        sent1 = ' '.join('word' for i in range(101))
        answer = next(self.lengthFilter.filter([(sent1, sent2)]))
        self.assertFalse(answer)
        self.lengthFilter.max_length = 101
        answer = next(self.lengthFilter.filter([(sent1, sent2)]))
        self.assertTrue(answer)

    def test_LongWordFilter_score(self):
        sent1 = 'This is a sentence'
        sent2 = 'This is also'
        score = next(self.longWordFilter.score([(sent1, sent2)]))
        self.assertEqual(score, 8)

    def test_LongWordFilter_filter(self):
        sent1 = 'This is a sentence'
        sent2 = 'This is also'
        answer = next(self.longWordFilter.filter([(sent1, sent2)]))
        self.assertTrue(answer)
        sent2 = sent2 + ' ' + ''.join('w' for i in range(40))
        answer = next(self.longWordFilter.filter([(sent1, sent2)]))
        self.assertFalse(answer)
        self.longWordFilter.threshold = 41
        answer = next(self.longWordFilter.filter([(sent1, sent2)]))
        self.assertTrue(answer)
        self.longWordFilter.threshold = 40

    def test_HtmlTagFilter_score(self):
        sent1 = '<s>This contains tags'
        sent2 = 'This does not'
        score = next(self.htmlTagFilter.score([(sent1, sent2)]))
        self.assertEqual(score, (True, False))

    def test_HtmlTagFilter_filter(self):
        sent1 = '<s>This contains tags'
        sent2 = 'This does not'
        answer = next(self.htmlTagFilter.filter([(sent1, sent2)]))
        self.assertFalse(answer)
        sent1 = 'This contains tags not'
        answer = next(self.htmlTagFilter.filter([(sent1, sent2)]))
        self.assertTrue(answer)

    def test_CharacterScoreFilter_characterScore(self):
        sent = 'This has ten.'
        score = self.characterScoreFilter.characterScore(sent, 'latin-1')
        self.assertEqual(score, 1)
        sent = 'This hαs ten.'
        score = self.characterScoreFilter.characterScore(sent, 'latin-1')
        self.assertEqual(score, 0.9)
        score = self.characterScoreFilter.characterScore('', 'latin-1')
        self.assertEqual(score, 1)

    def test_CharacterScoreFilter_score(self):
        sent1 = 'This has ten.'
        sent2 = 'This hαs ten.'
        score = next(self.characterScoreFilter.score([(sent1, sent2)]))
        self.assertEqual(score, (1, 0.9))

    def test_CharacterScoreFilter_filter(self):
        sent1 = 'This has ten.'
        sent2 = 'This has ten.'
        answer = next(self.characterScoreFilter.filter([(sent1, sent2)]))
        self.assertTrue(answer)
        sent2 = 'This hαs ten.'
        answer = next(self.characterScoreFilter.filter([(sent1, sent2)]))
        self.assertFalse(answer)
        self.characterScoreFilter.tgt_threshold=0.9
        answer = next(self.characterScoreFilter.filter([(sent1, sent2)]))
        self.assertTrue(answer)

    def test_LanguageIDFilter_confidence(self):
        english = 'This sentence is written in English.'
        conf = self.languageIDFilter.confidence(english, 'en')
        self.assertEqual(conf, 1.0)
        conf = self.languageIDFilter.confidence(english, 'fi')
        self.assertEqual(conf, 0.0)

    def test_LanguageIDFilter_score(self):
        english = 'This sentence is written in English.'
        finnish = 'Tämä lause on kirjoitettu suomeksi.'
        score = next(self.languageIDFilter.score([(english, finnish)]))
        self.assertEqual(score, (1.0, 1.0))

    def test_LanguageIDFilter_filter(self):
        english = 'This sentence is written in English.'
        finnish = 'Tämä lause on kirjoitettu suomeksi.'
        answer = next(self.languageIDFilter.filter([(english, finnish)]))
        self.assertTrue(answer)
        answer = next(self.languageIDFilter.filter([(finnish, english)]))
        self.assertFalse(answer)

    def test_TerminalPunctuationFilter_score(self):
        sent1 = 'This is sentence.'
        sent2 = 'This is sentence.'
        score = next(self.terminalPunctuationFilter.score([(sent1, sent2)]))
        self.assertEqual(score, 0)
        sent1 = 'This is sentence'
        sent2 = 'This is sentence.....'
        score = next(self.terminalPunctuationFilter.score([(sent1, sent2)]))
        self.assertEqual(round(score, 1), -2.3)

    def test_TerminalPunctuationFilter_filter(self):
        sent1 = 'This is sentence.'
        sent2 = 'This is sentence.'
        answer = next(self.terminalPunctuationFilter.filter([(sent1, sent2)]))
        self.assertTrue(answer)
        sent1 = 'This is sentence'
        sent2 = 'This is sentence.....'
        answer = next(self.terminalPunctuationFilter.filter([(sent1, sent2)]))
        self.assertFalse(answer)
        self.terminalPunctuationFilter.threshold = -2.4
        answer = next(self.terminalPunctuationFilter.filter([(sent1, sent2)]))
        self.assertTrue(answer)
        self.terminalPunctuationFilter.threshold = -2

    def test_NonZeroNumeralsFilter_score(self):
        sent1 = '12345'
        sent2 = '12345'
        score = next(self.nonZeroNumeralsFilter.score([(sent1, sent2)]))
        self.assertEqual(score, 1)
        sent2 = '23451'
        score = next(self.nonZeroNumeralsFilter.score([(sent1, sent2)]))
        self.assertEqual(score, 0.8)

    def test_NonZeroNumeralsFilter_filter(self):
        sent1 = '12345'
        sent2 = '23451'
        answer = next(self.nonZeroNumeralsFilter.filter([(sent1, sent2)]))
        self.assertTrue(answer)
        self.nonZeroNumeralsFilter.threshold = 0.81
        answer = next(self.nonZeroNumeralsFilter.filter([(sent1, sent2)]))
        self.assertFalse(answer)

#    def test_CleanCorpusN_score(self):
#        sent1 = 'This sentence has five words.'
#        sent2 = 'This has four words.'
#        score = self.cleanCorpusN.score(sent1, sent2)
#        self.assertEqual(score, 1)
#        sent1 = 'This sentence has five words This sentence has five words.'
#        sent2 = 'This.'
#        score = self.cleanCorpusN.score(sent1, sent2)
#        self.assertEqual(score, 0)
#        sent2 = ''
#        score = self.cleanCorpusN.score(sent1, sent2)
#        sent2 = ' '.join('word' for i in range(50))
#        score = self.cleanCorpusN.score(sent1, sent2)
#        self.assertEqual(score, 1)
#        sent2 = ' '.join('word' for i in range(51))
#        score = self.cleanCorpusN.score(sent1, sent2)
#        self.assertEqual(score, 0)
#
#    def test_CleanCorpusN_filter(self):
#        sent1 = 'This sentence has five words.'
#        sent2 = 'This has four words.'
#        answer = self.cleanCorpusN.filter(sent1, sent2)
#        self.assertTrue(answer)
#        self.cleanCorpusN.min_length = 5
#        answer = self.cleanCorpusN.filter(sent1, sent2)
#        self.assertFalse(answer)
#        self.cleanCorpusN.min_length = 1
#        self.cleanCorpusN.max_length = 4
#        answer = self.cleanCorpusN.filter(sent1, sent2)
#        self.assertFalse(answer)
#        self.cleanCorpusN.max_length = 50
#        self.cleanCorpusN.ratio_limit = 1
#        answer = self.cleanCorpusN.filter(sent1, sent2)
#        self.assertFalse(answer)
#        self.cleanCorpusN.ratio_limit = 9
#        answer = self.cleanCorpusN.filter(sent1, sent2)
#        self.assertTrue(answer)
