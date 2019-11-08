import zipfile
import gzip
import xml.parsers.expat
import re

from .alignment_parser import AlignmentParser
from .sentence_parser import SentenceParser
from .exhaustive_sentence_parser import ExhaustiveSentenceParser
from ..opus_get import OpusGet

class LinksAlignmentParser(AlignmentParser):

    def __init__(self, source=None, target=None, result=None, mosessrc=None,
            mosestrg=None, fromto=None, switch_langs=None, src_cld2=None,
            trg_cld2=None, src_langid=None, trg_langid=None,
            leave_non_alignments_out=None, src_range=None, tgt_range=None,
            download_dir=None, directory=None, release=None, preprocess=None,
            source_zip=None, target_zip=None, suppress_prompts=None,
            fast=None, write_mode=None, print_file_names=None, write=None,
            attribute=None, print_annotations=None, target_annotations=None,
            source_annotations=None, change_annotation_delimiter=None,
            preserve_inline_tags=None, threshold=None, verbose=None):
        """Parse xces alignment files without outputting sentence pairs.

        source -- Source zip file name
        target -- Target zip file name
        result -- Result file name
        mosessrc -- Moses source result file name
        mosestrg -- Moses target result file name
        fromto -- Language direction
        switch_langs -- Switch language direction
        src_cld2 -- Filter source sentence by cld2 language ids and confidence
        trg_cld2 -- Filter target sentence by cld2 language ids and confidence
        src_langid -- Filter source sentence by langid.py language ids and
            confidence
        trg_langid -- Filter target sentence by langid.py language ids and
            confidence
        leave_non_alignment_out -- Leave non-alignments out
        src_range -- Number of source sentences in alignment (default all)
        trg_range -- Number of target sentences in alignment (default all)
        download_dir -- Set directory where files will be downloaded
        directory -- Corpus directory name
        release -- Corpus release version (default latest)
        preprocess -- Corpus preprocessing type (default xml)
        source_zip -- Source zip file
        target_zip -- Target zip file
        suppress_prompts -- Download necessary files without prompting "(y/n)"
        fast -- Use fast parsing (unstable)
        write_mode -- Set write mode (default normal)
        print_file_names -- Print file names when using moses format
        write -- Write to a given file name. Give two file names to write
            moses format to two files.
        attribute -- Set attribute for filtering
        print_annotations -- Print annotations if they exist
        source_annotations -- Set source annotations to be printed
            (default pos,lem)
        target_annotations -- Set target annotations to be printed
            (default pos,lem)
        change_annotation_delimiter -- Change annotation delimiter (default |)
        preserve_inline_tags -- Preserve inline tags within sentences
        threshold -- Set threshold for filtering attribute
        verbose -- Print progress messages when writing results to files
        """

        super().__init__(source=source, target=target, result=result,
            mosessrc=mosessrc, mosestrg=mosestrg, fromto=fromto,
            switch_langs=switch_langs, src_cld2=src_cld2, trg_cld2=trg_cld2,
            src_langid=src_langid, trg_langid=trg_langid,
            leave_non_alignments_out=leave_non_alignments_out,
            src_range=src_range, tgt_range=tgt_range,
            download_dir=download_dir, directory=directory, release=release,
            preprocess=preprocess, source_zip=source_zip, target_zip=target_zip,
            suppress_prompts=suppress_prompts, fast=fast,
            write_mode=write_mode, print_file_names=print_file_names,
            write=write, attribute=attribute,
            print_annotations=print_annotations,
            target_annotations=target_annotations,
            source_annotations=source_annotations,
            change_annotation_delimiter=change_annotation_delimiter,
            preserve_inline_tags=preserve_inline_tags, threshold=threshold,
            verbose=verbose)

        self.attribute = attribute
        self.end = ''

        self.alignParser.EndElementHandler = self.end_element

    def end_element(self, name):
        self.end = ''
        if name == 'linkGrp':
            self.end = name

    def initializeSentenceParsers(self, attrs):
        """Initialize sentence parsers."""
        #If link printing mode is activated, no need to open 
        #zipfiles and create sentence parsers, unless language
        #id confidence is tested
        if self.testConfidenceOn:
            self.openSentenceParsers(attrs)

    def readPair(self):
        """Read sentence pair based on a link in alignment file and output
        whether is is accepted.
        """
        #Tags other than link are printed in link printing mode, 
        #otherwise they are skipped
        if self.start != 'link':
            return 1

        srcAttrs, trgAttrs = {}, {}
        #No need to parse sentences in link printing mode, unless
        #language id confidence is tested
        if self.testConfidenceOn:
            sourceSen, srcAttrs = self.sPar.readSentence(self.fromids)
            targetSen, trgAttrs = self.tPar.readSentence(self.toids)

        #If either side of the alignment is outside of the sentence limit, 
        #or the attribute value is under the given attribute
        #threshold, return -1, which skips printing of the alignment in 
        #PairPrinter.outputPair()
        if (self.sentencesOutsideLimit() or
                (self.attribute != 'any' and self.overThreshold == False)):
            return -1
        elif (self.testConfidenceOn and
                not self.langIdConfidence(srcAttrs, trgAttrs)):
            return -1
        #If filtering non-alignments is set to True and either side of 
        #the alignment has no sentences:
        #return -1
        elif (self.nonAlignments and
                (self.fromids[0] == '' or self.toids[0] == '')):
            return -1
        else:
            self.overThreshold = False
            return 1

