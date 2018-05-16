import argparse
import zipfile
import gzip
import xml.parsers.expat
import re

class SentenceParser:
	
	def __init__(self, document, direction, preprocessing, wmode, language):
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

		self.wmode = wmode
		self.language = language

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

	def addTuBeginning(self):
		sentences = " "
		if self.direction == "src":
			sentences = sentences + "\t\t<tu>\n"
		sentences = sentences + '\t\t\t<tuv xml:lang="'+self.language+'"><seg>'
		return sentences
		
	def addSentence(self, sentences, sentence):
		if self.wmode == "normal":
			sentences = sentences + "\n(" + self.direction + ')="' + str(self.sid) + '">' + sentence
		elif self.wmode == "moses" or self.wmode == "tmx":
			sentences = sentences + " " + sentence
			sentences = sentences.replace("<seg> ", "<seg>")
		return sentences

	def addTuEnding(self, sentences):
		sentences = sentences + "</seg></tuv>"
		if self.direction == "trg":
			sentences = sentences + "\n\t\t</tu>"
		return sentences

	def readSentence(self, ids):
		if len(ids) == 0 or ids[0] == "":
			return ""
		sentences = ""
		
		if self.wmode == "tmx":
			sentences = self.addTuBeginning()

		for i in ids:
			sentence = ""
			while True:
				line = self.document.readline()
				self.parseLine(line)
				newSentence, stop = self.processSentence[self.pre](sentence, ids)
				sentence = newSentence
				if stop == -1:
					break

			sentences = self.addSentence(sentences, sentence)
		
		if self.wmode == "tmx":
			sentences = self.addTuEnding(sentences)

		return sentences[1:]

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
			#if link printing mode is activated, no need to open zipfiles and create sentence parsers
			if not self.args.l:
				if self.args.wm == "normal":
					docnames = "\n# " + attrs["fromDoc"] + "\n# " + attrs["toDoc"] + "\n\n================================"
					if self.args.w != -1:
						self.result.write(docnames + "\n")
					else:
						print(docnames)

				szipfile = self.sourcezip.open(self.args.d+"/"+self.args.p+"/"+attrs["fromDoc"][:-3], "r")
				tzipfile = self.targetzip.open(self.args.d+"/"+self.args.p+"/"+attrs["toDoc"][:-3], "r")

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
		#tags other than link are printed in link printing mode, otherwise they are skipped
		if self.start != "link":
			if self.args.l:
				return 1
			else:
				return -1

		#no need to parse sentences in link printing mode
		if not self.args.l:
			sourceSen = self.sPar.readSentence(self.fromids)
			targetSen = self.tPar.readSentence(self.toids)

		#if either side of the alignment is outside of the sentence limit, or the attribute value is under the given attribute
		#treshold, return -1, which skips printing of the alignment in PairPrinter.outputPair()
		if self.sentencesOverLimit() or (self.args.a != "any" and self.overTreshold == False):
			return -1
		#if filtering non-alignments is set to True and either side of the alignment has no sentences:
		#return -1
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
		parser.add_argument("-S", help="Maximum number of source sentences in alignments (range is allowed, eg. -S 1-2)", default="all")
		parser.add_argument("-T", help="Maximum number of target sentences in alignments (range is allowed, eg. -T 1-2)", default="all")
		parser.add_argument("-a", help="Set attribute for filttering", default="any")
		parser.add_argument("-tr", help="Set threshold for an attribute", default=0)
		parser.add_argument("-ln", help="Leave non-alignments out", action="store_true")
		parser.add_argument("-w", help="Write to file. Enter two file names separated by a comma when writing in moses format \
										(eg. -w moses.src,moses.trg). Otherwise enter one file name.", default=-1)
		parser.add_argument("-wm", help="Set writing mode (moses, tmx)", default="normal")
		parser.add_argument("-l", help="Print links", action="store_true")
		
		self.args = parser.parse_args()

		self.fromto = [self.args.s, self.args.t]
		self.fromto.sort()

		self.alignment = "/proj/nlpl/data/OPUS/"+self.args.d+"/"+self.args.r+"/xml/"+self.fromto[0]+"-"+self.fromto[1]+".xml.gz"
		self.source = "/proj/nlpl/data/OPUS/"+self.args.d+"/"+self.args.r+"/"+self.args.p+"/"+self.fromto[0]+".zip"
		self.target = "/proj/nlpl/data/OPUS/"+self.args.d+"/"+self.args.r+"/"+self.args.p+"/"+self.fromto[1]+".zip"
		self.moses = "/proj/nlpl/data/OPUS/"+self.args.d+"/"+self.args.r+"/moses/"+self.fromto[0]+"-"+self.fromto[1]+".txt.zip"

		self.resultfile = None

		if self.args.w != -1:
			self.filenames = self.args.w.split(",")
			if self.args.wm == "moses":	
				self.mosessrc = open(self.filenames[0], "w")
				self.mosestrg = open(self.filenames[1], "w")
			else:
				self.resultfile = open(self.filenames[0], "w")

	def printPair(self, sPair):
		if self.args.l:
			print(sPair)
		else:
			if self.args.wm == "moses":
				print(sPair[0] + "\t" + sPair[1])
			else:
				print(sPair[0] + "\n" + sPair[1])
			if self.args.wm == "normal":
				print("================================")
	
	def writePair(self, sPair):
		if self.args.l:
			self.resultfile.write(sPair+"\n")
		else:
			if self.args.wm == "moses":
				self.mosessrc.write(sPair[0]+"\n")
				self.mosestrg.write(sPair[1]+"\n")
			else:
				self.resultfile.write(sPair[0] + "\n" + sPair[1] + "\n")
			if self.args.wm == "normal":
				self.resultfile.write("================================\n")

	def outputPair(self, par, line):
		par.parseLine(line)
		sPair = par.readPair()

		par.fromids = []
		par.toids = []
		
		#if the sentence pair doesn't meet the requirements in AlignmentParser.readLine(),
		#don't output the sentence pair and return 0, which won't increment the pairs-counter in printPairs()
		if sPair == -1:
			return 0, sPair
		
		if sPair == 1:
			sPair = line.decode("utf-8")[:-1]

		if self.args.w != -1:
			self.writePair(sPair)
		else:
			self.printPair(sPair)

		#if the sentence pair is printed:
		#return 1, which will increment the pairs-counter in printPairs()		
		if par.start == "link":
			return 1, sPair
		return 0, sPair

	def addTmxHeader(self):
		tmxheader = '<tmx version="1.4.">\n<header srclang="' + self.fromto[0] + \
					'"\n\tadminlang="en"\n\tsegtype="sentence"\n\tdatatype="PlainText" />\n\t<body>'
		if self.args.w != -1:
			self.resultfile.write(tmxheader + "\n")
		else:
			print(tmxheader)

	def addTmxEnding(self):
		if self.args.w != -1:
			self.resultfile.write("\t</body>\n</tmx>")
		else:
			print("\t</body>\n</tmx>")

	def addLinkFileEnding(self):
		if self.args.w != -1:
			self.resultfile.write("  </linkGrp>\n</cesAlign>")
		else:
			print("  </linkGrp>\n</cesAlign>")

	def closeResultFiles(self):
		if self.args.wm == "moses":	
			self.mosessrc.close()
			self.mosestrg.close()
		elif self.args.wm == "tmx":
			self.resultfile.close()

	def printPairs(self):
		par = AlignmentParser(self.alignment, self.source, self.target, self.args, self.resultfile)

		if self.args.wm == "tmx":
			self.addTmxHeader()

		with gzip.open(self.alignment) as gzipAlign:
			if self.args.m == "all":
				for line in gzipAlign:
					lastline = self.outputPair(par, line)[1]
			else:
				pairs = int(self.args.m)
				while True:
					line = gzipAlign.readline()
					link, lastline = self.outputPair(par, line)
					pairs -= link
					if pairs == 0:
						break

		if self.args.l and lastline != "</cesAlign>":
			self.addLinkFileEnding()

		if self.args.wm == "tmx":
			self.addTmxEnding()
			
		par.closeFiles()

		if self.args.w != -1:
			self.closeResultFiles()

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


