import sys
import io
import os
import tempfile
import shutil
import unittest
from unittest import mock

from opustools.opus_get import OpusGet

class TestOpusGet(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.tempdir = tempfile.mkdtemp()
        self.maxDiff = None

    @classmethod
    def tearDownClass(self):
        shutil.rmtree(self.tempdir)

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

    def test_remove_data_with_no_alignment(self):
        opg = OpusGet(source='en', target='sv', list_resources=True)
        data = {'corpora':
                [{'alignment_pairs': 219,
                    'corpus': 'RF',
                    'documents': 2,
                    'id': 321123,
                    'latest': 'True',
                    'preprocessing': 'xml',
                    'size': 4,
                    'source': 'en',
                    'source_tokens': 4393,
                    'target': 'sv',
                    'target_tokens': 2905,
                    'url': ('https://object.pouta.csc.fi/OPUS-RF/v1/xml/'
                        'en-sv.xml.gz'),
                    'version': 'v1'},
                {'alignment_pairs': 181,
                    'corpus': 'RF',
                    'documents': 2,
                    'id': 321124,
                    'latest': 'True',
                    'preprocessing': 'xml',
                    'size': 60,
                    'source': 'en',
                    'source_tokens': 4393,
                    'target': '',
                    'target_tokens': None,
                    'url': 'https://object.pouta.csc.fi/OPUS-RF/v1/xml/en.zip',
                    'version': 'v1'},
                {'alignment_pairs': 298,
                    'corpus': 'RF',
                    'documents': 4,
                    'id': 321130,
                    'latest': 'True',
                    'preprocessing': 'xml',
                    'size': 64,
                    'source': 'sv',
                    'source_tokens': 3456,
                    'target': '',
                    'target_tokens': None,
                    'url': 'https://object.pouta.csc.fi/OPUS-RF/v1/xml/sv.zip',
                    'version': 'v1'},
                {'alignment_pairs': 181,
                    'corpus': 'Test',
                    'documents': 2,
                    'id': 321124,
                    'latest': 'True',
                    'preprocessing': 'xml',
                    'size': 60,
                    'source': 'en',
                    'source_tokens': 4393,
                    'target': '',
                    'target_tokens': None,
                    'url': 'https://object.pouta.csc.fi/OPUS-T/v1/xml/en.zip',
                    'version': 'v1'},
                {'alignment_pairs': 298,
                    'corpus': 'Test',
                    'documents': 4,
                    'id': 321130,
                    'latest': 'True',
                    'preprocessing': 'xml',
                    'size': 64,
                    'source': 'sv',
                    'source_tokens': 3456,
                    'target': '',
                    'target_tokens': None,
                    'url': 'https://object.pouta.csc.fi/OPUS-T/v1/xml/sv.zip',
                    'version': 'v1'}]}

        new_data = opg.remove_data_with_no_alignment(data)
        self.assertEqual(len(new_data), 3)
        data['corpora'].pop(0)
        new_data = opg.remove_data_with_no_alignment(data)
        self.assertEqual(len(new_data), 0)

    def test_add_data_with_alignment(self):
        opg = OpusGet(directory= 'RF', source='en', target='sv',
            list_resources=True)
        data = [{'alignment_pairs': 219,
                    'corpus': 'RF',
                    'documents': 2,
                    'id': 321123,
                    'latest': 'True',
                    'preprocessing': 'xml',
                    'size': 4,
                    'source': 'en',
                    'source_tokens': 4393,
                    'target': 'sv',
                    'target_tokens': 2905,
                    'url': ('https://object.pouta.csc.fi/OPUS-RF/v1/xml/'
                        'en-sv.xml.gz'),
                    'version': 'v1'},
                {'alignment_pairs': 181,
                    'corpus': 'RF',
                    'documents': 2,
                    'id': 321124,
                    'latest': 'True',
                    'preprocessing': 'xml',
                    'size': 60,
                    'source': 'en',
                    'source_tokens': 4393,
                    'target': '',
                    'target_tokens': None,
                    'url': 'https://object.pouta.csc.fi/OPUS-RF/v1/xml/en.zip',
                    'version': 'v1'},
                {'alignment_pairs': 298,
                    'corpus': 'RF',
                    'documents': 4,
                    'id': 321130,
                    'latest': 'True',
                    'preprocessing': 'xml',
                    'size': 64,
                    'source': 'sv',
                    'source_tokens': 3456,
                    'target': '',
                    'target_tokens': None,
                    'url': 'https://object.pouta.csc.fi/OPUS-RF/v1/xml/sv.zip',
                    'version': 'v1'}]
        new_data = opg.add_data_with_aligment(data, [])
        self.assertEqual(len(new_data), 3)
        data.pop(0)
        new_data = opg.add_data_with_aligment(data, [])
        self.assertEqual(len(new_data),0 )

    def test_remove_data_with_no_alignment_from_OPUS(self):
        opg = OpusGet(source='en', target='sv', list_resources=True)
        data = opg.get_response(opg.url)
        new_data = opg.remove_data_with_no_alignment(data)
        self.assertEqual(len(new_data), len(data['corpora']))

    def test_get_files_invalid_url(self):
        opg = OpusGet(directory='RF', source='en', target='sv',
            list_resources=True)
        opg.url = 'http://slkdfjlks'
        old_stdout = sys.stdout
        printout = io.StringIO()
        sys.stdout = printout
        opg.get_files()
        sys.stdout = old_stdout

        self.assertEqual(printout.getvalue(), 'Unable to retrieve the data.\n')

    @mock.patch('opustools.opus_get.input', create=True)
    def test_download_invalid_url(self, mocked_input):
        mocked_input.side_effect = ['y']
        opg = OpusGet(directory='RF', source='en', target='sv',
            list_resources=True)
        corpora, file_n, total_size = opg.get_corpora_data()
        corpora[0]['url'] = 'http://alskdjfl'
        old_stdout = sys.stdout
        printout = io.StringIO()
        sys.stdout = printout
        opg.download(corpora, file_n, total_size)
        sys.stdout = old_stdout

        self.assertEqual(printout.getvalue(), 'Unable to retrieve the data.\n')

    @mock.patch('opustools.opus_get.input', create=True)
    def test_dont_list_files_that_are_already_in_path(self, mocked_input):
        mocked_input.side_effect = ['y']
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
            download_dir=self.tempdir, list_resources=True).get_files()
        sys.stdout = old_stdout
        os.remove(os.path.join(self.tempdir, 'RF_latest_xml_en-sv.xml.gz'))
        os.remove(os.path.join(self.tempdir, 'RF_latest_xml_en.zip'))
        os.remove(os.path.join(self.tempdir, 'RF_latest_xml_sv.zip'))

        self.assertEqual(printout.getvalue(),
            '        {tempdir}/RF_latest_xml_en-sv.xml.gz already exi'
            'sts\n        {tempdir}/RF_latest_xml_en.zip already exis'
            'ts\n        {tempdir}/RF_latest_xml_sv.zip already exist'
            's\n\n   0 KB Total size\n'.format(tempdir=self.tempdir))

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
            list_resources=True).get_files()
        sys.stdout = old_stdout
        self.assertEqual(len(printout.getvalue().split('\n')), 18)

if __name__ == '__main__':
    unittest.main()

