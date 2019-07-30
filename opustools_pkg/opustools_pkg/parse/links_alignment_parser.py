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

        self.end = ''

        self.alignParser.EndElementHandler = self.end_element

    def end_element(self, name):
        self.end = ''
        if name == 'linkGrp':
            self.end = name

    def initializeSentenceParsers(self, attrs):
        #if link printing mode is activated, no need to open 
        #zipfiles and create sentence parsers
        if self.testConfidenceOn:
            self.openSentenceParsers(attrs)

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
            return 1

