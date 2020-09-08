import html

from .block_parser import BlockParser

class ExhaustiveSentenceParser:

    def __init__(self, document, preprocessing=None, direction='src',
            wmode='normal', language=None, annotations=None,
            anno_attrs=['all_attrs'], delimiter='|', preserve=None):
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

        self.read_sent_f = {'normal': self.read_sentence_normal,
                            'tmx': self.read_sentence_tmx,
                            'moses': self.read_sentence_moses,
                            'new': self.read_sentence_new}

        self.sentences = {}
        self.done = False

    def store_sentences(self, id_set):
        """Read document and store sentences in a dictionary."""
        bp = BlockParser(self.document)
        sentence = []
        sid = None
        blocks = bp.get_complete_blocks()
        while blocks:
            for block in blocks:
                s_parent = bp.tag_in_parents('s', block)
                if block.name == 's' and block.attributes['id'] in id_set:
                    sid = block.attributes['id']
                    if self.pre in ['raw', 'rawos']:
                        sentence.append(block.data.strip())
                    sentence = ' '.join(sentence)
                    self.sentences[sid] = (sentence, block.attributes)
                    sentence = []
                    sid = None
                elif (block.name == 'w' and s_parent
                        and s_parent.attributes['id'] in id_set):
                    data = block.data.strip()
                    if self.pre == 'parsed':
                        data += self.get_annotations(block)
                    sentence.append(data)
                elif (self.preserve and block.name == 'time' and s_parent and
                        s_parent.attributes['id'] in id_set):
                    sentence.append(block.get_raw_tag())
            blocks = bp.get_complete_blocks()
        bp.close_document()

    def get_annotations(self, block):
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

    def get_sentence(self, sid):
        """Return a sentence based on given sentence id."""
        if sid in self.sentences.keys():
            return self.sentences[sid]
        else:
            return '', {}

    def read_sentence(self, ids):
        """Return a sequence of sentences based on given sentence ids."""
        if len(ids) == 0 or ids[0] == '':
            return '', []

        sentence, attrsList = self.read_sent_f[self.wmode](ids)

        if self.wmode == 'new':
            return sentence, attrsList

        return sentence[1:], attrsList

    def read_sentence_new(self, ids):
        sentence = []
        attrsList = []
        for sid in ids:
            newSentence, attrs = self.get_sentence(sid)
            sentence.append(newSentence)
            attrsList.append(attrs)

        return sentence, attrsList

    def read_sentence_normal(self, ids):
        sentence = ''
        attrsList = []
        for sid in ids:
            newSentence, attrs = self.get_sentence(sid)
            sentence = (sentence + '\n(' + self.direction + ')="' +
                str(sid) + '">' + newSentence)
            attrsList.append(attrs)

        return sentence, attrsList

    def read_sentence_tmx(self, ids):
        sentence = ''
        attrsList = []
        sentence = self.add_tu_beginning()
        for sid in ids:
            newSentence, attrs = self.get_sentence(sid)
            sentence = sentence + ' ' + html.escape(newSentence, quote=False)
            sentence = sentence.replace('<seg> ', '<seg>')
            attrsList.append(attrs)
        sentence = self.add_tu_ending(sentence)

        return sentence, attrsList

    def read_sentence_moses(self, ids):
        sentence = ''
        attrsList = []
        for sid in ids:
            newSentence, attrs = self.get_sentence(sid)
            sentence = sentence + ' ' + newSentence
            attrsList.append(attrs)

        return sentence, attrsList

    def add_tu_beginning(self):
        """Add translation unit beginning to tmx."""
        sentences = ' '
        if self.direction == 'src':
            sentences = sentences + '\t\t<tu>\n'
        sentences = (sentences + '\t\t\t<tuv xml:lang="' + self.language +
            '"><seg>')
        return sentences

    def add_tu_ending(self, sentences):
        """Add translation unit ending to tmx."""
        sentences = sentences + '</seg></tuv>'
        if self.direction == 'trg':
            sentences = sentences + '\n\t\t</tu>'
        return sentences
