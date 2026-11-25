import sys
import io
import json
import os
import tempfile
import shutil
import unittest
from unittest import mock

from opustools.opus_get import OpusGet

SYNTHETIC_COLLECTIONS = {
    'count': 2,
    'collections': [
        {'name': 'Europarl', 'versions': ['v8syn']},
        {'name': 'Wiki', 'versions': ['v1syn']},
    ],
}

SYNTHETIC_LANGUAGES = {
    'count': 2,
    'languages': ['bg', 'mk'],
}

SYNTHETIC_ITEMS = {
    'count': 2,
    'items': [
        {
            'id': 700,
            'name': 'Europarl',
            'version': 'v7syn',
            'lang_pair': 'bg-mk',
            'src_lang': 'bg',
            'tgt_lang': 'mk',
            'alignments': 100,
            'files': 2,
            'src_tokens': 1000,
            'tgt_tokens': 900,
            'downloads': {
                'alignments': {
                    'size': 100 * 1024,
                    'url': 'https://object.pouta.csc.fi/synOPUS-Europarl/'
                           'v7syn/xml/bg-mk.xml.gz',
                },
                'source_language': {
                    'size': 200 * 1024,
                    'url': 'https://object.pouta.csc.fi/synOPUS-Europarl/'
                           'v7syn/raw/bg.zip',
                },
                'target_language': {
                    'size': 300 * 1024,
                    'url': 'https://object.pouta.csc.fi/synOPUS-Europarl/'
                           'v7syn/raw/mk.zip',
                },
                'tokenized_source_language': {'size': None, 'url': None},
                'tokenized_target_language': {'size': None, 'url': None},
            },
            'updated_at': '2026-01-01T00:00:00.000000Z',
        },
        {
            'id': 716,
            'name': 'Europarl',
            'version': 'v8syn',
            'lang_pair': 'bg-mk',
            'src_lang': 'bg',
            'tgt_lang': 'mk',
            'alignments': 120,
            'files': 2,
            'src_tokens': 1200,
            'tgt_tokens': 1100,
            'downloads': {
                'alignments': {
                    'size': 110 * 1024,
                    'url': 'https://object.pouta.csc.fi/synOPUS-Europarl/'
                           'v8syn/xml/bg-mk.xml.gz',
                },
                'source_language': {
                    'size': 210 * 1024,
                    'url': 'https://object.pouta.csc.fi/synOPUS-Europarl/'
                           'v8syn/raw/bg.zip',
                },
                'target_language': {
                    'size': 310 * 1024,
                    'url': 'https://object.pouta.csc.fi/synOPUS-Europarl/'
                           'v8syn/raw/mk.zip',
                },
                'tokenized_source_language': {'size': None, 'url': None},
                'tokenized_target_language': {'size': None, 'url': None},
            },
            'updated_at': '2026-09-29T08:52:40.363708Z',
        },
    ],
}


