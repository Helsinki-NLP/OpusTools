import argparse
import gzip

from .parse.alignment_parser import AlignmentParser
from .parse.links_alignment_parser import LinksAlignmentParser
#from .parse.moses_read import MosesRead
from .opus_get import OpusGet

class OpusRead:

    def __init__(self, arguments):
        parser = argparse.ArgumentParser(prog='opus_read',
            description='Read sentence alignment in XCES align format')

        parser.add_argument('-d', '--directory', help='Corpus name',
            metavar='corpus_name',
            required=True)
        parser.add_argument('-s', '--source', help='Source language',
            metavar='langid',
            required=True)
        parser.add_argument('-t', '--target', help='Target language',
            metavar='langid',
            required=True)
        parser.add_argument('-r', '--release', help='Release (default=latest)',
            metavar='version',
            default='latest')
        parser.add_argument('-p', '--preprocess',
            help='Preprocess-type (raw, xml or parsed, default=xml)',
            default='xml', choices=['raw', 'xml', 'parsed'])
        parser.add_argument('-m', '--max', help='Maximum number of alignments',
            default='all')
        parser.add_argument('-S', '--src_range',
            help='Number of source sentences in alignments (range is '
                'allowed, eg. -S 1-2)',
            default='all')
        parser.add_argument('-T', '--tgt_range',
            help='Number of target sentences in alignments (range is '
                'allowed, eg. -T 1-2)',
            default='all')
        parser.add_argument('-a', '--attribute',
            help='Set attribute for filttering',
            metavar='attribute',
            default='any')
        parser.add_argument('-tr', '--threshold',
            help='Set threshold for an attribute')
        parser.add_argument('-ln', '--leave_non_alignments_out',
            help='Leave non-alignments out',
            action='store_true')
        parser.add_argument('-w', '--write',
            metavar='file_name',
            help='Write to file. To print moses format in separate files, '
                'enter two file names. Otherwise enter one file name.',
            nargs='+')
        parser.add_argument('-wm', '--write_mode',
            help='Set write mode',
            default='normal', choices=['normal', 'moses', 'tmx', 'links'])
        parser.add_argument('-pn', '--print_file_names',
            help='Print file names when using moses format',
            action='store_true')
        parser.add_argument('-f', '--fast',
            help='Fast parsing. Faster than normal parsing, if you print '
                'a small part of the whole corpus, but requires the sentence '
                'ids in alignment files to be in sequence.',
            action='store_true')
        parser.add_argument('-rd', '--root_directory',
            help='Change root directory (default=/proj/nlpl/data/OPUS/)',
            metavar='path_to_dir',
            default='/proj/nlpl/data/OPUS/')
        parser.add_argument('-af', '--alignment_file',
            help='Use given alignment file',
            metavar='path_to_file', default=-1)
        parser.add_argument('-sz', '--source_zip',
            help='Use given source zip file',
            metavar='path_to_zip')
        parser.add_argument('-tz', '--target_zip',
            help='Use given target zip file',
            metavar='path_to_zip')
        parser.add_argument('-cm', '--change_moses_delimiter',
            help='Change moses delimiter (default=tab)',
            metavar='delimiter',
            default='\t')
        parser.add_argument('-pa', '--print_annotations',
            help='Print annotations, if they exist',
            action='store_true')
        parser.add_argument('-sa', '--source_annotations',
            help='Set source sentence annotation attributes to be printed'
                ', e.g. -sa pos lem. To print all available attributes use '
                '-sa all_attrs (default=pos,lem)',
            metavar='attribute',
            nargs='+',
            default=['pos', 'lem'])
        parser.add_argument('-ta', '--target_annotations',
            help='Set target sentence annotation attributes to be printed'
                ', e.g. -ta pos lem. To print all available attributes use '
                '-ta all_attrs (default=pos,lem)',
            metavar='attribute',
            nargs='+',
            default=['pos', 'lem'])
        parser.add_argument('-ca', '--change_annotation_delimiter',
            help='Change annotation delimiter (default=|)',
            metavar='delimiter',
            default='|')
        parser.add_argument('--src_cld2',
            help='Filter source sentences by their cld2 language id labels '
                'and confidence score, e.g. en 0.9',
            metavar=('lang_id', 'score'),
            nargs=2)
        parser.add_argument('--trg_cld2',
            help='Filter target sentences by their cld2 language id labels '
                'and confidence score, e.g. en 0.9',
            metavar=('lang_id', 'score'),
            nargs=2)
        parser.add_argument('--src_langid',
            help='Filter source sentences by their langid.py language id '
                'labels and confidence score, e.g. en 0.9',
            metavar=('lang_id', 'score'),
            nargs=2)
        parser.add_argument('--trg_langid',
            help='Filter target sentences by their langid.py language id '
                'labels and confidence score, e.g. en 0.9',
            metavar=('lang_id', 'score'),
            nargs=2)
        parser.add_argument('-id', '--write_ids',
            metavar='file_name',
            help='Write sentence ids to a file.')
        parser.add_argument('-q', '--suppress_prompts',
            help='Download necessary files without prompting "(y/n)"',
            action='store_true')
        parser.add_argument('-pi', '--preserve_inline_tags',
            help='Preserve inline tags within sentences',
            action='store_true')

        if len(arguments) == 0:
            self.args = parser.parse_args()
        else:
            self.args = parser.parse_args(arguments)

        self.fromto = sorted([self.args.source, self.args.target])
        fromto_copy = [self.args.source, self.args.target]
        self.switch_langs = fromto_copy != self.fromto

        if self.switch_langs:
            temp = self.args.src_range
            self.args.src_range = self.args.tgt_range
            self.args.tgt_range = temp
            temp = self.args.src_cld2
            self.args.src_cld2 = self.args.trg_cld2
            self.args.trg_cld2 = temp
            temp = self.args.src_langid
            self.args.src_langid = self.args.trg_langid
            self.args.trg_langid = temp
            temp = self.args.source_zip
            self.args.source_zip = self.args.target_zip
            self.args.target_zip = temp
            temp = self.args.source_annotations.copy()
            self.args.source_annotations = self.args.target_annotations.copy()
            self.args.target_annotations = temp.copy()

        if self.args.alignment_file == -1:
            self.alignment = (self.args.root_directory+self.args.directory+
                '/'+self.args.release+'/xml/'+self.fromto[0]+'-'+
                self.fromto[1]+'.xml.gz')
        else:
            self.alignment = self.args.alignment_file
        self.source = (self.args.root_directory+self.args.directory+'/'+
            self.args.release+'/'+
            self.args.preprocess+'/'+self.fromto[0]+'.zip')
        self.target = (self.args.root_directory+self.args.directory+'/'+
            self.args.release+'/'+
            self.args.preprocess+'/'+self.fromto[1]+'.zip')
        self.moses = (self.args.root_directory+self.args.directory+'/'+
            self.args.release+
            '/moses/'+self.fromto[0]+'-'+self.fromto[1]+'.txt.zip')

        self.resultfile = None
        self.mosessrc = None
        self.mosestrg = None
        if self.args.write_ids != None:
            self.id_file = open(self.args.write_ids, 'w', encoding='utf-8')

        if self.args.write != None:
            if self.args.write_mode == 'moses' and len(self.args.write) == 2:
                self.mosessrc = open(self.args.write[0], 'w', encoding='utf-8')
                self.mosestrg = open(self.args.write[1], 'w', encoding='utf-8')
            else:
                self.resultfile = open(self.args.write[0], 'w',
                    encoding='utf-8')

        if self.args.write_mode == 'links':
            self.par = LinksAlignmentParser(self.source, self.target,
                self.args, self.resultfile, self.mosessrc, self.mosestrg,
                self.fromto, self.switch_langs)
        else:
            self.par = AlignmentParser(self.source, self.target, self.args,
                self.resultfile, self.mosessrc, self.mosestrg, self.fromto,
                self.switch_langs)

    def printPair(self, sPair):
        ret = ''
        if self.args.write_mode == 'links':
            ret = sPair
        else:
            if self.args.write_mode == 'moses':
                ret = sPair[0] + self.args.change_moses_delimiter + sPair[1]
            else:
                ret = sPair[0] + '\n' + sPair[1]
            if self.args.write_mode == 'normal':
                ret = ret + '\n================================'
        return ret

    def writePair(self, sPair):
        ret1, ret2 = '', ''
        if self.args.write_mode == 'links':
            ret1 = sPair+'\n'
        else:
            if self.args.write_mode == 'moses' and len(self.args.write) == 2:
                ret1 = sPair[0]+'\n'
                ret2 = sPair[1]+'\n'
            elif self.args.write_mode == 'moses' and len(self.args.write) == 1:
                ret1 = sPair[0] + self.args.change_moses_delimiter + sPair[1] + '\n'
            else:
                ret1 = sPair[0] + '\n' + sPair[1] + '\n'
            if self.args.write_mode == 'normal':
                ret1 = ret1 + '================================\n'
        return (ret1, ret2)

    def sendPairOutput(self, wpair):
        if self.args.write_mode == 'moses' and len(self.args.write) == 2:
            self.mosessrc.write(wpair[0])
            self.mosestrg.write(wpair[1])
        else:
            self.resultfile.write(wpair[0])

    def sendIdOutput(self, id_details):
        id_line = '{0}\t{1}\t{2}\t{3}\t{4}\n'.format(
            id_details[0], id_details[1], ' '.join(id_details[2]),
            ' '.join(id_details[3]), id_details[4])
        self.id_file.write(id_line)

    def outputPair(self, par, line):
        par.parseLine(line)
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

        if self.args.write != None:
            wpair = self.writePair(sPair)
            self.sendPairOutput(wpair)
        else:
            print(self.printPair(sPair))

        if self.args.write_ids != None:
            self.sendIdOutput(id_details)

        #if the sentence pair is printed:
        #return 1, which will increment the pairs-counter in printPairs()        
        if par.start == 'link':
            par.start = ''
            return 1, sPair
        return 0, sPair

    def addTmxHeader(self):
        tmxheader = ('<?xml version="1.0" encoding="utf-8"?>\n<tmx '
            'version="1.4.">\n<header srclang="' + self.args.source +
            '"\n\tadminlang="en"\n\tsegtype="sentence"\n\tdatatype='
            '"PlainText" />\n\t<body>')
        if self.args.write != None:
            self.resultfile.write(tmxheader + '\n')
        else:
            print(tmxheader)

    def addTmxEnding(self):
        if self.args.write != None:
            self.resultfile.write('\t</body>\n</tmx>')
        else:
            print('\t</body>\n</tmx>')

    def addLinkFileEnding(self):
        if self.args.write != None:
            self.resultfile.write(' </linkGrp>\n</cesAlign>')
        else:
            print(' </linkGrp>\n</cesAlign>')
    
    def addLinkGrpEnding(self, line):
        if type(line) == bytes:
            line = line.decode('utf-8')
        if (self.args.write_mode == 'links' and self.par.end == 'linkGrp' 
            and line.strip() != '</linkGrp>'):
            if self.args.write != None:
                self.resultfile.write(' </linkGrp>\n')
            else:
                print(' </linkGrp>')
            self.par.end = ''

    def closeResultFiles(self):
        if self.args.write_mode == 'moses' and len(self.args.write) == 2:    
            self.mosessrc.close()
            self.mosestrg.close()
        else:
            self.resultfile.close()

    def readAlignment(self, align):
        if self.args.max == 'all':
            for line in align:
                lastline = self.outputPair(self.par, line)[1]
                self.addLinkGrpEnding(line)
        else:
            pairs = int(self.args.max)
            while True:
                line = align.readline()
                if len(line) == 0:
                    break
                link, lastline = self.outputPair(self.par, line)
                self.addLinkGrpEnding(line)
                pairs -= link
                if pairs == 0:
                    break
        return lastline

    def printPairs(self):
        if self.args.write_mode == 'tmx':
            self.addTmxHeader()

        if self.alignment[-3:] == '.gz':
            try:
                try:
                    gzipAlign = gzip.open((self.args.directory+'_'+
                        self.args.release+'_xml_'+self.fromto[0]+'-'+
                        self.fromto[1]+'.xml.gz'))
                except FileNotFoundError:
                    gzipAlign = gzip.open(self.alignment)
            except FileNotFoundError:
                print(('\nAlignment file ' + self.alignment + ' not found. '
                    'The following files are available for downloading:\n'))
                arguments = ['-s', self.fromto[0], '-t', self.fromto[1], '-d',
                    self.args.directory, '-r', self.args.release, '-p',
                    self.args.preprocess, '-l']
                og = OpusGet(arguments)
                og.get_files()
                arguments.remove('-l')
                if self.args.suppress_prompts:
                    arguments.append('-q')
                og = OpusGet(arguments)
                og.get_files()
                try:
                    gzipAlign = gzip.open((self.args.directory+'_'+
                        self.args.release+'_xml_'+
                        self.fromto[0]+'-'+self.fromto[1]+'.xml.gz'))
                except FileNotFoundError:
                    return

            lastline = self.readAlignment(gzipAlign)
            gzipAlign.close()
        else:
            with open(self.alignment) as xmlAlign:
                lastline = self.readAlignment(xmlAlign)

        if self.args.write_mode == 'links' and lastline != '</cesAlign>':
            self.addLinkFileEnding()

        if self.args.write_mode == 'tmx':
            self.addTmxEnding()

        self.par.closeFiles()

        if self.args.write != None:
            self.closeResultFiles()

        if self.args.write_ids != None:
            self.id_file.close()

'''
    def printPairsMoses(self):
        mread = MosesRead(self.moses, self.args.directory, self.fromto[0], 
            self.fromto[1])
        if self.args.max == 'all':
            mread.printAll()
        else:
            print('\n# ' + self.moses + '\n\n================================')
    
            for i in range(int(self.args.max)):
                print(mread.readPair())

            mread.closeFiles()
'''
