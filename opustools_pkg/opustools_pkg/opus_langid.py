import os
import zipfile
import argparse
import xml.parsers.expat
import cgi
import pycld2
from langid.langid import LanguageIdentifier, model
identifier = LanguageIdentifier.from_modelstring(model, norm_probs=True)

from .parse.sentence_parser import SentenceParser

class LanguageIdAdder(SentenceParser):

    def __init__(self, document, preprocessing, suppress, fileformat):
        super().__init__(document, preprocessing, "", False, "", "", "", "")
        self.pre = preprocessing
        self.suppress = suppress
        self.fifo = fileformat
        self.done = False

    def addIds(self):
        outdata = []
        outdata.append(self.document.readline())
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
                    outdata.append(line)
                else:
                    sentenceTags.append(line)
                if self.pre == "xml":
                    sentence = self.addToken(sentence)
                elif self.pre == "raw":
                    if self.sfound and self.start == "s":
                        sentence = cgi.escape(self.chara)
                        self.chara = ""
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
id="{4}">'.format(cldlan, round(cldconf,2), lilan, round(liconf,2), self.sid)
            if len(sentenceTags) > 0:
                if self.pre == "xml":
                    if self.fifo == "zip":
                        sentenceTags[0]=bytes(stag+"\n", "utf-8")
                    else:
                        sentenceTags[0]=stag+"\n"
                elif self.pre == "raw":
                    if self.fifo == "zip":
                        sentenceTags[0]=bytes(stag+sentence+"</s>\n", "utf-8")
                    else:
                        sentenceTags[0]=stag+sentence+"</s>\n"
            for item in sentenceTags:
                outdata.append(item)
        self.document.close()
        if self.fifo == "zip":
            return(b"".join(outdata))
        else:
            return("".join(outdata))

class OpusLangid:

    def __init__(self, arguments):
        parser = argparse.ArgumentParser(prog="add_lan_ids", description="Add" +
                " language ids to sentences in plain xml files or xml files " +
                "in zip archives using pycld2 and langid.py")
        parser.add_argument("-f", help="File path", required=True)
        parser.add_argument("-p", help="Preprocessing type (xml/raw)",
                required=True)
        parser.add_argument("-e", help="File format (zip/xml)", required=True)
        parser.add_argument("-t", help="Target file path. By default, the" +
                " original file is edited")
        parser.add_argument("-v", help="Verbosity. -v: print current xml file",
            action='count', default=0)
        parser.add_argument("-s", help="Suppress error messages in language " +
                "detection", action='store_true')

        if len(arguments) == 0:
            self.args = parser.parse_args()
        else:
            self.args = parser.parse_args(arguments)

    def editOrRemove(self, tempname):
        if self.args.t:
            os.rename(tempname, self.args.t)
        else:
            os.remove(self.args.f)
            os.rename(tempname, self.args.f)

    def addIdsZip(self):
        tempname = self.args.f.replace("/","_")+"_"+"opus_langid_temp.temp.zip"
        with zipfile.ZipFile(self.args.f, "r") as zip_arc:
            with zipfile.ZipFile(tempname, "w") as new_arc:
                for filename in zip_arc.filelist:
                    if self.args.v > 0:
                        print(filename.filename)
                    with zip_arc.open(filename.filename) as text_file:
                        if filename.filename[-4:] == ".xml":
                            sparser = LanguageIdAdder(text_file, self.args.p,
                                    self.args.s, self.args.e)
                            new_bytes = sparser.addIds()
                        else:
                            new_bytes = b"".join(text_file.readlines())
                        new_arc.writestr(filename, new_bytes)
        self.editOrRemove(tempname)

    def addIdsXml(self):
        tempname = self.args.f.replace("/","_")+"_"+"opus_langid_temp.temp.xml"
        with open(self.args.f, "r") as xml_file:
            with open(tempname, "w") as new_xml:
                sparser = LanguageIdAdder(xml_file, self.args.p, self.args.s,
                        self.args.e)
                new_xml.write(sparser.addIds())
        self.editOrRemove(tempname)

    def addIds(self):
        if self.args.e == "zip":
            self.addIdsZip()
        elif self.args.e == "xml":
            self.addIdsXml()

