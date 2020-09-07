from .block_parser import BlockParser

def range_filter(*args):
    """Flag if number of ids is outside given ranges"""

    #args = (s_id, t_id, src_range, trg_range)
    if args[2] != 'all':
        if len(args[0]) not in args[2]:
            return True
    if args[3] != 'all':
        if len(args[1]) not in args[3]:
            return True
    return False

class AlignmentParser:

    def __init__(self, alignment_file, src_trg_range=('all', 'all')):
        """Parse xces alignment files and output sentence ids."""

        self.bp = BlockParser(alignment_file)
        self.filters = []

        self.src_range, self.trg_range = src_trg_range
        if src_trg_range != ('all', 'all'):
            if self.src_range.split('-')[0].isnumeric():
                nums = self.src_range.split('-')
                self.src_range = {i for i in range(int(nums[0]), int(nums[-1])+1)}
            if self.trg_range.split('-')[0].isnumeric():
                nums = self.trg_range.split('-')
                self.trg_range = {i for i in range(int(nums[0]), int(nums[-1])+1)}
            self.filters.append(range_filter)

    def get_tag(self, tag):
        blocks = self.bp.get_complete_blocks()
        while blocks:
            for block in blocks:
                if block.name == tag:
                    return block
            blocks = self.bp.get_complete_blocks()

    def add_link(self, link, attrs, src_id_set, trg_id_set):
        """Add link to set of links to be returned"""
        ids = link.attributes['xtargets'].split(';')
        s_id = ids[0].split(' ')
        t_id = ids[1].split(' ')

        for f in self.filters:
            if f(s_id, t_id, self.src_range, self.trg_range):
                return attrs, src_id_set, trg_id_set

        attrs.append(link.attributes)
        src_id_set.update(s_id)
        trg_id_set.update(t_id)

        return attrs, src_id_set, trg_id_set

    def collect_links(self, last=None):
        """Collect links for a linkGrp"""

        attrs = []
        src_id_set, trg_id_set = set(), set()
        if last:
            self.add_link(last, attrs, src_id_set, trg_id_set)

        last = None

        ids = None
        link = self.get_tag('link')
        if not link:
            return attrs, src_id_set, trg_id_set, last

        src_doc = link.parent.attributes['fromDoc']
        trg_doc = link.parent.attributes['toDoc']

        while link:
            self.add_link(link, attrs, src_id_set, trg_id_set)

            link = self.get_tag('link')
            if (link and
                    link.parent.attributes['fromDoc'] != src_doc and
                        link.parent.attributes['toDoc'] != trg_doc):
                last = link
                break
        return attrs, src_id_set, trg_id_set, last
