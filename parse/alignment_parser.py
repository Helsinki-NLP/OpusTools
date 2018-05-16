import zipfile
import xml.parsers.expat
import re

from parse.sentence_parser import SentenceParser


class AlignmentParser:

    def __init__(self, alignment, source, target, args, result):
        self.start = ""

        self.toids = []
        self.fromids = []

        self.sourcezip = zipfile.ZipFile(source, "r")
        self.targetzip = zipfile.ZipFile(target, "r")

        self.alignParser = xml.parsers.expat.ParserCreate()

        self.alignParser.StartElementHandler = self.start_element

        self.sPar = None
        self.tPar = None

        self.args = args

        self.overTreshold = False
        self.nonAlignments = self.args.ln

        self.result = result

        self.slim = self.args.S.split("-")
        self.slim.sort()
        self.tlim = self.args.T.split("-")
        self.tlim.sort()

    def start_element(self, name, attrs):
        self.start = name
        if name == "linkGrp":
            # if link printing mode is activated, no need to open zipfiles and create sentence parsers
            if not self.args.l:
                if self.args.wm == "normal":
                    docnames = "\n# " + attrs["fromDoc"] + "\n# " + attrs[
                        "toDoc"] + "\n\n================================"
                    if self.args.w != -1:
                        self.result.write(docnames + "\n")
                    else:
                        print(docnames)

                szipfile = self.sourcezip.open(self.args.d + "/" + self.args.p + "/" + attrs["fromDoc"][:-3], "r")
                tzipfile = self.targetzip.open(self.args.d + "/" + self.args.p + "/" + attrs["toDoc"][:-3], "r")

                if self.sPar and self.tPar:
                    self.sPar.document.close()
                    self.tPar.document.close()

                pre = self.args.p
                if pre == "raw" and self.args.d == "OpenSubtitles":
                    pre = "rawos"

                self.sPar = SentenceParser(szipfile, "src", pre, self.args.wm, self.args.s)
                self.tPar = SentenceParser(tzipfile, "trg", pre, self.args.wm, self.args.t)

        elif name == "link":
            if self.args.a in attrs.keys():
                if float(attrs[self.args.a]) >= float(self.args.tr):
                    self.overTreshold = True
            m = re.search("(.*);(.*)", attrs["xtargets"])
            self.toids = m.group(2).split(" ")
            self.fromids = m.group(1).split(" ")

    def parseLine(self, line):
        self.alignParser.Parse(line)

    def sentencesOverLimit(self):
        snum = len(self.fromids)
        tnum = len(self.toids)

        return (self.slim[0] != "all" and (snum < int(self.slim[0]) or snum > int(self.slim[-1]))) or \
               (self.tlim[0] != "all" and (tnum < int(self.tlim[0]) or tnum > int(self.tlim[-1])))

    def readPair(self):
        # tags other than link are printed in link printing mode, otherwise they are skipped
        if self.start != "link":
            if self.args.l:
                return 1
            else:
                return -1

        # no need to parse sentences in link printing mode
        if not self.args.l:
            sourceSen = self.sPar.readSentence(self.fromids)
            targetSen = self.tPar.readSentence(self.toids)

        # if either side of the alignment is outside of the sentence limit, or the attribute value is under the given attribute
        # treshold, return -1, which skips printing of the alignment in PairPrinter.outputPair()
        if self.sentencesOverLimit() or (self.args.a != "any" and self.overTreshold == False):
            return -1
        # if filtering non-alignments is set to True and either side of the alignment has no sentences:
        # return -1
        elif self.nonAlignments and (self.fromids[0] == "" or self.toids[0] == ""):
            return -1
        else:
            self.overTreshold = False
            if not self.args.l:
                return sourceSen, targetSen
            else:
                return 1

    def closeFiles(self):
        self.sourcezip.close()
        self.targetzip.close()
