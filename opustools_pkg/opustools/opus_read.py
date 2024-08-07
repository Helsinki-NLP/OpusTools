import logging
import os
import re
import sys
import tempfile

from .parse.alignment_parser import AlignmentParser
from .parse.sentence_parser import SentenceParser, SentenceParserError
from .util import file_open
from .formatting import *
from .opus_file_handler import OpusFileHandler


logger = logging.getLogger(__name__)


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

    def __init__(
            self, directory=None, source=None, target=None,
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
            preserve_inline_tags=False, n=None, N=None, chunk_size=1000000,
            verbose=False):
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
        chunk_size -- Number of sentence pairs in chunks to be processed
            (default 1000000)
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

        default_alignment = os.path.join(
            root_directory, directory, release, 'xml',
            self.fromto[0]+'-'+self.fromto[1]+'.xml.gz')
        if alignment_file == -1:
            self.alignment = default_alignment
        else:
            self.alignment = alignment_file

        dl_prefix = directory + '_' + release + '_' + preprocess + '_'
        if not source_zip:
            dl_src_zip = os.path.join(
                download_dir, dl_prefix + self.fromto[0] + '.zip')
            if os.path.isfile(dl_src_zip):
                source_zip = dl_src_zip
            else:
                source_zip = os.path.join(
                    root_directory, directory, release,
                    preprocess, self.fromto[0]+'.zip')
        if not target_zip:
            dl_trg_zip = os.path.join(
                download_dir, dl_prefix + self.fromto[1] + '.zip')
            if os.path.isfile(dl_trg_zip):
                target_zip = dl_trg_zip
            else:
                target_zip = os.path.join(
                    root_directory, directory, release,
                    preprocess, self.fromto[1]+'.zip')

        if write_ids:
            self.id_file = file_open(write_ids, 'w', encoding='utf-8')

        self.write_mode = write_mode
        self.write = write
        self.maximum = maximum
        self.preprocess = preprocess
        if print_annotations:
            self.preprocess = 'parsed'

        self.write_ids = write_ids

        self.preserve = preserve_inline_tags

        self.src_annot = source_annotations
        self.trg_annot = target_annotations
        self.annot_delimiter = change_annotation_delimiter

        self.skip_doc = skip_regex_type(n, N)

        self.chunk_size = chunk_size

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

        if preprocess == 'moses':
            if self.write_mode != 'moses':
                logger.warning("Only moses write_mode is supported for moses preprocessing. "
                               "Ignoring write_mode %s.", self.write_mode)
                self.write_mode = 'moses'
            return

        store_attrs = False
        if write_mode == "links" or write_ids is not None:
            store_attrs = True

        self.alignment = self.of_handler.open_alignment_file(self.alignment)
        self.alignmentParser = AlignmentParser(
            self.alignment, (src_range, tgt_range), attribute, threshold,
            store_attrs, leave_non_alignments_out)

    def printPairs(self):
        logger.debug("printPairs called!")
        resultfile = None
        mosessrc = None
        mosestrg = None
        id_file = None

        if self.write_ids:
            id_file = file_open(self.write_ids, 'w', encoding='utf-8')

        if self.write:
            if self.write_mode == 'moses' and len(self.write) == 2:
                mosessrc = file_open(self.write[0], mode='w', encoding='utf-8')
                mosestrg = file_open(self.write[1], mode='w', encoding='utf-8')
            else:
                resultfile = file_open(self.write[0], mode='w', encoding='utf-8')

        if self.preprocess == 'moses':
            # If preprocessing is moses, download
            if not self.write or len(self.write) != 2:
                # Write to current path and return
                if self.write and len(self.write) != 2:
                    logger.warning('"moses" preprocessing requires two output '
                                   'file names. Using default names.')
                moses_names = self.of_handler.open_moses_files(
                    outpath=self.of_handler.download_dir)
                logger.info('Moses files written to %s', ', '.join(moses_names))
                return
            with tempfile.TemporaryDirectory() as tmpdir:
                # Write to specified files
                logger.info('Extracting data...')
                moses_names = self.of_handler.open_moses_files(outpath=tmpdir)
                with file_open(os.path.join(tmpdir, moses_names[0])) as in1, \
                     file_open(os.path.join(tmpdir, moses_names[1])) as in2:
                    if self.switch_langs:
                        in1, in2 = in2, in1
                    for fin, fout in [(in1, mosessrc), (in2, mosestrg)]:
                        for line in fin:
                            fout.write(line)
                mosessrc.close()
                mosestrg.close()
                logger.info('Moses files written to %s', ', '.join(self.write))
            return

        self.add_file_header(resultfile)

        src_parser = None
        trg_parser = None

        total = 0
        stop = False
        cur_pos = 0

        prev_src_doc_name = None
        prev_trg_doc_name = None
        src_doc_size = -1
        trg_doc_size = -1

        while True:
            link_list, src_set, trg_set, attrs_list, src_doc_name, trg_doc_name, cur_pos = \
                self.alignmentParser.collect_links(cur_pos, self.chunk_size, self.verbose)

            if src_doc_name != prev_src_doc_name:
                src_doc_size = -1
            prev_src_doc_name = src_doc_name
            if trg_doc_name != prev_trg_doc_name:
                trg_doc_size = -1
            prev_trg_doc_name = trg_doc_name

            if self.verbose:
                print("", file=sys.stderr)

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
                    print('\n'+e.args[0]+'\nContinuing from next sentence file pair.', file=sys.stderr)
                    continue

                try:
                    src_parser = SentenceParser(
                        src_doc, preprocessing=self.preprocess, anno_attrs=self.src_annot,
                        preserve=self.preserve, delimiter=self.annot_delimiter)
                    src_doc_size = src_parser.store_sentences(src_set, src_doc_size, self.verbose)
                    trg_parser = SentenceParser(
                        trg_doc, preprocessing=self.preprocess, anno_attrs=self.trg_annot,
                        preserve=self.preserve, delimiter=self.annot_delimiter)
                    trg_doc_size = trg_parser.store_sentences(trg_set, trg_doc_size, self.verbose)
                except SentenceParserError as e:
                    print('\n'+e.message+'\nContinuing from next sentence file pair.', file=sys.stderr)
                    continue

            self.add_doc_names(
                src_doc_name, trg_doc_name, resultfile, mosessrc, mosestrg)

            len_link_list = len(link_list)

            for i, link_a in enumerate(link_list):
                if self.verbose:
                    if i % 1000 == 0 or i + 1 == len_link_list:
                        progress = str(round((i+1)/len_link_list*100, 2))
                        print("\x1b[2KWriting chunk ... {}%".format(progress), end="\r", file=sys.stderr)

                src_result, trg_result = self.format_pair(
                        link_a, src_parser, trg_parser, self.fromto)

                if src_result == -1:
                    continue

                link_attr = attrs_list[i] if i < len(attrs_list) else None

                self.out_put_pair(
                    src_result, trg_result, resultfile, mosessrc, mosestrg,
                    link_attr, id_file, src_doc_name, trg_doc_name)

                total += 1
                if total == self.maximum:
                    stop = True
                    break

            self.add_doc_ending(resultfile)

            if self.verbose and self.write:
                print("\033[F\033[F\033[F", end="", file=sys.stderr)

            if stop:
                break

        if self.verbose and self.write:
            print("\n\n", file=sys.stderr)

        self.add_file_ending(resultfile)

        self.alignmentParser.bp.close_document()

        if self.write:
            if self.write_mode == 'moses' and mosessrc:
                mosessrc.close()
                mosestrg.close()
            else:
                resultfile.close()

        if self.write_ids:
            id_file.close()

        self.of_handler.close_zipfiles()
