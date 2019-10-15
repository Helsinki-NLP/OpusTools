from .sentence_parser import SentenceParser

class ExhaustiveSentenceParser(SentenceParser):

    def __init__(self, document, preprocessing, direction, wmode,
            language, annotations, anno_attrs, delimiter, preserve):
        """Parse xml sentence files that have sentence ids in any order.

        Positional arguments:
        document -- Xml file to be parsed
        preprocessing -- Preprocessing type of the document
        direction -- Source/target direction
        wmode -- Write mode
        language -- Language id of the document
        annotations -- Print annotations
        anno_attrs -- Which annotations will be printed
        delimiter -- Annotation attribute delimiter
        preserve -- Preserve inline tags
        """

        super().__init__(document, direction, preprocessing, wmode,
            language, annotations, anno_attrs, delimiter, preserve)
        self.sentences = {}
        self.done = False

    def storeSentences(self):
        """Read document and store sentences in a dictionary."""
        self.document.readline()
        while not self.done:
            sentence = ''
            while True:
                line = self.document.readline()
                if not line:
                    self.done = True
                    break
                self.parseLine(line)
                if self.pre == 'xml' or self.pre == 'parsed':
                    sentence = self.addToken(sentence)
                    if (self.preserve and self.sfound
                            and self.start not in ['s', 'w']):
                        if type(line) == bytes:
                            line = line.decode('utf-8')
                        sentence += line.strip().replace('</s>', '')
                elif self.pre == 'raw':
                    if self.sfound and self.start == 's':
                        sentence = self.chara
                        self.chara = ''
                elif self.pre == 'rawos':
                    if self.preserve:
                        if self.sfound and self.start not in ['s', 'w']:
                            if type(line) == bytes:
                                line = line.decode('utf-8')
                            sentence += line.strip().replace('</s>', '')
                    else:
                        if self.sfound and self.start in ['s', 'time']:
                            sentence = self.chara
                if self.efound:
                    self.sfound = False
                    self.efound = False
                    self.chara = ''
                    break
            if self.sid != '':
                self.sentences[self.sid] = (sentence.strip(), self.attrs)
                self.sid = ''
        self.document.close()

    def getSentence(self, sid):
        """Return a sentence based on given sentence id."""
        if sid in self.sentences.keys():
            return self.sentences[sid]
        else:
            return '', {}

    def readSentence(self, ids):
        """Return a sequence of sentences based on given sentence ids."""
        if len(ids) == 0 or ids[0] == '':
            return '', []
        sentence = ''
        attrsList = []
        if self.wmode == 'tmx':
            sentence = self.addTuBeginning()
        for sid in ids:
            newSentence, attrs = self.getSentence(sid)
            sentence = self.addSentence(sentence, newSentence, sid)
            attrsList.append(attrs)
        if self.wmode == 'tmx':
            sentence = self.addTuEnding(sentence)

        return sentence[1:], attrsList
