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

	def start_element(self, name, attrs):
		self.start = name
		if "id" in attrs.keys() and name == "s":
			self.sfound = True
			self.sid = attrs["id"]

	def char_data(self, data):
		self.chara = repr(data)

	def end_element(self, name):
		self.end = name
		if name == "s":
			self.efound = True
		if name == "text":
			self.stopit = True

	def parseLine(self, line):
		self.parser.Parse(line.strip())

	def processTokenizedSentence(self, sentence):
		newSentence, stop = sentence, 0
		if self.efound:
			self.sfound = False
			self.efound = False
			stop = -1
		if self.sfound:
			if self.start == "w" and self.end == "w":
				newSentence = sentence + " " + self.chara[1:-1]
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

		sentence = sentence[1:]

		if sentence == "":
			return ""

		if self.args.i:
			return sentence
		else:
			return '("' + self.sid + '")>' + sentence

class OpusCat:

	def __init__(self):
		self.parser = argparse.ArgumentParser(prog="python3 opus_cat.py", description="Read a document from OPUS and print to STDOUT")

		self.parser.add_argument("-d", help="Corpus name", required=True)
		self.parser.add_argument("-l", help="Language", required=True)
		self.parser.add_argument("-i", help="Print without ids", action="store_true")
		self.parser.add_argument("-m", help="Maximum number of sentences", default="all")

		self.args = self.parser.parse_args()

		self.lzip = zipfile.ZipFile("/proj/nlpl/data/OPUS/" + self.args.d + "/latest/xml/" + self.args.l + ".zip" , "r")

		self.maximum = int(self.args.m)

	def printSentences(self):
		for n in self.lzip.namelist():
			if n[-4:] == ".xml":
				with self.lzip.open(n, "r") as f:
					spar = SentenceParser(f, self.args)
					print("\n#"+n+"\n")
					while True:
						sent = spar.readSentence()
						if sent != "":
							print(sent)
							self.maximum -= 1
						if spar.stopit or self.maximum == 0:
							break
					spar.document.close()
			if self.maximum == 0:
				break

if __name__ == "__main__":
	oc = OpusCat()
	oc.printSentences()
