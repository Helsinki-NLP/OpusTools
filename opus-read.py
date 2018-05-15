import argparse
import zipfile
import gzip
import xml.parsers.expat
import re

class SentenceParser:
	
	def __init__(self, document, direction, preprocessing, sentencen):
		self.document = document
		self.direction = direction
		self.pre = preprocessing

		self.start = ""
		self.sid = ""
		self.chara = ""
		self.end = ""
		
		self.parser = xml.parsers.expat.ParserCreate()
		self.parser.StartElementHandler = self.start_element
		self.parser.CharacterDataHandler = self.char_data
		self.parser.EndElementHandler = self.end_element
		
		self.sfound = False
		self.efound = False

		self.sentencen = sentencen.split("-")
		self.sentencen.sort()

		self.processSentence = {"xml":self.processTokenizedSentence, "raw":self.processRawSentence, 
								"rawos":self.processRawSentenceOS}

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

	def parseLine(self, line):
		self.parser.Parse(line.strip())

	def processTokenizedSentence(self, sentence, ids):
		newSentence, stop = sentence, 0
		if self.efound:
			self.sfound = False
			self.efound = False
			if self.sid in ids:
				stop = -1
		if self.sfound and self.sid in ids:
			if self.start == "w" and self.end == "w":
				newSentence = sentence + " " + self.chara[1:-1]
		return newSentence, stop

	def processRawSentenceOS(self, sentence, ids):
		newSentence, stop = sentence, 0
		if self.efound:
			self.sfound = False
			self.efound = False
			if self.sid in ids:
				stop = -1
		if self.sfound and self.sid in ids:
			if self.start == "time" or self.start == "s":
				newSentence = self.chara[1:-1]
		return newSentence, stop

	def processRawSentence(self, sentence, ids):
		if self.start == "s" and self.sid in ids:
			return self.chara[1:-1], -1
		else:
			return sentence, 0

	def readSentence(self, ids):
		if (self.sentencen[0] == "all") or (len(ids) >= int(self.sentencen[0]) and len(ids) <= int(self.sentencen[-1])):
			if len(ids) == 0 or ids[0] == "":
				return ""
			sentences = ""
			for i in ids:
				sentence = ""
				while True:
					line = self.document.readline()
					self.parseLine(line)
					newSentence, stop = self.processSentence[self.pre](sentence, ids)
					sentence = newSentence
					if stop == -1:
						break
				sentences = sentences + "\n(" + self.direction + ')="' + str(self.sid) + '">' + sentence
			
			return sentences[1:]
		else:
			return -1

class AlignmentParser:

	def __init__(self, alignment, source, target, args):
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

	def start_element(self, name, attrs):
		self.start = name
		if name == "linkGrp":
			print("\n# " + attrs["fromDoc"] + "\n# " + attrs["toDoc"] + "\n")
			print("================================")

			szipfile = self.sourcezip.open(self.args.d+"/"+self.args.p+"/"+attrs["fromDoc"][:-3], "r")
			tzipfile = self.targetzip.open(self.args.d+"/"+self.args.p+"/"+attrs["toDoc"][:-3], "r")

			if self.sPar and self.tPar:
				self.sPar.document.close()
				self.tPar.document.close()
			
			pre = self.args.p
			if pre == "raw" and self.args.d == "OpenSubtitles":
				pre = "rawos"
			self.sPar = SentenceParser(szipfile, "src", pre, self.args.S)
			self.tPar = SentenceParser(tzipfile, "trg", pre, self.args.T)
			
		elif name == "link":
			if self.args.a in attrs.keys():
				if float(attrs[self.args.a]) >= float(self.args.tr):
					self.overTreshold = True
			elif self.args.a == "any":
					self.overTreshold = True
			m = re.search("(.*);(.*)", attrs["xtargets"])
			self.toids = m.group(2).split(" ")
			self.fromids = m.group(1).split(" ")

	def parseLine(self, line):
		self.alignParser.Parse(line)

	def readPair(self):
		sourceSen = self.sPar.readSentence(self.fromids)
		targetSen = self.tPar.readSentence(self.toids)
		if sourceSen == -1 or targetSen == -1 or self.overTreshold == False:
			return -1
		else:
			self.overTreshold = False
			return sourceSen + "\n" + targetSen

	def closeFiles(self):
		self.sourcezip.close()
		self.targetzip.close()

