import zipfile
import xml.parsers.expat
import re

from .sentence_parser import SentenceParser
from .exhaustive_sentence_parser import ExhaustiveSentenceParser
from ..opus_get import OpusGet

class AlignmentParser:

    def __init__(self, source, target, args, result, fromto):
        self.source = source
        self.target = target
        self.fromto = fromto

        self.start = ""

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

        self.slim = self.args.S.split("-")
        self.slim.sort()
        self.tlim = self.args.T.split("-")
        self.tlim.sort()
    
    def openZipFiles(self):
        try:
            self.sourcezip = zipfile.ZipFile(self.args.d+"_"+self.args.r+"_"+self.args.p+"_"+self.fromto[0]+".zip")
            self.targetzip = zipfile.ZipFile(self.args.d+"_"+self.args.r+"_"+self.args.p+"_"+self.fromto[1]+".zip")
        except FileNotFoundError:
            self.sourcezip = zipfile.ZipFile(self.source, "r")
            self.targetzip = zipfile.ZipFile(self.target, "r")

    def initializeSentenceParsers(self, attrs):
        #if link printing mode is activated, no need to open zipfiles and create sentence parsers
        if self.args.wm != "links":
            if self.args.wm == "normal":
                docnames = "\n# " + attrs["fromDoc"] + "\n# " + attrs["toDoc"] + "\n\n================================"
                if self.args.w != -1:
                    self.result.write(docnames + "\n")
                else:
                    print(docnames)

            try:
                sourcefile = open(attrs["fromDoc"][:-3], "r")
                targetfile = open(attrs["toDoc"][:-3], "r")
            except FileNotFoundError:
                if self.zipFilesOpened == False:
                    try:
                        self.openZipFiles()
                        self.zipFilesOpened = True
                    except FileNotFoundError:
                        print("\nZip files are not found. The following files are available for downloading:\n")
                        arguments = ["-s", self.fromto[0], "-t", self.fromto[1], "-d", self.args.d, "-r", self.args.r, "-p", self.args.p, "-l"]
                        og = OpusGet(arguments)
                        og.get_files()
                        arguments.remove("-l")
                        og = OpusGet(arguments)
                        og.get_files()

                        self.openZipFiles()
                        self.zipFilesOpened = True

                sourcefile = self.sourcezip.open(self.args.d+"/"+self.args.p+"/"+attrs["fromDoc"][:-3], "r")
                targetfile = self.targetzip.open(self.args.d+"/"+self.args.p+"/"+attrs["toDoc"][:-3], "r")
                    
            if self.sPar and self.tPar:
                self.sPar.document.close()
                self.tPar.document.close()
        
            pre = self.args.p
            if pre == "raw" and self.args.d == "OpenSubtitles":
                pre = "rawos"

            if self.args.f:
                self.sPar = SentenceParser(sourcefile, "src", pre, self.args.wm, self.args.s, self.args.pa, self.args.sa, self.args.ca)
                self.tPar = SentenceParser(targetfile, "trg", pre, self.args.wm, self.args.t, self.args.pa, self.args.ta, self.args.ca)
            else:
                self.sPar = ExhaustiveSentenceParser(sourcefile, pre, "src", self.args.wm, self.args.s, self.args.pa, self.args.sa, self.args.ca)
                self.sPar.storeSentences()
                self.tPar = ExhaustiveSentenceParser(targetfile, pre, "trg", self.args.wm, self.args.t, self.args.pa, self.args.ta, self.args.ca)
                self.tPar.storeSentences()                

    def processLink(self, attrs):
        if self.args.a in attrs.keys():
            if float(attrs[self.args.a]) >= float(self.args.tr):
                self.overThreshold = True
        m = re.search("(.*);(.*)", attrs["xtargets"])
        self.toids = m.group(2).split(" ")
        self.fromids = m.group(1).split(" ")

    def start_element(self, name, attrs):
        self.start = name
        if name == "linkGrp":
            self.initializeSentenceParsers(attrs)
        elif name == "link":
            self.processLink(attrs)

    def parseLine(self, line):
        self.alignParser.Parse(line)

    def sentencesOutsideLimit(self):
        snum = len(self.fromids)
        tnum = len(self.toids)
        if snum == 0 or self.fromids[0] == "":
            snum = 0
        if tnum == 0 or self.toids[0] == "":
            tnum = 0
        
        return (self.slim[0] != "all" and (snum < int(self.slim[0]) or snum > int(self.slim[-1]))) or \
                (self.tlim[0] != "all" and (tnum < int(self.tlim[0]) or tnum > int(self.tlim[-1])))

    def readPair(self):
        #tags other than link are printed in link printing mode, otherwise they are skipped
        if self.start != "link":
            if self.args.wm == "links":
                return 1
            else:
                return -1

        #no need to parse sentences in link printing mode
        if self.args.wm != "links":
            sourceSen = self.sPar.readSentence(self.fromids)
            targetSen = self.tPar.readSentence(self.toids)

        #if either side of the alignment is outside of the sentence limit, or the attribute value is under the given attribute
        #threshold, return -1, which skips printing of the alignment in PairPrinter.outputPair()
        if self.sentencesOutsideLimit() or (self.args.a != "any" and self.overThreshold == False):
            return -1
        #if filtering non-alignments is set to True and either side of the alignment has no sentences:
        #return -1
        elif self.nonAlignments and (self.fromids[0] == "" or self.toids[0] == ""):
            return -1
        else:
            self.overThreshold = False
            if self.args.wm != "links":
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
