import html

from .block_parser import BlockParser

def parse_type(preprocess, preserve, get_annotations):
    """Select function to be used for parsing"""

    def parse_s(block, sentence, sentences):
        sid = block.attributes['id']
        sentence = ' '.join(sentence)
        sentences[sid] = (sentence, block.attributes)
        sentence = []
        return sentence

    def parse_s_raw(block, sentence, sentences):
        sid = block.attributes['id']
        sentence.append(block.data.strip())
        sentence = ' '.join(sentence)
        sentences[sid] = (sentence, block.attributes)
        sentence = []
        return sentence

    def parse_w(bp, block, sentence, id_set):
        s_parent = bp.tag_in_parents('s', block)
        if s_parent and s_parent.attributes['id'] in id_set:
            data = block.data.strip()
            sentence.append(data)
        return sentence

    def parse_w_parsed(bp, block, sentence, id_set):
        s_parent = bp.tag_in_parents('s', block)
        if s_parent and s_parent.attributes['id'] in id_set:
            data = block.data.strip()
            data += get_annotations(block)
            sentence.append(data)
        return sentence

    def parse_time(bp, block, sentence, id_set):
        s_parent = bp.tag_in_parents('s', block)
        if s_parent and s_parent.attributes['id'] in id_set:
            sentence.append(block.get_raw_tag())
        return sentence


    def xml(bp, block, sentence, sentences, id_set):
        if block.name == 's' and block.attributes['id'] in id_set:
            sentence = parse_s(block, sentence, sentences)
        elif block.name == 'w':
            sentence = parse_w(bp, block, sentence, id_set)
        return sentence

    def raw(bp, block, sentence, sentences, id_set):
        s_parent = bp.tag_in_parents('s', block)
        if block.name == 's' and block.attributes['id'] in id_set:
            sentence = parse_s_raw(block, sentence, sentences)
        elif block.name == 'w':
            sentence = parse_w(bp, block, sentence, id_set)
        return sentence

    def parsed(bp, block, sentence, sentences, id_set):
        s_parent = bp.tag_in_parents('s', block)
        if block.name == 's' and block.attributes['id'] in id_set:
            sentence = parse_s(block, sentence, sentences)
        elif block.name == 'w':
            sentence = parse_w_parsed(bp, block, sentence, id_set)
        return sentence

    def xml_preserve(bp, block, sentence, sentences, id_set):
        s_parent = bp.tag_in_parents('s', block)
        if block.name == 's' and block.attributes['id'] in id_set:
            sentence = parse_s(block, sentence, sentences)
        elif block.name == 'w':
            sentence = parse_w(bp, block, sentence, id_set)
        elif block.name == 'time':
            sentence = parse_time(bp, block, sentence, id_set)
        return sentence

    def raw_preserve(bp, block, sentence, sentences, id_set):
        s_parent = bp.tag_in_parents('s', block)
        if block.name == 's' and block.attributes['id'] in id_set:
            sentence = parse_s_raw(block, sentence, sentences)
        elif block.name == 'w':
            sentence = parse_w(bp, block, sentence, id_set)
        elif block.name == 'time':
            sentence = parse_time(bp, block, sentence, id_set)
        return sentence

    def parsed_preserve(bp, block, sentence, sentences, id_set):
        s_parent = bp.tag_in_parents('s', block)
        if block.name == 's' and block.attributes['id'] in id_set:
            sentence = parse_s(block, sentence, sentences)
        elif block.name == 'w':
            sentence = parse_w_parsed(bp, block, sentence, id_set)
        elif block.name == 'time':
            sentence = parse_time(bp, block, sentence, id_set)
        return sentence

    if preserve:
        if preprocess == 'xml':
            return xml_preserve
        if preprocess == 'raw':
            return raw_preserve
        if preprocess == 'parsed':
            return parsed_preserve
    else:
        if preprocess == 'xml':
            return xml
        if preprocess == 'raw':
            return raw
        if preprocess == 'parsed':
            return parsed


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

        self.parse_block = parse_type(preprocessing, preserve, self.get_annotations)

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
                sentence = self.parse_block(
                        bp, block, sentence, self.sentences, id_set)
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
