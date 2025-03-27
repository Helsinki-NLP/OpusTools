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

def attribute_add_type(store_attrs):
    """Store attributes only in links mode and when writing ids"""
    # args = (attrs_list, link_attrs)
    def normal_mode(*args):
        pass
    def attr_mode(*args):
        args[0].append(args[1])
    if store_attrs:
        return attr_mode
    else:
        return normal_mode

def non_alignment_filter(*args):
    """Flag if there are no source or target ids"""

    #args = (s_id, t_id, link_attr)
    if len(args[0]) == 0 or len(args[1]) == 0:
        return True
    return False


class AlignmentParser:

    def __init__(self, alignment_file, src_trg_range=('all', 'all'), attr=None, thres=None,
                 store_attrs=False, leave_non_alignments_out=False, len_name=50):
        """Parse xces alignment files and output sentence ids."""

        self.alignment_file = alignment_file

        self.alignment_file.seek(0, 2)
        self.af_size = self.alignment_file.tell()
        self.alignment_file.seek(0)

        self.bp = BlockParser(alignment_file, len_name=len_name)
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

        self.add_attributes = attribute_add_type(store_attrs)

        if leave_non_alignments_out:
            self.filters.append(non_alignment_filter)

    def add_link(self, link, link_list, src_id_set, trg_id_set, attrs):
        """Add link to set of links to be returned"""
        ids = link.attributes['xtargets'].split(';')
        s_id = ids[0].split()
        t_id = ids[1].split()

        for f in self.filters:
            if f(s_id, t_id, link.attributes):
                return link_list, src_id_set, trg_id_set, attrs

        self.add_attributes(attrs, link.attributes)
        link_list.append(tuple(ids))
        src_id_set.update(s_id)
        trg_id_set.update(t_id)

        return link_list, src_id_set, trg_id_set, attrs

    def collect_links(self, cur_pos=0, chunk_size=1000000, verbose=False):
        """Collect links for a linkGrp"""

        link_list = []
        attrs = []
        src_id_set, trg_id_set = set(), set()
        src_doc, trg_doc = None, None

        try:
            blocks, cur_pos = self.bp.get_complete_blocks(cur_pos, verbose)
            while blocks:
                for block in blocks:
                    if block.name == 'link':
                        self.add_link(block, link_list, src_id_set, trg_id_set, attrs)
                        if len(link_list) == chunk_size:
                            src_doc = block.parent.attributes['fromDoc']
                            trg_doc = block.parent.attributes['toDoc']
                            return link_list, src_id_set, trg_id_set, attrs, src_doc, trg_doc, cur_pos
                    elif block.name == 'linkGrp':
                        src_doc = block.attributes['fromDoc']
                        trg_doc = block.attributes['toDoc']
                        return link_list, src_id_set, trg_id_set, attrs, src_doc, trg_doc, cur_pos
                blocks, cur_pos = self.bp.get_complete_blocks(cur_pos, verbose)
        except BlockParserError as e:
            raise AlignmentParserError(
                'Error while parsing alignment file: {error}'.format(error=e.args[0]))

        return link_list, src_id_set, trg_id_set, attrs, src_doc, trg_doc, cur_pos

