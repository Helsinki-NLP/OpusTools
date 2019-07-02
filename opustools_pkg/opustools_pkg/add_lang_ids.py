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
            annotations, anno_attrs, delimiter, suppress):
        super().__init__(document, preprocessing, direction, wmode, language,
            annotations, anno_attrs, delimiter)
        self.suppress = suppress
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
            try:
                clddetails = pycld2.detect(sentence)[2][0]
                cldlan = clddetails[1]
                cldconf = clddetails[2]/100
            except Exception as e:
                if not self.suppress:
                    print("Sentence id <{0}>: {1}".format(self.sid, e))
                cldlan = "un"
                cldconf = 0.0
            try:
                lilan, liconf = identifier.classify(sentence)
            except Exception as e:
                if not self.suppress:
                    print("Sentence id <{0}>: {1}".format(self.sid, e))
                lilan = "un"
                liconf = 0.0
            stag = '<s cld2="{0}" cld2conf="{1}" langid="{2}" langidconf="{3}" \
id="{4}">\n'.format(cldlan, round(cldconf,2), lilan, round(liconf,2), self.sid)
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
        parser.add_argument("-t", help="Target zip file path. By default, the \
original zip file is edited")
        parser.add_argument("-v", help="Verbosity. -v: print current xml file",
            action='count', default=0)
        parser.add_argument("-s", help="Suppress error messages in language \
detection", action='store_true')

        if len(arguments) == 0:
            self.args = parser.parse_args()
        else:
            self.args = parser.parse_args(arguments)

    def addIds(self):
        tempname = self.args.f.replace("/","_")+"_"+"add_lang_ids_temp.temp.zip"
        with zipfile.ZipFile(self.args.f, "r") as zip_arc:
            with zipfile.ZipFile(tempname, "w") as new_arc:
                for filename in zip_arc.filelist:
                    if self.args.v > 0:
                        print(filename.filename)
                    with zip_arc.open(filename.filename) as text_file:
                        if filename.filename[-4:] == ".xml":
                            sparser = LanguageIdAdder(text_file, "", "", False,
                                "","","","", self.args.s)
                            new_bytes = sparser.addIds()
                        else:
                            new_bytes = b"".join(text_file.readlines())
                        new_arc.writestr(filename, new_bytes)

        if self.args.t:
            os.rename(tempname, self.args.t)
        else:
            os.remove(self.args.f)
            os.rename(tempname, self.args.f)

