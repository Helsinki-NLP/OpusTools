import sys

from .block_parser import BlockParser, BlockParserError


class SentenceParserError(Exception):

    def __init__(self, message):
        """Raise error when sentence parsing fails.

        Arguments:
        message -- Error message to be printed
        """
        self.message = message

def parse_type(preprocess, preserve, get_annotations):
    """Select function to be used for parsing"""

    def parse_s(block, sentence, sentences):
        sid = block.attributes['id']
        sentence = ' '.join(sentence)
        sentences[sid] = (sentence, block.attributes)
        sentence = []
        return sentence

    def parse_s_doc(block, sentence, sentences, doc_level_ids):
        sid = block.attributes['id']
        sentence = ' '.join(sentence)
        sentences[sid] = (sentence, block.attributes)
        doc_level_ids.append(sid)
        sentence = []
        return sentence

    def parse_s_raw(block, sentence, sentences):
        sid = block.attributes['id']
        sentence.append(block.data.strip())
        sentence = ' '.join(sentence)
        sentences[sid] = (sentence, block.attributes)
        sentence = []
        return sentence

    def parse_s_raw_doc(block, sentence, sentences, doc_level_ids):
        sid = block.attributes['id']
        sentence.append(block.data.strip())
        sentence = ' '.join(sentence)
        sentences[sid] = (sentence, block.attributes)
        doc_level_ids.append(sid)
        sentence = []
        return sentence

    def parse_w(bp, block, sentence, id_set):
        s_parent = bp.tag_in_parents('s', block)
        if s_parent and s_parent.attributes['id'] in id_set:
            data = block.data.strip()
            sentence.append(data)
        return sentence

    def parse_w_doc(bp, block, sentence, id_set):
        s_parent = bp.tag_in_parents('s', block)
        if s_parent:
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

    def parse_w_parsed_doc(bp, block, sentence, id_set):
        s_parent = bp.tag_in_parents('s', block)
        if s_parent:
            data = block.data.strip()
            data += get_annotations(block)
            sentence.append(data)
        return sentence

    def parse_time(bp, block, sentence, id_set):
        s_parent = bp.tag_in_parents('s', block)
        if s_parent and s_parent.attributes['id'] in id_set:
            sentence.append(block.get_raw_tag())
        return sentence

    def parse_time_doc(bp, block, sentence, id_set):
        s_parent = bp.tag_in_parents('s', block)
        if s_parent:
            sentence.append(block.get_raw_tag())
        return sentence

    def xml(bp, block, sentence, sentences, id_set):
        if block.name == 's' and block.attributes['id'] in id_set:
            sentence = parse_s(block, sentence, sentences)
        elif block.name == 'w':
            sentence = parse_w(bp, block, sentence, id_set)
        return sentence

    def xml_doc(bp, block, sentence, sentences, id_set, doc_level_ids):
        if block.name == 's':
            sentence = parse_s_doc(block, sentence, sentences, doc_level_ids)
        elif block.name == 'w':
            sentence = parse_w_doc(bp, block, sentence, id_set)
        return sentence

    def raw(bp, block, sentence, sentences, id_set):
        if block.name == 's' and block.attributes['id'] in id_set:
            sentence = parse_s_raw(block, sentence, sentences)
        return sentence

    def raw_doc(bp, block, sentence, sentences, id_set, doc_level_ids):
        if block.name == 's':
            sentence = parse_s_raw_doc(block, sentence, sentences, doc_level_ids)
        return sentence

    def parsed(bp, block, sentence, sentences, id_set):
        if block.name == 's' and block.attributes['id'] in id_set:
            sentence = parse_s(block, sentence, sentences)
        elif block.name == 'w':
            sentence = parse_w_parsed(bp, block, sentence, id_set)
        return sentence

    def parsed_doc(bp, block, sentence, sentences, id_set, doc_level_ids):
        if block.name == 's':
            sentence = parse_s_doc(block, sentence, sentences, doc_level_ids)
        elif block.name == 'w':
            sentence = parse_w_parsed_doc(bp, block, sentence, id_set)
        return sentence

    def xml_preserve(bp, block, sentence, sentences, id_set):
        if block.name == 's' and block.attributes['id'] in id_set:
            sentence = parse_s(block, sentence, sentences)
        elif block.name == 'w':
            sentence = parse_w(bp, block, sentence, id_set)
        elif block.name == 'time':
            sentence = parse_time(bp, block, sentence, id_set)
        return sentence

    def xml_preserve_doc(bp, block, sentence, sentences, id_set, doc_level_ids):
        if block.name == 's':
            sentence = parse_s_doc(block, sentence, sentences, doc_level_ids)
        elif block.name == 'w':
            sentence = parse_w_doc(bp, block, sentence, id_set)
        elif block.name == 'time':
            sentence = parse_time_doc(bp, block, sentence, id_set)
        return sentence

    def raw_preserve(bp, block, sentence, sentences, id_set):
        if block.name == 's' and block.attributes['id'] in id_set:
            sentence = parse_s_raw(block, sentence, sentences)
        elif block.name == 'time':
            sentence = parse_time(bp, block, sentence, id_set)
        return sentence

    def raw_preserve_doc(bp, block, sentence, sentences, id_set, doc_level_ids):
        if block.name == 's':
            sentence = parse_s_raw_doc(block, sentence, sentences)
        elif block.name == 'time':
            sentence = parse_time_doc(bp, block, sentence, id_set)
        return sentence

    def parsed_preserve(bp, block, sentence, sentences, id_set):
        if block.name == 's' and block.attributes['id'] in id_set:
            sentence = parse_s(block, sentence, sentences)
        elif block.name == 'w':
            sentence = parse_w_parsed(bp, block, sentence, id_set)
        elif block.name == 'time':
            sentence = parse_time(bp, block, sentence, id_set)
        return sentence

    def parsed_preserve_doc(bp, block, sentence, sentences, id_set, doc_level_ids):
        if block.name == 's':
            sentence = parse_s_doc(block, sentence, sentences)
        elif block.name == 'w':
            sentence = parse_w_parsed_doc(bp, block, sentence, id_set)
        elif block.name == 'time':
            sentence = parse_time_doc(bp, block, sentence, id_set)
        return sentence

    if preserve:
        if preprocess == 'xml':
            return xml_preserve
        if preprocess == 'xmldoc':
            return xml_preserve_doc
        if preprocess == 'raw':
            return raw_preserve
        if preprocess == 'rawdoc':
            return raw_preserve_doc
        if preprocess == 'parsed':
            return parsed_preserve
        if preprocess == 'parseddoc':
            return parsed_preserve_doc
    else:
        if preprocess == 'xml':
            return xml
        if preprocess == 'xmldoc':
            return xml_doc
        if preprocess == 'raw':
            return raw
        if preprocess == 'rawdoc':
            return raw_doc
        if preprocess == 'parsed':
            return parsed
        if preprocess == 'parseddoc':
            return parsed_doc


