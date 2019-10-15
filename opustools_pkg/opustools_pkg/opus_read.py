import argparse
import gzip
import os
import xml.parsers.expat

from .parse.alignment_parser import AlignmentParser
from .parse.links_alignment_parser import LinksAlignmentParser
#from .parse.moses_read import MosesRead
from .opus_get import OpusGet

class AlignmentParserError(Exception):

    def __init__(self, message):
        """Raise error when alignment parsing fails.

        Keyword arguments:
        message -- Error message to be printed
        """
        self.message = message

class OpusRead:

    def __init__(self, directory=None, source=None, target=None,
            release='latest', preprocess='xml', maximum=-1, src_range='all',
            tgt_range='all', attribute='any', threshold=None,
            leave_non_alignments_out=False, write=None, write_mode='normal',
            print_file_names=False, fast=False,
            root_directory='/proj/nlpl/data/OPUS', alignment_file=-1,
            source_zip=None, target_zip=None, change_moses_delimiter='\t',
            print_annotations=False, source_annotations=['pos', 'lem'],
            target_annotations=['pos', 'lem'],
            change_annotation_delimiter='|',
            src_cld2=None, trg_cld2=None, src_langid=None, trg_langid=None,
            write_ids=None, suppress_prompts=False, download_dir='.',
            preserve_inline_tags=False, verbose=False):
        """Read xces alignment files and xml sentence files and output in
        desired format.

        Keyword arguments:
        directory -- Corpus directory name
        source -- Source language
        target -- Target language
        release -- Corpus release version (default latest)
        preprocess -- Corpus preprocessing type (default xml)
        maximum -- Maximum number of alignments outputted (default all)
        src_range -- Number of source sentences in alignment (default all)
        trg_range -- Number of target sentences in alignment (default all)
        attribute -- Set attribute for filtering
        threshold -- Set threshold for filtering attribute
        leave_non_alignment_out -- Leave non-alignments out
        write -- Write to a given file name. Give two file names to write
            moses format to two files.
        write_mode -- Set write mode (default normal)
        print_file_names -- Print file names when using moses format
        fast -- Use fast parsing (unstable)
        root_directory -- Set root directory for corpora
            (default /proj/nlpl/data/OPUS)
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
        verbose -- Print progress messages when writing results to files
        """

        self.fromto = sorted([source, target])
        fromto_copy = [source, target]
        self.switch_langs = fromto_copy != self.fromto

        self.src_range = src_range
        self.tgt_range = tgt_range

        self.verbose = verbose
        if write == None:
            self.verbose = False

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

        if alignment_file == -1:
            self.alignment = os.path.join(root_directory, directory, release,
                'xml', self.fromto[0]+'-'+self.fromto[1]+'.xml.gz')
        else:
            self.alignment = alignment_file

        source_file = os.path.join(root_directory, directory, release,
            preprocess, self.fromto[0]+'.zip')
        target_file = os.path.join(root_directory, directory, release,
            preprocess, self.fromto[1]+'.zip')
        moses_file = os.path.join(root_directory, directory, release, 'moses',
            self.fromto[0]+'-'+self.fromto[1]+'.txt.zip')

        self.resultfile = None
        self.mosessrc = None
        self.mosestrg = None
        if write_ids != None:
            self.id_file = open(write_ids, 'w', encoding='utf-8')

        if write != None:
            if write_mode == 'moses' and len(write) == 2:
                self.mosessrc = open(write[0], 'w', encoding='utf-8')
                self.mosestrg = open(write[1], 'w', encoding='utf-8')
            else:
                self.resultfile = open(write[0], 'w', encoding='utf-8')

        if write_mode == 'links':
            self.par = LinksAlignmentParser(source=source_file,
                target=target_file, result=self.resultfile,
                mosessrc=self.mosessrc, mosestrg=self.mosestrg,
                fromto=self.fromto, switch_langs=self.switch_langs,
                src_cld2=src_cld2, trg_cld2=trg_cld2, src_langid=src_langid,
                trg_langid=trg_langid,
                leave_non_alignments_out=leave_non_alignments_out,
                src_range=src_range, tgt_range=tgt_range,
                download_dir=download_dir, directory=directory,
                release=release, preprocess=preprocess, source_zip=source_zip,
                target_zip=target_zip, suppress_prompts=suppress_prompts,
                fast=fast, write_mode=write_mode,
                print_file_names=print_file_names, write=write,
                attribute=attribute, print_annotations=print_annotations,
                target_annotations=target_annotations,
                source_annotations=source_annotations,
                change_annotation_delimiter=change_annotation_delimiter,
                preserve_inline_tags=preserve_inline_tags, threshold=threshold,
                verbose=self.verbose)
        else:
            self.par = AlignmentParser(source=source_file, target=target_file,
                result=self.resultfile, mosessrc=self.mosessrc,
                mosestrg=self.mosestrg, fromto=self.fromto,
                switch_langs=self.switch_langs, src_cld2=src_cld2,
                trg_cld2=trg_cld2, src_langid=src_langid,
                trg_langid=trg_langid,
                leave_non_alignments_out=leave_non_alignments_out,
                src_range=src_range, tgt_range=tgt_range,
                download_dir=download_dir, directory=directory,
                release=release, preprocess=preprocess, source_zip=source_zip,
                target_zip=target_zip, suppress_prompts=suppress_prompts,
                fast=fast, write_mode=write_mode,
                print_file_names=print_file_names, write=write,
                attribute=attribute, print_annotations=print_annotations,
                target_annotations=target_annotations,
                source_annotations=source_annotations,
                change_annotation_delimiter=change_annotation_delimiter,
                preserve_inline_tags=preserve_inline_tags, threshold=threshold,
                verbose=self.verbose)

        self.write_mode = write_mode
        self.change_moses_delimiter = change_moses_delimiter
        self.write = write
        self.source_lang = source
        self.maximum = maximum
        self.download_dir = download_dir
        self.directory = directory
        self.release = release
        self.preprocess = preprocess
        self.suppress_prompts = suppress_prompts
        self.write_ids=write_ids

    def printPair(self, sPair):
        """Return sentence pair in printing format."""
        ret = ''
        if self.write_mode == 'links':
            ret = sPair
        else:
            if self.write_mode == 'moses':
                ret = sPair[0] + self.change_moses_delimiter + sPair[1]
            else:
                ret = sPair[0] + '\n' + sPair[1]
            if self.write_mode == 'normal':
                ret = ret + '\n================================'
        return ret

    def writePair(self, sPair):
        """Return sentence pair in writing format."""
        ret1, ret2 = '', ''
        if self.write_mode == 'links':
            ret1 = sPair+'\n'
        else:
            if self.write_mode == 'moses' and len(self.write) == 2:
                ret1 = sPair[0]+'\n'
                ret2 = sPair[1]+'\n'
            elif self.write_mode == 'moses' and len(self.write) == 1:
                ret1 = sPair[0] + self.change_moses_delimiter + sPair[1] + '\n'
            else:
                ret1 = sPair[0] + '\n' + sPair[1] + '\n'
            if self.write_mode == 'normal':
                ret1 = ret1 + '================================\n'
        return (ret1, ret2)

    def sendPairOutput(self, wpair):
        """Write pair to output file."""
        if self.write_mode == 'moses' and len(self.write) == 2:
            self.mosessrc.write(wpair[0])
            self.mosestrg.write(wpair[1])
        else:
            self.resultfile.write(wpair[0])

    def sendIdOutput(self, id_details):
        """Write sentence ids to output file."""
        id_line = '{0}\t{1}\t{2}\t{3}\t{4}\n'.format(
            id_details[0], id_details[1], ' '.join(id_details[2]),
            ' '.join(id_details[3]), id_details[4])
        self.id_file.write(id_line)

    def outputPair(self, par, line):
        """Read pair from alignment parser and output in appropriate way."""
        try:
            par.parseLine(line)
        except xml.parsers.expat.ExpatError as e:
            raise AlignmentParserError(
                'Alignment file "{alignment}" could not be parsed: '
                '{error}'.format(
                    alignment=self.alignment, error=e.args[0]))

        sPair = par.readPair()
        ftDocs = [par.fromDoc, par.toDoc]
        ftIds = [par.fromids, par.toids]

        if self.switch_langs and type(sPair) == tuple:
            copypair = [sPair[1], sPair[0]]
            sPair = copypair.copy()
            copypair = [ftDocs[1], ftDocs[0]]
            ftDocs = copypair.copy()
            copypair = [ftIds[1], ftIds[0]]
            ftIds = copypair.copy()

        id_details = (ftDocs[0], ftDocs[1], ftIds[0], ftIds[1], par.ascore)

        par.fromids = []
        par.toids = []

        #if the sentence pair doesn't meet the requirements in 
        #AlignmentParser.readLine(), return -1 as the sentence pair and 
        #return 0, which won't increment the pairs-counter in printPairs()
        if sPair == -1:
            return 0, sPair

        if sPair == 1:
            if type(line) == bytes:
                sPair = line.decode('utf-8')[:-1]
            else:
                sPair = line.rstrip()

        if self.write != None:
            wpair = self.writePair(sPair)
            self.sendPairOutput(wpair)
        else:
            print(self.printPair(sPair))

        if self.write_ids != None:
            self.sendIdOutput(id_details)

        #if the sentence pair is printed:
        #return 1, which will increment the pairs-counter in printPairs()        
        if par.start == 'link':
            par.start = ''
            return 1, sPair
        return 0, sPair

    def addTmxHeader(self):
        tmxheader = ('<?xml version="1.0" encoding="utf-8"?>\n<tmx '
            'version="1.4.">\n<header srclang="' + self.source_lang +
            '"\n\tadminlang="en"\n\tsegtype="sentence"\n\tdatatype='
            '"PlainText" />\n\t<body>')
        if self.write != None:
            self.resultfile.write(tmxheader + '\n')
        else:
            print(tmxheader)

    def addTmxEnding(self):
        if self.write != None:
            self.resultfile.write('\t</body>\n</tmx>')
        else:
            print('\t</body>\n</tmx>')

    def addLinkFileEnding(self):
        if self.write != None:
            self.resultfile.write(' </linkGrp>\n</cesAlign>')
        else:
            print(' </linkGrp>\n</cesAlign>')

    def addLinkGrpEnding(self, line):
        if type(line) == bytes:
            line = line.decode('utf-8')
        if (self.write_mode == 'links' and self.par.end == 'linkGrp'
                and line.strip() != '</linkGrp>'):
            if self.write != None:
                self.resultfile.write(' </linkGrp>\n')
            else:
                print(' </linkGrp>')
            self.par.end = ''

    def closeResultFiles(self):
        if self.write_mode == 'moses' and len(self.write) == 2:
            self.mosessrc.close()
            self.mosestrg.close()
        else:
            self.resultfile.close()

    def readAlignment(self, align):
        """Read and process alignment file."""
        if self.maximum == -1:
            for line in align:
                lastline = self.outputPair(self.par, line)[1]
                self.addLinkGrpEnding(line)
        else:
            while True:
                line = align.readline()
                if len(line) == 0:
                    break
                link, lastline = self.outputPair(self.par, line)
                self.addLinkGrpEnding(line)
                self.maximum -= link
                if self.maximum == 0:
                    break
        return lastline

    def printPairs(self):
        """Open alignment file, parse it and output sentence pairs."""
        if self.write_mode == 'tmx':
            self.addTmxHeader()

        if self.verbose: print('Reading alignment file ', end='')
        if self.alignment[-3:] == '.gz':
            local_align_name = os.path.join(self.download_dir,
                self.directory+'_'+ self.release+'_xml_'+self.fromto[0]+'-'+
                self.fromto[1]+'.xml.gz')
            #See if downloaded alignment file exists
            if os.path.exists(local_align_name):
                if self.verbose: print('"{}"'.format(local_align_name))
                gzipAlign = gzip.open(local_align_name)
                self.alignment = local_align_name
            #See if default alignment file exists
            elif os.path.exists(self.alignment):
                if self.verbose: print('"{}"'.format(self.alignment))
                gzipAlign = gzip.open(self.alignment)
            #Else download necessary files
            else:
                print(('\nAlignment file ' + self.alignment + ' not found. '
                    'The following files are available for downloading:\n'))
                arguments = {'source': self.fromto[0],
                    'target': self.fromto[1], 'directory': self.directory,
                    'release': self.release, 'preprocess': self.preprocess,
                    'download_dir': self.download_dir, 'list_resources': True}
                og = OpusGet(**arguments)
                og.get_files()
                arguments['list_resources'] = False
                if self.suppress_prompts:
                    arguments['suppress_prompts'] = True
                og = OpusGet(**arguments)
                og.get_files()

                if os.path.exists(local_align_name):
                    if self.verbose: print('"{}"'.format(local_align_name))
                    gzipAlign = gzip.open(local_align_name)
                    self.alignment=local_align_name
                else:
                    print('No alignment file "{default}" or "{downloaded}"'
                        ' found'.format(default=self.alignment,
                            downloaded=local_align_name))
                    return

            lastline = self.readAlignment(gzipAlign)
            gzipAlign.close()
        else:
            if self.verbose: print('"{}"'.format(self.alignment))
            if os.path.exists(self.alignment):
                with open(self.alignment) as xmlAlign:
                    lastline = self.readAlignment(xmlAlign)
            else:
                print('No alignment file "{}" found'.format(self.alignment))
                return

        if self.write_mode == 'links' and lastline != '</cesAlign>':
            self.addLinkFileEnding()

        if self.write_mode == 'tmx':
            self.addTmxEnding()

        self.par.closeFiles()

        if self.write != None:
            self.closeResultFiles()

        if self.write_ids != None:
            self.id_file.close()

        if self.verbose: print('Done')

'''
    def printPairsMoses(self):
        mread = MosesRead(self.moses, self.directory, self.fromto[0],
            self.fromto[1])
        if self.maximum == 'all':
            mread.printAll()
        else:
            print('\n# ' + self.moses + '\n\n================================')

            for i in range(int(self.maximum)):
                print(mread.readPair())

            mread.closeFiles()
'''
