import xml.parsers.expat
import html

class SentenceParserError(Exception):

    def __init__(self, message):
        """Raise error when sentence parsing fails.

        Keyword arguments:
        message -- Error message to be printed
        """

        self.message = message

class SentenceParser:

    def __init__(self, document, direction, preprocessing, wmode,
            language, annotations, anno_attrs, delimiter, preserve):
        """Parse xml sentence files that have sentence ids in sequential
        order.

        Positional arguments:
        document -- Xml file to be parsed
        direction -- Source/target direction
        preprocessing -- Preprocessing type of the document
        wmode -- Write mode
        language -- Language id of the document
        annotations -- Print annotations
        anno_attrs -- Which annotations will be printed
        delimiter -- Annotation attribute delimiter
        preserve -- Preserve inline tags
        """

        self.document = document
        self.direction = direction
        self.pre = preprocessing
        self.annotations = annotations
        if self.annotations:
            self.anno_attrs = anno_attrs
        self.delimiter = delimiter
        self.preserve = preserve

        self.start = ''
        self.sid = ''
        self.chara = ''
        self.end = ''

        self.posses = []

        self.parser = xml.parsers.expat.ParserCreate()
        self.parser.StartElementHandler = self.start_element
        self.parser.CharacterDataHandler = self.char_data
        self.parser.EndElementHandler = self.end_element

        self.sfound = False
        self.efound = False

        self.oneLineSStart = False
        self.oneLineSEnd = False

        self.wmode = wmode
        self.language = language

        self.attrs = {}

        self.processSentence = {'parsed':self.processTokenizedSentence,
                                'xml':self.processTokenizedSentence,
                                'raw':self.processRawSentence,
                                'rawos':self.processRawSentenceOS}

    def start_element(self, name, attrs):
        self.start = name
        if 'id' in attrs.keys() and name == 's':
            self.attrs = attrs
            self.sfound = True
            self.oneLineSStart = True
            self.sid = attrs['id']
        if name == 'w' and self.annotations:
            self.posses = []
            if self.anno_attrs[0] == 'all_attrs':
                attributes = list(attrs.keys())
                attributes.sort()
                for a in attributes:
                    self.posses.append(attrs[a])
            for a in self.anno_attrs:
                if a in attrs.keys():
                    self.posses.append(attrs[a])

    def char_data(self, data):
        if self.sfound:
            self.chara += data

    def end_element(self, name):
        self.end = name
        if name == 's':
            self.efound = True
            self.oneLineSEnd = True

    def parseLine(self, line):
        """Parse a line of xml."""
        try:
            self.parser.Parse(line.strip())
        except xml.parsers.expat.ExpatError as e:
            raise SentenceParserError(
                'Sentence file "{document}" could not be parsed: '
                '{error}'.format(
                    document=self.document.name,
                    error=e.args[0]))

    def addToken(self, sentence):
        """Add a token to the sentence that is being built."""
        newSentence = sentence
        if self.sfound and  self.start == 'w' and self.end == 'w':
            newSentence = sentence + ' ' + self.chara
            self.chara = ''
            if self.annotations:
                for a in self.posses:
                    newSentence += self.delimiter + a
                self.posses = []
        return newSentence

    def processTokenizedSentence(self, sentence, ids, line):
        """Process and build a tokenized sentence."""
        newSentence, stop = sentence, 0
        if self.efound:
            self.sfound = False
            self.efound = False
            if self.sid in ids:
                stop = -1
            self.chara = ''
        if self.sid in ids:
            newSentence = self.addToken(sentence)
        if self.preserve and self.sfound and self.start not in ['s', 'w']:
            if type(line) == bytes:
                line = line.decode('utf-8')
            newSentence += line.strip()

        return newSentence, stop

    def processRawSentenceOS(self, sentence, ids, line):
        """Process and build a raw sentence in OpenSubtitles."""
        newSentence, stop = sentence, 0
        if self.efound:
            self.sfound = False
            self.efound = False
            if self.sid in ids:
                stop = -1
                self.chara = ''
        if self.sfound and self.sid in ids:
            if self.preserve:
                if self.start not in ['s', 'w']:
                    if type(line) == bytes:
                        line = line.decode('utf-8')
                    newSentence += line.strip()
            else:
                if self.start == 's' or self.start == 'time':
                    newSentence = self.chara
        return newSentence, stop

    def processRawSentence(self, sentence, ids, line):
        """Process and build a raw sentence."""
        if self.start == 's' and self.sid in ids:
            newSentence = self.chara
            self.chara = ''
            return newSentence, -1
        else:
            self.chara = ''
            return sentence, 0

    def addTuBeginning(self):
        """Add translation unit beginning to tmx."""
        sentences = ' '
        if self.direction == 'src':
            sentences = sentences + '\t\t<tu>\n'
        sentences = (sentences + '\t\t\t<tuv xml:lang="' + self.language +
            '"><seg>')
        return sentences

    def addSentence(self, sentences, sentence, sid):
        """Add a sentence to a sequence of sentences."""
        if self.wmode == 'normal':
            sentences = (sentences + '\n(' + self.direction + ')="' +
                str(sid) + '">' + sentence)
        elif self.wmode == 'tmx':
            sentences = sentences + ' ' + html.escape(sentence, quote=False)
            sentences = sentences.replace('<seg> ', '<seg>')
        elif self.wmode == 'moses':
            sentences = sentences + ' ' + sentence
        return sentences

    def addTuEnding(self, sentences):
        """Add translation unit ending to tmx."""
        sentences = sentences + '</seg></tuv>'
        if self.direction == 'trg':
            sentences = sentences + '\n\t\t</tu>'
        return sentences

    def readSentence(self, ids):
        """Read document and output sentence based on given sentence ids."""
        if len(ids) == 0 or ids[0] == '':
            return '', {}
        sentences = ''
        attrsList = []

        if self.wmode == 'tmx':
            sentences = self.addTuBeginning()

        eof = False
        for i in ids:
            sentence = ''
            while True:
                line = self.document.readline()
                if not line:
                    eof = True
                    break
                self.parseLine(line)
                newSentence, stop = self.processSentence[self.pre](
                    sentence, ids, line)
                sentence = newSentence
                if stop == -1:
                    break
            if eof:
                raise SentenceParserError(
                    'Sentence file "{}" could not be parsed with fast '
                    'parser'.format(self.document.name))

            if self.pre == 'xml' or self.pre == 'parsed':
                sentence = sentence.lstrip()

            sentences = self.addSentence(sentences, sentence, self.sid)
            attrsList.append(self.attrs)

        if self.wmode == 'tmx':
            sentences = self.addTuEnding(sentences)

        return sentences[1:], attrsList