class SentenceParser:

    def __init__(self, document, preprocessing=None, anno_attrs=['all_attrs'],
            delimiter='|', preserve=None, doc_level=False, len_name=50):
        """Parse xml sentence files that have sentence ids in any order.

        Arguments:
        document -- Xml file to be parsed
        preprocessing -- Preprocessing type of the document
        anno_attrs -- Which annotations will be printed
        delimiter -- Annotation attribute delimiter
        preserve -- Preserve inline tags
        doc_level -- Print whole documents
        len_name -- Show the first N characters of file names when displaying progress
        """

        self.document = document
        self.delimiter = delimiter
        self.anno_attrs = anno_attrs
        self.doc_level = doc_level
        self.len_name = len_name
        if doc_level:
            self.parse_block = parse_type(preprocessing+'doc', preserve, self.get_annotations)
        else:
            self.parse_block = parse_type(preprocessing, preserve, self.get_annotations)

        self.sentences = {}
        self.doc_level_ids = []
        self.done = False

        self.data_tag = 'w'
        if preprocessing == 'raw':
            self.data_tag = 's'

    def store_sentences(self, id_set, doc_size, verbose=False):
        """Read document and store sentences in a dictionary."""
        bp = BlockParser(self.document, data_tag=self.data_tag, doc_size=doc_size, len_name=self.len_name)
        sentence = []
        sid = None

        cur_pos = 0

        stop = False

        try:
            blocks, cur_pos = bp.get_complete_blocks(cur_pos, verbose)
            while blocks and not stop:
                for block in blocks:
                    if self.doc_level:
                        sentence = self.parse_block(
                                bp, block, sentence, self.sentences, id_set, self.doc_level_ids)
                    else:
                        sentence = self.parse_block(
                                bp, block, sentence, self.sentences, id_set)
                    if len(self.sentences) == len(id_set) and not self.doc_level:
                        stop = True
                        break
                blocks, cur_pos= bp.get_complete_blocks(cur_pos, verbose)
            bp.close_document()
            if verbose:
                bp.report_progress(cur_pos)
                print("", file=sys.stderr)
        except BlockParserError as e:
            raise SentenceParserError(
                'Error while parsing sentence file: {error}'.format(error=e.args[0]))
        return bp.doc_size

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

        sentence = []
        attrsList = []
        for sid in ids:
            newSentence, attrs = self.get_sentence(sid)
            sentence.append(newSentence)
            attrsList.append(attrs)

        return sentence, attrsList
