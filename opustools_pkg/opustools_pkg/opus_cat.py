import argparse
import zipfile
from .opus_get import OpusGet
from .parse.sentence_parser import SentenceParser

class SentenceParser(SentenceParser):
    
    def __init__(self, document, args):
        super().__init__(document, "", "", "", "", args.pa, args.sa, args.ca)
        self.args = args

        self.stopit = False

        self.parser.StartElementHandler = self.start_element_opuscat
        self.parser.EndElementHandler = self.end_element_opuscat
        
    def start_element_opuscat(self, name, attrs):
        self.start_element(name, attrs)
        if name == "s":
            self.posses = []

    def end_element_opuscat(self, name):
        self.end_element(name)
        if name in ["document", "text"]:
            self.stopit = True

    def processTokenizedSentence(self, sentence):
        newSentence, stop = sentence, 0
        if self.efound:
            self.sfound = False
            self.efound = False
            stop = -1
#            if newSentence == "":
#                newSentence = self.chara
#                self.chara = ""

        newSentence = self.addToken(sentence)

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
        parser.add_argument("-r", help="Release (default=latest)", default="latest")
        parser.add_argument("-pa", help="Print annotations, if they exist", action="store_true")
        parser.add_argument("-sa", help="Set sentence annotation attributes to be printed separated by commas, e.g. -sa pos,lem. To print all available attributes use -sa all_attrs (default=pos,lem)", default="pos,lem")
        parser.add_argument("-ca", help="Change annotation delimiter (default=|)", default="|")

        if len(arguments) == 0:
            self.args = parser.parse_args()
        else:
            self.args = parser.parse_args(arguments)

        try:
            try:
                self.lzip = zipfile.ZipFile(self.args.d+"_"+self.args.r+"_xml_"+self.args.l+".zip")
            except FileNotFoundError:
                self.lzip = zipfile.ZipFile("/proj/nlpl/data/OPUS/" + self.args.d + "/latest/xml/" + self.args.l + ".zip" , "r")
        except FileNotFoundError:
            print("\nRequested file not found. The following files are availble for downloading:\n")
            arguments = ["-d", self.args.d, "-s", self.args.l, "-t", " ", "-p", "xml", "-l", "-r", self.args.r]
            og = OpusGet(arguments)
            og.get_files()
            arguments.remove("-l")
            og = OpusGet(arguments)
            og.get_files()
            try:
                self.lzip = zipfile.ZipFile(self.args.d+"_"+self.args.r+"_xml_"+self.args.l+".zip")
            except FileNotFoundError:
                print("No file found with parameters " + str(self.args.__dict__))
            
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
        try:
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
        except AttributeError as e:
            print("Necessary files not found.")


