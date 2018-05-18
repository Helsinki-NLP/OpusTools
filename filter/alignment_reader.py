##############################################################
# Usage:                                                     #
##############################################################
# reader = AlignmentReader('OpenSubtitles', 'de', 'en')      #
# writer = AlignmentWriter('out.de-en.de', 'out.de-en.en')   #
#                                                            #
# while reader.has_next():                                   #
#     alignment = reader.next()                              #
#     writer.write(alignment)                                #
#                                                            #
# writer.close() # The reader auto-closes after a full scan. #
##############################################################


import gzip

from filter.alignment import Alignment
from parse.alignment_parser import AlignmentParser


data_root = '/proj/nlpl/data/OPUS'


class OPUSReadArgs:
    def __init__(self, d, s, t, r='latest', p='xml', m='all', S='all', T='all', a='any', tr=0, l=True, ln=True, w=-1, wm='normal', e=True):
        self.__dict__.update(d=d, s=s, t=t, r=r, p=p, m=m, S=S, T=T, a=a, tr=tr, l=l, ln=ln, w=w, wm=wm, e=e)


class AlignmentReader:
    def __init__(self, dataset, s_lang, t_lang):
        # Initialize the alignment parser
        s_lang, t_lang = sorted([s_lang, t_lang])
        args = OPUSReadArgs(dataset, s_lang, t_lang)

        alignment_path = data_root + '/' + args.d + '/' + args.r + '/xml/' + args.s + '-' + args.t + '.xml.gz'
        source_path = data_root + '/' + args.d + '/' + args.r + '/' + args.p + '/' + args.s + '.zip'
        target_path = data_root + '/' + args.d + '/' + args.r + '/' + args.p + '/' + args.t + '.zip'

        self.__parser = AlignmentParser(alignment_path, source_path, target_path, args, None)

        # Open the alignment file
        self.__alignment_file = gzip.open(alignment_path)

        # Initialize attributes
        self.__last_alignment = None
        self.__is_done = False

    def peek(self):
        return self.__last_alignment

    def has_next(self):
        return not self.__is_done

    def next(self):
        seeking = True
        while seeking:
            line = self.__alignment_file.readline()

            if line == '':
                self.close()
                seeking = False

            else:
                self.__parser.parseLine(line)

                if self.__parser.start == 'link':
                    parsed_pair = self.__parser.readPair()

                    if parsed_pair != -1:
                        self.__last_alignment = Alignment(line, parsed_pair)
                        seeking = False

        return self.__last_alignment

    def close(self):
        self.__parser.closeFiles()
        self.__alignment_file.close()
        self.__last_alignment = None
        self.__is_done = True
