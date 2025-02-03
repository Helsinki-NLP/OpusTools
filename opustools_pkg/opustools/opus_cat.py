import argparse
import zipfile
import os

from .opus_get import OpusGet
from .parse.block_parser import BlockParser
from .parse.sentence_parser import SentenceParser

def parse_type(preprocessing, get_annotations):
    def xml_parse(bp, block, sentence, no_ids, maximum):
        if block.name == 's':
            sid = block.attributes['id']
            sentence = ' '.join(sentence)
            if no_ids:
                print(sentence)
            else:
                print(f'("{sid}")>{sentence}')
            maximum -= 1
            sentence = []
        elif block.name == 'w':
            s_parent = bp.tag_in_parents('s', block)
            if s_parent:
                data = block.data.strip()
                sentence.append(data)
        return sentence, maximum

    def parsed_parse(bp, block, sentence, no_ids, maximum):
        if block.name == 's':
            sid = block.attributes['id']
            sentence = ' '.join(sentence)
            if no_ids:
                print(sentence)
            else:
                print(f'("{sid}")>{sentence}')
            maximum -= 1
            sentence = []
        elif block.name == 'w':
            s_parent = bp.tag_in_parents('s', block)
            if s_parent:
                data = block.data.strip()
                data += get_annotations(block)
                sentence.append(data)
        return sentence, maximum

    if preprocessing == 'xml':
        return xml_parse
    if preprocessing == 'parsed':
        return parsed_parse

class SentenceParser(SentenceParser):

    def __init__(self, document, preprocessing, set_attribute,
            change_annotation_delimiter):
        """Read sentence from a xml document.

        Arguments:
        document -- Xml document
        preprocessing -- Preprocessing type, xml or parsed
        set_attribute -- Set annotation attributes to be printed
        change_annotation_delimiter -- Change annotation delimiter
        """

        super().__init__(document, preprocessing, set_attribute,
                change_annotation_delimiter, None)

        #self.parse_block = parse_type(preprocessing, self.get_annotations)

class OpusCat:

    def __init__(self, directory=None, language=None, no_ids=False,
            maximum=-2, plain=False, file_name=None, release='latest',
            print_annotations=False, set_attribute=['pos', 'lem'],
            change_annotation_delimiter='|',
            root_directory='/projappl/nlpl/data/OPUS', download_dir='.' ):
        """Print the contents of a xml sentence file.

        Keyword arguments:
        directory -- Name of the corpus directory
        language -- Language of the corpus
        no_ids -- Print sentences without ids in plain mode
        maximum -- Maximum number of sentences to be printed (default all)
        plain -- Print sentence in plain text
        file_name -- Print a specific file within a corpus
        release -- Corpus release version (default latest)
        print_annotations -- Print annotations
        set_attribute -- Set annotation attributes (default pos,lem)
        change_annotation_delimiter -- Change annotation delimiter (default |)
        root_directory -- Root directory for corpus files
            (default /projappl/nlpl/data/OPUS)
        download_dir -- Directory where files will be downloaded (default .)
        """

        self.maximum = maximum
        self.directory = directory
        self.language = language
        self.release = release
        self.download_dir = download_dir
        self.set_attribute = set_attribute
        self.change_annotation_delimiter = change_annotation_delimiter
        self.no_ids = no_ids
        self.file_name = file_name
        self.plain = plain


        self.preprocess = 'xml'
        if print_annotations:
            self.preprocess = 'parsed'

        spar = SentenceParser(None, self.preprocess,
            self.set_attribute, self.change_annotation_delimiter)
        self.parse_block = parse_type(self.preprocess, spar.get_annotations)

        self.openFiles(
            os.path.join(download_dir, directory+'_'+release+'_xml_'+
                language+'.zip'),
            os.path.join(root_directory, directory, release, 'xml',
                language+'.zip'))

    def openFiles(self, localfile, defaultpath):
        """Open zip file."""
        try:
            try:
                self.lzip = zipfile.ZipFile(localfile)
            except FileNotFoundError:
                self.lzip = zipfile.ZipFile(defaultpath)
        except FileNotFoundError:
            print('\nRequested file not found. The following files are '
                'availble for downloading:\n')
            arguments = ['-d', self.directory, '-s', self.language, '-t', '',
                '-p', 'xml', '-l', '-r', self.release, '-dl',
                self.download_dir]
            arguments={'directory': self.directory, 'source': self.language,
                'target': '', 'preprocess': 'xml', 'list_resources': True,
                'release': self.release, 'download_dir': self.download_dir}
            og = OpusGet(**arguments)
            og.get_files()
            arguments['list_resources'] = False
            og = OpusGet(**arguments)
            og.get_files()
            try:
                self.lzip = zipfile.ZipFile(localfile)
            except FileNotFoundError:
                print('No file found')

    def printFile(self, f, n):
        """Print sentences from a document."""
        if self.maximum == 0:
            return
        if self.plain:
            print('\n# '+n+'\n')
            maximum = self.maximum
            stop = False
            sentence = []
            bp = BlockParser(f, data_tag='w', doc_size=0)
            blocks, cur_pos = bp.get_complete_blocks(0)
            while blocks:
                for block in blocks:
                    sentence, maximum = self.parse_block(bp, block, sentence, self.no_ids, maximum)
                    if maximum == 0:
                        self.maximum = 0
                        stop = True
                        break
                if stop:
                    break
                blocks, cur_pos = bp.get_complete_blocks(0)

        else:
            for line in f:
                line = line.decode('utf-8')
                print(line, end='')
                if '</s>' in line:
                    self.maximum -= 1
                    if self.maximum == 0:
                        break

    def printSentences(self):
        """Print sentences from documents in a zip file."""
        try:
            if self.file_name:
                with self.lzip.open(self.file_name, 'r') as f:
                    self.printFile(f, self.file_name)
            else:
                for n in self.lzip.namelist():
                    if n[-4:] == '.xml':
                        with self.lzip.open(n, 'r') as f:
                            self.printFile(f, n)
        except AttributeError as e:
            print('Necessary files not found.')


