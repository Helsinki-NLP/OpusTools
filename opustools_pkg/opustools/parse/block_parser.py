import xml.parsers.expat
from ..util import file_open

class Block:

    def __init__(self, parent=None, name=None, data='', attributes=None):
        """Xml block instance held in memory by BlockParser"""
        self.parent = parent
        self.name = name
        self.data = data
        self.attributes = attributes

    def __str__(self):
        parent_name = None
        if self.parent:
            parent_name = self.parent.name
        return ('name: {name}, data: {data}, attributes: {attributes}, '
            'parent: {parent}'.format(name=self.name, data=repr(self.data),
                attributes=self.attributes, parent=parent_name))

class BlockParser:

    def __init__(self, document):
        """Parse an xml document line by line removing each element
        from memory as soon as its end tag is found.

        Positional arguments:
        document -- Xml document to be parsed
        """

        #self.document = file_open(document)
        self.document = document
        self.block = Block(name='root')
        self.completeBlocks = []

        def start_element(name, attrs):
            """Update current block"""
            sub_block = Block(parent=self.block, name=name, attributes=attrs)
            self.block = sub_block

        def end_element(name):
            """Update complete blocks, and move up one level on block tree"""
            self.completeBlocks.append(self.block)
            self.block = self.block.parent

        def char_data(data):
            """Update current block's character data"""
            self.block.data += data

        self.p = xml.parsers.expat.ParserCreate()

        self.p.StartElementHandler = start_element
        self.p.EndElementHandler = end_element
        self.p.CharacterDataHandler = char_data

    def parse_line(self, line):
        self.p.Parse(line)

    def close_document(self):
        self.document.close()

    def get_complete_blocks(self):
        """
        Read lines until one or more end tags are found on a single line,
        and return the block trees corresponding to those end tags.
        """
        for line in self.document:
            self.parse_line(line)
            if len(self.completeBlocks) > 0:
                ret_blocks = self.completeBlocks
                self.completeBlocks = []
                return ret_blocks

    @staticmethod
    def tag_in_parents(tag, block):
        """Check if given tag is in blocks parents"""
        while block:
            if block.name == tag:
                return True
            block = block.parent
        return False
