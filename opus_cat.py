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

parser = argparse.ArgumentParser(prog="opus_cat", description="Read a document from OPUS and print to STDOUT")

parser.add_argument("-d", help="Corpus name", required=True)
parser.add_argument("-l", help="Language", required=True)
parser.add_argument("-i", help="Print without ids", action="store_true")
parser.add_argument("-m", help="Maximum number of sentences", default="all")

args = parser.parse_args()

lzip = zipfile.ZipFile("/proj/nlpl/data/OPUS/" + args.d + "/latest/xml/" + args.l + ".zip" , "r")

maximum = int(args.m)

for n in lzip.namelist():
	if n[-4:] == ".xml":
		with lzip.open(n, "r") as f:
			spar = SentenceParser(f, args)
			print("\n#"+n+"\n")
			while True:
				sent = spar.readSentence()
				if sent != "":
					print(sent)
					maximum -= 1
				if spar.stopit or maximum == 0:
					break
			spar.document.close()
	if maximum == 0:
		break
