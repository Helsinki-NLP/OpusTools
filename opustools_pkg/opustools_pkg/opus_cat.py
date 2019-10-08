import argparse
import zipfile
import os

from .opus_get import OpusGet
from .parse.sentence_parser import SentenceParser

class SentenceParser(SentenceParser):

    def __init__(self, document, print_annotations, set_attribute,
            change_annotation_delimiter, no_ids):
        super().__init__(document, '', '', '', '', print_annotations,
            set_attribute, change_annotation_delimiter, False)

        self.stopit = False
        self.no_ids = no_ids

        self.parser.StartElementHandler = self.start_element_opuscat
        self.parser.EndElementHandler = self.end_element_opuscat

    def start_element_opuscat(self, name, attrs):
        self.start_element(name, attrs)
        if name == 's':
            self.posses = []

    def end_element_opuscat(self, name):
        self.end_element(name)
        if name in ['document', 'text']:
            self.stopit = True

    def processTokenizedSentence(self, sentence):
        newSentence, stop = sentence, 0
        if self.efound:
            self.sfound = False
            self.efound = False
            stop = -1
#            if newSentence == "":
#                newSentence = self.chara
#                self.chara = ""

        newSentence = self.addToken(sentence)

        return newSentence, stop

    def readSentence(self):
        sentence = ''
        while True:
            line = self.document.readline()
            self.parseLine(line)
            newSentence, stop = self.processTokenizedSentence(sentence)
            sentence = newSentence
            if stop == -1 or self.stopit:
                break

        sentence = sentence.strip()

        if sentence == '':
            return ''

        if self.no_ids:
            return sentence
        else:
            return '("' + self.sid + '")>' + sentence

class OpusCat:

    def __init__(self, directory=None, language=None, no_ids=False,
            maximum='all', plain=False, file_name=None, release='latest',
            print_annotations=False, set_attribute=['pos', 'lem'],
            change_annotation_delimiter='|',
            root_directory='/proj/nlpl/data/OPUS', download_dir='.' ):

        if maximum == 'all':
            self.maximum = -2
        else:
            self.maximum = int(maximum)

        self.directory = directory
        self.language = language
        self.release = release
        self.download_dir = download_dir
        self.print_annotations = print_annotations
        self.set_attribute = set_attribute
        self.change_annotation_delimiter = change_annotation_delimiter
        self.no_ids = no_ids
        self.file_name = file_name
        self.plain = plain

        self.openFiles(
            os.path.join(download_dir, directory+'_'+release+'_xml_'+
                language+'.zip'),
            os.path.join(root_directory, directory, 'latest', 'xml',
                language+'.zip'))

    def openFiles(self, localfile, defaultpath):
        try:
            try:
                self.lzip = zipfile.ZipFile(localfile)
            except FileNotFoundError:
                self.lzip = zipfile.ZipFile(defaultpath)
        except FileNotFoundError:
            print('\nRequested file not found. The following files are '
                'availble for downloading:\n')
            arguments = ['-d', self.directory, '-s', self.language, '-t', ' ',
                '-p', 'xml', '-l', '-r', self.release, '-dl',
                self.download_dir]
            arguments={'directory': self.directory, 'source': self.language,
                'target': ' ', 'preprocess': 'xml', 'list_resources': True,
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
        xml_break = False
        if self.plain:
            spar = SentenceParser(f, self.print_annotations,
                self.set_attribute, self.change_annotation_delimiter,
                self.no_ids)
            print('\n# '+n+'\n')
            while True:
                sent = spar.readSentence()
                if sent != '':
                    print(sent)
                    self.maximum -= 1
                if spar.stopit or self.maximum == 0:
                    break
            spar.document.close()
        else:
            for line in f:
                line = line.decode('utf-8')
                if '<s id=' in line or '<s hun=' in line:
                    self.maximum -= 1
                    if self.maximum == -1:
                        xml_break = True
                        break
                print(line, end='')
        return xml_break

    def printSentences(self):
        try:
            if self.file_name:
                with self.lzip.open(self.file_name, 'r') as f:
                    self.printFile(f, self.file_name)
            else:
                for n in self.lzip.namelist():
                    if n[-4:] == '.xml':
                        with self.lzip.open(n, 'r') as f:
                            xml_break = self.printFile(f, n)
                        if xml_break:
                            break

                    if self.maximum == 0:
                        break
        except AttributeError as e:
            print('Necessary files not found.')


