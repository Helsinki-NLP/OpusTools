import os
import zipfile
import argparse
import cgi
import tempfile

import pycld2
from langid.langid import LanguageIdentifier, model
identifier = LanguageIdentifier.from_modelstring(model, norm_probs=True)

from .parse.sentence_parser import SentenceParser

class LanguageIdAdder(SentenceParser):

    def __init__(self, suppress, iszip):
        super().__init__('', '', '', False, '', '', '', '', False)
        self.iszip = iszip
        self.suppress = suppress

    def detectLanguage(self, sentence, sid):
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
        done = False
        outfile.write(infile.readline())
        while not done:
            skippedTags = []
            sentence = []
            while True:
                self.oneLineSStart = False
                self.oneLineSEnd = False
                line = infile.readline()
                if not line:
                    done = True
                    break
                self.parseLine(line)
                if not self.sfound:
                    outfile.write(line)
                else:
                    skippedTags.append(line)
                    sentence.append(self.chara)
                    self.chara = ''
                if self.efound:
                    self.sfound = False
                    self.efound = False
                    self.chara = ''
                    break
            sentence = ' '.join(sentence)
            indent = ''
            if len(skippedTags) > 0:
                for c in skippedTags[0]:
                    if c == ' ':
                        indent += ' '
                    else:
                        break
            cldlan, cldconf, lilan, liconf = self.detectLanguage(sentence,
                    self.sid)
            self.attrs['cld2'] = cldlan
            self.attrs['cld2conf'] = cldconf
            self.attrs['langid'] = lilan
            self.attrs['langidconf'] = liconf
            attributes = []
            for k in sorted(self.attrs.keys()):
                attributes.append('{0}="{1}"'.format(k, self.attrs[k]))

            stag = '{0}<s {1}>\n'.format(indent, ' '.join(attributes))
            if self.oneLineSStart and self.oneLineSEnd:
                stag = stag[:-1] + cgi.escape(sentence) + '</s>\n'
            if self.iszip:
                stag = bytes(stag, 'utf-8')
            if len(skippedTags) > 0:
                skippedTags[0]=stag
            for item in skippedTags:
                outfile.write(item)

class OpusLangid:

    def __init__(self, file_path=None, target_file_path=None, verbosity=0,
            suppress_errors=False):

        self.file_path = file_path
        self.target_file_path = target_file_path
        self.verbosity = verbosity
        self.suppress_errors = suppress_errors

    def processFiles(self):
        try:
            tempname = tempfile.mkstemp()
            with zipfile.ZipFile(self.file_path, 'r') as zip_arc:
                with zipfile.ZipFile(tempname[1], 'w') as new_arc:
                    for filename in zip_arc.filelist:
                        if self.verbosity > 0:
                            print(filename.filename)
                        with zip_arc.open(filename.filename) as infile:
                            if filename.filename[-4:] == '.xml':
                                tempxml = tempfile.mkstemp()
                                with open(tempxml[1], 'wb') as outfile:
                                    sparser = LanguageIdAdder(
                                        self.suppress_errors, True)
                                    sparser.addIds(infile, outfile)
                                new_arc.write(tempxml[1], filename.filename)
                                os.remove(tempxml[1])
                            else:
                                new_bytes = b''.join(infile.readlines())
                                new_arc.writestr(filename, new_bytes)
        except zipfile.BadZipfile:
            tempname = tempfile.mkstemp()
            sparser = LanguageIdAdder(self.suppress_errors, False)
            with open(self.file_path, 'r') as infile:
                with open(tempname[1], 'w') as outfile:
                    sparser.addIds(infile, outfile)

        if self.target_file_path:
            os.rename(tempname[1], self.target_file_path)
        else:
            os.remove(self.file_path)
            os.rename(tempname[1], self.file_path)


