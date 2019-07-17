import zipfile
import gzip
import xml.parsers.expat
import re

from .sentence_parser import SentenceParser
from .exhaustive_sentence_parser import ExhaustiveSentenceParser
from ..opus_get import OpusGet

class AlignmentParser:

    def __init__(self, source, target, args, result, mosessrc, mosestrg,
            fromto, switch_langs):
        self.source = source
        self.target = target
        self.fromto = fromto
        self.switch_langs = switch_langs
        self.testConfidenceOn = False
        for item in [args.src_cld2, args.trg_cld2,
                args.src_langid, args.trg_langid]:
            if item:
                self.testConfidenceOn = True

        self.start = ''

        self.toids = []
        self.fromids = []

        self.zipFilesOpened = False

        self.alignParser = xml.parsers.expat.ParserCreate()

        self.alignParser.StartElementHandler = self.start_element

        self.sPar = None
        self.tPar = None

        self.args = args

        self.overThreshold = False
        self.nonAlignments = self.args.ln

        self.result = result
        self.mosessrc = mosessrc
        self.mosestrg = mosestrg

        self.slim = self.args.S.split('-')
        self.slim.sort()
        self.tlim = self.args.T.split('-')
        self.tlim.sort()

    def getZipFile(self, zipname, soutar, localfile):
        if localfile != None:
            openedzip = zipfile.ZipFile(localfile, 'r')
        else:
            try:
                openedzip = zipfile.ZipFile(zipname, 'r')
            except FileNotFoundError:
                openedzip = zipfile.ZipFile(soutar, 'r')

        return openedzip

    def openZipFiles(self):
        self.sourcezip = self.getZipFile((self.args.d+'_'+self.args.r+'_'+
                        self.args.p+'_'+self.fromto[0]+'.zip'),
                        self.source,
                        self.args.sz)
        self.targetzip = self.getZipFile((self.args.d+'_'+self.args.r+'_'+
                        self.args.p+'_'+self.fromto[1]+'.zip'),
                        self.target,
                        self.args.tz)

    def initializeSentenceParsers(self, attrs):
        #if link printing mode is activated, no need to open 
        #zipfiles and create sentence parsers
        if self.args.wm != 'links':
            if self.args.wm == 'normal':
                docnames = ('\n# ' + attrs['fromDoc'] + '\n# ' +
                    attrs['toDoc'] + '\n\n================================')
                if self.args.w != None:
                    self.result.write(docnames + '\n')
                else:
                    print(docnames)
            elif self.args.wm == 'moses' and self.args.pn:
                sourceDoc = '\n<fromDoc>{}</fromDoc>'.format(attrs['fromDoc'])
                targetDoc = '\n<toDoc>{}</toDoc>'.format(attrs['toDoc'])
                if self.args.w != None:
                    if self.result:
                        self.result.write(sourceDoc + targetDoc + '\n\n')
                    else:
                        self.mosessrc.write(sourceDoc + '\n\n')
                        self.mosestrg.write(targetDoc + '\n\n')
                else:
                    print(sourceDoc + targetDoc + '\n')

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
                        print(('\nZip files are not found. The following '
                            'files are available for downloading:\n'))
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

                sourcefile = self.sourcezip.open((self.args.d+'/'+self.args.p+
                    '/'+attrs['fromDoc'][:-3]), 'r')
                targetfile = self.targetzip.open((self.args.d+'/'+self.args.p+
                    '/'+attrs['toDoc'][:-3]), 'r')

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

    def processLink(self, attrs):
        if self.args.a in attrs.keys():
            if float(attrs[self.args.a]) >= float(self.args.tr):
                self.overThreshold = True
        m = re.search('(.*);(.*)', attrs['xtargets'])
        self.toids = m.group(2).split(' ')
        self.fromids = m.group(1).split(' ')

    def start_element(self, name, attrs):
        self.start = name
        if name == 'linkGrp':
            self.initializeSentenceParsers(attrs)
        elif name == 'link':
            self.processLink(attrs)

    def parseLine(self, line):
        self.start = ''
        self.alignParser.Parse(line)

    def sentencesOutsideLimit(self):
        snum = len(self.fromids)
        tnum = len(self.toids)
        if snum == 0 or self.fromids[0] == '':
            snum = 0
        if tnum == 0 or self.toids[0] == '':
            tnum = 0

        return ((self.slim[0] != 'all' and (snum < int(self.slim[0]) or
            snum > int(self.slim[-1]))) or (self.tlim[0] != 'all' and
            (tnum < int(self.tlim[0]) or tnum > int(self.tlim[-1]))))

    def testConfidence(self, confidence, attrsList, ider):
        if attrsList == []:
            return False
        if confidence:
            lan, conf = confidence
            for attrs in attrsList:
                if (lan != attrs[ider] or
                        float(conf) > float(attrs[ider+'conf'])):
                    return False
        return True

    def langIdConfidence(self, srcAttrs, trgAttrs):
        return (self.testConfidence(self.args.src_cld2, srcAttrs, 'cld2')
            and self.testConfidence(self.args.trg_cld2, trgAttrs, 'cld2')
            and self.testConfidence(self.args.src_langid, srcAttrs, 'langid')
            and self.testConfidence(self.args.trg_langid, trgAttrs, 'langid'))

    def readPair(self):
        #tags other than link are printed in link printing mode, 
        #otherwise they are skipped
        if self.start != 'link':
            if self.args.wm == 'links':
                return 1
            else:
                return -1

        srcAttrs, trgAttrs = {}, {}
        #no need to parse sentences in link printing mode
        if self.args.wm != 'links':
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
                not self.langIdConfidence(srcAttrs, trgAttrs)
                and self.args.wm != 'links'):
            return -1
        #if filtering non-alignments is set to True and either side of 
        #the alignment has no sentences:
        #return -1
        elif (self.nonAlignments and
                (self.fromids[0] == '' or self.toids[0] == '')):
            return -1
        else:
            self.overThreshold = False
            if self.args.wm != 'links':
                return sourceSen, targetSen
            else:
                return 1
        
    def closeFiles(self):
        if self.zipFilesOpened:
            self.sourcezip.close()
            self.targetzip.close()
        if self.sPar and self.tPar:
            self.sPar.document.close()
            self.tPar.document.close()
