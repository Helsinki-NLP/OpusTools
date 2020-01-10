import html

from .block_parser import BlockParser

class ExhaustiveSentenceParser:

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

        self.document = document
        self.preserve = preserve
        self.pre = preprocessing
        self.wmode = wmode
        self.direction = direction
        self.annotations = annotations
        self.delimiter = delimiter
        self.anno_attrs = anno_attrs
        self.language = language

        self.sentences = {}
        self.done = False

    def storeSentences(self):
        """Read document and store sentences in a dictionary."""
        bp = BlockParser(self.document)
        sentence = []
        sid = None
        blocks = bp.get_complete_blocks()
        while blocks:
            for block in blocks:
                if block.name == 's':
                    sid = block.attributes['id']
                    if self.pre in ['raw', 'rawos']:
                        sentence.append(block.data.strip())
                        sentence = ''.join(sentence)
                    else:
                        sentence = ' '.join(sentence)
                    self.sentences[sid] = (sentence, block.attributes)
                    sentence = []
                    sid = None
                elif block.name == 'w' and bp.tag_in_parents('s', block):
                    data = block.data.strip()
                    if self.annotations:
                        data += self.getAnnotations(block)
                    sentence.append(data)
                elif self.preserve and block.name == 'time':
                    sentence.append(block.get_raw_tag())
            blocks = bp.get_complete_blocks()
        bp.document.close()

    def getAnnotations(self, block):
        annotations = ''
        if self.anno_attrs[0] == 'all_attrs':
            attributes = list(block.attributes.keys())
            attributes.sort()
            for a in attributes:
                annotations += self.delimiter + block.attributes[a]
        else:
            for a in self.anno_attrs:
                if a in block.attributes.keys():
                    annotations += self.delimiter + block.attributes[a]
        return annotations

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