class TestOpusGet(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.tempdir = tempfile.mkdtemp()
        self.maxDiff = None

    @classmethod
    def tearDownClass(self):
        shutil.rmtree(self.tempdir)

    @staticmethod
    def json_response(data):
        return io.BytesIO(json.dumps(data).encode('utf-8'))

    def test_format_size(self):
        opg = OpusGet(source='eo')
        self.assertEqual(opg.format_size(1), '1 KB')
        self.assertEqual(opg.format_size(291), '291 KB')
        self.assertEqual(opg.format_size(1000), '1 MB')
        self.assertEqual(opg.format_size(2514), '3 MB')
        self.assertEqual(opg.format_size(1000000), '1 GB')
        self.assertEqual(opg.format_size(3385993), '3 GB')
        self.assertEqual(opg.format_size(1000000000), '1 TB')
        self.assertEqual(opg.format_size(2304006273), '2 TB')

    def test_get_files_invalid_url(self):
        opg = OpusGet(directory='RF', source='en', target='sv',
            list_resources=True)
        opg.url = 'http://slkdfjlks'
        old_stdout = sys.stdout
        printout = io.StringIO()
        sys.stdout = printout
        opg.get_files()
        sys.stdout = old_stdout

        self.assertIn('Unable to retrieve the data', printout.getvalue())

    @mock.patch('opustools.opus_get.input', create=True)
    def test_download_invalid_url(self, mocked_input):
        mocked_input.side_effect = ['y']
        opg = OpusGet(directory='RF', source='en', target='sv',
            list_resources=True)
        corpora, total_size = opg.get_corpora_data()
        corpora[0]['url'] = 'http://alskdjfl'
        old_stdout = sys.stdout
        printout = io.StringIO()
        sys.stdout = printout
        opg.download(corpora, total_size)
        sys.stdout = old_stdout

        self.assertIn('Unable to retrieve the data', printout.getvalue())

    @mock.patch('opustools.opus_get.input', create=True)
    def test_dont_list_files_that_are_already_in_path(self, mocked_input):
        mocked_input.side_effect = ['y']
        old_stdout = sys.stdout
        printout = io.StringIO()
        sys.stdout = printout
        OpusGet(directory='RF', source='en', target='sv', preprocess='xml',
            download_dir=self.tempdir, local_db=True).get_files()
        sys.stdout = old_stdout
        old_stdout = sys.stdout
        printout = io.StringIO()
        sys.stdout = printout
        OpusGet(directory='RF', source='en', target='sv', preprocess='xml',
            download_dir=self.tempdir, list_resources=True, local_db=True).get_files()
        sys.stdout = old_stdout
        os.remove(os.path.join(self.tempdir, 'RF_latest_xml_en-sv.xml.gz'))
        os.remove(os.path.join(self.tempdir, 'RF_latest_xml_en.zip'))
        os.remove(os.path.join(self.tempdir, 'RF_latest_xml_sv.zip'))

        self.assertEqual(printout.getvalue(),
            '        {tempdir}/RF_latest_xml_en-sv.xml.gz already exi'
            'sts | 2 documents, 219 alignment pairs, 2905 source tokens, 4393 target tokens (id 350868)\n        {tempdir}/RF_latest_xml_en.zip already exis'
            'ts | 2 documents, 181 sentences, 4393 tokens (id 350890)\n        {tempdir}/RF_latest_xml_sv.zip already exist'
            's | 4 documents, 298 sentences, 3456 tokens (id 350908)\n\n   0 KB Total size\n'.format(tempdir=self.tempdir))

    @mock.patch('opustools.opus_get.input', create=True)
    def test_dont_download_files_that_are_already_in_path(self, mocked_input):
        mocked_input.side_effect = ['y', 'y']
        old_stdout = sys.stdout
        printout = io.StringIO()
        sys.stdout = printout
        OpusGet(directory='RF', source='en', target='sv', preprocess='xml',
            download_dir=self.tempdir).get_files()
        sys.stdout = old_stdout
        old_stdout = sys.stdout
        printout = io.StringIO()
        sys.stdout = printout
        OpusGet(directory='RF', source='en', target='sv', preprocess='xml',
            download_dir=self.tempdir).get_files()
        sys.stdout = old_stdout
        os.remove(os.path.join(self.tempdir, 'RF_latest_xml_en-sv.xml.gz'))
        os.remove(os.path.join(self.tempdir, 'RF_latest_xml_en.zip'))
        os.remove(os.path.join(self.tempdir, 'RF_latest_xml_sv.zip'))

        self.assertEqual(printout.getvalue(), '')

    def test_download_everything_from_a_corpus(self):
        old_stdout = sys.stdout
        printout = io.StringIO()
        sys.stdout = printout
        files = OpusGet(directory='RF', release='v1', preprocess='xml',
            list_resources=True, local_db=True).get_files()
        sys.stdout = old_stdout
        self.assertEqual(len(printout.getvalue().split('\n')), 18)

    def test_indonesian(self):
        old_stdout = sys.stdout
        printout = io.StringIO()

        sys.stdout = printout
        files = OpusGet(directory='bible-uedin', source='id', target='en', preprocess='xml',
            list_resources=True, local_db=True).get_files()
        sys.stdout = old_stdout
        self.assertEqual(len(printout.getvalue().split('\n')), 6)

        sys.stdout = printout
        files = OpusGet(list_languages=True, directory='bible-uedin', source='id',
                list_resources=True, local_db=True).get_files()
        sys.stdout = old_stdout
        self.assertEqual(len(printout.getvalue().split('\n')[-2].split(',')), 101)

        sys.stdout = printout
        files = OpusGet(list_corpora=True, source='id',
                list_resources=True, local_db=True).get_files()
        sys.stdout = old_stdout
        self.assertEqual(len(printout.getvalue().split('\n')[-2].split(',')), 24)

    def test_synthetic_url(self):
        opg = OpusGet(directory='Europarl', source='bg', target='mk',
            synthetic=True, download_dir=self.tempdir)
        self.assertEqual(opg.url,
            'https://opus.nlpl.eu/synthetic-api/items?'
            'name=Europarl&src=bg&tgt=mk')

        opg = OpusGet(directory='Europarl', release='v8syn',
            synthetic=True, download_dir=self.tempdir)
        self.assertEqual(opg.url,
            'https://opus.nlpl.eu/synthetic-api/items?'
            'name=Europarl&version=v8syn')

    def test_synthetic_invalid_options(self):
        with self.assertRaisesRegex(ValueError, 'synthetic and local_db'):
            OpusGet(synthetic=True, local_db=True)
        with self.assertRaisesRegex(ValueError, 'supports only xml and raw'):
            OpusGet(synthetic=True, preprocess='moses')

    def test_synthetic_latest_rows(self):
        opg = OpusGet(directory='Europarl', source='bg', target='mk',
            synthetic=True, download_dir=self.tempdir)
        with mock.patch('opustools.opus_get.urllib.request.urlopen',
                side_effect=lambda url: self.json_response(SYNTHETIC_ITEMS)) \
                as urlopen:
            corpora, total_size = opg.get_corpora_data()

        urlopen.assert_called_once_with(opg.url)
        self.assertEqual(total_size, '630 KB')
        self.assertEqual(
            [c['url'] for c in corpora],
            ['https://object.pouta.csc.fi/synOPUS-Europarl/v8syn/xml/bg-mk.xml.gz',
             'https://object.pouta.csc.fi/synOPUS-Europarl/v8syn/raw/bg.zip',
             'https://object.pouta.csc.fi/synOPUS-Europarl/v8syn/raw/mk.zip'])
        self.assertEqual(
            [c['filename'] for c in corpora],
            [os.path.join(self.tempdir, 'Europarl_latest_xml_bg-mk.xml.gz'),
             os.path.join(self.tempdir, 'Europarl_latest_xml_bg.zip'),
             os.path.join(self.tempdir, 'Europarl_latest_xml_mk.zip')])
        self.assertEqual(corpora[0]['id'], 716)
        self.assertEqual(corpora[0]['version'], 'v8syn')
        self.assertEqual(corpora[0]['alignment_pairs'], 120)
        self.assertEqual([c['size'] for c in corpora], [110, 210, 310])
        self.assertEqual(corpora[1]['target_tokens'], '')
        self.assertEqual(corpora[2]['source_tokens'], 1100)

    def test_synthetic_raw_rows(self):
        opg = OpusGet(directory='Europarl', source='bg', target='mk',
            release='v8syn', preprocess='raw', synthetic=True,
            download_dir=self.tempdir)
        with mock.patch('opustools.opus_get.urllib.request.urlopen',
                side_effect=lambda url: self.json_response(SYNTHETIC_ITEMS)):
            corpora, _ = opg.get_corpora_data()

        self.assertEqual(
            [c['url'] for c in corpora],
            ['https://object.pouta.csc.fi/synOPUS-Europarl/v8syn/raw/bg.zip',
             'https://object.pouta.csc.fi/synOPUS-Europarl/v8syn/raw/mk.zip'])
        self.assertEqual(
            [c['filename'] for c in corpora],
            [os.path.join(self.tempdir, 'Europarl_v8syn_raw_bg.zip'),
             os.path.join(self.tempdir, 'Europarl_v8syn_raw_mk.zip')])

    def test_synthetic_list_endpoints(self):
        requested_urls = []

        def fake_urlopen(url):
            requested_urls.append(url)
            if '/collections' in url:
                return self.json_response(SYNTHETIC_COLLECTIONS)
            if '/languages' in url:
                return self.json_response(SYNTHETIC_LANGUAGES)
            raise AssertionError('Unexpected URL: ' + url)

        with mock.patch('opustools.opus_get.urllib.request.urlopen',
                side_effect=fake_urlopen):
            old_stdout = sys.stdout
            printout = io.StringIO()
            sys.stdout = printout
            try:
                OpusGet(directory='Europarl', list_corpora=True,
                    synthetic=True, download_dir=self.tempdir).get_files()
                OpusGet(directory='Europarl', release='v8syn', source='bg',
                    list_languages=True, synthetic=True,
                    download_dir=self.tempdir).get_files()
            finally:
                sys.stdout = old_stdout

        self.assertEqual(requested_urls[0],
            'https://opus.nlpl.eu/synthetic-api/collections?name=Europarl')
        self.assertEqual(requested_urls[1],
            'https://opus.nlpl.eu/synthetic-api/languages?'
            'name=Europarl&version=v8syn&src=bg')
        self.assertEqual(printout.getvalue(), 'Europarl, Wiki\nbg, mk\n')

    def test_synthetic_download_uses_normalized_urls(self):
        expected_urls = [
            'https://object.pouta.csc.fi/synOPUS-Europarl/v8syn/xml/bg-mk.xml.gz',
            'https://object.pouta.csc.fi/synOPUS-Europarl/v8syn/raw/bg.zip',
            'https://object.pouta.csc.fi/synOPUS-Europarl/v8syn/raw/mk.zip',
        ]
        with mock.patch('opustools.opus_get.urllib.request.urlopen',
                side_effect=lambda url: self.json_response(SYNTHETIC_ITEMS)):
            with mock.patch(
                    'opustools.opus_get.urllib.request.urlretrieve') as retrieve:
                OpusGet(directory='Europarl', source='bg', target='mk',
                    synthetic=True, suppress_prompts=True,
                    download_dir=self.tempdir).get_files()

        self.assertEqual(
            [call.args[0] for call in retrieve.call_args_list],
            expected_urls)

if __name__ == '__main__':
    unittest.main()
