###########################################################
# Alignment and AlignmentStream usage:                    #
###########################################################
# stream = AlignmentStream('OpenSubtitles', 'de', 'en')   #
#                                                         #
# while stream.is_open():                                 #
#     alignment = stream.next()                           #
#                                                         #
#     for link in alignment.source:                       #
#         id, text = link['id'], link['text']             #
#                                                         #
#     overlap = alignment.overlap                         #
###########################################################


import gzip
from operator import itemgetter

from parse.alignment_parser import AlignmentParser


data_root = '/proj/nlpl/data/OPUS'


class OPUSReadArguments:
    def __init__(self, d, s, t, r='latest', p='xml', m='all', S='all', T='all', a='any', tr=0, l=True, ln=True, w=-1, wm='normal', e=False):
        self.__dict__.update(d=d, s=s, t=t, r=r, p=p, m=m, S=S, T=T, a=a, tr=tr, l=l, ln=ln, w=w, wm=wm, e=e)


class Alignment:
    def __init__(self, raw_line, parses):
        src_parses, trg_parses = parses

        self.source = [{'id': int(p.split('(src)="')[1].split('"')[0]), 'text': p.split('> ')[1]} for p in src_parses.split('\n')]
        self.target = [{'id': int(p.split('(trg)="')[1].split('"')[0]), 'text': p.split('> ')[1]} for p in trg_parses.split('\n')]

        overlap = str(raw_line).split('overlap="')[1].split('"')[0]

        self.overlap = float(overlap)

    def __parses_to_str(self, parses):
        texts = []

        for parse in sorted(parses, key=itemgetter('id')):
            texts.append(parse['text'])

        return ' '.join(texts)

    def source_str(self):
        return self.__parses_to_str(self.source)

    def target_str(self):
        return self.__parses_to_str(self.target)


class AlignmentStream:
    def __init__(self, dataset, s_lang, t_lang):
        # Initialize the alignment parser
        args = OPUSReadArguments(dataset, s_lang, t_lang)

        alignment_path = data_root + '/' + args.d + '/' + args.r + '/xml/' + args.s + '-' + args.t + '.xml.gz'
        source_path = data_root + '/' + args.d + '/' + args.r + '/' + args.p + '/' + args.s + '.zip'
        target_path = data_root + '/' + args.d + '/' + args.r + '/' + args.p + '/' + args.t + '.zip'

        self.parser = AlignmentParser(alignment_path, source_path, target_path, args, None)

        # Open the alignment file
        self.alignment_file = gzip.open(alignment_path)

        # Initialize attributes
        self.last_alignment = None
        self.is_done = False

    def next(self):
        seeking = True
        while seeking:
            line = self.alignment_file.readline()

            if line == '':
                self.alignment_file.close()
                self.last_alignment = None
                self.is_done = True
                seeking = False

            else:
                self.parser.parseLine(line)

                if self.parser.start == 'link':
                    parsed_pair = self.parser.readPair()

                    if parsed_pair != -1:
                        self.last_alignment = Alignment(line, parsed_pair)
                        seeking = False

        return self.last_alignment

    def peek(self):
        return self.last_alignment

    def is_open(self):
        return not self.is_done
