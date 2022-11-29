import os
import shutil
import zipfile
import argparse
import cgi
import tempfile
import re

import pycld2
from langid.langid import LanguageIdentifier, model
identifier = LanguageIdentifier.from_modelstring(model, norm_probs=True)

from .parse.block_parser import Block, BlockParser

class LanguageIdAdder(BlockParser):

    def __init__(self, document, out_file, suppress, iszip, preprocessing):
        """Add language ids and confidence scores to sentences in a xml file.

        Positional arguments:
        suppress -- Suppress errors in language identification
        iszip -- Parse zip file (bytes) instead of plain text
        """

        data_tag = 'w'
        if preprocessing == 'raw':
            data_tag = 's'

        super().__init__(document, data_tag, 0)
        self.out_file = out_file
        self.iszip = iszip
        self.suppress = suppress

        self.s_blocks = []

        def start_element(name, attrs):
            """Update current block"""
            sub_block = Block(parent=self.block, name=name, attributes=attrs)
            attr_str = ' '.join([f'{k}="{v}"' for k, v in sub_block.attributes.items()])
            if name not in {'s', 'w'}:
                self.write_to_out(f'<{sub_block.name} {attr_str}>\n')
            else:
                self.s_blocks.append(sub_block)
            self.block = sub_block

        def end_element(name):
            """Update complete blocks, and move up one level on block tree"""
            self.completeBlocks.append(self.block)
            if name not in {'s', 'w'}:
                self.write_to_out(f'{self.block.data}</{self.block.name}>\n')
            self.block = self.block.parent

        def char_data(data):
            """Update current block's character data"""
            self.block.data += data.lstrip()

        self.p.StartElementHandler = start_element
        self.p.EndElementHandler = end_element
        self.p.CharacterDataHandler = char_data

    def write_to_out(self, output):
        if self.iszip:
            output = bytes(output, 'utf-8')
        self.out_file.write(output)

    def xml_parse(self, block, sentence):
        if block.name == 's':
            sid = block.attributes['id']
            sentence.append(block.data.strip())
            sentence = ' '.join(sentence)
            cl, cc, ll, lc = self.detectLanguage(sentence, sid)
            for block in self.s_blocks:
                if block.name == 's':
                    block.attributes['cld2'] = cl
                    block.attributes['cld2conf'] = cc
                    block.attributes['langid'] = ll
                    block.attributes['langidconf'] = lc
                    attr_str = ' '.join([f'{k}="{v}"' for k, v in block.attributes.items()])
                    self.write_to_out(f'<{block.name} {attr_str}>{block.data}\n')
                else:
                    attr_str = ' '.join([f'{k}="{v}"' for k, v in block.attributes.items()])
                    self.write_to_out(f'<{block.name} {attr_str}>{block.data}</{block.name}>\n')
            self.write_to_out('</s>\n')

            sentence = []
            self.s_blocks = []
        elif block.name == 'w':
            s_parent = self.tag_in_parents('s', block)
            if s_parent:
                data = block.data.strip()
                sentence.append(data)
        return sentence

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

    def addIds(self):
        """Add language ids to sentences in an xml file."""

        sentence = []
        blocks, cur_pos = self.get_complete_blocks(0)
        while blocks:
            for block in blocks:
                sentence = self.xml_parse(block, sentence)
            blocks, cur_pos = self.get_complete_blocks(0)

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
                            with zip_arc.open(filename.filename) as infile, open(tempxml[1], 'wb') as outfile:
                                sparser = LanguageIdAdder(infile, outfile,
                                    self.suppress_errors, True, self.preprocess)
                                sparser.addIds()
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
                    sparser = LanguageIdAdder(infile, outfile,
                            self.suppress_errors, False, self.preprocess)
                    sparser.addIds()

        if self.target_file_path:
            shutil.move(tempname[1], self.target_file_path)
        else:
            os.remove(self.file_path)
            shutil.move(tempname[1], self.file_path)


