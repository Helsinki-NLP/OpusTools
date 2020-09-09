from .block_parser import BlockParser

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

class AlignmentParser:

    def __init__(self, alignment_file, src_trg_range=('all', 'all'),
            attr=None, thres=None):
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
            if f(s_id, t_id, link.attributes):
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
