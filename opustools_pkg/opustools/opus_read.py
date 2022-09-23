import os
import re
import tempfile
import shutil

from .parse.alignment_parser import AlignmentParser
from .parse.sentence_parser import SentenceParser, SentenceParserError
from .util import file_open
from .formatting import *
from .opus_file_handler import OpusFileHandler

def skip_regex_type(n, N):
    "Select function to skip document names"

    def get_re(doc_name):
        return not re.search(n, doc_name)
    def skip_re(doc_name):
        return re.search(N, doc_name)
    def nothing(doc_name):
        return False

    if n:
        return get_re
    if N:
        return skip_re
    return nothing


class OpusRead:

    def __init__(self, directory=None, source=None, target=None,
            release='latest', preprocess='xml', maximum=-1, src_range='all',
            tgt_range='all', attribute=None, threshold=None,
            leave_non_alignments_out=False, write=None, write_mode='normal',
            print_file_names=False,
            root_directory='/projappl/nlpl/data/OPUS', alignment_file=-1,
            source_zip=None, target_zip=None, change_moses_delimiter='\t',
            print_annotations=False, source_annotations=['pos', 'lem'],
            target_annotations=['pos', 'lem'],
            change_annotation_delimiter='|',
            src_cld2=None, trg_cld2=None, src_langid=None, trg_langid=None,
            write_ids=None, suppress_prompts=False, download_dir='.',
            preserve_inline_tags=False, n=None, N=None, verbose=False):
        """Read xces alignment files and xml sentence files and output in
        desired format.

        Arguments:
        directory -- Corpus directory name
        source -- Source language
        target -- Target language
        release -- Corpus release version (default latest)
        preprocess -- Corpus preprocessing type (default xml)
        maximum -- Maximum number of alignments outputted (default all)
        src_range -- Number of source sentences in alignment (default all)
        tgt_range -- Number of target sentences in alignment (default all)
        attribute -- Set attribute for filtering
        threshold -- Set threshold for filtering attribute
        leave_non_alignment_out -- Leave non-alignments out
        write -- Write to a given file name. Give two file names to write
            moses format to two files.
        write_mode -- Set write mode (default normal)
        print_file_names -- Print file names when using moses format
        root_directory -- Set root directory for corpora
            (default /projappl/nlpl/data/OPUS)
        alignment_file -- Use given alignment file
        source_zip -- Use given source zip file
        target_zip -- Use given target zip file
        change_moses_delimiter -- Change moses delimiter (default tab)
        print_annotations -- Print annotations if they exist
        source_annotations -- Set source annotations to be printed
            (default pos,lem)
        target_annotations -- Set target annotations to be printed
            (default pos,lem)
        change_annotation_delimiter -- Change annotation delimiter (default |)
        src_cld2 -- Filter source sentence by cld2 language ids and confidence
        trg_cld2 -- Filter target sentence by cld2 language ids and confidence
        src_langid -- Filter source sentence by langid.py language ids and
            confidence
        trg_langid -- Filter target sentence by langid.py language ids and
            confidence
        write_ids -- Write sentence ids to a given file
        suppress_prompts -- Download necessary files without prompting "(y/n)"
        download_dir -- Directory where files will be downloaded (default .)
        preserve_inline_tags -- Preserve inline tags within sentences
        n -- Get only documents that match the regex
        N -- Skip all doucments that match the regex
        verbose -- Print progress messages
        """

        self.fromto = sorted([source, target])
        fromto_copy = [source, target]
        self.switch_langs = fromto_copy != self.fromto

        self.src_range = src_range
        self.tgt_range = tgt_range

        self.verbose = verbose
        if write:
            self.verbose = True

        if self.switch_langs:
            temp = src_range
            src_range = tgt_range
            tgt_range = temp
            temp = src_cld2
            src_cld2 = trg_cld2
            trg_cld2 = temp
            temp = src_langid
            src_langid = trg_langid
            trg_langid = temp
            temp = source_zip
            source_zip = target_zip
            target_zip = temp
            temp = source_annotations.copy()
            source_annotations = target_annotations.copy()
            target_annotations = temp.copy()

        lang_filters = [src_cld2, src_langid, trg_cld2, trg_langid]

        default_alignment = os.path.join(root_directory, directory, release,
                'xml', self.fromto[0]+'-'+self.fromto[1]+'.xml.gz')
        if alignment_file == -1:
            self.alignment = default_alignment
        else:
            self.alignment = alignment_file

        if not source_zip:
            dl_src_zip = os.path.join(download_dir, directory+'_'+release+'_'+
                preprocess+'_'+self.fromto[0]+'.zip')
            if os.path.isfile(dl_src_zip):
                source_zip = dl_src_zip
            else:
                source_zip = os.path.join(root_directory, directory, release,
                    preprocess, self.fromto[0]+'.zip')
        if not target_zip:
            dl_trg_zip = os.path.join(download_dir, directory+'_'+release+'_'+
                preprocess+'_'+self.fromto[1]+'.zip')
            if os.path.isfile(dl_trg_zip):
                target_zip = dl_trg_zip
            else:
                target_zip = os.path.join(root_directory, directory, release,
                    preprocess, self.fromto[1]+'.zip')

        self.resultfile = None
        self.mosessrc = None
        self.mosestrg = None

        self.id_file = None
        if write_ids:
            self.id_file = file_open(write_ids, 'w', encoding='utf-8')

        if write:
            if write_mode == 'moses' and len(write) == 2:
                self.mosessrc = file_open(write[0], mode='w', encoding='utf-8')
                self.mosestrg = file_open(write[1], mode='w', encoding='utf-8')
            else:
                self.resultfile = file_open(write[0], mode='w', encoding='utf-8')

        self.write_mode = write_mode
        self.write = write
        self.maximum = maximum
        self.preprocess = preprocess
        if print_annotations:
            self.preprocess = 'parsed'

        self.write_ids=write_ids

        self.preserve = preserve_inline_tags

        self.src_annot = source_annotations
        self.trg_annot = target_annotations
        self.annot_delimiter = change_annotation_delimiter

        self.skip_doc = skip_regex_type(n, N)

        self.add_file_header = file_header_type(write_mode, write, source)
        self.add_doc_names = doc_name_type(write_mode, write, print_file_names)
        self.add_doc_ending = doc_ending_type(write_mode, write)
        self.add_file_ending = file_ending_type(write_mode, write)

        self.out_put_pair = out_put_type(
                write_mode, write, write_ids, self.switch_langs, attribute,
                change_moses_delimiter)

        form_sent_langs = self.fromto.copy()
        if self.switch_langs:
            form_sent_langs = [self.fromto[1], self.fromto[0]]
        format_sentences = sentence_format_type(write_mode, form_sent_langs)

        check_filters, self.check_lang = check_lang_conf_type(lang_filters)
        self.format_pair = pair_format_type(
                write_mode, self.switch_langs, check_filters, self.check_lang,
                format_sentences)

        self.of_handler = OpusFileHandler(
                download_dir, source_zip, target_zip, directory, release,
                preprocess, self.fromto, suppress_prompts)

        self.alignment = self.of_handler.open_alignment_file(self.alignment)
        self.alignmentParser = AlignmentParser(self.alignment,
                (src_range, tgt_range), attribute, threshold,
                leave_non_alignments_out)

    def printPairs(self):

        self.add_file_header(self.resultfile)

        prev_src_doc_name = None
        prev_trg_doc_name = None

        src_parser = None
        trg_parser = None

        total = 0
        stop = False
        cur_pos = 0

        src_result = open('moses.src', 'a').close()
        trg_result = open('moses.trg', 'a').close()

        while True:
            link_attrs, src_set, trg_set, src_doc_name, trg_doc_name, src_multis, trg_multis, src_multi_d, trg_multi_d, src_sid_to_lid, trg_sid_to_lid, cur_pos = \
                self.alignmentParser.collect_links_m(cur_pos, self.verbose)

            src_list = [d['xtargets'].split(';')[0] for d in link_attrs]
            trg_list = [d['xtargets'].split(';')[1] for d in link_attrs]

            # Get two versions of lists: one with multi-ids in one string, and one with multi-ids
            # separated. Get a chunk size of both lists, and multi-id-separated list size ajusted.
            # Read chunk size number of sentences. If all ids from multi-id separated list are not 
            # included in the chunk, read more until they are. Can we assume that multi-ids are 
            # always next to each other or at least close by? If not then this does not work.

            if self.verbose: print("")

            if not src_doc_name:
                break

            if self.skip_doc(src_doc_name):
                continue

            if (self.write_mode != 'links' or
                    (self.write_mode == 'links' and self.check_lang)):
                try:
                    src_doc = self.of_handler.open_sentence_file(src_doc_name, 'src')
                    trg_doc = self.of_handler.open_sentence_file(trg_doc_name, 'trg')
                except KeyError as e:
                    print('\n'+e.args[0]+'\nContinuing from next sentence file pair.')
                    continue

                try:
                    src_parser = SentenceParser(src_doc,
                            preprocessing=self.preprocess, anno_attrs=self.src_annot,
                            preserve=self.preserve, delimiter=self.annot_delimiter)
                    #src_parser.store_sentences(src_set, self.verbose)
                    trg_parser = SentenceParser(trg_doc,
                            preprocessing=self.preprocess, anno_attrs=self.trg_annot,
                            preserve=self.preserve, delimiter=self.annot_delimiter)
                    #trg_parser.store_sentences(trg_set, self.verbose)
                except SentenceParserError as e:
                    print('\n'+e.message+'\nContinuing from next sentence file pair.')
                    continue

            chunk_size = 10

            # read_chunk has to take in unsplitted multi-ids and process them and output
            # all sentences associated with the ids in a single tuple. This way we can use the 
            # multi-id when sorting according to the link order.
            src_sents = src_parser.read_chunk(src_set, src_multis, src_multi_d, src_sid_to_lid, self.verbose)
            trg_sents = trg_parser.read_chunk(trg_set, trg_multis, trg_multi_d, trg_sid_to_lid, self.verbose)

            if self.verbose and self.write:
                    print("\033[F\033[F\033[F", end="")

            self.add_doc_names(src_doc_name, trg_doc_name,
                    self.resultfile, self.mosessrc, self.mosestrg)

            # empty ids is a problem because this introduces mutliple identical ids. However, we don't
            # actually need any sentence for the empty ids, so this can probably be solved some other
            # way.
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as sf, open('moses.src', 'r') as src_result:
                src_sents = [(k,v) for k,v in src_sents.items()]
                src_sents.sort(key=lambda i: src_list.index(i[0]))

                src_line = src_result.readline()
                sid2 = src_sents[0][0]
                text_part2 = ' '.join([item[0] for item in src_sents[0][1]])
                i = 0
                while True:
                    if src_line and '\t' in src_line:
                        sid1, text_part1 = src_line.split('\t')
                        try:
                            if src_list.index(sid1) < src_list.index(sid2):
                                sf.write(f'{sid1}\t{text_part1}')
                                src_line = src_result.readline()
                                continue
                        except:
                            import ipdb; ipdb.set_trace()

                    sf.write(f'{sid2}\t{text_part2}\n')
                    i += 1
                    if i == len(src_sents):
                        break
                    sid2 = src_sents[i][0]
                    text_part2 = ' '.join([item[0] for item in src_sents[i][1]])
            shutil.move(sf.name, 'moses.src')
                        
            with tempfile.NamedTemporaryFile() as tf:
                trg_sents = [(k,v) for k,v in trg_sents.items()]
                trg_sents.sort(key=lambda i: trg_list.index(i[0]))

            #for link_a in link_attrs:
            #    src_result, trg_result = self.format_pair(
            #            link_a, src_parser, trg_parser, self.fromto)

            #    if src_result == -1:
            #        continue

            #    print(src_result)

            #    self.out_put_pair(src_result, trg_result, self.resultfile,
            #            self.mosessrc, self.mosestrg, link_a, self.id_file,
            #            src_doc_name, trg_doc_name)

            #    total +=1
            #    if total == self.maximum:
            #        stop = True
            #        break

            self.add_doc_ending(self.resultfile)

            if stop:
                break

        if self.verbose and self.write:
            print("\n")

        self.add_file_ending(self.resultfile)

        self.alignmentParser.bp.close_document()

        if self.write:
            if self.write_mode == 'moses' and self.mosessrc:
                self.mosessrc.close()
                self.mosestrg.close()
            else:
                self.resultfile.close()

        if self.write_ids:
            self.id_file.close()

        self.of_handler.close_zipfiles()

