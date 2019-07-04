import os
import zipfile
import argparse
import xml.etree.ElementTree as ET
import pycld2
from langid.langid import LanguageIdentifier, model
identifier = LanguageIdentifier.from_modelstring(model, norm_probs=True)

class OpusLangid:

    def __init__(self, arguments):
        parser = argparse.ArgumentParser(prog="add_lan_ids", description="Add" +
                " language ids to sentences in plain xml files or xml files " +
                "in zip archives using pycld2 and langid.py")
        parser.add_argument("-f", help="File path", required=True)
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

    def detectLanguage(self, sentence, sid):
        try:
            clddetails = pycld2.detect(sentence)[2][0]
            cldlan = clddetails[1]
            cldconf = clddetails[2]/100
        except Exception as e:
            if not self.suppress:
                print("Sentence id <{0}>: {1}".format(sid, e))
            cldlan = "un"
            cldconf = "0.0"
        try:
            lilan, liconf = identifier.classify(sentence)
        except Exception as e:
            if not self.suppress:
                print("Sentence id <{0}>: {1}".format(sid, e))
            lilan = "un"
            liconf = "0.0"

        return cldlan, str(round(cldconf, 2)), lilan, str(round(liconf, 2))

    def addIds(self, filename):
        tree = ET.parse(filename)
        root = tree.getroot()
        for stag in root.iter("s"):
            if stag.find("w") != None:
                sentence = []
                for wtag in stag.iter("w"):
                    sentence.append(wtag.text)
                sentence = " ".join(sentence)
            else:
                sentence = stag.text
            cldlan, cldconf, lilan, liconf = self.detectLanguage(sentence, stag.attrib["id"])
            stag.attrib["cld2"] = cldlan
            stag.attrib["cld2conf"] = cldconf
            stag.attrib["langid"] = lilan
            stag.attrib["langidconf"] = liconf

        return tree

    def editOrRemove(self, tempname):
        if self.args.t:
            os.rename(tempname, self.args.t)
        else:
            os.remove(self.args.f)
            os.rename(tempname, self.args.f)

    def writeIdsToFile(self, filename, fileobj):
        if self.args.v > 0:
            print(filename)
        filename = filename.replace("/","_")+"_opus_langid_temp.temp.xml"
        tree = self.addIds(fileobj)
        tree.write(filename, encoding="utf-8", xml_declaration=True)
        return filename

    def processFiles(self):
        try:
            tempname = self.args.f.replace("/","_")+"_opus_langid_temp.temp.zip"
            with zipfile.ZipFile(self.args.f, "r") as zip_arc:
                with zipfile.ZipFile(tempname, "w") as new_arc:
                    for filename in zip_arc.filelist:
                        with zip_arc.open(filename.filename) as text_file:
                            if filename.filename[-4:] == ".xml":
                                temp_xml = self.writeIdsToFile(
                                        filename.filename, text_file)
                                with open(temp_xml, "rb") as temp_bytes:
                                    new_bytes = b"".join(temp_bytes.readlines())
                                os.remove(temp_xml)
                            else:
                                new_bytes = b"".join(text_file.readlines())
                            new_arc.writestr(filename, new_bytes)
        except zipfile.BadZipFile:
            tempname = self.writeIdsToFile(self.args.f, self.args.f)
        self.editOrRemove(tempname)

