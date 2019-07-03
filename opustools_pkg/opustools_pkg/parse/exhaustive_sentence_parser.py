from .sentence_parser import SentenceParser

class ExhaustiveSentenceParser(SentenceParser):

    def __init__(self, document, preprocessing, direction, wmode, language, annotations, anno_attrs, delimiter):
        super().__init__(document, direction, preprocessing, wmode, language, annotations, anno_attrs, delimiter)
        self.sentences = {}
        self.done = False

    def storeSentences(self):
        self.document.readline()
        while not self.done:
            sentence = ""
            while True:
                line = self.document.readline()
                if not line:
                    self.done = True
                    break
                self.parseLine(line)
                if self.pre == "xml" or self.pre == "parsed":
                    sentence = self.addToken(sentence)
                elif self.pre == "raw":
                    if self.sfound and self.start == "s":
                        sentence = self.chara
                        self.chara = ""
                elif self.pre == "rawos":
                    if self.sfound and self.start == "time" or self.start == "s":
                        sentence = self.chara
                if self.efound:
                    self.sfound = False
                    self.efound = False
                    self.chara = ""
                    break
            if self.sid != "":
                self.sentences[self.sid] = (sentence.strip(), self.attrs)
                self.sid = ""
        self.document.close()

    def getSentence(self, sid):
        if sid in self.sentences.keys():
            return self.sentences[sid]
        else:
            return "", {}

    def readSentence(self, ids):
        if len(ids) == 0 or ids[0] == "":
            return "", {}
        sentence = ""
        if self.wmode == "tmx":
            sentence = self.addTuBeginning()
        for sid in ids:
            newSentence, attrs = self.getSentence(sid)
            sentence = self.addSentence(sentence, newSentence, sid)
        if self.wmode == "tmx":
            sentence = self.addTuEnding(sentence)

        return sentence[1:], attrs
