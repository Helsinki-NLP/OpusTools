import xml.parsers.expat

class SentenceParser:
	
	def __init__(self, document, direction, preprocessing, wmode, language, annotations, delimiter):
		self.document = document
		self.direction = direction
		self.pre = preprocessing
		self.annotations = annotations
		self.delimiter = delimiter

		self.start = ""
		self.sid = ""
		self.chara = ""
		self.end = ""

		self.lemma = ""
		self.pos = ""
		
		self.parser = xml.parsers.expat.ParserCreate()
		self.parser.StartElementHandler = self.start_element
		self.parser.CharacterDataHandler = self.char_data
		self.parser.EndElementHandler = self.end_element
		
		self.sfound = False
		self.efound = False

		self.wmode = wmode
		self.language = language

		self.processSentence = {"parsed":self.processTokenizedSentence, "xml":self.processTokenizedSentence, "raw":self.processRawSentence, 
								"rawos":self.processRawSentenceOS}

	def start_element(self, name, attrs):
		self.start = name
		if "id" in attrs.keys() and name == "s":
			self.sfound = True
			self.sid = attrs["id"]
		if name == "w":
			if self.pre == "parsed":
				if "lemma" in attrs.keys():
					self.lemma = attrs["lemma"]
				if "upos" in attrs.keys():
					self.pos = attrs["upos"]
				if "feats" in attrs.keys():
					self.pos = self.pos + self.delimiter + attrs["feats"].replace("|", self.delimiter)
			else:
				if "lem" in attrs.keys():
					self.lemma = attrs["lem"]
				if "pos" in attrs.keys():
					self.pos = attrs["pos"]

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
				if self.annotations:
					newSentence = newSentence + self.delimiter + self.pos + self.delimiter + self.lemma
					self.pos = ""
					self.lemma = ""
					self.feats = ""
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
		sentences = sentences + '\t\t\t<tuv xml:lang="' + self.language + '"><seg>'
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

			if self.pre == "xml" or self.pre == "parsed":
				sentence = sentence[1:]

			sentences = self.addSentence(sentences, sentence)
		
		if self.wmode == "tmx":
			sentences = self.addTuEnding(sentences)

		return sentences[1:]
