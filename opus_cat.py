import argparse
import xml.parsers.expat
import zipfile

class SentenceParser:
    
    def __init__(self, document, args):
        self.document = document
        self.args = args

        self.start = ""
        self.sid = ""
        self.chara = ""
        self.end = ""
        
        self.stopit = False

        self.parser = xml.parsers.expat.ParserCreate()
        self.parser.StartElementHandler = self.start_element
        self.parser.CharacterDataHandler = self.char_data
        self.parser.EndElementHandler = self.end_element
        
        self.sfound = False
        self.efound = False

        self.annotations = self.args.pa
        if self.annotations:
            self.anno_attrs = self.args.sa.split(",")

        self.posses = []
        self.delimiter = self.args.ca

    def start_element(self, name, attrs):
        self.start = name
        if "id" in attrs.keys() and name == "s":
            self.sfound = True
            self.sid = attrs["id"]
        if name == "w" and self.annotations:
            if self.anno_attrs[0] == "all_attrs":
                attributes = list(attrs.keys())
                attributes.sort()
                for a in attributes:
                    self.posses.append(attrs[a])
            for a in self.anno_attrs:
                if a in attrs.keys():
                    self.posses.append(attrs[a])
        if name == "s":
            self.posses = []

    def char_data(self, data):
        if self.sfound:
            self.chara += data

    def end_element(self, name):
        self.end = name
        if name == "s":
            self.efound = True
        if name in ["document", "text"]:
            self.stopit = True

    def parseLine(self, line):
        self.parser.Parse(line.strip())

    def processTokenizedSentence(self, sentence):
        newSentence, stop = sentence, 0
        if self.efound:
            self.sfound = False
            self.efound = False
            stop = -1
#            if newSentence == "":
#                newSentence = self.chara
#                self.chara = ""
        if self.sfound:
            if self.start == "w" and self.end == "w":
                newSentence = sentence + " " + self.chara
                self.chara = ""
                if self.annotations:
                    for a in self.posses:
                        newSentence += self.delimiter + a
                    self.posses = []
        return newSentence, stop

    def readSentence(self):
        sentence = ""
        while True:
            line = self.document.readline()
            self.parseLine(line)
            newSentence, stop = self.processTokenizedSentence(sentence)
            sentence = newSentence
            if stop == -1 or self.stopit:
                break

        sentence = sentence.strip()

        if sentence == "":
            return ""

        if self.args.i:
            return sentence
        else:
            return '("' + self.sid + '")>' + sentence

class OpusCat:

    def __init__(self, arguments):
        parser = argparse.ArgumentParser(prog="opus_cat", description="Read a document from OPUS and print to STDOUT")

        parser.add_argument("-d", help="Corpus name", required=True)
        parser.add_argument("-l", help="Language", required=True)
        parser.add_argument("-i", help="Print without ids when using -p", action="store_true")
        parser.add_argument("-m", help="Maximum number of sentences", default="all")
        parser.add_argument("-p", help="Print in plain txt", action="store_true")
        parser.add_argument("-f", help="File name (if not given, prints all files)")
        parser.add_argument("-pa", help="Print annotations, if they exist", action="store_true")
        parser.add_argument("-sa", help="Set sentence annotation attributes to be printed deparated by commas, e.g. -sa pos,lem. To print all available attributes use -sa all_attrs (default=pos,lem)", default="pos,lem")
        parser.add_argument("-ca", help="Change annotation delimiter (default=|)", default="|")

        if len(arguments) == 0:
            self.args = parser.parse_args()
        else:
            self.args = parser.parse_args(arguments)

        self.lzip = zipfile.ZipFile("/proj/nlpl/data/OPUS/" + self.args.d + "/latest/xml/" + self.args.l + ".zip" , "r")

        if self.args.m == "all":
            self.maximum = -2
        else:
            self.maximum = int(self.args.m)

    def printFile(self, f, n):
        xml_break = False
        if self.args.p:
            spar = SentenceParser(f, self.args)
            print("\n# "+n+"\n")
            while True:
                sent = spar.readSentence()
                if sent != "":
                    print(sent)
                    self.maximum -= 1
                if spar.stopit or self.maximum == 0:
                    break
            spar.document.close()
        else:
            for line in f:
                line = line.decode("utf-8")
                if "<s id=" in line or "<s hun=" in line:
                    self.maximum -= 1
                    if self.maximum == -1:
                        xml_break = True
                        break
                print(line, end="")
        return xml_break

            
    def printSentences(self):
        if self.args.f:
            with self.lzip.open(self.args.f, "r") as f:
                self.printFile(f, self.args.f)
        else:
            for n in self.lzip.namelist():
                if n[-4:] == ".xml":
                    with self.lzip.open(n, "r") as f:
                        xml_break = self.printFile(f, n)
                    if xml_break:
                        break

                if self.maximum == 0:
                    break


