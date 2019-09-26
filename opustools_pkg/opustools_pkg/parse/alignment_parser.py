import zipfile
import gzip
import xml.parsers.expat
import re
import os

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
        self.ascore = None
        self.fromDoc = ''
        self.toDoc = ''

        self.zipFilesOpened = False

        self.alignParser = xml.parsers.expat.ParserCreate()

        self.alignParser.StartElementHandler = self.start_element

        self.sPar = None
        self.tPar = None

        self.args = args

        self.overThreshold = False
        self.nonAlignments = self.args.leave_non_alignments_out

        self.result = result
        self.mosessrc = mosessrc
        self.mosestrg = mosestrg

        self.slim = self.args.src_range.split('-')
        self.slim.sort()
        self.tlim = self.args.tgt_range.split('-')
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
        self.sourcezip = self.getZipFile(os.path.join(self.args.download_dir,
            self.args.directory+'_'+self.args.release+'_'+
            self.args.preprocess+'_'+self.fromto[0]+'.zip'),
            self.source,
            self.args.source_zip)
        self.targetzip = self.getZipFile(os.path.join(self.args.download_dir,
            self.args.directory+'_'+self.args.release+'_'+
            self.args.preprocess+'_'+self.fromto[1]+'.zip'),
            self.target,
            self.args.target_zip)

    def openSentenceParsers(self, attrs):
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
                        self.fromto[1], '-d', self.args.directory, '-r',
                        self.args.release, '-p', self.args.preprocess,
                        '-dl', self.args.download_dir, '-l']
                    if self.args.suppress_prompts:
                        arguments.append('-q')
                    og = OpusGet(arguments)
                    og.get_files()
                    arguments.remove('-l')
                    og = OpusGet(arguments)
                    og.get_files()

                    self.openZipFiles()
                    self.zipFilesOpened = True

            try:
                sourcefile = self.sourcezip.open(self.args.directory+'/'+
                    self.args.preprocess+'/'+attrs['fromDoc'][:-3], 'r')
                targetfile = self.targetzip.open(self.args.directory+'/'+
                    self.args.preprocess+'/'+attrs['toDoc'][:-3], 'r')
            except KeyError:
                sourcefile = self.sourcezip.open(attrs['fromDoc'], 'r')
                targetfile = self.targetzip.open(attrs['toDoc'], 'r')

        if self.sPar and self.tPar:
            self.sPar.document.close()
            self.tPar.document.close()

        pre = self.args.preprocess
        if pre == 'raw' and self.args.directory == 'OpenSubtitles':
            pre = 'rawos'

        st = ['src', 'trg']
        langs = [self.args.source, self.args.target]
        if self.switch_langs:
            st = ['trg', 'src']
            langs = [self.args.target, self.args.source]

        if self.args.fast:
            self.sPar = SentenceParser(sourcefile, st[0], pre,
                self.args.write_mode, langs[0], self.args.print_annotations,
                self.args.source_annotations,
                self.args.change_annotation_delimiter,
                self.args.preserve_inline_tags)
            self.tPar = SentenceParser(targetfile, st[1], pre,
                self.args.write_mode, langs[1], self.args.print_annotations,
                self.args.target_annotations,
                self.args.change_annotation_delimiter,
                self.args.preserve_inline_tags)
        else:
            self.sPar = ExhaustiveSentenceParser(sourcefile, pre, st[0],
                self.args.write_mode, langs[0], self.args.print_annotations,
                self.args.source_annotations,
                self.args.change_annotation_delimiter,
                self.args.preserve_inline_tags)
            self.sPar.storeSentences()
            self.tPar = ExhaustiveSentenceParser(targetfile, pre, st[1],
                self.args.write_mode, langs[1], self.args.print_annotations,
                self.args.target_annotations,
                self.args.change_annotation_delimiter,
                self.args.preserve_inline_tags)
            self.tPar.storeSentences()

    def initializeSentenceParsers(self, attrs):
        if self.args.write_mode == 'normal':
            docnames = ('\n# ' + attrs['fromDoc'] + '\n# ' +
                attrs['toDoc'] + '\n\n================================')
            if self.args.write != None:
                self.result.write(docnames + '\n')
            else:
                print(docnames)
        elif self.args.write_mode == 'moses' and self.args.print_file_names:
            sourceDoc = '\n<fromDoc>{}</fromDoc>'.format(attrs['fromDoc'])
            targetDoc = '\n<toDoc>{}</toDoc>'.format(attrs['toDoc'])
            if self.args.write != None:
                if self.result:
                    self.result.write(sourceDoc + targetDoc + '\n\n')
                else:
                    self.mosessrc.write(sourceDoc + '\n\n')
                    self.mosestrg.write(targetDoc + '\n\n')
            else:
                print(sourceDoc + targetDoc + '\n')
        self.openSentenceParsers(attrs)

    def processLink(self, attrs):
        self.ascore = None
        if self.args.attribute in attrs.keys():
            self.ascore = attrs[self.args.attribute]
            if self.args.threshold != None:
                if float(self.ascore) >= float(self.args.threshold):
                    self.overThreshold = True
            else:
                self.overThreshold = True
        else:
            if self.args.threshold == None:
                self.overThreshold = True
        m = re.search('(.*);(.*)', attrs['xtargets'])
        self.toids = m.group(2).split(' ')
        self.fromids = m.group(1).split(' ')

    def start_element(self, name, attrs):
        self.start = name
        if name == 'linkGrp':
            self.fromDoc = attrs['fromDoc']
            self.toDoc = attrs['toDoc']
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
            return -1

        srcAttrs, trgAttrs = {}, {}

        sourceSen, srcAttrs = self.sPar.readSentence(self.fromids)
        targetSen, trgAttrs = self.tPar.readSentence(self.toids)

        #if either side of the alignment is outside of the sentence limit, 
        #or the attribute value is under the given attribute
        #threshold, return -1, which skips printing of the alignment in 
        #PairPrinter.outputPair()
        if (self.sentencesOutsideLimit() or
                (self.args.attribute != 'any' and
                    self.overThreshold == False)):
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
            return sourceSen, targetSen

    def closeFiles(self):
        if self.zipFilesOpened:
            self.sourcezip.close()
            self.targetzip.close()
        if self.sPar and self.tPar:
            self.sPar.document.close()
            self.tPar.document.close()
