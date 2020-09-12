import os
import sys
import io
import shutil
import tempfile
import unittest
from unittest import mock

from opustools import OpusCat, OpusGet
from .test_opus_read import add_to_root_dir

class TestOpusCat(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.maxDiff = None

        if ('OPUSCAT_TEST_TEMPDIR' in os.environ.keys() and
            os.path.exists(os.environ['OPUSCAT_TEST_TEMPDIR'])):
                self.tempdir1 = os.environ['OPUSCAT_TEST_TEMPDIR']
        else:
            self.tempdir1 = tempfile.mkdtemp()
            os.mkdir(os.path.join(self.tempdir1, 'test_files'))

        if ('OPUSCAT_TEST_ROOTDIR' in os.environ.keys() and
            os.path.exists(os.environ['OPUSCAT_TEST_ROOTDIR'])):
            self.root_directory = os.environ['OPUSCAT_TEST_ROOTDIR']
        else:
            self.root_directory = tempfile.mkdtemp()

            os.makedirs(os.path.join(self.root_directory, 'RF', 'latest',
                'xml'))

            add_to_root_dir(corpus='RF', source='en', target='sv',
                preprocess='xml', root_dir=self.root_directory)

    @classmethod
    def tearDownClass(self):
        if ('OPUSCAT_TEST_SAVE' in os.environ.keys() and
                os.environ['OPUSCAT_TEST_SAVE'] == 'true'):
            print('\nTEMPDIR:', self.tempdir1)
            print('ROOTDIR:', self.root_directory)
        else:
            shutil.rmtree(self.tempdir1)
            shutil.rmtree(self.root_directory)

    def printSentencesToVariable(self, **kwargs):
        old_stdout = sys.stdout
        printout = io.StringIO()
        sys.stdout = printout
        oprinter = OpusCat(**kwargs)
        oprinter.printSentences()
        sys.stdout = old_stdout
        return printout.getvalue()

    def test_printing_sentences(self):
        var = self.printSentencesToVariable(directory='RF', language='en',
            plain=True, root_directory=self.root_directory)
        self.assertEqual(var[-183:],
            """("s72.1")>It is the Government 's resposibility and ai"""
            """m to put to use all good initiatives , to work for bro"""
            """ad solutions and to pursue a policy in the interests o"""
            """f the whole nation .\n""")

    def test_printing_sentences_with_limit(self):
        var = self.printSentencesToVariable(directory='RF', language='en',
            maximum=1, plain=True, root_directory=self.root_directory)
        self.assertEqual(var,
            '\n# RF/xml/en/1996.xml\n\n("s1.1")>MINISTRY FOR FOREIGN'
            ' AFFAIRS Press Section Check against delivery\n')

    def test_printing_sentences_without_ids(self):
        var = self.printSentencesToVariable(directory='RF', language='en',
            maximum=1, no_ids=True, plain=True,
            root_directory=self.root_directory)
        self.assertEqual(var,
            '\n# RF/xml/en/1996.xml\n\nMINISTRY FOR FOREIGN'
            ' AFFAIRS Press Section Check against delivery\n')

    def test_print_annotations(self):
        var = self.printSentencesToVariable(directory='RF', language='en',
            maximum=1, no_ids=True, plain=True, print_annotations=True,
            root_directory=self.root_directory)
        self.assertEqual(var,
            '\n# RF/xml/en/1996.xml\n\nMINISTRY|NNP|ministry FOR|NNP'
            '|for FOREIGN|NNP|FOREIGN AFFAIRS|NNP Press|NNP|Press Sec'
            'tion|NNP|Section Check|NNP|Check against|IN|against deli'
            'very|NN|delivery\n')

    def test_print_annotations_all_attributes(self):
        var = self.printSentencesToVariable(directory='RF', language='en',
            maximum=1, no_ids=True, plain=True, print_annotations=True,
            set_attribute=['all_attrs'], root_directory=self.root_directory)
        self.assertEqual(var,
            '\n# RF/xml/en/1996.xml\n\nMINISTRY|null|0|NN|w1.1.1|mini'
            'stry|NNP|NN FOR|prep|1|IN|w1.1.2|for|NNP|IN FOREIGN|nn|7'
            '|NNP|w1.1.3|FOREIGN|NNP|NP AFFAIRS|nn|7|NNP|w1.1.4|NNP|N'
            'P Press|nn|7|NNP|w1.1.5|Press|NNP|NP Section|nn|7|NNP|w1'
            '.1.6|Section|NNP|NP Check|pobj|2|NNP|w1.1.7|Check|NNP|NP'
            ' against|prep|1|IN|w1.1.8|against|IN|IN delivery|pobj|8|N'
            'N|w1.1.9|delivery|NN|NN\n')

    def test_print_xml(self):
        var = self.printSentencesToVariable(directory='RF', language='en',
            maximum=2, root_directory=self.root_directory)
        self.assertEqual(var[-38:],
            '"w3.1.4" deprel="null">)</w>\n</s></p>\n')

    def test_printing_specific_file(self):
        var = self.printSentencesToVariable(directory='RF', language='en',
            maximum=1, no_ids=True, plain=True, file_name='RF/xml/en/1988.xml',
            root_directory=self.root_directory)
        self.assertEqual(var,
            '\n# RF/xml/en/1988.xml\n\nStatement of Government Policy'
            ' by the Prime Minister , Mr Ingvar Carlsson , at the Open'
            'ing of the Swedish Parliament on Tuesday , 4 October , 1'
            '988 .\n')

    @mock.patch('opustools.opus_get.input', create=True)
    def test_file_not_found(self, mocked_input):
        mocked_input.side_effect = ['y']
        var = self.printSentencesToVariable(directory='RFOSIAJ', language='en',
            maximum=1, plain=True, root_directory=self.root_directory)

        self.assertEqual(var[-28:],
            '\nNecessary files not found.\n')

    @mock.patch('opustools.opus_get.input', create=True)
    def test_download_necessary_files(self, mocked_input):
        mocked_input.side_effect = ['y', 'n', 'n']

        old_stdout = sys.stdout
        printout = io.StringIO()
        sys.stdout = printout
        OpusCat.openFiles(
            OpusCat(directory='RF', language='en', download_dir=self.tempdir1),
            os.path.join(self.tempdir1, 'RF_latest_xml_en.zip'), '')
        os.remove(os.path.join(self.tempdir1, 'RF_latest_xml_en.zip'))
        OpusCat.openFiles(
            OpusCat(directory='RF', language='en', download_dir=self.tempdir1),
            os.path.join(self.tempdir1, 'RF_latest_xml_en.zip'), '')
        sys.stdout = old_stdout
        self.assertTrue('No file found' in printout.getvalue())


if __name__ == '__main__':
    unittest.main()
