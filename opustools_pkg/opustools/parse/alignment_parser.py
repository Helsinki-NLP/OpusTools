from .block_parser import BlockParser, BlockParserError

class AlignmentParserError(Exception):

    def __init__(self, message):
        """Raise error when alignment parsing fails.

        Arguments:
        message -- Error message to be printed
        """
        self.message = message

def range_filter_type(src_range, trg_range):
    def range_filter(*args):
        """Flag if number of ids is outside given ranges"""

        #args = (s_id, t_id, link_attr)
        if src_range != 'all':
            if len(args[0]) not in src_range:
                return True
        if trg_range != 'all':
            if len(args[1]) not in trg_range:
                return True
        return False
    return range_filter

def attribute_filter_type(attribute, threshold):
    def attribute_filter(*args):
        """Flag if attribute score doesn't cross threshold"""

        #args = (s_id, t_id, link_attr)
        if attribute not in args[2].keys():
            #if attribute is not included in link_attr, should this return True or False?
            return True
        if float(args[2][attribute]) < threshold:
            return True
        return False
    return attribute_filter

def non_alignment_filter(*args):
    """Flag if there are no source or target ids"""

    #args = (s_id, t_id, link_attr)
    if len(args[0]) == 0 or len(args[1]) == 0:
        return True
    return False


class AlignmentParser:

    def __init__(self, alignment_file, src_trg_range=('all', 'all'),
            attr=None, thres=None, leave_non_alignments_out=False):
        """Parse xces alignment files and output sentence ids."""

        self.bp = BlockParser(alignment_file)
        self.filters = []

        src_range, trg_range = src_trg_range
        if src_trg_range != ('all', 'all'):
            nums = src_range.split('-')
            if nums[0].isnumeric():
                src_range = {i for i in range(int(nums[0]), int(nums[-1])+1)}
            nums = trg_range.split('-')
            if nums[0].isnumeric():
                trg_range = {i for i in range(int(nums[0]), int(nums[-1])+1)}
            self.filters.append(range_filter_type(src_range, trg_range))

        if attr and thres:
            self.filters.append(attribute_filter_type(attr, float(thres)))

        if leave_non_alignments_out:
            self.filters.append(non_alignment_filter)

    def add_link(self, link, attrs, src_id_set, trg_id_set):
        """Add link to set of links to be returned"""
        ids = link.attributes['xtargets'].split(';')
        s_id = ids[0].split()
        t_id = ids[1].split()

        for f in self.filters:
            if f(s_id, t_id, link.attributes):
                return attrs, src_id_set, trg_id_set

        attrs.append(link.attributes)
        src_id_set.update(s_id)
        trg_id_set.update(t_id)

        return attrs, src_id_set, trg_id_set

    def collect_links(self):
        """Collect links for a linkGrp"""

        attrs = []
        src_id_set, trg_id_set = set(), set()
        src_doc, trg_doc = None, None

        try:
            blocks = self.bp.get_complete_blocks()
            while blocks:
                for block in blocks:
                    if block.name == 'link':
                        self.add_link(block, attrs, src_id_set, trg_id_set)
                    elif block.name == 'linkGrp':
                        src_doc = block.attributes['fromDoc']
                        trg_doc = block.attributes['toDoc']
                        return attrs, src_id_set, trg_id_set, src_doc, trg_doc
                blocks = self.bp.get_complete_blocks()
        except BlockParserError as e:
            raise AlignmentParserError(
                'Error while parsing alignment file: {error}'.format(error=e.args[0]))

        return attrs, src_id_set, trg_id_set, src_doc, trg_doc

