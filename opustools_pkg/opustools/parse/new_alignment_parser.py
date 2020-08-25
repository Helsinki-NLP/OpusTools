import re

from .block_parser import BlockParser

class AlignmentParser:

    def __init__(self, alignment_file):
        """Parse xces alignment files and output sentence ids."""

        self.bp = BlockParser(alignment_file)

    def get_link(self):
        blocks = self.bp.get_complete_blocks()
        while blocks:
            for block in blocks:
                if block.name == 'link':
                    return block
            blocks = self.bp.get_complete_blocks()

