import os
import zipfile
import argparse
import xml.parsers.expat
import pycld2
from langid.langid import LanguageIdentifier, model
identifier = LanguageIdentifier.from_modelstring(model, norm_probs=True)

from .parse.sentence_parser import SentenceParser

class LanguageIdAdder(SentenceParser):

    def __init__(self, document, preprocessing, direction, wmode, language,
            annotations, anno_attrs, delimiter):
        super().__init__(document, preprocessing, direction, wmode, language,
            annotations, anno_attrs, delimiter)
        self.done = False

    def addIds(self):
        outbytes = []
        outbytes.append(self.document.readline())
        while not self.done:
            sentenceTags = []
            sentence = ""
            while True:
                line = self.document.readline()
                if not line:
                    self.done = True
                    break
                self.parseLine(line)
                if not self.sfound:
                    outbytes.append(line)
                else:
                    sentenceTags.append(line)
                sentence = self.addToken(sentence)
                if self.efound:
                    self.sfound = False
                    self.efound = False
                    self.chara = ""
                    break
            clddetails = pycld2.detect(sentence)[2][0]
            cldlan = clddetails[1]
            cldconf = clddetails[2]
            lilan, liconf = identifier.classify(sentence)
            stag = '<s cld2="{0}" cld2conf="{1}" langid="{2}" langidconf="{3}" \
id="{4}">\n'.format(cldlan, cldconf, lilan, round(liconf, 2), self.sid)
            if len(sentenceTags) > 0:
                sentenceTags[0]=bytes(stag, "utf-8")
            for item in sentenceTags:
                outbytes.append(item)
        self.document.close()
        return(b"".join(outbytes))

class AddLanguageIds:

    def __init__(self, arguments):
        parser = argparse.ArgumentParser(prog="add_lan_ids", description="Add \
language ids to sentences in xml files in zip archives using pycld2 and \
langid.py")
        parser.add_argument("-f", help="Zip file path", required=True)

        if len(arguments) == 0:
            self.args = parser.parse_args()
        else:
            self.args = parser.parse_args(arguments)

    def addIds(self):
        with zipfile.ZipFile(self.args.f, "r") as zip_arc:
            with zipfile.ZipFile(self.args.f+"_temp.temp", "w") as new_arc:
                for filename in zip_arc.filelist:
                    print(filename.filename)
                    with zip_arc.open(filename.filename) as text_file:
                        if filename.filename[-4:] == ".xml":
                            sparser = LanguageIdAdder(text_file, "", "", False,
                                "","","","")
                            new_bytes = sparser.addIds()
                        else:
                            new_bytes = b"".join(text_file.readlines())
                        new_arc.writestr(filename, new_bytes)

        os.remove(self.args.f)
        os.rename(self.args.f+"_temp.temp", self.args.f)