class MosesRead:

	def __init__(self, path, corpus, src, trg):
		self.documents = zipfile.ZipFile(path, "r")
		self.source = self.documents.open(corpus+"."+src+"-"+trg+"."+src, "r")
		self.target = self.documents.open(corpus+"."+src+"-"+trg+"."+trg, "r")

	def readPair(self):
		return "(src)>" + self.source.readline().decode("utf-8") + \
			"(trg)>"+ self.target.readline().decode("utf-8") + "================================"

	def printAll(self):
		for srcline in self.source:
			trgline = self.target.readline()
			print("(src)>" + srcline.decode("utf-8") + \
			"(trg)>"+ trgline.decode("utf-8") + "================================")
		
	def closeFiles(self):
		self.documents.close()

class PairPrinter:

	def __init__(self):
		parser = argparse.ArgumentParser(prog="opus-read", description="Read sentence alignments")

		parser.add_argument("-d", help="Corpus name", required=True)
		parser.add_argument("-s", help="Source language", required=True)
		parser.add_argument("-t", help="Target language", required=True)
		parser.add_argument("-r", help="Release (default=latest)", default="latest")
		parser.add_argument("-p", help="Pre-process-type (default=xml)", default="xml")
		parser.add_argument("-m", help="Maximum number of alignments", default="all")
		parser.add_argument("-S", help="Maximum number of source sentences in alignments (range is allowed, eg. 1-2)", default="all")
		parser.add_argument("-T", help="Maximum number of target sentences in alignments (range is allowed, eg. 1-2)", default="all")
		parser.add_argument("-a", help="Set attribute to filter by", default="any")
		parser.add_argument("-tr", help="Set threshold for an attribute", default=0)

		self.args = parser.parse_args()

		self.fromto = [self.args.s, self.args.t]
		self.fromto.sort()

		self.alignment = "/proj/nlpl/data/OPUS/"+self.args.d+"/"+self.args.r+"/xml/"+self.fromto[0]+"-"+self.fromto[1]+".xml.gz"
		self.source = "/proj/nlpl/data/OPUS/"+self.args.d+"/"+self.args.r+"/"+self.args.p+"/"+self.fromto[0]+".zip"
		self.target = "/proj/nlpl/data/OPUS/"+self.args.d+"/"+self.args.r+"/"+self.args.p+"/"+self.fromto[1]+".zip"
		self.moses = "/proj/nlpl/data/OPUS/"+self.args.d+"/"+self.args.r+"/moses/"+self.fromto[0]+"-"+self.fromto[1]+".txt.zip"

	def printPair(self, par, line):
		par.parseLine(line)
		if par.start == "link":
			sPair = par.readPair()

			par.fromids = []
			par.toids = []

			if sPair == -1:
				return 0

			print(sPair)
			print("================================")

			return 1
		return 0

	def printPairs(self):
		par = AlignmentParser(self.alignment, self.source, self.target, self.args)

		with gzip.open(self.alignment) as gzipAlign:
			if self.args.m == "all":
				for line in gzipAlign:
					self.printPair(par, line)
			else:
				pairs = int(self.args.m)
				while True:
					line = gzipAlign.readline()
					link = self.printPair(par, line)
					pairs -= link
					if pairs == 0:
						break

		par.closeFiles()

	def printPairsMoses(self):
		mread = MosesRead(self.moses, self.args.d, self.fromto[0], self.fromto[1])
		if self.args.m == "all":
			mread.printAll()
		else:
			print("\n# " + self.moses + "\n\n================================")
	
			for i in range(int(self.args.m)):
				print(mread.readPair())

			mread.closeFiles()

pp = PairPrinter()
if pp.args.p == "moses":
	pp.printPairsMoses()
else:
	pp.printPairs()


