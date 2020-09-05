import re

from .block_parser import BlockParser

class AlignmentParser:

    def __init__(self, alignment_file):
        """Parse xces alignment files and output sentence ids."""

        self.bp = BlockParser(alignment_file)

    def get_tag(self, tag):
        blocks = self.bp.get_complete_blocks()
        while blocks:
            for block in blocks:
                if block.name == tag:
                    return block
            blocks = self.bp.get_complete_blocks()

    def collect_links(self, last=None):
        """Collect links for a linkGrp"""

        attrs = []
        src_id_set, trg_id_set = set(), set()
        if last:
            ids = last.attributes['xtargets'].split(';')
            s_id = ids[0].split(' ')
            t_id = ids[1].split(' ')
            attrs.append(last.attributes)
            src_id_set.update(s_id)
            trg_id_set.update(t_id)
        last = None

        ids = None
        link = self.get_tag('link')
        if not link:
            return [], set(), set(), ids

        src_doc = link.parent.attributes['fromDoc']
        trg_doc = link.parent.attributes['toDoc']

        while link:
            ids = link.attributes['xtargets'].split(';')
            s_id = ids[0].split(' ')
            t_id = ids[1].split(' ')
            attrs.append(link.attributes)
            src_id_set.update(s_id)
            trg_id_set.update(t_id)

            link = self.get_tag('link')
            if (link and
                    link.parent.attributes['fromDoc'] != src_doc and
                        link.parent.attributes['toDoc'] != trg_doc):
                last = link
                break
        return attrs, src_id_set, trg_id_set, last
