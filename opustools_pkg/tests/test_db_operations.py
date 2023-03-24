import sqlite3
import unittest

from opustools import db_operations, clean_up_parameters, run_query, run_default_query, run_corpora_query, run_languages_query, get_corpora

DB_FILE = 'tests/testdata.db'
db_operations.DB_FILE = DB_FILE

class TestDbOperations(unittest.TestCase):

    def test_get_latest_bilingual(self):
        params = {'source': 'en', 'target': 'fi', 'corpus': 'OpenSubtitles', 'preprocessing': 'xml', 'latest': 'True'}
        ret = run_default_query(params)
        self.assertEqual(ret[0]['id'], 136272)

    def test_get_all_versions_bilingual(self):
        params = {'source': 'en', 'target': 'fi', 'corpus': 'OpenSubtitles', 'preprocessing': 'xml'}
        ret = run_default_query(params)
        self.assertEqual(len(ret), 8)
        for i in ret:
            self.assertTrue(i['id'] in [112278, 112934, 114221, 115588, 123919, 123920, 136272, 136273])

    def test_get_specific_bilingual(self):
        params = {'source': 'en', 'target': 'fi', 'corpus': 'OpenSubtitles', 'preprocessing': 'xml', 'version': 'v1'}
        ret = run_default_query(params)
        self.assertEqual(ret[0]['id'], 112278)

    def test_get_all_preprocessings_for_latest_bilingual(self):
        params = {'source': 'en', 'target': 'fi', 'corpus': 'OpenSubtitles', 'latest': 'True'}
        ret = run_default_query(params)
        self.assertEqual(len(ret), 7)
        for i in ret:
            self.assertTrue(i['id'] in [126145, 128126, 130626, 130627, 133658, 136272, 136273])

    def test_get_specific_preprocessing_bilingual(self):
        params = {'source': 'en', 'target': 'fi', 'corpus': 'OpenSubtitles', 'preprocessing': 'moses',  'latest': 'True'}
        ret = run_default_query(params)
        self.assertEqual(ret[0]['id'], 128126)

    def test_get_latest_monolingual(self):
        params = {'source': 'en', 'target': '', 'corpus': 'OpenSubtitles', 'preprocessing': 'xml', 'latest': 'True'}
        ret = run_default_query(params)
        self.assertEqual(ret[0]['id'], 136362)

    def test_get_all_versions_monolingual(self):
        params = {'source': 'en', 'target': '', 'corpus': 'OpenSubtitles', 'preprocessing': 'xml'}
        ret = run_default_query(params)
        self.assertEqual(len(ret), 6)
        for i in ret:
            self.assertTrue(i['id'] in [112299, 112972, 114258, 115629, 123968, 136362])

    def test_get_specific_version_monolingual(self):
        params = {'source': 'en', 'target': '', 'corpus': 'OpenSubtitles', 'preprocessing': 'xml', 'version': 'v1'}
        ret = run_default_query(params)
        self.assertEqual(ret[0]['id'], 112299)

    def test_get_all_preprocessings_for_latest_monolingual(self):
        params = {'source': 'en', 'target': '', 'corpus': 'OpenSubtitles', 'latest': 'True'}
        ret = run_default_query(params)
        self.assertEqual(len(ret), 6)
        for i in ret:
            self.assertTrue(i['id'] in [127362, 127435, 127436, 129380, 129423, 136362])

    def test_get_specific_preprocessing_monolingual(self):
        params = {'source': 'en', 'target': '', 'corpus': 'OpenSubtitles', 'preprocessing': 'raw', 'latest': 'True'}
        ret = run_default_query(params)
        self.assertEqual(ret[0]['id'], 129423)

    def test_list_all_corpora(self):
        params = {'corpora': 'true'}
        ret = run_corpora_query(params)
        self.assertEqual(len(ret), 45)

    def test_list_corpora_one_lan(self):
        params = {'corpora': 'true', 'source': 'fi'}
        ret = run_corpora_query(params)
        self.assertEqual(len(ret), 17)

    def test_list_corpora_two_lan(self):
        params = {'corpora': 'true', 'source': 'en', 'target': 'fi'}
        ret = run_corpora_query(params)
        self.assertEqual(len(ret), 16)

    def test_list_all_languages(self):
        params = {'languages': 'true'}
        ret = run_languages_query(params)
        self.assertEqual(len(ret), 339)

    def test_list_languages_one_lan(self):
        params = {'languages': 'true', 'source': 'zh'}
        ret = run_languages_query(params)
        self.assertEqual(len(ret), 93)

    def test_list_languages_one_corp(self):
        params = {'languages': 'true', 'corpus': 'RF'}
        ret = run_languages_query(params)
        self.assertEqual(len(ret), 5)

    def test_list_languages_one_lan_one_corp(self):
        params = {'languages': 'true', 'corpus': 'RF', 'source': 'sv'}
        ret = run_languages_query(params)
        self.assertEqual(len(ret), 4)

    def test_corpus_xml(self):
        params = {'source': 'en', 'target': 'fi', 'corpus': 'OpenSubtitles', 'preprocessing': 'xml', 'latest': 'True'}
        ret = get_corpora(params)
        self.assertEqual(len(ret), 4)
        for i in ret:
            self.assertTrue(i['id'] in [136272, 136273, 136943, 136362])

    def test_corpus_raw(self):
        params = {'source': 'en', 'target': 'fi', 'corpus': 'OpenSubtitles', 'preprocessing': 'raw', 'latest': 'True'}
        ret = get_corpora(params)
        self.assertEqual(len(ret), 4)
        for i in ret:
            self.assertTrue(i['id'] in [136272, 136273, 129423, 129429])

    def test_corpus_moses(self):
        params = {'source': 'en', 'target': 'fi', 'corpus': 'OpenSubtitles', 'preprocessing': 'moses', 'latest': 'True'}
        ret = get_corpora(params)
        self.assertEqual(ret[0]['id'], 128126)

    def test_corpus_xml_no_target(self):
        params = {'source': 'en', 'corpus': 'RF', 'preprocessing': 'xml', 'latest': 'True'}
        ret = get_corpora(params)
        self.assertEqual(len(ret), 9)
        for i in ret:
            self.assertTrue(i['id'] in [140742, 140746, 140747, 140748, 140749, 140756, 140755, 140753, 140750])

    def test_corpus_xml_unalphabetical(self):
        params = {'source': 'fi', 'target': 'en', 'corpus': 'OpenSubtitles', 'preprocessing': 'xml', 'latest': 'True'}
        ret = get_corpora(params)
        for i in ret:
            self.assertTrue(i['id'] in [136272, 136273, 136943, 136362])

    def test_corpus_xml_no_langs(self):
        params = {'corpus': 'RF', 'preprocessing': 'xml', 'latest': 'True'}
        ret = get_corpora(params)
        self.assertEqual(len(ret), 15)
        for i in ret:
            self.assertTrue(i['id'] in [140742, 140743, 140744, 140745, 140747, 140748, 140749, 140751, 140752, 140754, 140755, 140756, 140753, 140750, 140746])
