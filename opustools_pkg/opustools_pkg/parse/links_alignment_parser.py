import zipfile
import gzip
import xml.parsers.expat
import re

from .alignment_parser import AlignmentParser
from .sentence_parser import SentenceParser
from .exhaustive_sentence_parser import ExhaustiveSentenceParser
from ..opus_get import OpusGet

class LinksAlignmentParser(AlignmentParser):

    def __init__(self, source, target, args, result, mosessrc, mosestrg,
            fromto, switch_langs):
        super().__init__(source, target, args, result, mosessrc,
            mosestrg, fromto, switch_langs)

    def initializeSentenceParsers(self, attrs):
        #if link printing mode is activated, no need to open 
        #zipfiles and create sentence parsers
        if self.testConfidenceOn:
            docnames = ('\n# ' + attrs['fromDoc'] + '\n# ' +
                attrs['toDoc'] + '\n\n================================')
            if self.args.w != None:
                self.result.write(docnames + '\n')
            else:
                print(docnames)

            try:
                if attrs['fromDoc'][-3:] == '.gz':
                    sourcefile = gzip.open(attrs['fromDoc'], 'rb')
                else:
                    sourcefile = open(attrs['fromDoc'], 'r')
                if attrs['toDoc'][-3:] == '.gz':
                    targetfile = gzip.open(attrs['toDoc'], 'rb')
                else:
                    targetfile = open(attrs['toDoc'], 'r')
            except FileNotFoundError:
                if self.zipFilesOpened == False:
                    try:
                        self.openZipFiles()
                        self.zipFilesOpened = True
                    except FileNotFoundError:
                        print('\nZip files are not found. The following '
                            'files are available for downloading:\n')
                        arguments = ['-s', self.fromto[0], '-t',
                            self.fromto[1], '-d', self.args.d, '-r',
                            self.args.r, '-p', self.args.p, '-l']
                        og = OpusGet(arguments)
                        og.get_files()
                        arguments.remove('-l')
                        og = OpusGet(arguments)
                        og.get_files()

                        self.openZipFiles()
                        self.zipFilesOpened = True

                sourcefile = self.sourcezip.open(self.args.d+'/'+self.args.p+
                    '/'+attrs['fromDoc'][:-3], 'r')
                targetfile = self.targetzip.open(self.args.d+'/'+self.args.p+
                    '/'+attrs['toDoc'][:-3], 'r')

            if self.sPar and self.tPar:
                self.sPar.document.close()
                self.tPar.document.close()

            pre = self.args.p
            if pre == 'raw' and self.args.d == 'OpenSubtitles':
                pre = 'rawos'

            st = ['src', 'trg']
            langs = [self.args.s, self.args.t]
            if self.switch_langs:
                st = ['trg', 'src']
                langs = [self.args.t, self.args.s]

            if self.args.f:
                self.sPar = SentenceParser(sourcefile, st[0], pre,
                    self.args.wm, langs[0], self.args.pa, self.args.sa,
                    self.args.ca)
                self.tPar = SentenceParser(targetfile, st[1], pre,
                    self.args.wm, langs[1], self.args.pa, self.args.ta,
                    self.args.ca)
            else:
                self.sPar = ExhaustiveSentenceParser(sourcefile, pre, st[0],
                    self.args.wm, langs[0], self.args.pa, self.args.sa,
                    self.args.ca)
                self.sPar.storeSentences()
                self.tPar = ExhaustiveSentenceParser(targetfile, pre, st[1],
                    self.args.wm, langs[1], self.args.pa, self.args.ta,
                    self.args.ca)
                self.tPar.storeSentences()

    def readPair(self):
        #tags other than link are printed in link printing mode, 
        #otherwise they are skipped
        if self.start != 'link':
            return 1

        srcAttrs, trgAttrs = {}, {}
        #no need to parse sentences in link printing mode
        if self.testConfidenceOn:
            sourceSen, srcAttrs = self.sPar.readSentence(self.fromids)
            targetSen, trgAttrs = self.tPar.readSentence(self.toids)

        #if either side of the alignment is outside of the sentence limit, 
        #or the attribute value is under the given attribute
        #threshold, return -1, which skips printing of the alignment in 
        #PairPrinter.outputPair()
        if (self.sentencesOutsideLimit() or
                (self.args.a != 'any' and self.overThreshold == False)):
            return -1
        elif (self.testConfidenceOn and
                not self.langIdConfidence(srcAttrs, trgAttrs)):
            return -1
        #if filtering non-alignments is set to True and either side of 
        #the alignment has no sentences:
        #return -1
        elif (self.nonAlignments and
                (self.fromids[0] == '' or self.toids[0] == '')):
            return -1
        else:
            self.overThreshold = False
            if self.testConfidenceOn:
                return sourceSen, targetSen
            else:
                return 1
