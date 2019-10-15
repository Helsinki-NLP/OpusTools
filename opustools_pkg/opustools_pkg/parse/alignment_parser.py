import zipfile
import gzip
import xml.parsers.expat
import re
import os

from .sentence_parser import SentenceParser
from .exhaustive_sentence_parser import ExhaustiveSentenceParser
from ..opus_get import OpusGet

class AlignmentParser:

    def __init__(self, source=None, target=None, result=None, mosessrc=None,
            mosestrg=None, fromto=None, switch_langs=None, src_cld2=None,
            trg_cld2=None, src_langid=None, trg_langid=None,
            leave_non_alignments_out=None, src_range=None, tgt_range=None,
            download_dir=None, directory=None, release=None, preprocess=None,
            source_zip=None, target_zip=None, suppress_prompts=None,
            fast=None, write_mode=None, print_file_names=None, write=None,
            attribute=None, print_annotations=None, target_annotations=None,
            source_annotations=None, change_annotation_delimiter=None,
            preserve_inline_tags=None, threshold=None, verbose=False):
        """Parse xces alignment files and output sentence pairs.

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

        self.source = source
        self.target = target
        self.fromto = fromto
        self.switch_langs = switch_langs
        self.testConfidenceOn = False
        self.download_dir = download_dir
        self.directory = directory
        self.release = release
        self.preprocess = preprocess
        self.source_zip = source_zip
        self.target_zip = target_zip
        self.suppress_prompts = suppress_prompts
        self.fast = fast
        self.write_mode = write_mode
        self.print_file_names = print_file_names
        self.write = write
        self.attribute = attribute
        self.print_annotations = print_annotations
        self.target_annotations = target_annotations
        self.source_annotations = source_annotations
        self.change_annotation_delimiter = change_annotation_delimiter
        self.preserve_inline_tags = preserve_inline_tags
        self.threshold = threshold
        self.src_cld2 = src_cld2
        self.trg_cld2 = trg_cld2
        self.src_langid = src_langid
        self.trg_langid = trg_langid
        self.verbose = verbose

        for item in [src_cld2, trg_cld2, src_langid, trg_langid]:
            if item:
                self.testConfidenceOn = True

        self.start = ''

        self.toids = []
        self.fromids = []
        self.ascore = None
        self.fromDoc = ''
        self.toDoc = ''

        self.zipFilesOpened = False

        self.alignParser = xml.parsers.expat.ParserCreate()

        self.alignParser.StartElementHandler = self.start_element

        self.sPar = None
        self.tPar = None

        self.overThreshold = False
        self.nonAlignments = leave_non_alignments_out

        self.result = result
        self.mosessrc = mosessrc
        self.mosestrg = mosestrg

        self.slim = src_range.split('-')
        self.slim.sort()
        self.tlim = tgt_range.split('-')
        self.tlim.sort()

    def getZipFile(self, downloaded, default, localfile):
        """Open zip file."""
        if self.verbose: print('Opening zip archive ', end='')
        if localfile != None and os.path.exists(localfile):
            if self.verbose: print('"{}" ... '.format(localfile), end='')
            return zipfile.ZipFile(localfile, 'r')
        elif os.path.exists(downloaded):
            if self.verbose: print('"{}" ... '.format(downloaded), end='')
            return zipfile.ZipFile(downloaded, 'r')
        elif os.path.exists(default):
            if self.verbose: print('"{}" ... '.format(default), end='')
            return zipfile.ZipFile(default, 'r')

        return None

    def openZipFiles(self):
        """Open source and target zip files."""
        self.sourcezip = self.getZipFile(
            os.path.join(self.download_dir, self.directory+'_'+
                self.release+'_'+ self.preprocess+'_'+self.fromto[0]+'.zip'),
            self.source,
            self.source_zip)
        if self.verbose: print('Done')
        self.targetzip = self.getZipFile(
            os.path.join(self.download_dir, self.directory+'_'+
                self.release+'_'+ self.preprocess+'_'+self.fromto[1]+'.zip'),
            self.target,
            self.target_zip)
        if self.verbose: print('Done')

    def openSentenceParsers(self, attrs):
        """Open sentence parsers."""
        fromDoc = attrs['fromDoc']
        toDoc = attrs['toDoc']
        sourcefile_path = os.path.join(self.download_dir, fromDoc)
        targetfile_path = os.path.join(self.download_dir, toDoc)

        #See if source and target files exist locally outside zip archives
        if os.path.exists(sourcefile_path) and os.path.exists(targetfile_path):
            if sourcefile_path[-3:] == '.gz':
                sourcefile = gzip.open(sourcefile_path, 'rb')
            else:
                sourcefile = open(sourcefile_path, 'r')

            if targetfile_path[-3:] == '.gz':
                targetfile = gzip.open(targetfile_path, 'rb')
            else:
                targetfile = open(targetfile_path, 'r')
        #Else open local zip archives
        else:
            if self.zipFilesOpened == False:
                self.openZipFiles()
                if self.sourcezip and self.targetzip:
                    self.zipFilesOpened = True
                #If local zip archives don't exists, download them
                else:
                    print('\nZip files are not found. The following '
                        'files are available for downloading:\n')

                    arguments = {'source': self.fromto[0],
                        'target': self.fromto[1], 'directory': self.directory,
                        'release': self.release, 'preprocess': self.preprocess,
                        'download_dir': self.download_dir,
                        'list_resources': True}
                    og = OpusGet(**arguments)
                    og.get_files()
                    arguments['list_resources'] = False
                    if self.suppress_prompts:
                        arguments['suppress_prompts'] = True
                    og = OpusGet(**arguments)
                    og.get_files()

                    self.openZipFiles()
                    if self.sourcezip and self.targetzip:
                        self.zipFilesOpened = True
                    else:
                        exit('No zip files found')

            #Try OPUS style file names in zip archives first. In OPUS,
            #directory and preprocessing information need to be added and
            #the ".gz" ending needs to be removed.
            opus_style_name_source = (self.directory+'/'+ self.preprocess+'/'+
                fromDoc[:-3])
            opus_style_name_target = (self.directory+'/'+ self.preprocess+'/'+
                toDoc[:-3])

            if opus_style_name_source in self.sourcezip.namelist():
                sourcefile = self.sourcezip.open(opus_style_name_source, 'r')
            elif fromDoc in self.sourcezip.namelist():
                sourcefile = self.sourcezip.open(fromDoc, 'r')
            else:
                raise FileNotFoundError('No sentence file "{plain}" or '
                    '"{opus}" (OPUS format) found in {zipfile}'.format(
                        plain=fromDoc,
                        opus=opus_style_name_source,
                        zipfile=self.sourcezip.filename))

            if opus_style_name_target in self.targetzip.namelist():
                targetfile = self.targetzip.open(opus_style_name_target, 'r')
            elif toDoc in self.targetzip.namelist():
                targetfile = self.targetzip.open(toDoc, 'r')
            else:
                raise FileNotFoundError('No sentence file "{plain}" or '
                    '"{opus}" (OPUS format) found in {zipfile}'.format(
                        plain=toDoc,
                        opus=opus_style_name_target,
                        zipfile=self.targetzip.filename))

        if self.sPar and self.tPar:
            self.sPar.document.close()
            self.tPar.document.close()

        pre = self.preprocess
        if pre == 'raw' and self.directory == 'OpenSubtitles':
            pre = 'rawos'

        st = ['src', 'trg']
        if self.switch_langs:
            st = ['trg', 'src']

        if self.verbose: print('Reading source file "{source}" and target '
            'file "{target}"'.format(
                source=sourcefile.name,
                target=targetfile.name))
        if self.fast:
            self.sPar = SentenceParser(sourcefile, st[0], pre,
                self.write_mode, self.fromto[0], self.print_annotations,
                self.source_annotations,
                self.change_annotation_delimiter,
                self.preserve_inline_tags)
            self.tPar = SentenceParser(targetfile, st[1], pre,
                self.write_mode, self.fromto[1], self.print_annotations,
                self.target_annotations,
                self.change_annotation_delimiter,
                self.preserve_inline_tags)
        else:
            self.sPar = ExhaustiveSentenceParser(sourcefile, pre, st[0],
                self.write_mode, self.fromto[0], self.print_annotations,
                self.source_annotations,
                self.change_annotation_delimiter,
                self.preserve_inline_tags)
            self.sPar.storeSentences()
            self.tPar = ExhaustiveSentenceParser(targetfile, pre, st[1],
                self.write_mode, self.fromto[1], self.print_annotations,
                self.target_annotations,
                self.change_annotation_delimiter,
                self.preserve_inline_tags)
            self.tPar.storeSentences()

    def initializeSentenceParsers(self, attrs):
        """Initialize sentence parsers."""
        if self.write_mode == 'normal':
            docnames = ('\n# ' + attrs['fromDoc'] + '\n# ' +
                attrs['toDoc'] + '\n\n================================')
            if self.write != None:
                self.result.write(docnames + '\n')
            else:
                print(docnames)
        elif self.write_mode == 'moses' and self.print_file_names:
            sourceDoc = '\n<fromDoc>{}</fromDoc>'.format(attrs['fromDoc'])
            targetDoc = '\n<toDoc>{}</toDoc>'.format(attrs['toDoc'])
            if self.write != None:
                if self.result:
                    self.result.write(sourceDoc + targetDoc + '\n\n')
                else:
                    self.mosessrc.write(sourceDoc + '\n\n')
                    self.mosestrg.write(targetDoc + '\n\n')
            else:
                print(sourceDoc + targetDoc + '\n')
        self.openSentenceParsers(attrs)

    def processLink(self, attrs):
        """Process a link in a xces alignment file."""
        self.ascore = None
        if self.attribute in attrs.keys():
            self.ascore = attrs[self.attribute]
            if self.threshold != None:
                if float(self.ascore) >= float(self.threshold):
                    self.overThreshold = True
            else:
                self.overThreshold = True
        else:
            if self.threshold == None:
                self.overThreshold = True
        m = re.search('(.*);(.*)', attrs['xtargets'])
        self.toids = m.group(2).split(' ')
        self.fromids = m.group(1).split(' ')

    def start_element(self, name, attrs):
        self.start = name
        if name == 'linkGrp':
            self.fromDoc = attrs['fromDoc']
            self.toDoc = attrs['toDoc']
            self.initializeSentenceParsers(attrs)
        elif name == 'link':
            self.processLink(attrs)

    def parseLine(self, line):
        """Parse a line in alignment file."""
        self.start = ''
        self.alignParser.Parse(line)

    def sentencesOutsideLimit(self):
        """Test if numbers of sentences are outside specifed limits."""
        snum = len(self.fromids)
        tnum = len(self.toids)
        if snum == 0 or self.fromids[0] == '':
            snum = 0
        if tnum == 0 or self.toids[0] == '':
            tnum = 0

        return ((self.slim[0] != 'all' and (snum < int(self.slim[0]) or
            snum > int(self.slim[-1]))) or (self.tlim[0] != 'all' and
            (tnum < int(self.tlim[0]) or tnum > int(self.tlim[-1]))))

    def testConfidence(self, confidence, attrsList, ider):
        """See if language id confidence is over spcified limit."""
        if attrsList == []:
            return False
        if confidence:
            lan, conf = confidence
            for attrs in attrsList:
                if (lan != attrs[ider] or
                        float(conf) > float(attrs[ider+'conf'])):
                    return False
        return True

    def langIdConfidence(self, srcAttrs, trgAttrs):
        """Test language id confidence for all settings."""
        return (self.testConfidence(self.src_cld2, srcAttrs, 'cld2')
            and self.testConfidence(self.trg_cld2, trgAttrs, 'cld2')
            and self.testConfidence(self.src_langid, srcAttrs, 'langid')
            and self.testConfidence(self.trg_langid, trgAttrs, 'langid'))

    def readPair(self):
        """Read and output sentence pair based on a link in alignment file."""
        #tags other than link are printed in link printing mode, 
        #otherwise they are skipped
        if self.start != 'link':
            return -1

        srcAttrs, trgAttrs = {}, {}

        sourceSen, srcAttrs = self.sPar.readSentence(self.fromids)
        targetSen, trgAttrs = self.tPar.readSentence(self.toids)

        #if either side of the alignment is outside of the sentence limit, 
        #or the attribute value is under the given attribute
        #threshold, return -1, which skips printing of the alignment in 
        #PairPrinter.outputPair()
        if (self.sentencesOutsideLimit() or
                (self.attribute != 'any' and
                    self.overThreshold == False)):
            return -1
        elif (self.testConfidenceOn and
                not self.langIdConfidence(srcAttrs, trgAttrs)):
            return -1
        #if filtering non-alignments is set to True and either side of 
        #the alignment has no sentences:
        #return -1
        elif (self.nonAlignments and
                (self.fromids[0] == '' or self.toids[0] == '')):
            return -1
        else:
            self.overThreshold = False
            return sourceSen, targetSen

    def closeFiles(self):
        """Close zip files and document files."""
        if self.zipFilesOpened:
            self.sourcezip.close()
            self.targetzip.close()
        if self.sPar and self.tPar:
            self.sPar.document.close()
            self.tPar.document.close()
