import os
import zipfile
import argparse
import cgi
import tempfile
import re

import pycld2
from langid.langid import LanguageIdentifier, model
identifier = LanguageIdentifier.from_modelstring(model, norm_probs=True)

from .parse.sentence_parser import SentenceParser

def xml_parse(bp, block, sentence, sentences, id_set):
    if block.name == 's':
        sid = block.attributes['id']
        sentence.append(block.data.strip())
        sentence = ' '.join(sentence)
        sentences[sid] = (sentence, block.attributes)
        sentence = []
    elif block.name == 'w':
        s_parent = bp.tag_in_parents('s', block)
        if s_parent:
            data = block.data.strip()
            sentence.append(data)
    return sentence

class LanguageIdAdder(SentenceParser):

    def __init__(self, document, suppress, iszip, preprocessing):
        """Add language ids and confidence scores to sentences in a xml file.

        Positional arguments:
        suppress -- Suppress errors in language identification
        iszip -- Parse zip file (bytes) instead of plain text
        """

        super().__init__(document, preprocessing, '', '', None)
        self.iszip = iszip
        self.suppress = suppress

        self.parse_block = xml_parse

    def detectLanguage(self, sentence, sid):
        """Assign language ids and scores to a sentence."""
        try:
            clddetails = pycld2.detect(sentence)
        except Exception as e:
            if not self.suppress:
                print('Sentence id <{0}>: {1}'.format(sid, e))
            clddetails = (0, 0, ((0, 'un', 0.0), 0))
        try:
            lidetails = identifier.classify(sentence)
        except Exception as e:
            if not self.suppress:
                print('Sentence id <{0}>: {1}'.format(sid, e))
            lidetails = ('un', 0.0)

        cldlan = clddetails[2][0][1]
        cldconf = str(round(clddetails[2][0][2]/100, 2))
        lilan, liconf = [str(round(x,2)) if type(x) == float
                else x for x in lidetails]

        return cldlan, cldconf, lilan, liconf

    def addIds(self, infile, outfile):
        """Add language ids to sentences in an xml file."""

        for line in infile:
            if self.iszip:
                line = line.decode('utf-8')
            if '<s' in line:
                m = re.search('( cld2=".*?" cld2conf=".*?" langid=".*?" '
                    'langidconf=".*?")', line)
                if m:
                    line = line.replace(m.group(1), '')
                m = re.search(' id\="(.*?)"', line)
                if m:
                    sid = m.group(1)
                    sentence = self.get_sentence(sid)[0]
                    cldlan, cldconf, lilan, liconf = self.detectLanguage(sentence, sid)
                    new_tag_start = ('<s cld2="{}" cld2conf="{}" langid="{}" '
                        'langidconf="{}"'.format(cldlan, cldconf, lilan, liconf))
                    line = line.replace('<s', new_tag_start)
            if self.iszip:
                line = bytes(line, 'utf-8')
            outfile.write(line)

class OpusLangid:

    def __init__(self, file_path=None, target_file_path=None, verbosity=0,
            suppress_errors=False, preprocess='xml'):
        """Add language ids and confidence scores to sentences in plain xml
        files or xml file in zip archives.

        Keyword arguments:
        file_path -- Path to the file where language ids will be added
        target_file -- Path to the output file
        verbosity -- Report progress during language identification
        suppress_errors -- Suppress errors in language detection
        """

        self.file_path = file_path
        self.target_file_path = target_file_path
        self.verbosity = verbosity
        self.suppress_errors = suppress_errors
        self.preprocess = preprocess

    def processFiles(self):
        """Add language ids and confidence score to xml files."""
        try:
            tempname = tempfile.mkstemp()
            with zipfile.ZipFile(self.file_path, 'r') as zip_arc:
                with zipfile.ZipFile(tempname[1], 'w') as new_arc:
                    for filename in zip_arc.filelist:
                        if self.verbosity > 0:
                            print(filename.filename)
                        tempxml = tempfile.mkstemp()
                        if filename.filename[-4:] == '.xml':
                            with zip_arc.open(filename.filename) as infile:
                                sparser = LanguageIdAdder(infile,
                                    self.suppress_errors, True, self.preprocess)
                                sparser.store_sentences({})
                            with zip_arc.open(filename.filename) as infile:
                                with open(tempxml[1], 'wb') as outfile:
                                    sparser.addIds(infile, outfile)
                            new_arc.write(tempxml[1], filename.filename)
                        else:
                            with zip_arc.open(filename.filename) as infile:
                                new_bytes = b''.join(infile.readlines())
                            new_arc.writestr(filename, new_bytes)
                        os.remove(tempxml[1])
        except zipfile.BadZipfile:
            tempname = tempfile.mkstemp()
            with open(tempname[1], 'w') as outfile:
                with open(self.file_path, 'r') as infile:
                    sparser = LanguageIdAdder(infile,
                            self.suppress_errors, False, self.preprocess)
                    sparser.store_sentences({})
                with open(self.file_path, 'r') as infile:
                    sparser.addIds(infile, outfile)

        if self.target_file_path:
            os.rename(tempname[1], self.target_file_path)
        else:
            os.remove(self.file_path)
            os.rename(tempname[1], self.file_path)


