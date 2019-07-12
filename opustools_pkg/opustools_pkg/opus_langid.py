import os
import zipfile
import argparse
import pycld2
import cgi
from langid.langid import LanguageIdentifier, model
identifier = LanguageIdentifier.from_modelstring(model, norm_probs=True)

from .parse.sentence_parser import SentenceParser

class LanguageIdAdder(SentenceParser):

    def __init__(self, suppress, iszip):
        super().__init__('', '', '', False, '', '', '', '')
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

    def __init__(self, arguments):
        parser = argparse.ArgumentParser(prog='add_lan_ids',
            description= ('Add language ids to sentences in plain xml files '
                        'or xml files in zip archives using pycld2 and '
                        'langid.py'))
        parser.add_argument('-f', help='File path', required=True)
        parser.add_argument('-t',
            help='Target file path. By default, the original file is edited')
        parser.add_argument('-v', help='Verbosity. -v: print current xml file',
            action='count', default=0)
        parser.add_argument('-s',
            help='Suppress error messages in language detection',
            action='store_true')

        if len(arguments) == 0:
            self.args = parser.parse_args()
        else:
            self.args = parser.parse_args(arguments)

    def processFiles(self):
        try:
            tempname = (self.args.f.replace('/','_')+
                    '_opus_langid_temp.temp.zip')
            with zipfile.ZipFile(self.args.f, 'r') as zip_arc:
                with zipfile.ZipFile(tempname, 'w') as new_arc:
                    for filename in zip_arc.filelist:
                        if self.args.v > 0:
                            print(filename.filename)
                        with zip_arc.open(filename.filename) as infile:
                            if filename.filename[-4:] == '.xml':
                                tempxml = (filename.filename.replace('/','_')+
                                        '_opus_langid_temp.temp.xml')
                                with open(tempxml, 'wb') as outfile:
                                    sparser = LanguageIdAdder(self.args.s, True)
                                    sparser.addIds(infile, outfile)
                                new_arc.write(tempxml, filename.filename)
                                os.remove(tempxml)
                            else:
                                new_bytes = b''.join(infile.readlines())
                                new_arc.writestr(filename, new_bytes)
        except zipfile.BadZipfile:
            tempname = (self.args.f.replace('/','_')+
                    '_opus_langid_temp.temp.xml')
            sparser = LanguageIdAdder(self.args.s, False)
            with open(self.args.f, 'r') as infile:
                with open(tempname, 'w') as outfile:
                    sparser.addIds(infile, outfile)

        if self.args.t:
            os.rename(tempname, self.args.t)
        else:
            os.remove(self.args.f)
            os.rename(tempname, self.args.f)

