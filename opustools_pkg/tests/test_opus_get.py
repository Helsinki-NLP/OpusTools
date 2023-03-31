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

    def test_get_files_invalid_url(self):
        opg = OpusGet(directory='RF', source='en', target='sv',
            list_resources=True, online_api=True)
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
        corpora, total_size = opg.get_corpora_data()
        corpora[0]['url'] = 'http://alskdjfl'
        old_stdout = sys.stdout
        printout = io.StringIO()
        sys.stdout = printout
        opg.download(corpora, total_size)
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
            'sts | 2 documents, 219 alignment pairs, 4393 source tokens, 2905 target tokens (id 140749)\n        {tempdir}/RF_latest_xml_en.zip already exis'
            'ts | 2 documents, 181 alignment pairs, 4393 source tokens, None target tokens (id 140750)\n        {tempdir}/RF_latest_xml_sv.zip already exist'
            's | 4 documents, 298 alignment pairs, 3456 source tokens, None target tokens (id 140756)\n\n   0 KB Total size\n'.format(tempdir=self.tempdir))

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

