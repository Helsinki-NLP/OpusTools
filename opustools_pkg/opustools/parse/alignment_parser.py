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

        self.alignment_file = alignment_file

        self.alignment_file.seek(0, 2)
        self.af_size = self.alignment_file.tell()
        self.alignment_file.seek(0)

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

    def add_link(self, link, attrs, src_id_set, trg_id_set, src_multis, trg_multis, src_multi_d, trg_multi_d, src_sid_to_lid, trg_sid_to_lid):
        """Add link to set of links to be returned"""
        ids = link.attributes['xtargets'].split(';')
        s_id = ids[0].split()
        t_id = ids[1].split()

        for f in self.filters:
            if f(s_id, t_id, link.attributes):
                return attrs, src_id_set, trg_id_set

        attrs.append(link.attributes)
        src_id_set.update(s_id)
        if len(s_id) > 1:
            # add each member of a multi-id separately in a set so we can identify multi-ids members
            # when reading individual sentence ids
            src_multis.update(s_id)
            # add multi-ids as tuples so we can find the correct multi-id members for a given link id
            src_multi_d[link.attributes['id']] = (tuple(s_id), [])
            # update sid_to_lid dictionary so we can find the link id for a given sentence id
            for s in s_id:
                src_sid_to_lid[s] = link.attributes['id']
        trg_id_set.update(t_id)
        if len(t_id) > 1:
            trg_multis.update(t_id)
            trg_multi_d[link.attributes['id']] = (tuple(t_id), [])
            for t in t_id:
                trg_sid_to_lid[t] = link.attributes['id']

        return attrs, src_id_set, trg_id_set, src_multis, trg_multis, src_multi_d, trg_multi_d, src_sid_to_lid, trg_sid_to_lid

    def collect_links(self, cur_pos=0, verbose=False):
        """Collect links for a linkGrp"""

        attrs = []
        src_id_set, trg_id_set = set(), set()
        src_doc, trg_doc = None, None

        try:
            blocks, cur_pos = self.bp.get_complete_blocks(cur_pos, verbose)
            while blocks:
                for block in blocks:
                    if block.name == 'link':
                        self.add_link(block, attrs, src_id_set, trg_id_set)
                    elif block.name == 'linkGrp':
                        src_doc = block.attributes['fromDoc']
                        trg_doc = block.attributes['toDoc']
                        return attrs, src_id_set, trg_id_set, src_doc, trg_doc, cur_pos
                blocks, cur_pos = self.bp.get_complete_blocks(cur_pos, verbose)
        except BlockParserError as e:
            raise AlignmentParserError(
                'Error while parsing alignment file: {error}'.format(error=e.args[0]))

        return attrs, src_id_set, trg_id_set, src_doc, trg_doc, cur_pos

    def collect_links_m(self, cur_pos=0, verbose=False):
        """Collect links for a linkGrp"""

        attrs = []
        src_id_set, trg_id_set = set(), set()
        # links with multiple ids on either side
        src_multis, trg_multis = set(), set()
        # sentence id tuple from link id
        src_multi_d, trg_multi_d = {}, {}
        # link id from a sentence id
        src_sid_to_lid, trg_sid_to_lid = {}, {}

        src_doc, trg_doc = None, None

        try:
            blocks, cur_pos = self.bp.get_complete_blocks(cur_pos, verbose)
            while blocks:
                for block in blocks:
                    if block.name == 'link':
                        self.add_link(block, attrs, src_id_set, trg_id_set, src_multis, trg_multis, src_multi_d, trg_multi_d, src_sid_to_lid, trg_sid_to_lid)
                    elif block.name == 'linkGrp':
                        src_doc = block.attributes['fromDoc']
                        trg_doc = block.attributes['toDoc']
                        return attrs, src_id_set, trg_id_set, src_doc, trg_doc, src_multis, trg_multis, src_multi_d, trg_multi_d, src_sid_to_lid, trg_sid_to_lid, cur_pos
                blocks, cur_pos = self.bp.get_complete_blocks(cur_pos, verbose)
        except BlockParserError as e:
            raise AlignmentParserError(
                'Error while parsing alignment file: {error}'.format(error=e.args[0]))

        return attrs, src_id_set, trg_id_set, src_doc, trg_doc, src_multis, trg_multis, src_multi_d, trg_multi_d, src_sid_to_lid, trg_sid_to_lid, cur_pos

